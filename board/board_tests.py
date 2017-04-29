import unittest
import numpy as np
import board


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

    def test_board_read(self):
        game_state = board.Board(self.init)
        assert self.turn_count == game_state.turn_count
        assert self.whites_turn == game_state.whites_turn
        assert self.white_piece_list == game_state.white_piece_list
        assert self.black_piece_list == game_state.black_piece_list
        assert self.numpy_board == game_state.numpy_board
        assert self.init == game_state.get_char_state()

if __name__ == "__main__":
    unittest.main()
