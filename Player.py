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
            # TODO: is this proper behavior? or should it lose?
            self.board.winner = "draw"
            return None
        return moves[0]


class Negamax(Player):
    def __init__(self, board: Board, is_white: bool, depth: int):
        self.board = board
        self.is_white = is_white
        self.depth = depth

    def get_move(self):
        assert self.is_white == self.board.whites_turn
        # initialize max_val to something too low
        max_val = -10000
        # generate and test each move
        # TODO: what if there aren't any moves?
        moves = MoveGenerator(self.board).get_moves()
        for move in moves:
            # apply move
            captured_piece, promoted_piece = self.board.apply_move(move, self.is_white)
            # get the value of this move
            val = - self.negamax(self.depth, not self.is_white)
            # if this is a better move, remember it
            # the better move is the smallest value because its the value of the opponents turn
            if val > max_val:
                max_val = val
                best_move = move
            # undo move
            self.board.undo_move(move, captured_piece, promoted_piece)
        return best_move

    # TODO: this is a huge pile of untested code. plz be careful with it!
    def negamax(self, depth: int, is_white):
        # check if the game is done or depth is reached
        if depth <= 0 or self.board.winner is not None:
            # TODO: the incremental evaluator isn't working right. until it is, we are scanning the board to get the value
            return self.board.get_value()
        moves = MoveGenerator(self.board).get_moves()
        max_val = -10000
        for move in moves:
            # apply move
            captured_piece, promoted_piece = self.board.apply_move(move, is_white)
            # get the value of this move
            val = -self.negamax(depth - 1, not is_white)
            # remember the best value
            if val > max_val:
                max_val = val
            # undo move
            self.board.undo_move(move, captured_piece, promoted_piece)
        return max_val

