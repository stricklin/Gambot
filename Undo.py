class Undo:
    """
    the information needed to undo a state into the former state
    """
    def __init__(self, move, value):
        self.old_value = value
        self.old_src = move.src
        self.old_dest = move.dest
