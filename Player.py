from Client import Client
from MoveGenerator import MoveGenerator
from Move import Move
from Square import Square
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


class Negamax(Player):
    def __init__(self, board, is_white, max_depth, ab_pruning=False, time_limit=None, testing=False):
        Player.__init__(self, board, is_white, testing)
        self.max_depth = max_depth
        self.ab_pruning = ab_pruning
        self.max_val = -10000
        self.time_limit = time_limit
        self.start_time = None
        # vals is for testing
        self.vals = []

    def get_moves(self):
        assert self.is_white == self.board.whites_turn
        # start timer for iteritive deepening
        if self.time_limit:
            self.start_time = time.time()
        best_moves = []
        # initialize max_val to something too low
        self.max_val = -10000
        # generate and test each move
        moves = MoveGenerator(self.board).moves
        if not moves:
            self.board.lose()
            return None
        for move in moves:
            # return nothing if out of time
            if self.out_of_time():
                return None
            # save old state for checking undo
            if self.testing:
                old_state, old_pieces = self.get_state()
            # apply move
            self.board.apply_move(move)
            # get the value of this move
            if self.ab_pruning:
                # this is the widest window possible for alpha beta
                # maybe_value catches None values for early return from timeouts
                maybe_value = self.negamax(self.max_depth, -10000, 10000)
                if maybe_value is not None:
                    val = - maybe_value
                else:
                    self.board.undo_move()
                    return None
            else:
                val = - self.negamax(self.max_depth)
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
            self.check_undo(old_state, old_pieces, move, self.max_depth)

        if self.testing and self.ab_pruning and not self.time_limit:
            # this checks that the same moves are being produced
            # it's turned off during iteritive deepening because it is slow
            nega_player = Negamax(self.board, self.is_white, self.max_depth, ab_pruning=False, testing=True)
            unpruned_moves = nega_player.get_moves()
            assert set(best_moves) == set(unpruned_moves)

        return best_moves

    def negamax(self, depth, alpha=None, beta=None):
        # return nothing if out of time
        if self.out_of_time():
            return None
        # check if the game is done or max_depth is reached
        if depth <= 0 or self.board.winner:
            return self.board.value
        moves = MoveGenerator(self.board).moves
        if self.testing:
            # grab the before state to test undo
            old_state, old_pieces = self.get_state()
        self.board.apply_move(moves[0])
        # get value of the first one to initalize max_val
        if self.ab_pruning:
            # maybe_value catches none values for early return from timeouts
            maybe_value = self.negamax(depth - 1, -beta, -alpha)
            if maybe_value is not None:
                max_val = - maybe_value
            else:
                self.board.undo_move()
                return None
        else:
            max_val = -self.negamax(depth - 1)
        # undo move
        self.board.undo_move()
        self.check_undo(old_state, old_pieces, moves[0], depth)
        #TODO: comment here to explain how this pruning works
        if self.ab_pruning:
            if max_val > beta:
                return max_val
            alpha = max(alpha, max_val)

        # try remaining moves
        for move in moves[1:]:
            # return nothing if out of time
            if self.out_of_time():
                return None
            if self.testing:
                # grab the old state to check undo
                old_state, old_pieces = self.get_state()
            # apply move
            self.board.apply_move(move)
            # get the value of this move
            if self.ab_pruning:
                # maybe_value catches none values for early return from timeouts
                maybe_value = self.negamax(depth - 1, -beta, -alpha)
                if maybe_value is not None:
                    val = - maybe_value
                else:
                    self.board.undo_move()
                    self.check_undo(old_state, move, depth)
                    return None
            else:
                val = -self.negamax(depth - 1)
            # remember the best value
            if val > max_val:
                max_val = val
            # undo move
            self.board.undo_move()
            self.check_undo(old_state, old_pieces, move, depth)
        return max_val

    def get_state(self):
        old_state = self.board.get_char_state_val()
        if self.is_white:
            old_pieces = self.board.white_piece_list.get_pieces()
        else:
            old_pieces = self.board.white_piece_list.get_pieces()
        return old_state, old_pieces

    def check_undo(self, old_state, old_pieces, move, depth):
        if self.testing:
            # compare the old state with the undone state
            undone_state, undone_pieces = self.get_state()
            for index in range(len(undone_pieces)):
                old = sorted(old_pieces)[index]
                undone = sorted(undone_pieces)[index]
                assert old == undone
            assert set(old_pieces) == set(undone_pieces)
            assert set(old_state) == set(undone_state)

    def out_of_time(self):
        # check if iteritive deepening
        if self.time_limit:
            time_elapsed = time.time() - self.start_time
            if time_elapsed > self.time_limit:
                return True
        return False


