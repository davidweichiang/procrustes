from typing import List, Tuple

from utils.algorithms.data_structures.tree import Tree
from utils.modes.alignment import Alignment


class TreeAlignment(Alignment):
    def __init__(self, source_line: str, **alignment_kwargs):
        super().__init__()
        self.tree = Tree.from_str(source_line)
        self.characters = " ".join(n.label for n in self.tree.leaves())
        label_index: int = 0
        for node in self.tree.bottomup():
            if len(node.children) == 0:
                if label_index > 0:
                    label_index += 1   # space
                node.span = (label_index, label_index + len(node.label))
                label_index += len(node.label)
            else:
                node.span = (node.children[0].span[0], node.children[-1].span[-1])

    def __str__(self):
        return str(self.tree)

    def get_characters(self):
        return self.characters

    def project(self, revised_target_line: str, character_alignment: List[Tuple[int, int]]):
        raise NotImplementedError
