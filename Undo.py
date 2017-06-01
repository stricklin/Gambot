import Move
import Square


class Undo:
    def __init__(self, dict_board, move, value):
        self.old_value = value
        self.old_src = move.src
        self.old_dest = move.dest
        self.promotion = False
        # white promotion
        if self.old_src.piece == "P" and self.old_dest.row == 0:
            self.promotion = True
        # black promotion
        if self.old_src.piece == "p" and self.old_dest.row == 5:
            self.promotion = True
        self.captured_piece = dict_board[move.dest.cords]
