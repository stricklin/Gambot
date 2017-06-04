import State
from MoveGenerator import MoveGenerator
from main import Game
import Player
import unittest
import os
import numpy as np
from Square import Square
from Move import Move
from Undo import Undo


# having a blank state is handy
init = ["0 W",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        "....."]


def test_moves(board_init, moves):
    game_state = State.Board(board_init)
    move_generator = MoveGenerator(game_state)
    generated_moves = set(move_generator.moves)
    assert set(moves) == set(generated_moves)


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
    white_piece_list = [Square((4, 0), "P"),
                        Square((4, 1), "P"),
                        Square((4, 2), "P"),
                        Square((4, 3), "P"),
                        Square((4, 4), "P"),
                        Square((5, 0), "R"),
                        Square((5, 1), "N"),
                        Square((5, 2), "B"),
                        Square((5, 3), "Q"),
                        Square((5, 4), "K"),
                        ]
    black_piece_list = [((0, 0), "k"),
                        Square((0, 1), "q"),
                        Square((0, 2), "b"),
                        Square((0, 3), "n"),
                        Square((0, 4), "r"),
                        Square((1, 0), "p"),
                        Square((1, 1), "p"),
                        Square((1, 2), "p"),
                        Square((1, 3), "p"),
                        Square((1, 4), "p"),
                        ]

    def test_board_read(self):
        game_state = State.Board(self.init)
        assert self.turn_count == game_state.turn_count
        assert self.whites_turn == game_state.whites_turn
        assert self.white_piece_list == game_state.white_piece_list
        assert self.black_piece_list == game_state.black_piece_list
        assert self.init == game_state.get_char_state()


class PawnTest(unittest.TestCase):
    init = ["0 W",
            ".....",
            ".....",
            ".....",
            ".p.p.",
            "P.P.P",
            ".....",
            ]
    p1 = Square((4, 0), "P")
    p2 = Square((4, 2), "P")
    p3 = Square((4, 4), "P")

    p1_moves = [
        Move(p1, Square((3, 0), ".")),
        Move(p1, Square((3, 1), "p"))
    ]

    p2_moves = [
        Move(p2, Square((3, 1), "p")),
        Move(p2, Square((3, 2), ".")),
        Move(p2, Square((3, 3), "p"))
    ]
    p3_moves = [
        Move(p3, Square((3, 3), "p")),
        Move(p3, Square((3, 4), "."))
    ]

    all_moves = p1_moves + p2_moves + p3_moves

    def test_moves(self):
        test_moves(self.init, self.all_moves)


class KnightTest(unittest.TestCase):
    init = ["0 W",
            ".p.p.",
            "p...p",
            "..N..",
            "p...p",
            ".p.p.",
            ".....",
            ]
    n = Square((2, 2), "N")
    N_moves = [
        Move(n, Square((0, 1), "p")),
        Move(n, Square((0, 3), "p")),
        Move(n, Square((1, 0), "p")),
        Move(n, Square((1, 4), "p")),
        Move(n, Square((3, 0), "p")),
        Move(n, Square((3, 4), "p")),
        Move(n, Square((4, 1), "p")),
        Move(n, Square((4, 3), "p")),
    ]

    def test_moves(self):
        test_moves(self.init, self.N_moves)


class BishopTest(unittest.TestCase):
    init = ["0 W",
            "....p",
            ".p...",
            ".pB..",
            ".....",
            ".....",
            ".....",
            ]
    b = Square((2, 2), "B")
    B_moves = [
        Move(b, Square((2, 3), ".")),
        Move(b, Square((1, 2), ".")),
        Move(b, Square((3, 2), ".")),
        Move(b, Square((1, 3), ".")),
        Move(b, Square((3, 1), ".")),
        Move(b, Square((0, 4), "p")),
        Move(b, Square((3, 3), ".")),
        Move(b, Square((4, 4), ".")),
        Move(b, Square((4, 0), ".")),
        Move(b, Square((1, 1), "p")),
    ]

    def test_moves(self):
        test_moves(self.init, self.B_moves)


