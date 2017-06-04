import State as Board
from Move import Move
from Square import Square
from Undo import Undo


class MoveGenerator:
    # TODO: write a move sorter
    # difference in capturing piece and captured piece
    # xray, if you can threaten a piece through another piece, check out that move
    # order the pieces

    def __init__(self, board):
        """takes a state, gets the pieces, gets all legal moves"""
        self.board = board
        self.pieces = self.get_all_pieces()
        self.moves = []
        self.get_moves(self.pieces)

    def get_all_pieces(self):
        """ the pieces of the side on move"""
        if self.board.whites_turn:
            return self.board.white_piece_list.get_pieces()
        else:
            return self.board.black_piece_list.get_pieces()

    def get_all_moves(self):
        """gets all the moves for all the pieces"""
        self.get_moves(self.get_all_pieces())

    def get_moves(self, pieces):
        """gets all the moves for the specified pieces"""
        for piece in pieces:
            self.find_pieces_moves(piece)

    def find_pieces_moves(self, src):
        """finds all the moves for a src"""
        piece_type = src.piece.upper()

        # add the moves based on what kind of src it is
        if piece_type == "P":
            # set the forward direction
            if self.board.whites_turn:
                f = -1
            else:
                f = 1
            self.scan(src, src, f, -1, True, True, True)
            self.scan(src, src, f, 0, True, False, False)
            self.scan(src, src, f, 1, True, True, True)

        elif piece_type == "N":
            self.symscan(src, src, 2, 1, True, True)
            self.symscan(src, src, 1, 2, True, True)

        elif piece_type == "B":
            self.symscan(src, src, 1, 1, False, True)
            self.symscan(src, src, 0, 1, True, False)

        elif piece_type == "R":
            self.symscan(src, src, 0, 1, False, True)

        elif piece_type == "Q":
            self.symscan(src, src, 0, 1, False, True)
            self.symscan(src, src, 1, 1, False, True)

        elif piece_type == "K":
            self.symscan(src, src, 0, 1, True, True)
            self.symscan(src, src, 1, 1, True, True)

    def scan(self, src, intermediate, row_change, col_change, short, can_capture, must_capture=False):
        """looks at all the squares projected in the direction"""
        if not self.check_bounds(intermediate, row_change, col_change):
            return
        dest_cords = (intermediate.row + row_change, intermediate.col + col_change)
        dest = self.board.dict_board[dest_cords]

        if dest.piece == '.' and not must_capture:
            self.moves.append(Move(src, dest))
        else:
            short = True
        if dest.piece != '.':
            if src.piece.isupper() != dest.piece.isupper():
                if can_capture:
                    self.moves.append(Move(src, dest))
        if not short:
            self.scan(src, dest, row_change, col_change, short, can_capture, must_capture)

    def check_bounds(self, src, row_change, col_change):
        r = src.row + row_change
        c = src.col + col_change
        if r < 0 or r >= self.board.row_count:
            return False
        if c < 0 or c >= self.board.col_count:
            return False
        return True

    def symscan(self, src, intermediate, row_change, col_change, short, can_capture, must_capture=False):
        self.scan(src, intermediate, row_change, col_change, short, can_capture, must_capture)
        self.scan(src, intermediate, -col_change, row_change, short, can_capture, must_capture)
        self.scan(src, intermediate, -row_change, -col_change, short, can_capture, must_capture)
        self.scan(src, intermediate, col_change, -row_change, short, can_capture, must_capture)



