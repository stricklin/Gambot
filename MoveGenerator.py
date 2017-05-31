import State as Board


class MoveGenerator:
    # TODO: write a move sorter
    # difference in capturing piece and captured piece
    # xray, if you can threaten a piece through another piece, check out that move
    # order the pieces

    def __init__(self, board):
        """takes a state, gets the pieces, gets all legal moves"""
        self.board = board
        self.pieces = self.find_pieces()
        self.moves = []
        self.find_moves()

    def find_pieces(self):
        """ the piece of the side on move"""
        if self.board.whites_turn:
            return self.board.white_piece_list
        else:
            return self.board.black_piece_list

    def find_moves(self):
        """finds all the moves for all the pieces"""
        for piece in self.pieces:
            self.find_pieces_moves(piece)

    def find_pieces_moves(self, piece):
        """finds all the moves for a piece"""
        src = piece[0]
        char_rep = piece[1].upper()

        # add the moves based on what kind of piece it is
        if char_rep == "P":
            # set the forward direction
            if self.board.whites_turn:
                f = -1
            else:
                f = 1
            self.scan(src, src, f, -1, True, True, True)
            self.scan(src, src, f, 0, True, False, False)
            self.scan(src, src, f, 1, True, True, True)

        elif char_rep == "N":
            self.symscan(src, src, 2, 1, True, True)
            self.symscan(src, src, 1, 2, True, True)

        elif char_rep == "B":
            self.symscan(src, src, 1, 1, False, True)
            self.symscan(src, src, 0, 1, True, False)

        elif char_rep == "R":
            self.symscan(src, src, 0, 1, False, True)

        elif char_rep == "Q":
            self.symscan(src, src, 0, 1, False, True)
            self.symscan(src, src, 1, 1, False, True)

        elif char_rep == "K":
            self.symscan(src, src, 0, 1, True, True)
            self.symscan(src, src, 1, 1, True, True)

    def scan(self, src, intermediate, row_change, col_change, short, can_capture, must_capture=False):
        """looks at all the squares projected in the direction"""
        if not self.check_bounds(intermediate, row_change, col_change):
            return
        captured = False
        piece_captured = '.'
        stop = short
        src_piece = self.board.numpy_board[src]
        dest = (intermediate[0] + row_change, intermediate[1] + col_change)
        dest_piece = self.board.numpy_board[dest]
        if dest_piece == 0 and not must_capture:
            self.moves.append((src, dest))
        else:
            stop = True
        if src_piece * dest_piece < 0:
            if can_capture:
                captured = True
                piece_captured = self.board.num_to_char_piece[self.board.numpy_board[dest]]
                self.moves.append((src, dest))
                stop = True
        if not stop:
            self.scan(src, dest, row_change, col_change, short, can_capture, must_capture)

    def check_bounds(self, src, row_change, col_change):
        r = src[0] + row_change
        c = src[1] + col_change
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

    def get_char_moves(self):
        char_moves = []
        for move in self.moves:
            char_moves.append(self.move_to_char_move(move))
        return char_moves

    @staticmethod
    def move_to_char_move(move):
        move_translator = {(5, 0): "a1", (5, 1): "b1", (5, 2): "c1", (5, 3): "d1", (5, 4): "e1",
                           (4, 0): "a2", (4, 1): "b2", (4, 2): "c2", (4, 3): "d2", (4, 4): "e2",
                           (3, 0): "a3", (3, 1): "b3", (3, 2): "c3", (3, 3): "d3", (3, 4): "e3",
                           (2, 0): "a4", (2, 1): "b4", (2, 2): "c4", (2, 3): "d4", (2, 4): "e4",
                           (1, 0): "a5", (1, 1): "b5", (1, 2): "c5", (1, 3): "d5", (1, 4): "e5",
                           (0, 0): "a6", (0, 1): "b6", (0, 2): "c6", (0, 3): "d6", (0, 4): "e6",
                           }
        return move_translator[move[0]] + "-" + move_translator[move[1]]

    @staticmethod
    def char_move_to_move(char_move):
        move_translator = {"a1": (5, 0), "b1": (5, 1), "c1": (5, 2), "d1": (5, 3),  "e1":(5, 4),
                           "a2": (4, 0), "b2": (4, 1), "c2": (4, 2), "d2": (4, 3),  "e2":(4, 4),
                           "a3": (3, 0), "b3": (3, 1), "c3": (3, 2), "d3": (3, 3),  "e3":(3, 4),
                           "a4": (2, 0), "b4": (2, 1), "c4": (2, 2), "d4": (2, 3),  "e4":(2, 4),
                           "a5": (1, 0), "b5": (1, 1), "c5": (1, 2), "d5": (1, 3),  "e5":(1, 4),
                           "a6": (0, 0), "b6": (0, 1), "c6": (0, 2), "d6": (0, 3),  "e6":(0, 4),
                           }
        char_move = char_move[2:]
        char_move = char_move.split("-")
        move = (move_translator[char_move[0]], move_translator[char_move[1]])
        return move

