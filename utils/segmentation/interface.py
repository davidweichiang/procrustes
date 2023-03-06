from functools import partial
from re import split
from string import punctuation
from typing import Callable, Dict, List


DIVIDING_PUNCTUATION: List[str] = [".", "?", "!", ":", ";"]


def identity_segmentation(string: str) -> List[str]:
    return [string]


def segment_by_characters(string: str, characters: List[str]) -> List[str]:
    if len(characters) == 0:
        raise ValueError("No characters provided.")
    else:
        segmentation_regex: str = f"([^{''.join(characters)}]+[{''.join(characters)}][\s]+)"
        segments: List[str] = split(segmentation_regex, string)
        segments = [segment for segment in segments if segment != '']

    return segments


SEGMENTATION_FUNCTIONS: Dict[str, Callable] = {
    "dividing-punctuation": partial(segment_by_characters, characters=DIVIDING_PUNCTUATION),
    "identity": identity_segmentation,
    "punctuation": partial(segment_by_characters, characters=[character for character in punctuation])
}


def get_segmentation_function(function_name: str) -> Callable:
    try:
        segmentation_function: Callable = SEGMENTATION_FUNCTIONS[function_name]
    except KeyError:
        raise ValueError(f"The segmentation function <{function_name}> is not recognized")

    return segmentation_function
