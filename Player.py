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
    def __init__(self, board: Board, is_white: bool):
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
        move = self.negamax_move(self.depth)

    # TODO: this is a huge pile of untested code. plz be careful with it!
    def negamax(self, depth: int):
        moves = MoveGenerator(self.board).get_moves()
        if not moves:
            # TODO: this is probably fucky
            self.board.winner = "draw"
            return None
        max_val = -90000
        for move in moves:
            captured_piece, promoted_piece, = self.board.apply_move(move, self.is_white)
            # if that move is a win, undo and return it
            if self.board.value >= 10000:
                self.board.undo_move(move, captured_piece, promoted_piece)
                return move, self.board.value
            else:
                # if we aren't as deep as we want to go
                # try the next turns move to see what happens
                if depth < self.depth:
                    move, val = self.negamax_move(depth + 1)
                    # the very important minus sign
                    val = -val
            if val > max_val:
                best_move = move
                max_val = val
            if max_val >= 90000:
                # if a winning move has been found, return that move
                self.board.undo_move(move, captured_piece, promoted_piece)
                return best_move, 90000
            self.board.undo_move(move, captured_piece, promoted_piece)
        return best_move, max_val
