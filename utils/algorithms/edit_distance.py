from typing import List, Sequence, Tuple, Union

from utils.algorithms.data_structures.exceptions import EditFailure
from utils.algorithms.data_structures.item import Item


SPACE_PENALTY: float = 0.5


def levenshtein(s: Sequence[str], t: Sequence[str]):
    """http://en.wikipedia.org/wiki/Levenshtein_distance"""
    m = len(s)
    n = len(t)
    # d[i][j] says how to get t[:j] from s[:i]
    d: List[List[Union[None, Item]]] = [[None for j in range(n + 1)] for i in range(m + 1)]
    d[0][0] = Item()
    for i in range(m + 1):
        for j in range(n + 1):
            if i == j == 0:
                continue

            candidates: List[Item] = []

            if i > 0 and j > 0:
                ancestor = d[i - 1][j - 1]
                if s[i - 1] == t[j - 1]:
                    candidates.append(Item(cost=ancestor.cost + 0, ancestor=ancestor, alignment=[(i - 1, j - 1)]))
                elif not s[i - 1].isspace() and not t[j - 1].isspace():
                    # substitution. don't allow substitution of/for space
                    candidates.append(Item(cost=ancestor.cost + 1, ancestor=ancestor, alignment=[(i - 1, j - 1)]))

            if i > 0:
                # deletion
                ancestor: Item = d[i - 1][j]
                if s[i - 1].isspace():
                    cost = ancestor.cost + SPACE_PENALTY
                else:
                    cost = ancestor.cost + 1
                candidates.append(Item(cost=cost, ancestor=ancestor))

            if j > 0:
                # insertion
                ancestor = d[i][j - 1]
                if t[j - 1].isspace():
                    cost = ancestor.cost + SPACE_PENALTY
                else:
                    cost = ancestor.cost + 1
                candidates.append(Item(cost=cost, ancestor=ancestor))

            d[i][j] = min(candidates)

    goal = d[m][n]
    if goal is not None:
        alignment: List[Tuple[int, int]] = []
        current = goal
        while current is not None:
            alignment.extend(current.alignment)
            current = current.ancestor
        alignment.reverse()
        return alignment
    else:
        raise EditFailure
