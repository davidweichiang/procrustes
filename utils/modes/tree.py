from utils.algorithms.data_structures.tree import Tree


class TreeAlignment(object):
    def __init__(self, s):
        self.tree = Tree.from_str(s)
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

    def project(self, target_spaced_line, character_alignment):
        raise NotImplementedError
