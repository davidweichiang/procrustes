#!/usr/bin/env python

from argparse import ArgumentParser, Namespace
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


def align_files(source_filepath: str, target_filepath: str, alignment_type, alignment_kwargs: Dict[str, Any],
                output_filepath: Union[str, None] = None):
    source_file: TextIO = open(source_filepath, mode="r", encoding="utf-8")
    target_file: TextIO = open(target_filepath, mode="r", encoding="utf-8")
    output_file: TextIO = open(output_filepath, mode="w+", encoding="utf-8") if output_filepath is not None else None
    for line_index, (source_line, target_line) in enumerate(zip(source_file, target_file)):
        source_label = alignment_type(source_line, **alignment_kwargs)
        target_spaced_line: str = " ".join(target_line.split())
        line_alignment: List[Tuple[int, int]] = levenshtein(source_label.get_characters(), target_spaced_line)
        if args.verbose is True:
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


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("source", type=str)
    parser.add_argument("target", type=str)
    parser.add_argument("--flip", action="store_true", default=False, help="operate on target side instead of source")
    parser.add_argument("--mode", "-m", type=get_alignment_type, default=WordAlignment, help="input/output mode")
    parser.add_argument("--output-file", type=str, default=None)
    parser.add_argument("--verbose", action="store_true", default=False, help="verbose output")
    args: Namespace = parser.parse_args()

    alignment_class: Type[Alignment] = args.mode
    alignment_class_kwargs: Dict[str, Any] = {"is_flipped": args.flip}
    align_files(args.source, args.target, alignment_class, alignment_class_kwargs, args.output_file)
