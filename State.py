import unittest
import numpy as np
import Move
import sys


class Board:

    @staticmethod
    def read_file(file):
        return open(file).read().splitlines()

    @staticmethod
    def read_stdin():
        return sys.stdin.read().splitlines()

    def __init__(self, game_state: list):
        # Separate the turn info from the board and store
        self.turn_count = int(game_state[0].split()[0])
        players_turn = game_state[0].split()[1]
        self.whites_turn = players_turn == "W"

        # Store a char representation of the board
        self.char_board = game_state[1:]
        self.char_board = [list(x) for x in self.char_board]

        # Set up invarients
        self.row_count = 6
        self.col_count = 5
        self.num_to_char_piece = {0: ".",
                                  1: "P", -1: "p",
                                  2: "N", -2: "n",
                                  3: "B", -3: "b",
                                  4: "R", -4: "r",
                                  5: "Q", -5: "q",
                                  6: "K", -6: "k",
                                  }
        self.char_to_num_piece = {".": 0,
                                  "P": 1, "p": -1,
                                  "N": 2, "n": -2,
                                  "B": 3, "b": -3,
                                  "R": 4, "r": -4,
                                  "Q": 5, "q": -5,
                                  "K": 6, "k": -6,
                                  }

        # Set up piece lists
        self.white_piece_list = []
        self.black_piece_list = []
        self.get_pieces()

        # Set up matrix representation of the board
        self.numpy_board = []
        self.init_numpy_board()

    def get_pieces(self):
        """Walks the board and adds each piece to the correct piece list"""
        for r in range(self.row_count):
            for c in range(self.col_count):
                square = self.char_board[r][c]
                if square != ".":
                    self.append_to_piece_list(r, c, square)

    def append_to_piece_list(self, r, c, piece):
        """Puts a piece into it's piece list"""
        if piece.isupper():
            self.white_piece_list.append((r, c, piece))
        else:
            self.black_piece_list.append((r, c, piece))

    def init_numpy_board(self):
        """Makes a matrix and puts number representations of pieces into it"""
        self.numpy_board = np.zeros((self.row_count, self.col_count))
        for piece in self.white_piece_list + self.black_piece_list:
            self.insert_into_numpy_board(piece)

    def insert_into_numpy_board(self, piece):
        """Puts a piece into the numpy board"""
        r = piece[0]
        c = piece[1]
        char_rep = piece[2]
        num_rep = self.char_to_num_piece[char_rep]
        self.numpy_board[r][c] = num_rep

    def get_char_state(self):
        """returns a character representation of the state"""
        state = []
        # convert numpy_board to char Board
        for r in range(self.row_count):
            row = ""
            for c in range(self.col_count):
                row += self.num_to_char_piece[self.numpy_board[r][c]]
            state.append(row)

        # attach the turn info
        turn_info = str(self.turn_count)
        if self.whites_turn:
            turn_info += " W"
        else:
            turn_info += " B"
        state.insert(0, turn_info)

        return state

    def move(self, move: Move):
        """
        Will raise exception if the move is not legal
        :param move: The move in question
        :return: None
        """
        piece = move.source.get_piece

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
        game_state = Board(self.init)
        assert self.turn_count == game_state.turn_count
        assert self.whites_turn == game_state.whites_turn
        assert self.white_piece_list == game_state.white_piece_list
        assert self.black_piece_list == game_state.black_piece_list
        # todo: make numpy_board check
        # assert self.numpy_board == game_state.numpy_board
        assert self.init == game_state.get_char_state()

if __name__ == "__main__":
    unittest.main()
