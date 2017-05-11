import numpy as np
import sys


def read_file(file):
    return open(file).read().splitlines()


def read_stdin():
    return sys.stdin.read().splitlines()


class Board:

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
        self.piece_value = {"P": 100,
                            "N": 200,
                            "B": 300,
                            "R": 400,
                            "Q": 500,
                            "K": 9999999,
                            }

        # Set up piece lists
        self.white_piece_list = []
        self.black_piece_list = []
        self.get_pieces()

        # Set up matrix representation of the board
        self.numpy_board = []
        self.init_numpy_board()

        # Set done flag
        self.winner = None

        # Get value of pieces
        self.value = self.get_value()

    def get_value(self):
        white_value = 0
        black_value = 0
        for piece in self.white_piece_list:
            white_value += self.piece_value[piece[2]]
        for piece in self.black_piece_list:
            black_value += self.piece_value[piece[2].upper()]
        if self.whites_turn:
            return white_value - black_value
        else:
            return black_value - white_value

    def get_pieces(self):
        """Walks the board and adds each piece to the correct piece list"""
        for r in range(self.row_count):
            for c in range(self.col_count):
                square = self.char_board[r][c]
                if square != ".":
                    if square.isupper():
                        self.append_to_piece_list(r, c, square, True)
                    else:
                        self.append_to_piece_list(r, c, square, False)

    def append_to_piece_list(self, r, c, piece, is_white: bool):
        """Puts a piece into it's piece list"""
        if is_white:
            self.white_piece_list.append((r, c, piece))
        else:
            self.black_piece_list.append((r, c, piece))

    def remove_from_piece_list(self, r, c, is_white: bool):
        removed = False
        target_piece = None
        if is_white:
            for piece in self.white_piece_list:
                if piece[0] == r and piece[1] == c:
                    target_piece = piece
                    self.white_piece_list.remove(piece)
                    removed = True
        else:
            for piece in self.black_piece_list:
                if piece[0] == r and piece[1] == c:
                    target_piece = piece
                    self.black_piece_list.remove(piece)
                    removed = True
        assert removed is True
        return target_piece

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

    def print_char_state(self):
        char_state = self.get_char_state()
        for line in char_state:
            print(line)

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

    def apply_move(self, move, is_white: bool):
        assert self.move_is_legal(move)
        captured_piece = None
        # pick up piece
        piece = self.remove_from_piece_list(move[0][0], move[0][1], is_white)
        self.numpy_board[move[0][0]][move[0][1]] = 0
        # put down piece
        self.append_to_piece_list(move[1][0], move[1][1], piece[2], is_white)
        self.numpy_board[move[1][0]][move[1][1]] = self.char_to_num_piece[piece[2]]
        # promote pawns
        promoted_piece = self.check_for_promotion(is_white)
        # remove captured piece
        if move[2]:
            captured_piece = self.remove_from_piece_list(move[1][0], move[1][1], not is_white)
        # update value
        if captured_piece:
            if captured_piece[2].upper() == "K":
                if is_white:
                    self.winner = "White"
                else:
                    self.winner = "Black"
            self.value += self.piece_value[captured_piece[2].upper()]
        if promoted_piece:
            self.value += self.piece_value['Q']
            self.value -= self.piece_value['P']
        # update turn counter, switch sides, and flip value
        if not self.whites_turn:
            self.turn_count += 1
        if self.turn_count > 40:
            if self.winner is None:
                self.winner = "draw"
        self.whites_turn = not self.whites_turn
        self.value = -self.value
        return captured_piece, promoted_piece,

    def check_for_promotion(self, is_white: bool):
        # TODO: check for promotion in the moves generated
        promoted = False
        if is_white:
            for piece in self.white_piece_list:
                if piece[0] == 0 and piece[2] == "P":
                    self.white_piece_list.remove(piece)
                    piece = (piece[0], piece[1], "Q")
                    self.white_piece_list.append(piece)
                    self.numpy_board[piece[0]][piece[1]] = 5
                    promoted = True
        else:
            for piece in self.black_piece_list:
                if piece[0] == 5 and piece[2] == "p":
                    self.black_piece_list.remove(piece)
                    piece = (piece[0], piece[1], "q")
                    self.black_piece_list.append(piece)
                    self.numpy_board[piece[0]][piece[1]] = -5
                    promoted = True
        return promoted

    def undo_move(self, move, captured_piece, promoted_piece):
        # update turn counter and switch sides
        if self.whites_turn:
            self.turn_count -= 1
        assert self.turn_count >= 0
        self.whites_turn = not self.whites_turn

        # pick up piece
        piece = self.remove_from_piece_list(move[1][0], move[1][1], self.whites_turn)
        self.numpy_board[move[1][0]][move[1][1]] = 0
        # undo promotion
        if promoted_piece:
            if self.whites_turn:
                piece = (piece[0], piece[1], "P")
            else:
                piece = (piece[0], piece[1], "p")
        # put down piece
        self.append_to_piece_list(move[0][0], move[0][1], piece[2], self.whites_turn)
        self.numpy_board[move[0][0]][move[0][1]] = self.char_to_num_piece[piece[2]]
        # replace captured piece
        if move[2]:
            self.append_to_piece_list(captured_piece[0], captured_piece[1], captured_piece[2], captured_piece[3])
            self.numpy_board[move[1][0]][1][1] = self.char_to_num_piece[captured_piece]

    def move_is_legal(self, move):
        # TODO make this assertion
        return True


