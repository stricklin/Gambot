from State import Board
from MoveGenerator import MoveGenerator
import random


class Player:
    pass
    # TODO: make this a base class for the other types of players
    # TODO: make a random player
    # TODO: make a net player
    # TODO: make a human player
    # TODO: make a negamax player
    # TODO: make a alpha-beta negamax player
    # TODO: make a iteritive deepening alpha-beta player with a time limit
    # TODO: add TT

class Random(Player):
    def __init__(self, board: Board, is_white: bool, depth):
        self.board = board
        self.is_white = is_white

    def get_move(self):
        assert self.is_white == self.board.whites_turn
        moves = MoveGenerator(self.board).get_moves()
        random.shuffle(moves)
        if not moves:
            self.board.lose()
            return None
        return moves[0]


class Negamax(Player):
    def __init__(self, board: Board, is_white: bool, depth: int, testing=False):
        self.board = board
        self.is_white = is_white
        self.depth = depth
        self.testing = testing

    def get_move(self):
        assert self.is_white == self.board.whites_turn
        best_moves = []
        # initialize max_val to something too low
        max_val = -10000
        # generate and test each move
        moves = MoveGenerator(self.board).get_moves()
        if not moves:
            self.board.lose()
            return None
        for move in moves:
            # apply move
            captured_piece, promoted_piece = self.board.apply_move(move,)
            # get the value of this move
            val = - self.negamax(self.depth, not self.is_white)
            # if this is a better move, remember it
            # the better move is the smallest value because its the value of the opponents turn
            if val > max_val:
                max_val = val
                best_moves = [move]
            # if more than one move is best, keep them all
            elif val == max_val:
                best_moves.append(move)
            # undo move
            self.board.undo_move(move, captured_piece, promoted_piece)
        # return a random move from the best moves
        random.shuffle(best_moves)
        return best_moves[0]

    def negamax(self, depth: int, is_white):
        # check if the game is done or depth is reached
        if depth <= 0 or self.board.winner:
            return self.board.value
            # return self.board.get_value()
        moves = MoveGenerator(self.board).get_moves()
        max_val = -10000
        for move in moves:
            if self.testing:
                old_state = self.board.get_char_state()
            # apply move
            captured_piece, promoted_piece = self.board.apply_move(move)
            # get the value of this move
            val = -self.negamax(depth - 1, not is_white)
            # remember the best value
            if val > max_val:
                max_val = val
            # undo move
            self.board.undo_move(move, captured_piece, promoted_piece)
            if self.testing:
                assert set(old_state) == set(self.board.get_char_state())
        return max_val

