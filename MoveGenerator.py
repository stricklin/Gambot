import State as Board
import unittest
import os


class MoveGenerator:

    def __init__(self, board: Board):
        """takes a board, gets the pieces, gets all legal moves"""
        self.board = board
        self.pieces = self.get_pieces()
        self.moves = self.get_all_moves()

    def get_pieces(self):
        if self.board.whites_turn:
            return self.board.white_piece_list
        else:
            return self.board.black_piece_list

    def get_all_moves(self):
        moves = []
        for piece in self.pieces:
            moves += self.get_moves(piece)
        return moves

    def get_moves(self, piece):
        moves = []
        r = piece[0]
        c = piece[1]
        char_rep = piece[2].upper()

        if char_rep == "P":
            if self.board.whites_turn:
                f = -1
            else:
                f = 1
            moves += self.scan(r, c, f, -1, True, True)
            moves += self.scan(r, c, f, 0, True, False)
            moves += self.scan(r, c, f, 1, True, True)

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

    def scan(self, r, c, tr, tc, short, capture):
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
        if target == 0:
            add_move = True
            move_to_add = (origin_cord, target_cord, captured, piece_captured)
        else:
            stop = True
        if origin * target < 0:
            if capture:
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
            return [move_to_add] + self.scan(r, c, tr + row_change, tc + col_change, short, capture)
        return self.scan(r, c, tr * 2, tc * 2, short, capture)

    def check_bounds(self, r, c):
        if r < 0 or r >= self.board.row_count:
            return False
        if c < 0 or c >= self.board.col_count:
            return False
        return True


    def symscan(self, r, c, tr, tc, short, capture):
        moves = list()
        moves += self.scan(r, c, tr, tc, short, capture)
        moves += self.scan(r, c, -tc, tr, short, capture)
        moves += self.scan(r, c, -tr, -tc, short, capture)
        moves += self.scan(r, c, tc, -tr, short, capture)
        return moves


class PawnTest(unittest.TestCase):
    init = ["0 W",
            ".....",
            ".....",
            ".....",
            ".p.p.",
            "P.P.P",
            ".....",
            ]
    p1 = (4, 0, "P")
    p2 = (4, 2, "P")
    p3 = (4, 4, "P")

    p1_moves = [
        ((4, 0), (3, 0), False, '.'),
        ((4, 0), (3, 1), True,  'p')
    ]

    p2_moves = [
        ((4, 2), (3, 1), True, 'p'),
        ((4, 2), (3, 2), False, '.'),
        ((4, 2), (3, 3), True, 'p')
    ]
    p3_moves = [
        ((4, 4), (3, 3), True,  'p'),
        ((4, 4), (3, 4), False, '.')
    ]

    # TODO: turn this test back on
    all_moves = p1_moves + p2_moves + p3_moves

    def test_pawns(self):
        self.check_pawn(self.p1, self.p1_moves)
        self.check_pawn(self.p2, self.p2_moves)
        self.check_pawn(self.p3, self.p3_moves)

    def check_pawn(self, pawn, moves):
        game_state = Board.Board(self.init)
        move_generator = MoveGenerator(game_state)
        assert set(moves) == set(move_generator.get_moves(pawn))

    def test_moves(self):
        game_state = Board.Board(self.init)
        move_generator = MoveGenerator(game_state)
        assert set(self.all_moves) == set(move_generator.moves)


class KnightTest(unittest.TestCase):
    init = ["0 W",
            ".p.p.",
            "p...p",
            "..N..",
            "p...p",
            ".p.p.",
            ".....",
            ]

    N_moves = [
        ((2, 2), (0, 1), True, 'p'),
        ((2, 2), (0, 3), True, 'p'),
        ((2, 2), (1, 0), True, 'p'),
        ((2, 2), (1, 4), True, 'p'),
        ((2, 2), (3, 0), True, 'p'),
        ((2, 2), (3, 4), True, 'p'),
        ((2, 2), (4, 1), True, 'p'),
        ((2, 2), (4, 3), True, 'p'),
    ]

    def test_moves(self):
        game_state = Board.Board(self.init)
        move_generator = MoveGenerator(game_state)
        assert set(self.N_moves) == set(move_generator.moves)


class BishopTest(unittest.TestCase):
    init = ["0 W",
            "....p",
            ".p...",
            ".pB..",
            ".....",
            ".....",
            ".....",
            ]
    B_moves = [
        ((2, 2), (2, 3), False, '.'),
        ((2, 2), (1, 2), False, '.'),
        ((2, 2), (3, 2), False, '.'),
        ((2, 2), (1, 3), False, '.'),
        ((2, 2), (1, 3), False, '.'),
        ((2, 2), (0, 4), True, 'p'),
        ((2, 2), (3, 3), False, '.'),
        ((2, 2), (4, 4), False, '.'),
        ((2, 2), (3, 1), False, '.'),
        ((2, 2), (4, 0), False, '.'),
        ((2, 2), (1, 1), True, 'p'),
    ]

    def test_moves(self):
        game_state = Board.Board(self.init)
        move_generator = MoveGenerator(game_state)
        assert set(self.B_moves) == set(move_generator.moves)

