import sys
import numpy as np
from Square import Square
from Undo import Undo
from PieceList import PieceList


def read_file(file):
    return open(file).read().splitlines()


def read_stdin():
    return sys.stdin.read().splitlines()


class Board:

    def __init__(self, game_state, pawn_evaluation=False, testing=False):
        # Separate the turn info from the state and store
        self.turn_count = int(game_state[0].split()[0])
        players_turn = game_state[0].split()[1]
        self.whites_turn = players_turn == "W"

        # Store a char representation of the state
        init_board = game_state[1:]
        init_board = [list(x) for x in init_board]

        # Set up invarients
        self.pawn_evaluation = pawn_evaluation
        self.testing = testing
        self.row_count = 6
        self.col_count = 5
        # first dimension is rows, second is columns, third is piece type
        self.zobrist_key = np.load("zobrist_square_key.npy")
        player_key = np.load("zobrist_player_key.npy")
        self.white_zob_hash = player_key[0]
        self.black_zob_hash = player_key[1]
        self.num_to_piece = {0: ".",
                             1: "P", 7: "p",
                             2: "N", 8: "n",
                             3: "B", 9: "b",
                             4: "R", 10: "r",
                             5: "Q", 11: "q",
                             6: "K", 12: "k",
                             }
        self.piece_to_num = {".": 0,
                             "P": 1, "p": 7,
                             "N": 2, "n": 8,
                             "B": 3, "b": 9,
                             "R": 4, "r": 10,
                             "Q": 5, "q": 11,
                             "K": 6, "k": 12,
                             }
        self.piece_value = {"P": 100,
                            "N": 75,
                            "B": 300,
                            "R": 500,
                            "Q": 700,
                            "K": 10000,
                            }
        self.gaurded_pawn_value = 1.5 * self.piece_value["P"]
        self.doubled_pawn_value = -.5 * self.piece_value["P"]

        # Set up piece lists, dict_board, and zob_hash
        self.white_piece_list = PieceList()
        self.black_piece_list = PieceList()
        self.dict_board = {}
        self.zob_hash = 0
        self.read_init_board(init_board)

        # Set up undo stack
        self.undos = []

        # Set done flag
        self.winner = None

        # Get value of pieces
        self.white_pawn_value = 0
        self.black_pawn_value = 0
        self.value = self.get_value()

    def get_value(self):
        """sums the values of the piece lists and gets the difference. side on move - other side"""
        # TODO: this seems like it could be done better
        if self.winner is None:
            white_value = 0
            black_value = 0

            for square in self.white_piece_list.get_pieces():
                white_value += self.piece_value[square.piece]
            for square in self.black_piece_list.get_pieces():
                black_value += self.piece_value[square.piece.upper()]
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
        """
        Walks the init_board and adds each piece to the correct piece list
        Also initalizes zob_hash
        """
        for r in range(self.row_count):
            for c in range(self.col_count):
                # todo: replace the column numbers with letters
                char_piece = init_board[r][c]
                self.add_square(Square((r, c), char_piece))
        # apply player zob hash
        if self.whites_turn:
            self.zob_hash = self.zob_hash ^ self.white_zob_hash
        else:
            self.zob_hash = self.zob_hash ^ self.black_zob_hash

    def evaluate_all_pawns(self):
        self.evaluate_pawns(True)
        self.evaluate_pawns(False)

    def evaluate_pawns(self, is_white):
        total_value = 0
        if is_white:
            self.value -= self.white_pawn_value
            pawns = self.white_piece_list.get_pieces("P")
        else:
            self.value -= self.black_pawn_value
            pawns = self.black_piece_list.get_pieces("P")
        # todo: should i negate the pawn values?
        # negate original value of pawns
        # total_value = -len(pawns) * pawn_value

        # turn squares into cords and cols
        cord_pawns = []
        col_pawns = []
        for pawn in pawns:
            cord_pawns.append(pawn.cords)
            col_pawns.append(pawn.col)

        for pawn_index in range(len(pawns)):
            # add for gaurding pawns
            total_value += self.evaluate_gaurding_pawns(cord_pawns[pawn_index], cord_pawns, is_white)
            # subtract for passed pawns
            total_value += self.evaluate_doubled_pawns(col_pawns[pawn_index], col_pawns, pawn_index)
        if is_white:
            self.white_pawn_value = total_value
            self.value += self.white_pawn_value
        else:
            self.black_pawn_value = total_value
            self.value += self.black_pawn_value

    def evaluate_gaurding_pawns(self, cord_pawn, cord_pawns, is_white):
        gaurd_value = 0
        if is_white:
            forward = -1
        else:
            forward = 1
        west_attact = (cord_pawn[0] + forward, cord_pawn[1] - 1)
        east_attact = (cord_pawn[0] + forward, cord_pawn[1] + 1)
        if west_attact in cord_pawns:
            gaurd_value += self.gaurded_pawn_value
        if east_attact in cord_pawns:
            gaurd_value += self.gaurded_pawn_value
        return gaurd_value

    def evaluate_doubled_pawns(self, col_pawn, col_pawns, pawn_index):
        passed_value = 0
        for index in range(len(col_pawns)):
            if index != pawn_index:
                if col_pawn == col_pawns[index]:
                    passed_value += self.doubled_pawn_value
        return passed_value

    def add_square(self, square):
        """
        adds a square to the dict_board and updates zob_hash
        if the square is non-empty, that square is added to it's piece list
        :param square: the square to add
        :return: 
        """
        # add square to board and update zob_hash
        self.dict_board[square.cords] = square
        self.update_zob_hash_square(square)
        # if square is not empty put piece into piece list
        if square.is_empty():
            return
        if square.piece.isupper():
            self.white_piece_list.add(square)
        else:
            self.black_piece_list.add(square)

    def remove_square(self, square):
        """
        updates zob_hash and the square is non-empty, 
        it is removed from the dict_board and it's piece list
        :param square: the square to remove
        :return: the piece inside the square
        """
        # update zob_hash
        self.update_zob_hash_square(square)
        # if there is a piece, see which side it belongs to
        if not square.is_empty():
            # TODO: This could be more DRY
            is_white = square.piece.isupper()
            if is_white:
                    self.white_piece_list.remove(square)
            else:
                    self.black_piece_list.remove(square)
            replacement_square = Square(square.cords, ".")
            self.dict_board[square.cords] = replacement_square
        return square.piece

    def update_zob_hash_square(self, square):
        # xors zob_hash with hash value of square
        square_hash = self.zobrist_key[square.row, square.col, self.piece_to_num[square.piece]]
        self.zob_hash = self.zob_hash ^ square_hash

    def update_zob_hash_player(self):
        self.zob_hash = self.zob_hash ^ self.white_zob_hash
        self.zob_hash = self.zob_hash ^ self.black_zob_hash

    def test_zob_hash(self):
        if self.testing:
            predicted_zob_hash = 0
            for square in self.dict_board.items():
                square_hash = self.zobrist_key[square.row, square.col, self.piece_to_num[square.piece]]
                predicted_zob_hash = predicted_zob_hash ^ square_hash
            assert predicted_zob_hash == self.zob_hash

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
                square = self.dict_board[(r, c)].piece
                # the "." is too small by itself, ". " is easier to read
                if square == ".":
                    square = "."
                row += square
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
        self.undos.append(Undo(move, self.value))
        # replace old src
        piece = self.remove_square(move.src)
        # remove captured piece
        captured_piece = self.remove_square(move.dest)
        if captured_piece != '.':
            # update value and check for win by capture
            # if a king was taken, win the game
            if captured_piece == "k":
                self.win("white_player")
            elif captured_piece == "K":
                self.win("black_player")
            else:
                self.value += self.piece_value[captured_piece.upper()]
        # if the piece is a pawn:
        if piece.upper() == "P":
            # update pawn values
            if self.pawn_evaluation:
                self.evaluate_pawns(self.whites_turn)
            # white promotion
            if piece == "P" and move.dest.row == 0:
                piece = "Q"
                self.value += self.piece_value["Q"] - self.piece_value["P"]
            # black promotion
            elif piece == "p" and move.dest.row == 5:
                piece = "q"
                self.value += self.piece_value["Q"] - self.piece_value["P"]
        # replace piece
        self.add_square(Square(move.dest.cords, piece))
        # update turn counter, switch sides, and flip value
        if not self.whites_turn:
            self.turn_count += 1
            # check for draw
            if self.turn_count > 40:
                if self.winner is None:
                    self.draw()
        self.whites_turn = not self.whites_turn
        self.value = -self.value
        self.update_zob_hash_player()
        self.test_zob_hash()

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
        new_dest = self.dict_board[undo.old_dest.cords]
        self.remove_square(new_dest)
        # replace old squares
        self.add_square(undo.old_src)
        self.add_square(undo.old_dest)
        self.update_zob_hash_player()
        self.test_zob_hash()
