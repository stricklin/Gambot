class Move:
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

