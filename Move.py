class Move:
    """
    a representation of a move for minichess
    """
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

    def __cmp__(self, other):
        difference = self.src.__cmp__(other.src)
        if difference == 0:
            difference = self.dest.__cmp__(other.dest)
        return difference

    def __hash__(self):
        return self.src.__hash__() * self.dest.__hash__()

    def __str__(self):
        return self.src.__str__() + " -> " + self.dest.__str__()

