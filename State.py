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
                            "K": 0,
                            }

        # Set up piece lists and numpy board
        self.white_piece_list = []
        self.black_piece_list = []
        self.numpy_board = np.zeros((6, 5))
        self.get_pieces()

        # Set done flag
        self.winner = None

        # Get value of pieces
        self.value = self.get_value()

    def get_value(self):
        """sums the values of the piece lists and gets the difference. side on move - other side"""
        white_value = 0
        black_value = 0
        # TODO: this seems like it could be done better
        if self.winner is None:
            white_value = 0
            black_value = 0
            for piece in self.white_piece_list:
                white_value += self.piece_value[piece[1]]
            for piece in self.black_piece_list:
                black_value += self.piece_value[piece[1].upper()]
            if self.whites_turn:
                return white_value - black_value
            else:
                return black_value - white_value
        elif self.winner == "draw":
            return 0
        elif self.winner == "white":
            if self.whites_turn:
                return 10000
            else:
                return -10000
        elif self.winner == "black":
            if not self.whites_turn:
                return 10000
            else:
                return -10000
        # this function should never get here
        assert False

    def get_pieces(self):
        """Walks the board and adds each piece to the correct piece list"""
        for r in range(self.row_count):
            for c in range(self.col_count):
                square = self.char_board[r][c]
                if square != ".":
                        self.place_piece((r, c), square)

    def place_piece(self, cords, piece):
        """
        Puts a piece into it's piece list and onto the numpy board
        :param cords: cordinates for where the piece should go
        :param piece: the char_rep of the piece
        :return: 
        """
        # TODO: DRY
        if piece.isupper():
            self.white_piece_list.append((cords, piece))
            self.numpy_board[cords] = self.char_to_num_piece[piece]
        else:
            self.black_piece_list.append((cords, piece))
            self.numpy_board[cords] = self.char_to_num_piece[piece]

    def pick_up_piece(self, cords):
        """
        Takes a piece out of the piece list and updates the numpy board
        :param cords: the cordinates where the piece is on the numpy board
        :return: the char_rep of the picked up piece
        """
        # removed is a flag to make sure that a piece is actually getting picked up
        removed = False
        target_piece = None
        # see if the piece is black or white
        char_piece = self.num_to_char_piece[self.numpy_board[cords]]
        is_white = char_piece.isupper()
        # TODO: This could be more DRY
        if is_white:
            for piece in self.white_piece_list:
                if piece[0] == cords:
                    target_piece = piece[1]
                    self.white_piece_list.remove(piece)
                    self.numpy_board[cords] = 0
                    removed = True
        else:
            for piece in self.black_piece_list:
                if piece[0] == cords:
                    target_piece = piece[1]
                    self.black_piece_list.remove(piece)
                    self.numpy_board[cords] = 0
                    removed = True
        assert removed is True
        return target_piece

    def print_char_state(self):
        """prints the state of the board to stdout"""
        char_state = self.get_char_state()
        for line in char_state:
            print(line)
        print()

    def get_char_state(self):
        """returns a character representation of the state"""
        state = []
        # get the turn info
        turn_info = str(self.turn_count)
        if self.whites_turn:
            turn_info += " W"
        else:
            turn_info += " B"
        state.append(turn_info)

        # convert numpy_board to char Board
        for r in range(self.row_count):
            row = ""
            for c in range(self.col_count):
                row += self.num_to_char_piece[self.numpy_board[r][c]]
            state.append(row)

        # get the board value
        state.append(str(self.value))
        return state

    def win(self):
        self.value = 10000
        if self.whites_turn:
            self.winner = "white"
        else:
            self.winner = "black"

    def lose(self):
        self.value = -10000
        if self.whites_turn:
            self.winner = "black"
        else:
            self.winner = "white"

    def draw(self):
        self.value = 0
        self.winner = "draw"




    def apply_move(self, move):
        """
        applies a move to the board
        :param move: the move to apply, is of form (src, dest, char_rep of piece) where src and dest are both (r, c)
        :return: None
        """
        # TODO: make this assertion work if it can be done cheaply
        assert self.move_is_legal(move)
        captured_piece = None
        # remove captured piece
        if move[2]:
            captured_piece = self.pick_up_piece(move[1])
        # update value and check for win by capture
        if captured_piece:
            # if a king was taken, win the game
            if captured_piece.upper() == "K":
                self.win()
            else:
                self.value += self.piece_value[captured_piece.upper()]

        # pick up piece
        piece = self.pick_up_piece(move[0])
        # put down piece
        self.place_piece(move[1], piece)

        # promote pawns
        promoted_piece = self.check_for_promotion()
        if promoted_piece:
            self.value += self.piece_value['Q']
            self.value -= self.piece_value['P']
        # update turn counter, switch sides, and flip value
        if not self.whites_turn:
            self.turn_count += 1
            # check for draw
            if self.turn_count > 40:
                if self.winner is None:
                    self.draw()
        self.whites_turn = not self.whites_turn
        self.value = -self.value
        return captured_piece, promoted_piece,

    def check_for_promotion(self):
        # TODO: check for promotion in the moves generated to save scanning the piece lists
        promoted = False
        if self.whites_turn:
            for piece in self.white_piece_list:
                if piece[0][0] == 0 and piece[1] == "P":
                    self.pick_up_piece(piece[0])
                    self.place_piece(piece[0], "Q")
                    promoted = True
        else:
            for piece in self.black_piece_list:
                if piece[0][0] == 5 and piece[1] == "p":
                    self.pick_up_piece(piece[0])
                    self.place_piece(piece[0], 'q')
                    promoted = True
        return promoted

    def undo_move(self, move, captured_piece, promoted_piece: bool):
        # TODO: there is extra information here, captured piece is inside move
        """
        changes the games state to what it was before the move was applied
        :param move: The move to undo (src, dest, captured, piece_captured)
        :param captured_piece: The char_rep of the piece captured
        :param promoted_piece: If a piece was promoted 
        :return: 
        """
        # update turn counter and  switch sides
        if self.whites_turn:
            self.turn_count -= 1
        assert self.turn_count >= 0
        self.whites_turn = not self.whites_turn
        self.value = -self.value

        # undo the end of a game
        if self.winner is not None:
            self.winner = None
            self.value = self.get_value()

        # pick up piece
        piece = self.pick_up_piece(move[1])
        # undo promotion
        if promoted_piece:
            if self.whites_turn:
                piece = "P"
            else:
                piece = "p"
            self.value -= self.piece_value['Q']
            self.value += self.piece_value['P']
        # put down piece
        self.place_piece(move[0], piece)
        # replace captured piece
        if move[2]:
            self.place_piece(move[1], captured_piece)
            self.value -= self.piece_value[captured_piece.upper()]

    def move_is_legal(self, move):
        # TODO make this assertion
        return True


