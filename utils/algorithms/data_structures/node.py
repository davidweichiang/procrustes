from itertools import zip_longest

from utils.algorithms.data_structures.exceptions import RootDeletedException


class PrettyPrinter:
    def __init__(self):
        self.roots = []
        self.lines = []  # (left margin, string)

    def width(self):
        if len(self.lines) == 0:
            return 0
        else:
            return max(left + len(string) for (left, string) in self.lines)

    def root(self, string):
        if len(self.roots) == 0:
            self.roots = [len(string) // 2]
            self.lines[0:0] = [(0, string)]
            return

        w = self.width()

        newroot = (self.roots[0] + self.roots[-1]) // 2
        nodeline = (newroot - (len(string) - 1) // 2, string)

        if nodeline[0] < 0:
            shift = -nodeline[0]
            nodeline = (0, string)
            self.lines = [(left + shift, s) for (left, s) in self.lines]
            self.roots = [r + shift for r in self.roots]

        if len(self.roots) == 1:
            edgeline = (self.roots[0], '│')
            self.lines[0:0] = [nodeline, edgeline]
        elif len(self.roots) > 1:
            top = ['─'] * (self.roots[-1] - self.roots[0] + 1)
            top[0] = '┌'
            for i in range(1, len(self.roots) - 1):
                top[self.roots[i] - self.roots[0]] = '┬'
            top[self.roots[-1] - self.roots[0]] = '┐'
            i = newroot - self.roots[0]
            top[i] = {'─': '┴', '┬': '┼', '┌': '├', '┐': '┤'}[top[i]]
            edgeline = (self.roots[0], ''.join(top))
            self.roots = [newroot]
            self.lines[0:0] = [nodeline, edgeline]

    def append(self, other):
        w = self.width()

        # How close can we put them without a collision?
        minspace = None
        for (sline, oline) in zip(self.lines, other.lines):
            sleft, sstring = sline
            oleft, ostring = oline
            space = w - sleft - len(sstring) + oleft
            if minspace is None or space < minspace:
                minspace = space
        if minspace is None: minspace = 0

        if w > 0:
            offset = -minspace + 1
        else:
            offset = 0
        offset = max(-1, offset)

        new = []
        for (sline, oline) in zip_longest(self.lines, other.lines, fillvalue=None):
            if sline is None:
                oleft, ostring = oline
                new.append((w + offset + oleft, ostring))
            elif oline is None:
                new.append(sline)
            else:
                sleft, sstring = sline
                sright = w - sleft - len(sstring)
                oleft, ostring = oline
                new.append((sleft, sstring + ' ' * (sright + offset + oleft) + ostring))
        self.lines = new
        self.roots.extend([w + offset + r for r in other.roots])

    def __str__(self):
        ret = []
        for (left, string) in self.lines:
            ret.append(' ' * left + string)
        return '\n'.join(ret)


class Node:
    def __init__(self, label, children=None):
        self.label = label
        self.children = children or []
        for (i, child) in enumerate(self.children):
            if child.parent is not None:
                child.detach()
            child.parent = self
            child.order = i
        self.parent = None
        self.order = 0

    def __str__(self):
        return self.label

    def _pretty_print(self):
        p = PrettyPrinter()
        for child in self.children:
            p.append(child._pretty_print())
        p.root(self.label)
        return p

    def _subtree_str(self):
        if len(self.children) != 0:
            return "(%s %s)" % (self.label, " ".join(child._subtree_str() for child in self.children))
        else:
            s = '%s' % self.label
            return s

    def insert_child(self, i, child):
        if child.parent is not None:
            child.detach()
        child.parent = self
        self.children[i:i] = [child]
        for j in range(i, len(self.children)):
            self.children[j].order = j

    def append_child(self, child):
        if child.parent is not None:
            child.detach()
        child.parent = self
        self.children.append(child)
        child.order = len(self.children)-1

    def delete_child(self, i):
        self.children[i].parent = None
        self.children[i].order = 0
        self.children[i:i+1] = []
        for j in range(i,len(self.children)):
            self.children[j].order = j

    def detach(self):
        if self.parent is None:
            raise RootDeletedException
        self.parent.delete_child(self.order)

    def delete_clean(self):
        """Cleans up childless ancestors."""
        parent = self.parent
        self.detach()
        if len(parent.children) == 0:
            parent.delete_clean()

    def bottom_up(self):
        for child in self.children:
            for node in child.bottom_up():
                yield node
        yield self

    def leaves(self):
        if len(self.children) == 0:
            yield self
        else:
            for child in self.children:
                for leaf in child.leaves():
                    yield leaf
