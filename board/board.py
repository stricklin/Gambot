import numpy as np


class Board:

    def __init__(self, game_state: list):
        self.turn_count = int(game_state[0].split()[0])
        players_turn = game_state[0].split()[1]
        self.char_board = game_state[1:]
        self.char_board = [list(x) for x in self.char_board]
        self.whites_turn = players_turn == "W"
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
        self.white_piece_list = []
        self.black_piece_list = []
        self.get_pieces()
        self.numpy_board = []
        self.init_numpy_board()

    def get_pieces(self):
        for r in range(self.row_count):
            for c in range(self.col_count):
                square = self.char_board[r][c]
                if square != ".":
                    self.add_piece(r, c, square)

    def add_piece(self, r, c, piece):
        if piece.isupper():
            self.white_piece_list.append((r, c, piece))
        else:
            self.black_piece_list.append((r, c, piece))

    def init_numpy_board(self):
        self.numpy_board = np.zeros((self.row_count, self.col_count))

        for piece in self.white_piece_list + self.black_piece_list:
            self.place_piece(piece)

    def place_piece(self, piece):
        r = piece[0]
        c = piece[1]
        char_rep = piece[2]
        num_rep = self.char_to_num_piece[char_rep]
        self.numpy_board[r][c] = num_rep

    def get_char_state(self):
        state = []
        # convert numpy_board to char board
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