class IterativeDeepening(Player):
    def __init__(self, board, is_white, time_limit, testing=False):
        Player.__init__(self, board, is_white, testing)
        self.time_limit = time_limit
        self.time_elapsed = None
        self.start_time = None

    def get_moves(self):
        depth = 0
        old_moves = []
        new_moves = []
        self.start_time = time.time()
        while not self.out_of_time():
            depth += 1
            old_moves = new_moves
            self.time_elapsed = time.time() - self.start_time
            time_left = self.time_limit - self.time_elapsed
            new_moves = Negamax(board=self.board, is_white=self.is_white, max_depth=depth,
                                ab_pruning=True, time_limit=time_left, testing=self.testing).get_moves()
        print "depth reached: " + str(depth)
        return old_moves

    def out_of_time(self):
        self.time_elapsed = time.time() - self.start_time
        if self.time_elapsed > self.time_limit:
            return True
        return False


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
                self.client.write(self.move_to_char_move(self.board.last_move))
            # get the new move
            move, server_board, game_times = self.client.get_message()
            # todo: verify state and update time
        return [self.char_move_to_move(move)]

    @staticmethod
    def move_to_char_move(move):
        move_translator = {(5, 0): "a1", (5, 1): "b1", (5, 2): "c1", (5, 3): "d1", (5, 4): "e1",
                           (4, 0): "a2", (4, 1): "b2", (4, 2): "c2", (4, 3): "d2", (4, 4): "e2",
                           (3, 0): "a3", (3, 1): "b3", (3, 2): "c3", (3, 3): "d3", (3, 4): "e3",
                           (2, 0): "a4", (2, 1): "b4", (2, 2): "c4", (2, 3): "d4", (2, 4): "e4",
                           (1, 0): "a5", (1, 1): "b5", (1, 2): "c5", (1, 3): "d5", (1, 4): "e5",
                           (0, 0): "a6", (0, 1): "b6", (0, 2): "c6", (0, 3): "d6", (0, 4): "e6",
                           }
        return move_translator[move.src.cords] + "-" + move_translator[move.dest.cords]

    def char_move_to_move(self, char_move):
        move_translator = {"a1": (5, 0), "b1": (5, 1), "c1": (5, 2), "d1": (5, 3),  "e1": (5, 4),
                           "a2": (4, 0), "b2": (4, 1), "c2": (4, 2), "d2": (4, 3),  "e2": (4, 4),
                           "a3": (3, 0), "b3": (3, 1), "c3": (3, 2), "d3": (3, 3),  "e3": (3, 4),
                           "a4": (2, 0), "b4": (2, 1), "c4": (2, 2), "d4": (2, 3),  "e4": (2, 4),
                           "a5": (1, 0), "b5": (1, 1), "c5": (1, 2), "d5": (1, 3),  "e5": (1, 4),
                           "a6": (0, 0), "b6": (0, 1), "c6": (0, 2), "d6": (0, 3),  "e6": (0, 4),
                           }
        # if no move was passed, return nothing
        if "-" not in char_move:
            return None
        char_move = char_move[2:]
        char_move = char_move.split("-")
        src_cords = move_translator[char_move[0]]
        dest_cords = move_translator[char_move[1]]
        src = self.board.dict_board[src_cords]
        dest = self.board.dict_board[dest_cords]
        move = Move(src, dest)
        return move

    @staticmethod
    def get_char_moves(moves):
        char_moves = []
        for move in moves:
            char_moves.append(Net.move_to_char_move(move))
        return char_moves



