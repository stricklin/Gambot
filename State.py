import sys
from Square import Square
from Undo import Undo
from PieceList import PieceList


def read_file(file):
    return open(file).read().splitlines()


def read_stdin():
    return sys.stdin.read().splitlines()


class Board:

    def __init__(self, game_state):
        # Separate the turn info from the state and store
        self.turn_count = int(game_state[0].split()[0])
        players_turn = game_state[0].split()[1]
        self.whites_turn = players_turn == "W"

        # Store a char representation of the state
        init_board = game_state[1:]
        init_board = [list(x) for x in init_board]
        # todo: update char board? or discard after init?

        # Set up invarients
        self.row_count = 6
        self.col_count = 5
        self.col_letters = ['a', 'b', 'c', 'd', 'e']
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
                            "N": 75,
                            "B": 300,
                            "R": 500,
                            "Q": 700,
                            "K": 10000,
                            }

        # Set up piece lists and dict_board
        self.white_piece_list = PieceList()
        self.black_piece_list = PieceList()
        self.dict_board = {}
        self.read_init_board(init_board)

        # Set up undo stack
        self.undos = []

        # Set done flag
        self.winner = None

        # Get value of pieces
        self.value = self.get_value()

    def get_value(self):
        """sums the values of the piece lists and gets the difference. side on move - other side"""
        # TODO: this seems like it could be done better
        if self.winner is None:
            white_value = 0
            black_value = 0
            for piece in self.white_piece_list.get_pieces():
                white_value += self.piece_value[piece.piece]
            for piece in self.black_piece_list.get_pieces():
                black_value += self.piece_value[piece.piece.upper()]
            if self.whites_turn:
                return white_value - black_value
            else:
                return black_value - white_value
        elif self.winner == "draw":
            return 0
        elif self.winner == "white_player":
            if self.whites_turn:
                return 10000
            else:
                return -10000
        elif self.winner == "black_player":
            if not self.whites_turn:
                return 10000
            else:
                return -10000
        # this function should never get here
        assert False

    def read_init_board(self, init_board):
        """Walks the init_board and adds each piece to the correct piece list"""
        for r in range(self.row_count):
            for c in range(self.col_count):
                # todo: replace the column numbers with letters
                char_piece = init_board[r][c]
                self.place_piece(Square((r, c), char_piece))

    def place_piece(self, square):
        """
        Puts a piece into it's piece list and into the dict_board
        :param square: the square where the piece should go
        :return: 
        """
        self.dict_board[square.cords] = square
        # if square is not empty put piece into piece list
        if square.piece == '.':
            return
        if square.piece.isupper():
            self.white_piece_list.add(square)
        else:
            self.black_piece_list.add(square)

    def pick_up_piece(self, square):
        """
        Takes a piece out of the piece list and updates the dict_board
        :param square: the cords where the piece is on the dict_board
        :return: the char_rep of the picked up piece
        """
        # if there is a piece, see which side it belongs to
        if square.piece != '.':
            # TODO: This could be more DRY
            is_white = square.piece.isupper()
            if is_white:
                    self.white_piece_list.remove(square)
            else:
                    self.black_piece_list.remove(square)
        replacement_square = Square(square.cords, ".")
        self.dict_board[square.cords] = replacement_square
        return square.piece

    def print_char_state(self):
        """prints the state of the state to stdout"""
        char_state = self.get_char_state()
        for line in char_state:
            print line
        print

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

        # convert dict_board to char Board
        for r in range(self.row_count):
            row = ""
            for c in range(self.col_count):
                row += self.dict_board[(r, c)].piece
            state.append(row)

        return state

    def get_char_state_val(self):
        """returns a character representation of the state with value"""
        state = self.get_char_state()
        # get the state value
        state.append(str(self.value))

        return state

    def win(self, winner):
        self.winner = winner
        if self.winner == "white_player":
            if self.whites_turn:
                self.value = 10000
            else:
                self.value = -10000
        else:
            if not self.whites_turn:
                self.value = 10000
            else:
                self.value = -10000

    def lose(self):
        self.value = -10000
        if self.whites_turn:
            self.winner = "black_player"
        else:
            self.winner = "white_player"

    def draw(self):
        self.value = 0
        self.winner = "draw"

    def apply_move(self, move):
        """
        applies a move to the state
        :param move: the move to apply, is of form (src, dest) where src and dest are both Squares
        :return: None
        """

        # store undo information
        undo = Undo(self.dict_board, move, self.value)
        self.undos.append(undo)

        # remove captured piece
        captured_piece = self.pick_up_piece(move.dest)
        if captured_piece != '.':
            # update value and check for win by capture
            # if a king was taken, win the game
            if captured_piece == "k":
                self.win("white_player")
            elif captured_piece == "K":
                self.win("black_player")
            else:
                self.value += self.piece_value[captured_piece.upper()]

        # remove piece
        piece = self.pick_up_piece(move.src)
        # promote pawns
        if undo.promotion:
            self.value += self.piece_value['Q']
            self.value -= self.piece_value['P']
            if self.whites_turn:
                piece = "Q"
            else:
                piece = "q"
        # replace piece
        self.place_piece(Square(move.dest.cords, piece))

        # update turn counter, switch sides, and flip value
        if not self.whites_turn:
            self.turn_count += 1
            # check for draw
            if self.turn_count > 40:
                if self.winner is None:
                    self.draw()
        self.whites_turn = not self.whites_turn
        self.value = -self.value

    def undo_move(self):
        """
        changes the games state to what it was before the move was applied
        :return: 
        """
        # get the old undo information
        undo = self.undos.pop()
        # update turn counter and  switch sides
        if self.whites_turn:
            self.turn_count -= 1
        assert self.turn_count >= 0
        self.winner = None
        self.whites_turn = not self.whites_turn
        self.value = undo.old_value
        # remove new dest
        self.pick_up_piece(self.dict_board[undo.old_dest.cords])
        # place old squares
        self.place_piece(undo.old_src)
        self.place_piece(undo.old_dest)
