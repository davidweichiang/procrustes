#!/usr/bin/env python

from argparse import ArgumentParser, Namespace
from functools import partial
from os import listdir, path
from multiprocessing import Pool
from sys import stderr
from typing import Any, Callable, Dict, List, TextIO, Tuple, Type, Union

from numpy import finfo, iinfo

from utils.algorithms.data_structures.exceptions import EditFailure
from utils.algorithms.options.cost_functions import ENTRY_SIZES, get_cost_function
from utils.algorithms.wf_edit_distance import calculate_minimum_edit_distance, collect_alignment_path, PointerTable
from utils.modes.alignment import Alignment
from utils.modes.tree import TreeAlignment
from utils.modes.word import WordAlignment
from utils.modes.xml import XMLAlignment
from utils.segmentation.interface import get_segmentation_function
from utils.zipping.interface import get_zip_function


def get_alignment_type(alignment_name: str) -> Type[Alignment]:
    if alignment_name == "word":
        alignment_type = WordAlignment
    elif alignment_name == "tree":
        alignment_type = TreeAlignment
    elif alignment_name == "xml":
        alignment_type = XMLAlignment
    else:
        raise ValueError(f"The mode <{alignment_name}> is not currently supported.")
    return alignment_type


def gather_filepaths(directory_path: str, file_iterator_path: str) -> List[str]:
    filepaths: List[str] = []
    for filename in listdir(file_iterator_path):
        new_filepath: str = f"{directory_path}/{filename}"
        filepaths.append(new_filepath)
    return filepaths


def align_files(source_filepath: str, target_filepath: str, output_filepath: Union[str, None],
                alignment_type: Type[Alignment], alignment_kwargs: Dict[str, Any], **kwargs):
    source_file: TextIO = open(source_filepath, mode="r", encoding="utf-8")
    target_file: TextIO = open(target_filepath, mode="r", encoding="utf-8")
    output_file: TextIO = open(output_filepath, mode="w+", encoding="utf-8") if output_filepath is not None else None

    zip_function: Callable = kwargs["zipper"]
    ed_cost_function: Callable = kwargs["cost_function"]
    data_type_base: str = kwargs["data_type"]
    for line_index, (source_line, target_line) in enumerate(zip_function(source_file, target_file)):
        # TODO: what's the correct type annotation for alignment_type here?
        source_label = alignment_type(source_line, **alignment_kwargs)   # type: ignore
        target_spaced_line: str = " ".join(target_line.split())

        data_type_size: str = get_entry_size(data_type_base, source_label.get_characters(), target_spaced_line)
        full_data_type: str = data_type_base + data_type_size

        pointer_table: PointerTable = {}
        edit_distance, d_table = calculate_minimum_edit_distance(
            source_label.get_characters(), target_spaced_line, ed_cost_function, full_data_type, pointer_table
        )
        line_alignment: List[Tuple[int, int]] = collect_alignment_path(d_table, pointer_table)

        if kwargs["verbose"] is True:
            print(f"SOURCE LABEL: {source_label}\n", file=stderr)
            print(f"SOURCE LABEL CHARACTERS: {source_label.get_characters()}\n", file=stderr)
            print(f"TARGET LINE: {target_spaced_line}\n", file=stderr)
            for source_index, target_index in line_alignment:
                source_match: str = source_label.get_characters()[source_index]
                target_match: str = target_spaced_line[target_index]
                print(f"[{source_match}]-[{target_match}]", file=stderr)

        source_label.project(target_spaced_line, line_alignment)
        if source_label.get_characters() != target_spaced_line:
            raise EditFailure(f'{source_label.get_characters()} != {target_spaced_line}')

        if output_file is not None:
            output_file.write(f"{source_label}")
        else:
            print(f"PROJECTION: {source_label}")

    source_file.close()
    target_file.close()
    output_file.close()


def get_entry_size(base_type: str, source_text: str, target_text: str) -> str:
    max_length: int = max(len(source_text), len(target_text))
    if base_type == "float":
        info_function: Callable = finfo
    elif base_type == "int":
        info_function = iinfo
    else:
        raise ValueError(f"Unrecognized base type <{base_type}>.")

    for entry_size in ENTRY_SIZES:
        # Since the edit distance can be at most max_length for Levenshtein edit distance,
        #   we can compute the needed data size for the d_table to support smaller or larger data comparisons.
        if max_length < info_function(base_type + entry_size).max:
            data_entry_size: str = entry_size
            break
    else:
        raise ValueError(f"The maximum document length, <{max_length}>, is too large to be supported.")
    return data_entry_size


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("source", type=str)
    parser.add_argument("target", type=str)
    parser.add_argument("--cost-function", type=get_cost_function, default="procrustes-levenshtein")
    parser.add_argument("--flip", action="store_true", default=False, help="operate on target side instead of source")
    parser.add_argument("--mode", "-m", type=get_alignment_type, default=WordAlignment, help="input/output mode")
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--processes", type=int, default=1)
    parser.add_argument("--segmenter", type=get_segmentation_function, default=None)
    parser.add_argument("--verbose", action="store_true", default=False, help="verbose output")
    parser.add_argument("--zipper", type=get_zip_function, default="line")
    args: Namespace = parser.parse_args()

    if not path.exists(args.source):
        raise ValueError(f"The given source path, <{args.source}>, does not exist.")
    elif not path.exists(args.target):
        raise ValueError(f"The given target path, <{args.target}>, does not exist.")
    elif path.isfile(args.source) and path.isfile(args.target):
        source_filepaths: List[str] = [args.source]
        target_filepaths: List[str] = [args.target]
        output_filepaths: List[str] = [args.output]
    elif path.isfile(args.source) and path.isdir(args.target):
        raise NotImplementedError
    elif path.isdir(args.source) and path.isfile(args.target):
        raise NotImplementedError
    elif path.isdir(args.source) and path.isdir(args.target):
        source_filepaths: List[str] = gather_filepaths(args.source, args.source)
        target_filepaths: List[str] = gather_filepaths(args.target, args.target)
        output_filepaths: List[str] = gather_filepaths(args.output, args.target)
    else:
        raise ValueError("Invalid combination of source and target filepaths.")

    combined_filepaths: List[Tuple[str, str, str]] = list(zip(source_filepaths, target_filepaths, output_filepaths))
    alignment_class: Type[Alignment] = args.mode
    alignment_class_kwargs: Dict[str, Any] = {
        "is_flipped": args.flip,
        "segmentation_function": args.segmenter
    }

    cost_function, data_type = args.cost_function
    other_kwargs: Dict[str, Any] = {
        "cost_function": cost_function,
        "data_type": data_type,
        "verbose": args.verbose,
        "zipper": args.zipper
    }

    if args.processes > 1:
        with Pool(processes=args.processes) as pool:
            aligner_partial = partial(
                align_files, alignment_type=alignment_class, alignment_kwargs=alignment_class_kwargs, **other_kwargs
            )
            pool.starmap(aligner_partial, combined_filepaths)
    elif args.processes == 1:
        for source_path, target_path, output_path in combined_filepaths:
            align_files(source_path, target_path, output_path, alignment_class, alignment_class_kwargs, **other_kwargs)
    else:
        raise ValueError("An invalid number of processes was supplied. Please supply a value greater than 0.")
