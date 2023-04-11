from re import sub
from typing import Callable, Dict, List, TextIO, Tuple


EXTENDED_WHITESPACE_REGEX: str = "[\r\n\t]+"
WHITESPACE_REDUCTION_REGEX: str = r"[\s]{2,}"


def zip_by_file(first_file: TextIO, second_file: TextIO) -> List[Tuple[str, str]]:
    zipped_content: List[Tuple[str, str]] = []
    first_lines: List[str] = first_file.readlines()
    second_lines: List[str] = second_file.readlines()

    first_full_text: str = "".join(first_lines)
    second_full_text: str = "".join(second_lines)

    # We remove all non-space whitespace.
    first_full_text = sub(EXTENDED_WHITESPACE_REGEX, " ", first_full_text)
    second_full_text = sub(EXTENDED_WHITESPACE_REGEX, " ", second_full_text)

    # We then resolve the fact that additional spaces between tokens may have been added due to this,
    #   removing them such that at most one space exists between adjacent tokens.
    first_full_text = sub(WHITESPACE_REDUCTION_REGEX, " ", first_full_text)
    second_full_text = sub(WHITESPACE_REDUCTION_REGEX, " ", second_full_text)

    zipped_content.append((first_full_text, second_full_text))
    return zipped_content


ZIPPERS: Dict[str, Callable] = {
    "file": zip_by_file,
    "line": zip
}


def get_zip_function(zipper_name: str):
    try:
        zipper: Callable = ZIPPERS[zipper_name]
    except KeyError:
        raise ValueError(f"The zip function <{zipper_name}> is not recognized.")
    return zipper
