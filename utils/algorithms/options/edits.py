from enum import IntEnum
from typing import List


class EditOperation(IntEnum):
    SUBSTITUTE = 1
    DELETE = 2
    INSERT = 3


EDIT_OPERATIONS: List[EditOperation] = list(EditOperation)

