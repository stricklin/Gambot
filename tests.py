import State
from MoveGenerator import MoveGenerator
import Player
import unittest
import os
import numpy as np


# having a blank board is handy
init = ["0 W",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        "....."]


class StartingBoard(unittest.TestCase):
    init = ["0 W",
            "kqbnr",
            "ppppp",
            ".....",
            ".....",
            "PPPPP",
            "RNBQK"]
    numpy_board = np.array([[-6., -5., -3., -2., -4.],
                            [-1., -1., -1., -1., -1.],
                            [ 0.,  0.,  0.,  0.,  0.],
                            [ 0.,  0.,  0.,  0.,  0.],
                            [ 1.,  1.,  1.,  1.,  1.],
                            [ 4.,  2.,  3.,  5.,  6.]])

    numpy_board = np.array
    turn_count = 0
    whites_turn = True
    white_piece_list = [((4, 0), "P"),
                        ((4, 1), "P"),
                        ((4, 2), "P"),
                        ((4, 3), "P"),
                        ((4, 4), "P"),
                        ((5, 0), "R"),
                        ((5, 1), "N"),
                        ((5, 2), "B"),
                        ((5, 3), "Q"),
                        ((5, 4), "K"),
                        ]
    black_piece_list = [((0, 0), "k"),
                        ((0, 1), "q"),
                        ((0, 2), "b"),
                        ((0, 3), "n"),
                        ((0, 4), "r"),
                        ((1, 0), "p"),
                        ((1, 1), "p"),
                        ((1, 2), "p"),
                        ((1, 3), "p"),
                        ((1, 4), "p"),
                        ]

    def test_board_read(self):
        game_state = State.Board(self.init)
        assert self.turn_count == game_state.turn_count
        assert self.whites_turn == game_state.whites_turn
        assert self.white_piece_list == game_state.white_piece_list
        assert self.black_piece_list == game_state.black_piece_list
        assert self.init == game_state.get_char_state_val()


class PawnTest(unittest.TestCase):
    init = ["0 W",
            ".....",
            ".....",
            ".....",
            ".p.p.",
            "P.P.P",
            ".....",
            ]
    p1 = ((4, 0), "P")
    p2 = ((4, 2), "P")
    p3 = ((4, 4), "P")

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

    all_moves = p1_moves + p2_moves + p3_moves

    def test_pawns(self):
        self.check_pawn(self.p1, self.p1_moves)
        self.check_pawn(self.p2, self.p2_moves)
        self.check_pawn(self.p3, self.p3_moves)

    def check_pawn(self, pawn, moves):
        game_state = State.Board(self.init)
        move_generator = MoveGenerator(game_state)
        assert set(moves) == set(move_generator.get_pieces_moves(pawn))

    def test_moves(self):
        game_state = State.Board(self.init)
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
        game_state = State.Board(self.init)
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
        game_state = State.Board(self.init)
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
        game_state = State.Board(self.init)
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
        game_state = State.Board(self.init)
        move_generator = MoveGenerator(game_state)
        assert set(self.Q_moves) == set(move_generator.moves)


class KingTest(unittest.TestCase):
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
        game_state = State.Board(self.init)
        move_generator = MoveGenerator(game_state)
        assert set(self.K_moves) == set(move_generator.moves)


class AutoTest(unittest.TestCase):

    directory = "genmoves-tests/"
    files = os.listdir(directory)
    files.sort()
    tests = []
    targets = []
    for file in files:
        if file.endswith(".in"):
            tests.append(file)
        else:
            targets.append(file)

    def test_generated_moves(self):
        for i in range(len(self.tests)):
            board_prep = State.read_file(self.directory + self.tests[i])
            game_state = State.Board(board_prep)
            move_generator = MoveGenerator(game_state)
            target = State.read_file(self.directory + self.targets[i])
            assert set(target) == set(move_generator.get_char_moves())


class Promotion(unittest.TestCase):
    init = ["0 W",
            ".....",
            "P....",
            ".....",
            ".....",
            ".....",
            "....."]

    before = ["0 W",
              ".....",
              "P....",
              ".....",
              ".....",
              ".....",
              ".....",
              "200"]

    after = ["0 B",
             "Q....",
             ".....",
             ".....",
             ".....",
             ".....",
             ".....",
             "-700"]

    def test_do_undo(self):
        board = State.Board(self.init)
        move_generator = MoveGenerator(board)
        move = move_generator.get_moves()[0]
        board.apply_move(move)
        assert self.after == board.get_char_state_val()
        board.undo_move(move, None, True)
        assert self.before == board.get_char_state_val()


class Turn40Win(unittest.TestCase):
    init = ["40 B",
            "....k",
            ".....",
            ".....",
            ".....",
            "...p.",
            "....K"]
    move = ((4, 3), (5, 4), True, "K")
    winner = "black"

    def test_win(self):
        board = State.Board(self.init)
        board.apply_move(self.move)
        assert  self.winner == board.winner


class StartingBoard(unittest.TestCase):
    init = ["0 W",
            "kqbnr",
            "ppppp",
            ".....",
            ".....",
            "PPPPP",
            "RNBQK"]
    white_piece_list = [((4, 0), "P"),
                        ((4, 1), "P"),
                        ((4, 2), "P"),
                        ((4, 3), "P"),
                        ((4, 4), "P"),
                        ((5, 0), "R"),
                        ((5, 1), "N"),
                        ((5, 2), "B"),
                        ((5, 3), "Q"),
                        ((5, 4), "K"),
                        ]
    black_piece_list = [((0, 0), "k"),
                        ((0, 1), "q"),
                        ((0, 2), "b"),
                        ((0, 3), "n"),
                        ((0, 4), "r"),
                        ((1, 0), "p"),
                        ((1, 1), "p"),
                        ((1, 2), "p"),
                        ((1, 3), "p"),
                        ((1, 4), "p"),
                        ]

    moves = [
        ((4, 0), (3, 0), False, '.'),
        ((4, 1), (3, 1), False, '.'),
        ((4, 2), (3, 2), False, '.'),
        ((4, 3), (3, 3), False, '.'),
        ((4, 4), (3, 4), False, '.'),
        ((5, 1), (3, 0), False, '.'),
        ((5, 1), (3, 2), False, '.')
    ]

    def test_moves(self):
        game_state = State.Board(self.init)
        move_generator = MoveGenerator(game_state)
        assert set(self.moves) == set(move_generator.moves)

    @staticmethod
    def play_game(board, white, black):
        # play game
        while not board.winner:
            move = white.get_move()
            board.apply_move(move)
            if not board.winner:
                move = black.get_move()
                board.apply_move(move)
        print "winner: " + board.winner

    def test_evaluator(self):
        # set up players
        board = State.Board(self.init)
        white = Player.Negamax(board, True, 2, True)
        black = Player.Negamax(board, False, 2, True)
        self.play_game(board, white, black)

    def test_alpha_beta(self):
        board = State.Board(self.init)
        white = Player.AlphaBeta(board, True, 2, True)
        black = Player.AlphaBeta(board, False, 2, True)
        self.play_game(board, white, black)

if __name__ == "__main__":
    unittest.main()
