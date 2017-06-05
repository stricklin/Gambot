class TTableEntry:
    def __init__(self, value, depth, zob_hash, ab_pruning=False, bound=None):
        # value is whites value of the board
        self.value = value
        self.depth = depth
        self.zob_hash = zob_hash
        self.ab_pruning = ab_pruning
        self.bound = bound
