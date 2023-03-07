from enum import IntEnum
from typing import List


class EditOperation(IntEnum):
    SUBSTITUTE = 0
    DELETE = 1
    INSERT = 2


EDIT_OPERATIONS: List[EditOperation] = list(EditOperation)

