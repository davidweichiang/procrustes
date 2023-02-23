from functools import total_ordering


@total_ordering
class Item(object):
    def __init__(self, cost=0., ancestor=None, alignment=None):
        self.cost = cost
        self.alignment = alignment or []
        self.ancestor = ancestor

    def __eq__(self, other):
        return self.cost == other.cost

    def __ne__(self, other):
        return self.cost != other.cost

    def __lt__(self, other):
        return self.cost < other.cost
