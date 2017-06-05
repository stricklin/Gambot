class TTableEntry:
    """
    a representation of a t_table entry
    """
    def __init__(self, value, depth, zob_hash, ab_pruning=False, bound=None):
        self.value = value
        self.depth = depth
        self.zob_hash = zob_hash
        self.ab_pruning = ab_pruning
        self.bound = bound
