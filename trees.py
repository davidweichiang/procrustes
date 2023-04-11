from utils.algorithms.data_structures.tree import Tree


if __name__ == "__main__":
    import sys
    for line in sys.stdin:
        t = Tree.from_str(line)
        if t.root is not None:
            print(t.pretty_print())
            print()
            
