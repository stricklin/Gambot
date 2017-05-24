from Client import Client
from MoveGenerator import MoveGenerator
import random


class Player:
    def __init__(self, board, is_white, depth=0, testing=False):
        self.board = board
        self.is_white = is_white
        self.depth = depth
        self.testing = testing

    def get_moves(self): raise NotImplementedError

    def get_move(self):
        # return a random move from the best moves
        if self.testing:
            best_moves, val, vals = self.get_moves()
        else:
            best_moves = self.get_moves()
        # if the game is over, return none
        if not best_moves:
            return None
        if not self.testing:
            random.shuffle(best_moves)
        return best_moves[0]

    # TODO: make a iteritive deepening alpha-beta player with a time limit
    # TODO: add TT


class Human(Player):
    def __init__(self, board, is_white):
        Player.__init__(self, board, is_white)

    def get_moves(self):
        # get all the moves
        moves = MoveGenerator(self.board).moves
        move_count = len(moves)
        selected_move = ""
        for i in range(move_count):
            print str(i) + ". " + MoveGenerator.move_to_char_move(moves[i]) + " " + str(moves[i])
        while not selected_move.isdigit() or int(selected_move) >= move_count:
            selected_move = input("Choose which numbered move you would like to take: ")
        return [moves[int(selected_move)]]


class Random(Player):
    def __init__(self, board, is_white):
        Player.__init__(self, board, is_white)

    def get_moves(self):
        assert self.is_white == self.board.whites_turn
        moves = MoveGenerator(self.board).move
        # the 0 and [0] are to comply with gemoves in other player classes
        return moves


class Negamax(Player):
    def __init__(self, board, is_white, depth, testing=False):
        Player.__init__(self, board, is_white, depth, testing)

    def get_moves(self):
        best_moves = []
        # TODO: vals is for debug
        vals = []
        assert self.is_white == self.board.whites_turn
        # initialize max_val to something too low
        max_val = -10000
        # generate and test each move
        moves = MoveGenerator(self.board).moves
        if not moves:
            self.board.lose()
            return None
        for move in moves:
            # apply move
            captured_piece, promoted_piece = self.board.apply_move(move)
            # get the value of this move
            val = - self.negamax(self.depth)
            # if this is a better move, remember it
            # the better move is the smallest value because its the value of the opponents turn
            if val > max_val:
                max_val = val
                best_moves = [move]
                if self.testing:
                    vals = [val]
            # if more than one move is best, keep them all
            elif val == max_val:
                best_moves.append(move)
                if self.testing:
                    vals.append(val)
            # undo move
            self.board.undo_move(move, captured_piece, promoted_piece)
        if self.testing:
            return best_moves, max_val, vals
        return best_moves

    def negamax(self, depth):
        # check if the game is done or depth is reached
        if depth <= 0 or self.board.winner:
            return self.board.value
        moves = MoveGenerator(self.board).moves
        max_val = -10000
        for move in moves:
            if self.testing:
                old_state = self.board.get_char_state_val()
            # apply move
            captured_piece, promoted_piece = self.board.apply_move(move)
            # get the value of this move
            val = -self.negamax(depth - 1)
            # remember the best value
            if val > max_val:
                max_val = val
            # undo move
            self.board.undo_move(move, captured_piece, promoted_piece)
            if self.testing:
                assert set(old_state) == set(self.board.get_char_state_val())
        return max_val


class AlphaBeta(Player):
    def __init__(self, board, is_white, depth, testing=False):
        Player.__init__(self, board, is_white, depth, testing)

    def get_moves(self):
        assert self.is_white == self.board.whites_turn
        best_moves = []
        # TODO: vals is for debug
        vals = []
        # initalize max_val to lowest possible
        # generate and test each move
        moves = MoveGenerator(self.board).moves
        if not moves:
            self.board.lose()
            return None
        max_val = -10000
        for move in moves:
            # apply move
            captured_piece, promoted_piece = self.board.apply_move(move)
            # get the value of this move
            # this is the widest window possible for alpha beta
            val = - self.alphabeta(self.depth, -10000, 10000)
            # if this is a better move, remember it
            # the better move is the smallest value because its the value of the opponents turn
            if val > max_val:
                max_val = val
                best_moves = [move]
                if self.testing:
                    vals = [val]
            # if more than one move is best, keep them all
            elif val == max_val:
                best_moves.append(move)
                if self.testing:
                    vals.append(val)
            # undo move
            self.board.undo_move(move, captured_piece, promoted_piece)
        if self.testing:
            # make sure that negamax and alpha beta are returning the same values
            negamax_moves, negamax_val, negamax_vals = Negamax(self.board, self.is_white, self.depth, True).get_moves()
            assert set(negamax_moves) == set(best_moves)
        if self.testing:
            return best_moves, max_val, vals
        return best_moves

    def alphabeta(self, depth, alpha, beta):
        # check if the game is done or depth is reached
        if depth <= 0 or self.board.winner:
            return self.board.value
        moves = MoveGenerator(self.board).moves
        # get value of the first one to initalize max_val
        captured_piece, promoted_piece = self.board.apply_move(moves[0])
        # get the value of this move
        max_val = -self.alphabeta(depth - 1, -beta, -alpha)
        # undo move
        self.board.undo_move(moves[0], captured_piece, promoted_piece)
        # if this value is better than beta prune the subtree
        if max_val > beta:
            return max_val
        alpha = max(alpha, max_val)

        # try remaining values
        for move in moves[1:]:
            # apply move
            captured_piece, promoted_piece = self.board.apply_move(move)
            # get the value of this move
            val = -self.alphabeta(depth - 1, -beta, -alpha)
            # undo move
            self.board.undo_move(move, captured_piece, promoted_piece)
            # if this value is equal or better than beta prune the subtree
            if val >= beta:
                return val
            max_val = max(val, max_val)
            alpha = max(alpha, val)
        return max_val


class Net(Player):
    def __init__(self, board, is_white, username, password, game_type, game_number = None):
        Player.__init__(self, board, is_white)
        self.username = username
        self.password = password
        self.game_type = game_type
        self.game_number = game_number
        self.client = Client()

        if not self.client.login(self.username, self.password):
            if not self.client.register(self.username, self.password):
                exit("unable to login or register")

        # the returns are negated because net players are the opposite color serverside
        if "offer" in game_type:
            self.is_white = not self.client.offer()
        else:
            self.is_white = not self.accept()

    def accept(self):
        # read the games
        if self.game_number:
            return self.client.accept(self.game_number)
        games = self.client.get_games()
        game_number = -1
        for game in games:
            if game.split()[4] != "[in-progress]":
                game_number = game.split()[0]
        assert game_number > 0
        return self.client.accept(game_number)

    def get_moves(self):
        # this only happens when Net is black serverside
        move = self.client.get_first_move()
        if move is None:
            # send the move that the opponent just made
            if self.board.last_move:
                self.client.write(MoveGenerator.move_to_char_move(self.board.last_move))
            # get the new move
            move, server_board, game_times = self.client.get_message()
            # todo: verify board and update time
        return [self.char_move_to_move(move)]

    def char_move_to_move(self, char_move):
        if char_move == '':
            return None
        char_move = char_move.split()[1]
        src, dest = MoveGenerator.char_move_to_src_dest(char_move)
        moves = MoveGenerator(self.board).moves
        for move in moves:
            if src == move[0] and dest == move[1]:
                return move
        assert False


