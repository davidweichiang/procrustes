#!/usr/bin/env python

from argparse import ArgumentParser, Namespace
from functools import partial
from os import listdir, path
from multiprocessing import Pool
from sys import stderr
from typing import Any, Dict, List, TextIO, Tuple, Type, Union

from utils.algorithms.edit_distance import levenshtein
from utils.algorithms.data_structures.exceptions import EditFailure
from utils.modes.alignment import Alignment
from utils.modes.tree import TreeAlignment
from utils.modes.word import WordAlignment
from utils.modes.xml import XMLAlignment


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

    for line_index, (source_line, target_line) in enumerate(zip(source_file, target_file)):
        # TODO: what's the correct type annotation for alignment_type here?
        source_label = alignment_type(source_line, **alignment_kwargs)   # type: ignore
        target_spaced_line: str = " ".join(target_line.split())
        line_alignment: List[Tuple[int, int]] = levenshtein(source_label.get_characters(), target_spaced_line)
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


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("source", type=str)
    parser.add_argument("target", type=str)
    parser.add_argument("--flip", action="store_true", default=False, help="operate on target side instead of source")
    parser.add_argument("--mode", "-m", type=get_alignment_type, default=WordAlignment, help="input/output mode")
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--processes", type=int, default=1)
    parser.add_argument("--verbose", action="store_true", default=False, help="verbose output")
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
    alignment_class_kwargs: Dict[str, Any] = {"is_flipped": args.flip}
    other_kwargs: Dict[str, Any] = {"verbose": args.verbose}

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
