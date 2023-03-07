from typing import Callable, Dict, List, Sequence, Tuple, Union

from numpy import argmin, dtype, zeros
from numpy.typing import NDArray, DTypeLike

from utils.algorithms.options.edits import EditOperation, EDIT_OPERATIONS


PointerTable = Dict[Tuple[int, int], EditOperation]


# We initialize the chart in accordance with Wagner and Fischer's Algorithm X.
def initialize_chart(source: Sequence[str], destination: Sequence[str], cost: Callable, data_type: str) -> \
        NDArray[float]:
    chart_size: Tuple[int, int] = (len(source) + 1, len(destination) + 1)
    data_type: DTypeLike = dtype(data_type)
    new_chart: NDArray[float] = zeros(chart_size, data_type)
    fill_edges(source, destination, new_chart, cost)
    return new_chart


def fill_edges(source: Sequence, destination: Sequence, chart: NDArray[float], cost: Callable,
               row_constraint: int = 1, column_constraint: int = 1):
    fill_rows(source, chart, cost, row_constraint)
    fill_columns(destination, chart, cost, column_constraint)


def fill_rows(source: Sequence, chart: NDArray[float], cost: Callable, row_constraint: int):
    for i in range(row_constraint, len(source) + 1):
        chart[i, 0] = chart[i - 1, 0] + cost(source[i - 1], None, EditOperation.DELETE)


def fill_columns(destination: Sequence, chart: NDArray[float], cost: Callable, column_constraint: int):
    for j in range(column_constraint, len(destination) + 1):
        chart[0, j] = chart[0, j - 1] + cost(None, destination[j - 1], EditOperation.INSERT)


# We perform the main edit distance algorithm presented in Fischer and Wagner 1974.
def calculate_minimum_edit_distance(source: Sequence[str], destination: Sequence[str], cost: Callable, data_type: str,
                                    pointer_table: Union[PointerTable, None] = None) \
        -> Tuple[float, NDArray[float]]:
    chart: NDArray[float] = initialize_chart(source, destination, cost, data_type)
    for i in range(1, len(source) + 1):
        for j in range(1, len(destination) + 1):
            compute_edit_cost(source, destination, chart, cost, i, j, pointer_table)

    minimized_edit_distance: NDArray[float] = chart[len(source), len(destination)]
    return minimized_edit_distance.item(), chart


def compute_edit_cost(source: Sequence, destination: Sequence, chart: NDArray[float], cost: Callable,
                      row: int, column: int, pointer_table: Union[PointerTable, None] = None):
    substitution_cost: int = chart[row - 1, column - 1] + \
        cost(source[row - 1], destination[column - 1], EditOperation.SUBSTITUTE)
    deletion_cost: int = chart[row - 1, column] + cost(source[row - 1], None, EditOperation.DELETE)
    insertion_cost: int = chart[row, column - 1] + cost(None, destination[column - 1], EditOperation.INSERT)

    costs: Tuple[int, int, int] = (substitution_cost, deletion_cost, insertion_cost)
    minimum_cost_index: int = argmin(costs).item()
    chart[row, column] = costs[minimum_cost_index]

    if pointer_table is not None:
        pointer_table[(row, column)] = EDIT_OPERATIONS[minimum_cost_index]


def collect_alignment_path(d_table: NDArray[float], pointer_table: PointerTable) -> List[Tuple[int, int]]:
    alignment_path: List[Tuple[int, int]] = []

    goal_entry: Tuple[int, int] = d_table.shape
    goal_rows, goal_columns = goal_entry
    goal_entry = (goal_rows - 1, goal_columns - 1)

    current_entry: Tuple[int, int] = goal_entry
    edge_index: int = 0
    while edge_index not in current_entry:
        current_row, current_column = current_entry
        if pointer_table.get(current_entry, None) is not None:
            if pointer_table[current_entry] == EditOperation.SUBSTITUTE:
                previous_row: int = current_row - 1
                previous_column: int = current_column - 1
                alignment_path.insert(0, (previous_row, previous_column))
            elif pointer_table[current_entry] == EditOperation.DELETE:
                previous_row: int = current_row - 1
                previous_column: int = current_column
            elif pointer_table[current_entry] == EditOperation.INSERT:
                previous_row: int = current_row
                previous_column: int = current_column - 1
            else:
                raise ValueError(f"The edit operation <{pointer_table[current_entry]}> is not supported.")
            current_entry = (previous_row, previous_column)
        else:
            raise ValueError(f"A pointer was not stored for <{current_entry}>.")

    return alignment_path
