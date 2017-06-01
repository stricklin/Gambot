from Client import Client
from MoveGenerator import MoveGenerator
import random
import time


class Player:
    def __init__(self, board, is_white, testing=False):
        self.board = board
        self.is_white = is_white
        self.testing = testing

    def get_moves(self): raise NotImplementedError

    def get_move(self):
        # return a random move from the best moves
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
    def __init__(self, board, is_white, testing=False):
        Player.__init__(self, board, is_white, testing)

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
    def __init__(self, board, is_white, testing=False):
        Player.__init__(self, board, is_white, testing)

    def get_moves(self):
        assert self.is_white == self.board.whites_turn
        moves = MoveGenerator(self.board).moves
        # the 0 and [0] are to comply with gemoves in other player classes
        return moves


class NewNegamax(Player):
    def __init__(self, board, is_white, depth, alphabeta_pruning=False, testing=False):
        Player.__init__(self, board, is_white, testing)
        self.depth = depth
        self.alphabeta_pruning = alphabeta_pruning
        self.max_val = -10000
        # vals is for testing
        self.vals = []

    def get_moves(self):
        assert self.is_white == self.board.whites_turn
        best_moves = []
        # initialize max_val to something too low
        self.max_val = -10000
        # generate and test each move
        moves = MoveGenerator(self.board).moves
        if not moves:
            self.board.lose()
            return None
        for move in moves:
            # apply move
            self.board.apply_move(move)
            # get the value of this move
            if self.alphabeta_pruning:
                # this is the widest window possible for alpha beta
                val = - self.negamax(self.depth, -10000, 10000)
            else:
                val = - self.negamax(self.depth)
            # if this is a better move, remember it
            if val > self.max_val:
                self.max_val = val
                best_moves = [move]
                if self.testing:
                    self.vals = [val]
            # if more than one move is best, keep them all
            elif val == self.max_val:
                best_moves.append(move)
                if self.testing:
                    self.vals.append(val)
            # undo move
            self.board.undo_move()
        if self.testing:
            # make sure that newnegamax, negamax and alphabeta are returning the same values
            negamax_moves = Negamax(self.board, self.is_white, self.depth, True).get_moves()
            alphabeta_moves = Negamax(self.board, self.is_white, self.depth, True).get_moves()
            assert set(negamax_moves) == set(best_moves) == set(alphabeta_moves)
        return best_moves

    def negamax(self, depth, alpha=None, beta=None):
        # check if the game is done or depth is reached
        if depth <= 0 or self.board.winner:
            return self.board.value
        moves = MoveGenerator(self.board).moves
        self.board.apply_move(moves[0])
        # get value of the first one to initalize max_val
        if self.alphabeta_pruning:
            max_val = -self.negamax(depth - 1, -beta, -alpha)
        else:
            max_val = -self.negamax(depth - 1)
        # undo move
        self.board.undo_move()
        #TODO: comment here to explain how this pruning works
        if self.alphabeta_pruning:
            if max_val > beta:
                return max_val
            alpha = max(alpha, max_val)

        # try remaining moves
        for move in moves[1:]:
            # this tests that undo is working correctly
            if self.testing:
                old_state = self.board.get_char_state_val()
            # apply move
            self.board.apply_move(move)
            # get the value of this move
            if self.alphabeta_pruning:
                val = -self.negamax(depth - 1, -beta, -alpha)
            else:
                val = -self.negamax(depth - 1)
            # remember the best value
            if val > max_val:
                max_val = val
            # undo move
            self.board.undo_move()

            # this tests that undo is working correctly
            if self.testing:
                foo = self.board.get_char_state_val()
                assert set(old_state) == set(self.board.get_char_state_val())
        return max_val


