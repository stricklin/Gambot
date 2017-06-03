class Undo:
    def __init__(self, move, value):
        self.old_value = value
        self.old_src = move.src
        self.old_dest = move.dest