class RookTest(unittest.TestCase):
    init = ["0 W",
            "..k..",
            ".....",
            ".pR..",
            ".....",
            ".....",
            "..p..",
            ]
    r = Square((2, 2), "R")
    R_moves = [
        Move(r, Square((1, 2), ".")),
        Move(r, Square((0, 2), "k")),
        Move(r, Square((2, 1), "p")),
        Move(r, Square((2, 3), ".")),
        Move(r, Square((2, 4), ".")),
        Move(r, Square((3, 2), ".")),
        Move(r, Square((4, 2), ".")),
        Move(r, Square((5, 2), "p")),
    ]

    def test_moves(self):
        test_moves(self.init, self.R_moves)


class QueenTest(unittest.TestCase):
    init = ["0 W",
            "p.p.p",
            ".....",
            "p.Q.p",
            ".....",
            "p.p.p",
            ".....",
            ]
    q = Square((2, 2), "Q")
    Q_moves = [
        Move(q, Square((2, 3), ".")),
        Move(q, Square((2, 4), "p")),
        Move(q, Square((3, 2), ".")),
        Move(q, Square((4, 2), "p")),
        Move(q, Square((2, 1), ".")),
        Move(q, Square((2, 0), "p")),
        Move(q, Square((1, 2), ".")),
        Move(q, Square((0, 2), "p")),
        Move(q, Square((1, 3), ".")),
        Move(q, Square((0, 4), "p")),
        Move(q, Square((3, 3), ".")),
        Move(q, Square((4, 4), "p")),
        Move(q, Square((3, 1), ".")),
        Move(q, Square((4, 0), "p")),
        Move(q, Square((1, 1), ".")),
        Move(q, Square((0, 0), "p")),
    ]

    def test_moves(self):
        test_moves(self.init, self.Q_moves)


class KingTest(unittest.TestCase):
    init = ["0 W",
            ".....",
            ".p.p.",
            "..K..",
            ".p.p.",
            ".....",
            ".....",
            ]
    k = Square((2, 2), "K")
    K_moves = [
        Move(k, Square((2, 3), ".")),
        Move(k, Square((3, 2), ".")),
        Move(k, Square((2, 1), ".")),
        Move(k, Square((1, 2), ".")),
        Move(k, Square((1, 3), "p")),
        Move(k, Square((3, 3), "p")),
        Move(k, Square((3, 1), "p")),
        Move(k, Square((1, 1), "p")),
    ]

    def test_moves(self):
        test_moves(self.init, self.K_moves)


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
            moves = MoveGenerator(game_state).moves
            char_moves = set(Player.Net.get_char_moves(moves))
            target = set(State.read_file(self.directory + self.targets[i]))
            assert target == char_moves


class Promotion(unittest.TestCase):
    init = ["0 W",
            ".....",
            "P....",
            ".....",
            ".....",
            ".....",
            "....."]
    board = State.Board(init)

    before = ["0 W",
              ".....",
              "P....",
              ".....",
              ".....",
              ".....",
              ".....",
              str(board.piece_value["P"])]

    after = ["0 B",
             "Q....",
             ".....",
             ".....",
             ".....",
             ".....",
             ".....",
             str(-board.piece_value["Q"])]

    def test_do_undo(self):
        move_generator = MoveGenerator(self.board)
        move = move_generator.moves[0]
        self.board.apply_move(move)
        applied_state = self.board.get_char_state_val()
        assert self.after == applied_state
        self.board.undo_move()
        undone_state = self.board.get_char_state_val()
        assert self.before == undone_state


class Turn40Win(unittest.TestCase):
    init = ["40 B",
            "....k",
            ".....",
            ".....",
            ".....",
            "...p.",
            "....K"]
    move = Move(Square((4, 3), "p"), Square((5, 4), "K"))
    winner = "black_player"

    def test_win(self):
        board = State.Board(self.init)
        board.apply_move(self.move)
        assert self.winner == board.winner


class Turn40Draw(unittest.TestCase):
    init = ["40 B",
            "....k",
            ".....",
            ".....",
            ".....",
            "...p.",
            "....K"]
    move = Move(Square((4, 3), "p"), Square((5, 3), "."))
    winner = "draw"

    def test_win(self):
        board = State.Board(self.init)
        board.apply_move(self.move)
        assert self.winner == board.winner


