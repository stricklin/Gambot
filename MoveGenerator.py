import State as Board


class MoveGenerator:
    # TODO: write a move sorter

    def __init__(self, board):
        """takes a board, gets the pieces, gets all legal moves"""
        self.board = board
        self.pieces = self.get_pieces()
        self.moves = self.get_moves()

    def get_pieces(self):
        """gets the piece of the side on move"""
        if self.board.whites_turn:
            return self.board.white_piece_list
        else:
            return self.board.black_piece_list

    def get_moves(self):
        """gets all the moves for all the pieces"""
        moves = []
        for piece in self.pieces:
            moves += self.get_pieces_moves(piece)
        return moves

    def get_pieces_moves(self, piece):
        """gets all the moves for a piece"""
        moves = []
        r = piece[0][0]
        c = piece[0][1]
        char_rep = piece[1].upper()

        # add the moves based on what kind of piece it is
        if char_rep == "P":
            # set the forward direction
            if self.board.whites_turn:
                f = -1
            else:
                f = 1
            moves += self.scan(r, c, f, -1, True, True, True)
            moves += self.scan(r, c, f, 0, True, False, False)
            moves += self.scan(r, c, f, 1, True, True, True)

        elif char_rep == "N":
            moves += self.symscan(r, c, 2, 1, True, True)
            moves += self.symscan(r, c, 1, 2, True, True)

        elif char_rep == "B":
            moves += self.symscan(r, c, 1, 1, False, True)
            moves += self.symscan(r, c, 0, 1, True, False)

        elif char_rep == "R":
            moves += self.symscan(r, c, 0, 1, False, True)

        elif char_rep == "Q":
            moves += self.symscan(r, c, 0, 1, False, True)
            moves += self.symscan(r, c, 1, 1, False, True)

        elif char_rep == "K":
            moves += self.symscan(r, c, 0, 1, True, True)
            moves += self.symscan(r, c, 1, 1, True, True)

        return moves

    def scan(self, r, c, tr, tc, short, can_capture, must_capture=False):
        """looks at all the squares projected in the direction"""
        # TODO: This is cludgdy
        if not self.check_bounds(r + tr, c + tc):
            return []
        if tr == 0:
            row_change = 0
        elif tr > 0:
            row_change = 1
        else:
            row_change = -1
        if tc == 0:
            col_change = 0
        elif tc > 0:
            col_change = 1
        else:
            col_change = -1
        add_move = False
        captured = False
        piece_captured = '.'
        stop = short
        origin_cord = (r, c)
        origin = self.board.numpy_board[origin_cord]
        target_cord = (r + tr, c + tc)
        target = self.board.numpy_board[target_cord]
        if target == 0 and not must_capture:
            add_move = True
            move_to_add = (origin_cord, target_cord, captured, piece_captured)
        else:
            stop = True
        if origin * target < 0:
            if can_capture:
                add_move = True
                captured = True
                piece_captured = self.board.num_to_char_piece[self.board.numpy_board[target_cord]]
                move_to_add = (origin_cord, target_cord, captured, piece_captured)
        if stop:
            if add_move:
                return [move_to_add]
            else:
                return []
        if add_move:
            return [move_to_add] + self.scan(r, c, tr + row_change, tc + col_change, short, can_capture, must_capture)
        return self.scan(r, c, tr * 2, tc * 2, short, can_capture, must_capture)

    def check_bounds(self, r, c):
        if r < 0 or r >= self.board.row_count:
            return False
        if c < 0 or c >= self.board.col_count:
            return False
        return True

    def symscan(self, r, c, tr, tc, short, can_capture, must_capture=False):
        moves = list()
        moves += self.scan(r, c, tr, tc, short, can_capture, must_capture)
        moves += self.scan(r, c, -tc, tr, short, can_capture, must_capture)
        moves += self.scan(r, c, -tr, -tc, short, can_capture, must_capture)
        moves += self.scan(r, c, tc, -tr, short, can_capture, must_capture)
        return moves

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
    def char_move_to_src_dest(char_move):
        move_translator = { "a1": (5, 0), "b1": (5, 1), "c1": (5, 2), "d1": (5, 3),  "e1":(5, 4),
                            "a2": (4, 0), "b2": (4, 1), "c2": (4, 2), "d2": (4, 3),  "e2":(4, 4),
                            "a3": (3, 0), "b3": (3, 1), "c3": (3, 2), "d3": (3, 3),  "e3":(3, 4),
                            "a4": (2, 0), "b4": (2, 1), "c4": (2, 2), "d4": (2, 3),  "e4":(2, 4),
                            "a5": (1, 0), "b5": (1, 1), "c5": (1, 2), "d5": (1, 3),  "e5":(1, 4),
                            "a6": (0, 0), "b6": (0, 1), "c6": (0, 2), "d6": (0, 3),  "e6":(0, 4),
                           }
        char_move = char_move.split("-")
        return move_translator[char_move[0]], move_translator[char_move[1]]

