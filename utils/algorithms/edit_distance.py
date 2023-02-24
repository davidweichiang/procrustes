from typing import List, Sequence, Tuple, Union

from utils.algorithms.data_structures.exceptions import EditFailure
from utils.algorithms.data_structures.item import Item


SPACE_PENALTY: float = 0.5


def levenshtein(source: Sequence[str], target: Sequence[str]):
    """http://en.wikipedia.org/wiki/Levenshtein_distance"""
    m: int = len(source)
    n: int = len(target)
    # d_table[i][j] says how to get target[:j] from source[:i]
    d_table: List[List[Union[None, Item]]] = [[None for j in range(n + 1)] for i in range(m + 1)]
    d_table[0][0] = Item()
    for i in range(m + 1):
        for j in range(n + 1):
            if i == j == 0:
                continue

            candidates: List[Item] = []

            if i > 0 and j > 0:
                ancestor: Item = d_table[i - 1][j - 1]
                if source[i - 1] == target[j - 1]:
                    candidates.append(Item(cost=ancestor.cost + 0, ancestor=ancestor, alignment=[(i - 1, j - 1)]))
                elif not source[i - 1].isspace() and not target[j - 1].isspace():
                    # substitution. don't allow substitution of/for space
                    candidates.append(Item(cost=ancestor.cost + 1, ancestor=ancestor, alignment=[(i - 1, j - 1)]))

            if i > 0:
                # deletion
                ancestor: Item = d_table[i - 1][j]
                if source[i - 1].isspace():
                    cost = ancestor.cost + SPACE_PENALTY
                else:
                    cost = ancestor.cost + 1
                candidates.append(Item(cost=cost, ancestor=ancestor))

            if j > 0:
                # insertion
                ancestor: Item = d_table[i][j - 1]
                if target[j - 1].isspace():
                    cost = ancestor.cost + SPACE_PENALTY
                else:
                    cost = ancestor.cost + 1
                candidates.append(Item(cost=cost, ancestor=ancestor))

            d_table[i][j] = min(candidates)

    goal: Item = d_table[m][n]
    if goal is not None:
        alignment: List[Tuple[int, int]] = []
        current: Item = goal
        while current is not None:
            alignment.extend(current.alignment)
            current = current.ancestor
        alignment.reverse()
        return alignment
    else:
        raise EditFailure
