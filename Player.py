from Client import Client
from MoveGenerator import MoveGenerator
from Move import Move
from Square import Square
from TTable import TTable
from TTableEntry import TTableEntry
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


class Human(Player):
    def __init__(self, board, is_white, testing=False):
        Player.__init__(self, board, is_white, testing)

    def get_moves(self):
        # get all the moves
        moves = MoveGenerator(self.board).moves
        move_count = len(moves)
        selected_move = ""
        for i in range(move_count):
            print str(i) + ". " + self.move_to_char_move(moves[i]) + " " + str(moves[i])
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
    def __init__(self, board, is_white, max_depth, ab_pruning=False, use_t_table=False, t_table=None, time_limit=None,
                 testing=False, print_visited=True):
        Player.__init__(self, board, is_white, testing)
        self.max_depth = max_depth
        self.ab_pruning = ab_pruning
        if use_t_table:
            if t_table is None:
                self.t_table = TTable()
            else:
                self.t_table = t_table
        else:
            self.t_table = None
        self.print_node_hit_info = print_visited
        self.max_val = -10000
        self.time_limit = time_limit
        self.start_time = None
        self.states_visited = 0
        self.t_table_hits = 0
        # vals is for testing
        self.vals = []

    def get_moves(self):
        assert self.is_white == self.board.whites_turn
        self.states_visited = 0
        self.t_table_hits = 0
        # start timer for iteritive deepening
        if self.time_limit:
            self.start_time = time.time()
        best_moves = []
        # initialize max_val to lowest value
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
                old_state, old_pieces, old_zob_hash = self.get_state()
            # apply move
            self.board.apply_move(move)
            self.states_visited += 1
            val = self.get_board_value(0, -10000, 10000)
            if val is None:
                # val could only be none because of timeout
                self.board.undo_move()
                if self.testing:
                    self.check_undo(old_state, old_pieces, old_zob_hash)
                return None
            self.update_t_table(0, val, -10000, 10000)
            best_moves = self.update_best_moves(move, best_moves, val)
            # undo move
            self.board.undo_move()
            if self.testing:
                self.check_undo(old_state, old_pieces, old_zob_hash)

        if self.testing and self.ab_pruning and not self.time_limit:
            # this checks that the same moves are being produced
            # it's turned off during iteritive deepening because it is slow
            nega_player = Negamax(self.board, self.is_white, self.max_depth, ab_pruning=False,
                                  testing=True, print_visited=False)
            unpruned_moves = nega_player.get_moves()
            assert set(best_moves) == set(unpruned_moves)
        if self.print_node_hit_info:
            print str(self.states_visited) + " states visited"
            print str(self.t_table_hits) + " TTable hits"
        return best_moves

    def negamax(self, depth, alpha=None, beta=None):
        original_alpha = alpha
        # return nothing if out of time
        if self.out_of_time():
            return None
        # check if the game is done or max_depth is reached
        if depth >= self.max_depth or self.board.winner:
            return self.board.value
        moves = MoveGenerator(self.board).moves
        if self.testing:
            # grab the before state to test undo
            old_state, old_pieces, old_zob_hash = self.get_state()
        self.board.apply_move(moves[0])
        self.states_visited += 1
        # get value of the first one to initalize max_val
        max_val, alpha, beta = self.get_board_value(depth, alpha, beta)
        if max_val is None:
            self.board.undo_move()
            if self.testing:
                self.check_undo(old_state, old_pieces, old_zob_hash)
            return None
        self.update_t_table(depth, max_val, original_alpha, beta)
        # undo move
        self.board.undo_move()
        if self.testing:
            self.check_undo(old_state, old_pieces, old_zob_hash)
        # TODO: comment here to explain how this pruning works
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
                old_state, old_pieces, old_zob_hash = self.get_state()
            # apply move
            self.board.apply_move(move)
            self.states_visited += 1
            # get the value of this move
            val, alpha, beta = self.get_board_value(depth, alpha, beta)
            if val is None:
                self.board.undo_move()
                if self.testing:
                    self.check_undo(old_state, old_pieces, old_zob_hash)
                return None
            self.update_t_table(depth, val, original_alpha, beta)
            # remember the best value
            if val > max_val:
                max_val = val
            # undo move
            self.board.undo_move()
            if self.testing:
                self.check_undo(old_state, old_pieces, old_zob_hash)
        return max_val

    def get_board_value(self, depth, alpha, beta):
        # initalize flags
        val = None
        more_search_required = True
        # check t_table
        if self.t_table:
            entry = self.t_table.get_entry(self.board.zob_hash)
            # if this is a valid entry
            if entry and entry.depth >= depth:
                self.t_table_hits += 1
                # if no alpha beta pruning, the ttable entry is exact
                if not entry.ab_pruning or entry.bound == "exact":
                    more_search_required = False
                else:
                    if entry.bound == "lower":
                        alpha = max(entry.value, alpha)
                    else:
                        beta = min(entry.value, alpha)
                    if alpha >= beta:
                        more_search_required = False
                if not more_search_required:
                    val = entry.value
        if val is None or more_search_required:
                val = self.get_negamax_value(depth, alpha, beta)
        return val, alpha, beta

    def get_negamax_value(self, depth, alpha=None, beta=None):
        if self.ab_pruning:
            val = self.negamax(depth + 1, -beta, -alpha)
        else:
            val = self.negamax(depth + 1)
        if val is not None:
            val = -val
        return val

    def update_best_moves(self, move, best_moves, val):
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
        return best_moves

    def update_t_table(self, depth, value, alpha=None, beta=None):
        if self.t_table is None:
            return
        zob_hash = self.board.zob_hash
        if self.ab_pruning:
            if value <= alpha:
                bound = "upper"
            elif value >= beta:
                bound = "lower"
            else:
                bound = "exact"
            entry = TTableEntry(value, depth, zob_hash, True, bound)
        else:
            entry = TTableEntry(value, depth, zob_hash)
        self.t_table.try_to_add(entry)

    def get_state(self):
        state = self.board.get_char_state_val()
        zob_hash = self.board.zob_hash
        if self.is_white:
            pieces = self.board.white_piece_list.get_pieces()
        else:
            pieces = self.board.white_piece_list.get_pieces()
        return state, pieces, zob_hash

    def check_undo(self, old_state, old_pieces, old_zob_hash):
        # compare the old state with the undone state
        undone_state, undone_pieces, undone_zob_hash = self.get_state()
        assert set(old_state) == set(undone_state)
        assert set(old_pieces) == set(undone_pieces)
        assert old_zob_hash == undone_zob_hash

    def out_of_time(self):
        # check if iteritive deepening
        if self.time_limit:
            time_elapsed = time.time() - self.start_time
            if time_elapsed > self.time_limit:
                return True
        return False


class IterativeDeepening(Player):
    def __init__(self, board, is_white, time_limit, ab_pruning, t_table, testing=False):
        Player.__init__(self, board, is_white, testing)
        self.time_limit = time_limit
        self.time_elapsed = None
        self.start_time = None
        self.ab_pruning = ab_pruning
        if t_table:
            self.use_t_table = True
            self.t_table = TTable()
        else:
            self.use_t_table = False
            self.t_table = None
        self.states_visited = 0
        self.t_table_hits = 0

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
            player = Negamax(board=self.board, is_white=self.is_white, max_depth=depth, ab_pruning=self.ab_pruning,
                             time_limit=self.time_limit, use_t_table=self.use_t_table,
                             testing=self.testing)
            new_moves = player.get_moves()
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