class StartingBoard(unittest.TestCase):
    init = ["0 W",
            "kqbnr",
            "ppppp",
            ".....",
            ".....",
            "PPPPP",
            "RNBQK"]
    white_piece_list = [Square((4, 0), "P"),
                        Square((4, 1), "P"),
                        Square((4, 2), "P"),
                        Square((4, 3), "P"),
                        Square((4, 4), "P"),
                        Square((5, 0), "R"),
                        Square((5, 1), "N"),
                        Square((5, 2), "B"),
                        Square((5, 3), "Q"),
                        Square((5, 4), "K"),
                        ]
    black_piece_list = [Square((0, 0), "k"),
                        Square((0, 1), "q"),
                        Square((0, 2), "b"),
                        Square((0, 3), "n"),
                        Square((0, 4), "r"),
                        Square((1, 0), "p"),
                        Square((1, 1), "p"),
                        Square((1, 2), "p"),
                        Square((1, 3), "p"),
                        Square((1, 4), "p"),
                        ]

    moves = [
        Move(white_piece_list[0], Square((3, 0), ".")),
        Move(white_piece_list[1], Square((3, 1), ".")),
        Move(white_piece_list[2], Square((3, 2), ".")),
        Move(white_piece_list[3], Square((3, 3), ".")),
        Move(white_piece_list[4], Square((3, 4), ".")),
        Move(white_piece_list[6], Square((3, 0), ".")),
        Move(white_piece_list[6], Square((3, 2), "."))
    ]

    def test_moves(self):
        test_moves(self.init, self.moves)

    def test_alpha_beta_and_do_undo(self):
        board = State.Board(self.init)
        white = Player.Random(board, True, testing=True)
        black = Player.Negamax(board, False, 2, ab_pruning=True, testing=True)
        game = Game(board, white, black, display=False)
        game.play_game()


class Ordering(unittest.TestCase):
    pawn22 = Square((2, 2), "p")
    king22 = Square((2, 2), "k")
    Pawn23 = Square((2, 3), "P")
    King23 = Square((2, 3), "K")

    pawnKing = Move(pawn22, King23)
    Kingpawn = Move(Pawn23, king22)

    def test_square_ordering(self):
        # equality tests
        assert self.pawn22.__cmp__(self.pawn22) == 0
        assert self.king22.__cmp__(self.king22) == 0
        assert self.Pawn23.__cmp__(self.Pawn23) == 0
        assert self.King23.__cmp__(self.King23) == 0

        # less than tests
        assert self.king22.__cmp__(self.King23) < 0
        assert self.king22.__cmp__(self.pawn22) < 0
        assert self.King23.__cmp__(self.Pawn23) < 0

        # greater than tests
        assert self.pawn22.__cmp__(self.king22) > 0
        assert self.Pawn23.__cmp__(self.King23) > 0
        assert self.Pawn23.__cmp__(self.king22) > 0

    def test_move_ordering(self):
        # equality tests
        assert self.pawnKing.__cmp__(self.pawnKing) == 0
        assert self.Kingpawn.__cmp__(self.Kingpawn) == 0

        # greater than test
        assert self.Kingpawn.__cmp__(self.pawnKing) > 0

        # less than test
        assert self.pawnKing.__cmp__(self.Kingpawn) < 0


class PawnEval(unittest.TestCase):
    doubled_init = ["0 W",
                   ".....",
                   ".....",
                   "P....",
                   "P....",
                   ".....",
                   "....."]
    doubled_board = State.Board(doubled_init)
    expected_doubled_value = 2 * doubled_board.doubled_pawn_value

    gaurded_init = ["0 W",
                    ".....",
                    ".....",
                    "P.P..",
                    ".P...",
                    ".....",
                    "....."]
    gaurded_board = State.Board(gaurded_init)
    expected_gaurded_value = 2 * gaurded_board.gaurded_pawn_value

    def test_doubled_pawn_eval(self):
        self.doubled_board.evaluate_pawns(True)
        pawn_value = self.doubled_board.white_pawn_value
        assert self.expected_doubled_value == pawn_value

    def test_pass_gaurded_pawn_eval(self):
        self.gaurded_board.evaluate_pawns(True)
        pawn_value = self.gaurded_board.white_pawn_value
        assert self.expected_gaurded_value == pawn_value

# todo: shortest win, longest lost tests

if __name__ == "__main__":
    unittest.main()
