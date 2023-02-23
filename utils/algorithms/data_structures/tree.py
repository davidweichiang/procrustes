from re import compile, Pattern

from utils.algorithms.data_structures.exceptions import RootDeletedException
from utils.algorithms.data_structures.node import Node, PrettyPrinter


class Tree:
    def __init__(self, root):
        self.root = root

    def __str__(self):
        return self.root._subtree_str()

    def pretty_print(self):
        root_printer: PrettyPrinter = self.root._pretty_print()
        return str(root_printer)

    interior_node: Pattern = compile(r"\s*\(([^\s)]*)")
    close_brace: Pattern = compile(r"\s*\)")
    leaf_node: Pattern = compile(r'\s*([^\s)]+)')

    @staticmethod
    def _scan_tree(s):
        result = Tree.interior_node.match(s)
        if result is not None:
            label = result.group(1)
            pos = result.end()
            children = []
            (child, length) = Tree._scan_tree(s[pos:])
            while child is not None:
                children.append(child)
                pos += length
                (child, length) = Tree._scan_tree(s[pos:])

            result = Tree.close_brace.match(s[pos:])
            if result is not None:
                pos += result.end()
                return Node(label, children), pos
            else:
                return None, 0
        else:
            result = Tree.leaf_node.match(s)
            if result is not None:
                pos = result.end()
                label = result.group(1)
                return Node(label, []), pos
            else:
                return None, 0

    @staticmethod
    def from_str(s):
        s = s.strip()
        (tree, n) = Tree._scan_tree(s)
        return Tree(tree)

    def bottom_up(self):
        """ Traverse the nodes of the tree bottom-up. """
        return self.root.bottom_up()

    def leaves(self):
        """ Traverse the leaf nodes of the tree. """
        return self.root.leaves()

    def remove_empty(self):
        """ Remove empty nodes. """
        nodes = list(self.bottom_up())
        for node in nodes:
            if node.label == '-NONE-':
                try:
                    node.delete_clean()
                except RootDeletedException:
                    self.root = None

    def remove_unit(self):
        """ Remove unary nodes by fusing them with their parents. """
        nodes = list(self.bottom_up())
        for node in nodes:
            if len(node.children) == 1:
                child = node.children[0]
                if len(child.children) > 0:
                    node.label = "%s_%s" % (node.label, child.label)
                    child.detach()
                    for grandchild in list(child.children):
                        node.append_child(grandchild)

    def restore_unit(self):
        """ Restore the unary nodes that were removed by remove_unit(). """
        def visit(node):
            children = [visit(child) for child in node.children]
            labels = node.label.split('_')
            node = Node(labels[-1], children)
            for label in reversed(labels[:-1]):
                node = Node(label, [node])
            return node
        self.root = visit(self.root)

    def binarize_right(self):
        """ Binarize into a right-branching structure. """
        nodes = list(self.bottom_up())
        for node in nodes:
            if len(node.children) > 2:
                # create a right-branching structure
                children = list(node.children)
                children.reverse()
                vlabel = node.label + "*"
                prev = children[0]
                for child in children[1:-1]:
                    prev = Node(vlabel, [child, prev])
                node.append_child(prev)

    def binarize_left(self):
        """ Binarize into a left-branching structure. """
        nodes = list(self.bottom_up())
        for node in nodes:
            if len(node.children) > 2:
                vlabel = node.label + "*"
                children = list(node.children)
                prev = children[0]
                for child in children[1:-1]:
                    prev = Node(vlabel, [prev, child])
                node.insert_child(0, prev)

    binarize = binarize_right

    def unbinarize(self):
        """ Undo binarization by removing any nodes ending with *. """
        def visit(node):
            children = sum([visit(child) for child in node.children], [])
            if node.label.endswith('*'):
                return children
            else:
                return [Node(node.label, children)]
        roots = visit(self.root)
        assert len(roots) == 1
        self.root = roots[0]