class RookTest(unittest.TestCase):
    init = ["0 W",
            "..k..",
            ".....",
            ".pR..",
            ".....",
            ".....",
            "..p..",
            ]

    R_moves = [
        ((2, 2), (1, 2), False, '.'),
        ((2, 2), (0, 2), True, 'k'),
        ((2, 2), (2, 1), True, 'p'),
        ((2, 2), (2, 3), False, '.'),
        ((2, 2), (2, 4), False, '.'),
        ((2, 2), (3, 2), False, '.'),
        ((2, 2), (4, 2), False, '.'),
        ((2, 2), (5, 2), True, 'p'),
    ]

    def test_moves(self):
        game_state = Board.Board(self.init)
        move_generator = MoveGenerator(game_state)
        assert set(self.R_moves) == set(move_generator.moves)

class QueenTest(unittest.TestCase):
    init = ["0 W",
            "p.p.p",
            ".....",
            "p.Q.p",
            ".....",
            "p.p.p",
            ".....",
            ]

    Q_moves = [
        ((2, 2), (2, 3), False, '.'),
        ((2, 2), (2, 4), True, 'p'),
        ((2, 2), (3, 2), False, '.'),
        ((2, 2), (4, 2), True, 'p'),
        ((2, 2), (2, 1), False, '.'),
        ((2, 2), (2, 0), True, 'p'),
        ((2, 2), (1, 2), False, '.'),
        ((2, 2), (0, 2), True, 'p'),
        ((2, 2), (1, 3), False, '.'),
        ((2, 2), (0, 4), True, 'p'),
        ((2, 2), (3, 3), False, '.'),
        ((2, 2), (4, 4), True, 'p'),
        ((2, 2), (3, 1), False, '.'),
        ((2, 2), (4, 0), True, 'p'),
        ((2, 2), (1, 1), False, '.'),
        ((2, 2), (0, 0), True, 'p'),
    ]

    def test_moves(self):
        game_state = Board.Board(self.init)
        move_generator = MoveGenerator(game_state)
        assert set(self.Q_moves) == set(move_generator.moves)


class King(unittest.TestCase):
    init = ["0 W",
            ".....",
            ".p.p.",
            "..K..",
            ".p.p.",
            ".....",
            ".....",
            ]

    K_moves = [
        ((2, 2), (2, 3), False, '.'),
        ((2, 2), (3, 2), False, '.'),
        ((2, 2), (2, 1), False, '.'),
        ((2, 2), (1, 2), False, '.'),
        ((2, 2), (1, 3), True, 'p'),
        ((2, 2), (3, 3), True, 'p'),
        ((2, 2), (3, 1), True, 'p'),
        ((2, 2), (1, 1), True, 'p'),
    ]

    def test_moves(self):
        game_state = Board.Board(self.init)
        move_generator = MoveGenerator(game_state)
        assert set(self.K_moves) == set(move_generator.moves)


class StartingBoard(unittest.TestCase):
    init = ["0 W",
            "kqbnr",
            "ppppp",
            ".....",
            ".....",
            "PPPPP",
            "RNBQK"]
    white_piece_list = [(4, 0, "P"),
                        (4, 1, "P"),
                        (4, 2, "P"),
                        (4, 3, "P"),
                        (4, 4, "P"),
                        (5, 0, "R"),
                        (5, 1, "N"),
                        (5, 2, "B"),
                        (5, 3, "Q"),
                        (5, 4, "K"),
                        ]
    black_piece_list = [(0, 0, "k"),
                        (0, 1, "q"),
                        (0, 2, "b"),
                        (0, 3, "n"),
                        (0, 4, "r"),
                        (1, 0, "p"),
                        (1, 1, "p"),
                        (1, 2, "p"),
                        (1, 3, "p"),
                        (1, 4, "p"),
                        ]

    moves = [
        ((4, 0), (5, 0), False, '.'),
        ((4, 1), (5, 1), False, '.'),
        ((4, 2), (5, 2), False, '.'),
        ((4, 3), (5, 3), False, '.'),
        ((4, 4), (5, 4), False, '.'),
        ((5, 1), (3, 0), False, '.'),
        ((5, 1), (3, 2), False, '.')
    ]

    def moves(self):
        game_state = Board.Board(self.init)
        move_generator = MoveGenerator(game_state)
        assert set(self.moves) == set(move_generator.moves)


class AutoTest(unittest.TestCase):

    def __init__(self):
        self.directory = "genmoves-tests/"
        self.files = os.listdir(self.directory)
        self.tests = []
        self.targets = []
        for file in self.files:
            if file.endswith(".in"):
                self.tests.append(file)
            else:
                self.targets.append(file)

    def generated_moves(self):
        for i in range(len(self.tests)):
            game_state = Board.Board(self.tests[i])
            move_generator = MoveGenerator(game_state)




if __name__ == "__main__":
    unittest.main()