class Negamax(Player):
    def __init__(self, board, is_white, depth, alphabeta_pruning=False, testing=False):
        Player.__init__(self, board, is_white, testing)
        self.depth = depth
        self.alphabeta_pruning = alphabeta_pruning
        self.max_val = -10000
        # vals is for testing
        self.vals = []

    def get_moves(self):
        if self.alphabeta_pruning:
            return self.get_alphabeta_moves()
        else:
            return self.get_negamax_moves()

    def get_negamax_moves(self):
        best_moves = []
        assert self.is_white == self.board.whites_turn
        # initialize max_val to something too low
        self.max_val = -10000
        # generate and test each move
        moves = MoveGenerator(self.board).moves
        if not moves:
            self.board.lose()
            return None
        for move in moves:
            # apply move
            self.board.apply_move(move)
            # get the value of this move
            val = - self.negamax(self.depth)
            # if this is a better move, remember it
            # the better move is the smallest value because its the value of the opponents turn
            if val > self.max_val:
                self.max_val = val
                best_moves = [move]
                if self.testing:
                    self.vals = [val]
            # if more than one move is best, keep them all
            elif val == self.max_val:
                best_moves.append(move)
                if self.testing:
                    self.vals.append(val)
            # undo move
            self.board.undo_move()
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
            self.board.apply_move(move)
            # get the value of this move
            val = -self.negamax(depth - 1)
            # remember the best value
            if val > max_val:
                max_val = val
            # undo move
            self.board.undo_move()
            if self.testing:
                assert set(old_state) == set(self.board.get_char_state_val())
        return max_val

    def get_alphabeta_moves(self):
        assert self.is_white == self.board.whites_turn
        best_moves = []
        # initalize max_val to lowest possible
        # generate and test each move
        moves = MoveGenerator(self.board).moves
        if not moves:
            self.board.lose()
            return None
        self.max_val = -10000
        for move in moves:
            # apply move
            self.board.apply_move(move)
            # get the value of this move
            # this is the widest window possible for alpha beta
            val = - self.alphabeta(self.depth, -10000, 10000)
            # if this is a better move, remember it
            # the better move is the smallest value because its the value of the opponents turn
            if val > self.max_val:
                self.max_val = val
                best_moves = [move]
                if self.testing:
                    self.vals = [val]
            # if more than one move is best, keep them all
            elif val == self.max_val:
                best_moves.append(move)
                if self.testing:
                    self.vals.append(val)
            # undo move
            self.board.undo_move()
        if self.testing:
            # make sure that negamax and alpha beta are returning the same values
            negamax_moves = Negamax(self.board, self.is_white, self.depth, True).get_moves()
            assert set(negamax_moves) == set(best_moves)
        return best_moves

    def alphabeta(self, depth, alpha, beta):
        # check if the game is done or depth is reached
        if depth <= 0 or self.board.winner:
            return self.board.value
        moves = MoveGenerator(self.board).moves
        # get value of the first one to initalize max_val
        self.board.apply_move(moves[0])
        # get the value of this move
        max_val = -self.alphabeta(depth - 1, -beta, -alpha)
        # undo move
        self.board.undo_move()
        # if this value is better than beta prune the subtree
        if max_val > beta:
            return max_val
        alpha = max(alpha, max_val)

        # try remaining values
        for move in moves[1:]:
            # apply move
            self.board.apply_move(move)
            # get the value of this move
            val = -self.alphabeta(depth - 1, -beta, -alpha)
            # undo move
            self.board.undo_move()
            # if this value is equal or better than beta prune the subtree
            if val >= beta:
                return val
            max_val = max(val, max_val)
            alpha = max(alpha, val)
        return max_val


class Net(Player):
    def __init__(self, board, is_white, username, password, game_type, game_number=None):
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
        # this only happens when Net is black_player serverside
        move = self.client.get_first_move()
        if move is None:
            # send the move that the opponent just made
            if self.board.last_move:
                self.client.write(MoveGenerator.move_to_char_move(self.board.last_move))
            # get the new move
            move, server_board, game_times = self.client.get_message()
            # todo: verify state and update time
        return [MoveGenerator.char_move_to_move(move)]


class IterativeDeepening(Player):
    def __init__(self, board, is_white, time_limit, testing=False):
        Player.__init__(self, board, is_white, testing)
        self.time_limit = time_limit
        self.start_time = None

    def get_moves(self):
        depth = 0
        old_moves = []
        new_moves = []
        self.start_time = time.time()
        while not self.out_of_time():
            depth += 1
            old_moves = new_moves
            time_elapsed = time.time() - self.start_time
            time_left = self.time_limit - time_elapsed
            if self.testing:
                new_moves = Negamax(board=self.board, is_white=self.is_white, depth=depth,
                                    alphabeta_pruning=True, time_limit=time_left, testing=self.testing)
        if self.testing:
            print "depth reached: " + str(depth)
            return old_moves,
