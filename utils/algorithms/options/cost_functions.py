from math import inf
from typing import Callable, Dict, List, Tuple, Union

from utils.algorithms.options.edits import EditOperation
from utils.algorithms.wf_edit_distance import calculate_minimum_edit_distance


ENTRY_SIZES: List[str] = ["16", "32", "64"]


# This serves as an example function for the cost of moves in minimum edit distance.
# In this case, current_input and proposed_output don't get used--but they could be in more complex variations.
def levenshtein_cost_function(current_input: Union[str, None], proposed_output: Union[str, None],
                              move: EditOperation) -> int:
    if move == EditOperation.INSERT:
        cost = 1
    elif move == EditOperation.DELETE:
        cost = 1
    elif move == EditOperation.SUBSTITUTE:
        if current_input == proposed_output:
            cost = 0
        else:
            cost = 1
    else:
        raise ValueError(f"Invalid move <{move}> provided. Please try again with a valid move.")
    return cost


# This serves as an example function for the cost of moves in minimum edit distance.
# In this case, current_input and proposed_output don't get used--
# but they could be in variations that aren't as simple.
def debug_levenshtein_cost_function(current_input: Union[str, None], proposed_output: Union[str, None],
                                    move: EditOperation) -> int:
    if move == EditOperation.INSERT:
        cost = 1
        print(f"Move: adding {proposed_output}...")
    elif move == EditOperation.DELETE:
        cost = 1
        print(f"Move: removing {current_input}...")
    elif move == EditOperation.SUBSTITUTE:
        if current_input == proposed_output:
            cost = 0
        else:
            cost = 1
        print(f"Move: replacing {current_input} with {proposed_output}...")
    else:
        raise ValueError(f"Invalid move <{move}> provided. Please try again with a valid move.")
    return cost


def lcs_cost_function(current_input: Union[str, None], proposed_output: Union[str, None], move: EditOperation) -> int:
    if move == EditOperation.INSERT:
        cost = 1
    elif move == EditOperation.DELETE:
        cost = 1
    elif move == EditOperation.SUBSTITUTE:
        if current_input == proposed_output:
            cost = 0
        else:
            cost = 2
    else:
        raise ValueError(f"Invalid move <{move}> provided. Please try again with a valid move.")
    return cost


def dual_levenshtein_cost_function(current_input: Union[str, None], proposed_output: Union[str, None],
                                   move: EditOperation) -> Union[int, float]:
    if move == EditOperation.INSERT:
        cost = 1.0
    elif move == EditOperation.DELETE:
        cost = 1.0
    elif move == EditOperation.SUBSTITUTE:
        if current_input == proposed_output:
            cost = 0.0
        else:
            cost_function, table_type = COST_FUNCTIONS["levenshtein"]
            edit_distance, _ = \
                calculate_minimum_edit_distance(current_input, proposed_output, cost_function, table_type)
            cost: float = edit_distance / max(len(current_input), len(proposed_output))
    else:
        raise ValueError(f"Invalid move <{move}> provided. Please try again with a valid move.")
    return cost


def procrustes_levenshtein_function(current_input: Union[str, None], proposed_output: Union[str, None],
                                    move: EditOperation, space_penalty: float = 0.5) -> int:
    if move == EditOperation.INSERT:
        cost = 1 if not proposed_output.isspace() else space_penalty
    elif move == EditOperation.DELETE:
        cost = 1 if not current_input.isspace() else space_penalty
    elif move == EditOperation.SUBSTITUTE:
        if current_input == proposed_output:
            cost = 0
        elif current_input.isspace() or proposed_output.isspace():
            cost = inf   # As a surrogate for not wanting spaces to invoke substitution, we use a large value.
        else:
            cost = 1
    else:
        raise ValueError(f"Invalid move <{move}> provided. Please try again with a valid move.")
    return cost


COST_FUNCTIONS: Dict[str, Tuple[Callable, str]] = {
    "debug": (debug_levenshtein_cost_function, "int"),
    "dual": (dual_levenshtein_cost_function, "float"),
    "lcs": (lcs_cost_function, "int"),
    "levenshtein": (levenshtein_cost_function, "int"),
    "procrustes-levenshtein": (procrustes_levenshtein_function, "float")
}


def get_cost_function(cost_function_name: str) -> Tuple[Callable, str]:
    try:
        cost_function, data_type = COST_FUNCTIONS[cost_function_name]
    except KeyError:
        raise ValueError(f"The cost function <{cost_function_name}> is currently not supported.")

    return cost_function, data_type
