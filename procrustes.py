#!/usr/bin/env python

from argparse import ArgumentParser, FileType, Namespace
from sys import stderr

from utils.algorithms.edit_distance import levenshtein
from utils.algorithms.data_structures.exceptions import EditFailure
from utils.modes.tree import TreeAlignment
from utils.modes.word import WordAlignment
from utils.modes.xml import XMLAlignment


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("source", type=FileType(encoding="utf-8", mode="r"))
    parser.add_argument("target", type=FileType(encoding="utf-8", mode="r"))
    parser.add_argument("--flip", action="store_true", default=False, help="operate on target side instead of source")
    parser.add_argument("--mode", "-m", default="word", choices=["trees", "word", "xml"], help="input/output mode")
    parser.add_argument("--output-file", type=FileType(encoding="utf-8", mode="w+"), default=None)
    parser.add_argument("--verbose", action="store_true", default=False, help="verbose output")
    args: Namespace = parser.parse_args()

    for line_index, (source_line, target_line) in enumerate(zip(args.source, args.target)):
        if args.mode == "word":
            source_label = WordAlignment(source_line, args.flip)
        elif args.mode == "tree":
            source_label = TreeAlignment(source_line)
        elif args.mode == "xml":
            source_label = XMLAlignment(source_line)
        else:
            raise ValueError(f"The mode <{args.mode}> is not currently supported.")

        target_spaced_line = " ".join(target_line.split())
        line_alignment = levenshtein(source_label.get_characters(), target_spaced_line)
        if args.verbose is True:
            print(f"SOURCE LABEL: {source_label}\n", file=stderr)
            print(f"SOURCE LABEL CHARACTERS: {source_label.get_characters()}\n", file=stderr)
            print(f"TARGET LINE: {target_spaced_line}\n", file=stderr)
            for source_index, target_index in line_alignment:
                print(f"[{source_label.get_characters()[source_index]}]-[{target_spaced_line[target_index]}]",
                      file=stderr)

        source_label.project(target_spaced_line, line_alignment)
        if source_label.get_characters() != target_spaced_line:
            raise EditFailure(f'{source_label.get_characters()} != {target_spaced_line}')

        if args.output_file is not None:
            args.output_file.write(f"{source_label}")
        else:
            print(f"PROJECTION: {source_label}")
