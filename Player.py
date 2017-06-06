from Client import Client
from MoveGenerator import MoveGenerator
from Move import Move
from TTable import TTable
from TTableEntry import TTableEntry
import random
import time


class Player:
    """
    a base class for other player types
    """
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
            # it's helpful for games to be deterministic when debugging
            random.shuffle(best_moves)
        return best_moves[0]

    @staticmethod
    def move_to_char_move(move):
        """
        turns a move into a char string for talking to the server
        :param move: the move to translate
        :return: the translated move
        """
        move_translator = {(5, 0): "a1", (5, 1): "b1", (5, 2): "c1", (5, 3): "d1", (5, 4): "e1",
                           (4, 0): "a2", (4, 1): "b2", (4, 2): "c2", (4, 3): "d2", (4, 4): "e2",
                           (3, 0): "a3", (3, 1): "b3", (3, 2): "c3", (3, 3): "d3", (3, 4): "e3",
                           (2, 0): "a4", (2, 1): "b4", (2, 2): "c4", (2, 3): "d4", (2, 4): "e4",
                           (1, 0): "a5", (1, 1): "b5", (1, 2): "c5", (1, 3): "d5", (1, 4): "e5",
                           (0, 0): "a6", (0, 1): "b6", (0, 2): "c6", (0, 3): "d6", (0, 4): "e6",
                           }
        return move_translator[move.src.cords] + "-" + move_translator[move.dest.cords]

    def char_move_to_move(self, char_move):
        """
        turns a char string into a move
        :param char_move: the char string to translate
        :return: the translated move
        """
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
        """
        turns a list of moves into char moves
        used for testing against move generator
        :param moves: the moves to translate
        :return: the translated moves
        """
        char_moves = []
        for move in moves:
            char_moves.append(Net.move_to_char_move(move))
        return char_moves


class Human(Player):
    """
    a player that lets a human play the game
    """
    def __init__(self, board, is_white, testing=False):
        Player.__init__(self, board, is_white, testing)

    def get_moves(self):
        """
        generates all moves then allows human to choose one
        :return: the chosen move
        """
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
    """
    a player that makes random moves
    """
    def __init__(self, board, is_white, testing=False):
        Player.__init__(self, board, is_white, testing)

    def get_moves(self):
        """
        generates all moves and selects a random one
        :return: the random move chosen
        """
        assert self.is_white == self.board.whites_turn
        moves = MoveGenerator(self.board).moves
        # the 0 and [0] are to comply with gemoves in other player classes
        return moves


class Negamax(Player):
    """
    a player that uses negamax to choose moves
    """
    def __init__(self, board, is_white, max_depth, ab_pruning=False, use_t_table=False, t_table=None, time_limit=None,
                 testing=False, print_visited=True):
        Player.__init__(self, board, is_white, testing)
        self.max_depth = max_depth
        self.ab_pruning = ab_pruning
        # initalize t_table
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

    def get_moves(self):
        """
        explores negamax tree to select moves
        :return: returns the moves with the highest value
        """
        alpha = -10000
        beta = 10000
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
            val, alpha, beta = self.get_board_value(0, alpha, beta)
            if val is None:
                # val could only be none because of timeout
                self.board.undo_move()
                if self.testing:
                    self.check_undo(old_state, old_pieces, old_zob_hash)
                return None
            self.update_t_table(0, val, alpha, beta)
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
            print str(self.states_visited) + " states visited | " + str(self.t_table_hits) + " TTable hits"
        return best_moves

    def negamax(self, depth, alpha=None, beta=None):
        """
        the recursive function that explores the negamax tree to get move values
        :param depth: the depth to explore to
        :param alpha: the best value for player on move along path to root
        :param beta: the best value for other player along path to root
        :return: the value of the move, or None if ran out of time
        """
        original_alpha = alpha
        # return nothing if out of time
        if self.out_of_time():
            return None
        # check if the game is done or max_depth is reached
        if depth >= self.max_depth or self.board.winner:
            return self.board.value
        moves = MoveGenerator(self.board).moves
        if not moves:
            self.board.lose()
            return None
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
        """
        a wrapper function that checks the t_table and does the right kind of negamax
        :param depth: the depth to search to
        :param alpha: the best value for player on move along path to root
        :param beta: the best value for other player along path to root
        :return: the value of the move, or None if ran out of time
        """
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
        """
        a wrapper that handles returning vals being None
        :param depth: the depth to search to
        :param alpha: the best value for player on move along path to root
        :param beta: the best value for other player along path to root
        :return: the value of the move, or None if ran out of time
        """
        if self.ab_pruning:
            val = self.negamax(depth + 1, -beta, -alpha)
        else:
            val = self.negamax(depth + 1)
        if val is not None:
            val = -val
        return val

    def update_best_moves(self, move, best_moves, val):
        """
        updates the list of best moves
        :param move: the current move 
        :param best_moves: the list of best moves so far
        :param val: the val of current move
        :return: the new list of best moves
        """
        # if this is a better move, remember it
        if val > self.max_val:
            self.max_val = val
            best_moves = [move]
        # if more than one move is best, keep them all
        elif val == self.max_val:
            best_moves.append(move)
        return best_moves

    def update_t_table(self, depth, value, alpha=None, beta=None):
        """
        attempts to put a TTEntry into the table
        :param depth: the current depth
        :param value: the value of the state
        :param alpha: the best value for player on move along path to root
        :param beta: the best value for other player along path to root
        :return: None
        """
        # return early if not using t_table
        if self.t_table is None:
            return
        zob_hash = self.board.zob_hash
        # get ab bound
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
        """
        used for getting before state to test undo
        :return: the char state, piece list, and zob_hash of current board
        """
        state = self.board.get_char_state_val()
        zob_hash = self.board.zob_hash
        if self.is_white:
            pieces = self.board.white_piece_list.get_pieces()
        else:
            pieces = self.board.white_piece_list.get_pieces()
        return state, pieces, zob_hash

    def check_undo(self, old_state, old_pieces, old_zob_hash):
        """
        checks the old state values vs the undone state values
        :param old_state: the old char state
        :param old_pieces: the old piece list
        :param old_zob_hash: the old zob_hash
        :return: 
        """
        # compare the old state with the undone state
        undone_state, undone_pieces, undone_zob_hash = self.get_state()
        assert set(old_state) == set(undone_state)
        assert set(old_pieces) == set(undone_pieces)
        assert old_zob_hash == undone_zob_hash

    def out_of_time(self):
        """
        checks if out of time
        :return: True if out of time, False otherwise
        """
        # check if iteritive deepening
        if self.time_limit:
            if self.time_limit < 0:
                return True
            time_elapsed = time.time() - self.start_time
            if time_elapsed > self.time_limit:
                return True
        return False


class IterativeDeepening(Player):
    """
    a player that uses iterative deepening negamax to choose moves
    """
    def __init__(self, board, is_white, early_time_limit, late_time_limit, ab_pruning, t_table, testing=False):
        Player.__init__(self, board, is_white, testing)
        self.early_time_limit = early_time_limit
        self.late_time_limit = late_time_limit
        self.time_elapsed = None
        self.start_time = None
        self.ab_pruning = ab_pruning
        self.use_t_table = t_table
        self.states_visited = 0
        self.t_table_hits = 0

    def get_moves(self):
        """
        gets moves from multiple negamax searches
        :return: the best moves from the deepest completed negamax search
        """
        depth = 0
        old_moves = []
        new_moves = []
        self.start_time = time.time()
        if self.board.turn_count > 10:
            time_limit = self.late_time_limit
        else:
            time_limit = self.early_time_limit
        while not self.out_of_time(time_limit):
            depth += 1
            # this keeps partially completed searches from being used
            old_moves = new_moves
            self.time_elapsed = time.time() - self.start_time
            time_left = time_limit - self.time_elapsed
            # TODO: right now the old t_table is thrown away each time because otherwise it doesnt keep going deeper
            # it would be better if it wasnt like that
            player = Negamax(board=self.board, is_white=self.is_white, max_depth=depth, ab_pruning=self.ab_pruning,
                             time_limit=time_left, use_t_table=self.use_t_table,
                             testing=self.testing)
            new_moves = player.get_moves()
        print "depth reached: " + str(depth -1)
        return old_moves

    def out_of_time(self, time_limit):
        """
        checks if out of time
        :return: True if out of time, False otherwise
        """
        self.time_elapsed = time.time() - self.start_time
        if self.time_elapsed > time_limit:
            return True
        return False


class Net(Player):
    """
    a player that gets it's moves from the chess server
    """
    def __init__(self, board, is_white, username, password, game_type, game_id=None):
        Player.__init__(self, board, is_white)
        self.username = username
        self.password = password
        self.game_type = game_type
        self.game_id = game_id
        self.client = Client()

        # try to login or register
        if not self.client.login(self.username, self.password):
            if not self.client.register(self.username, self.password):
                exit("unable to login or register")

        # the returns are negated because net players are the opposite color serverside
        if "offer" in game_type:
            if self.is_white:
                self.is_white = not self.client.offer("w")
            else:
                self.is_white = not self.client.offer("b")

        else:
            self.is_white = not self.accept()

    def accept(self):
        """
        accepts a game
        :return: the game id of game accepted
        """
        # if game id specified, accept that game
        if self.game_id:
            return self.client.accept(self.game_id)
        # read the games
        games = self.client.get_games()
        game_number = -1
        for game in games:
            if game.split()[4] != "[in-progress]":
                game_number = game.split()[0]
        assert game_number > 0
        return self.client.accept(game_number)

    def get_moves(self):
        """
        sends the last move made and recives the next move
        :return: the move recieved from the server
        """
        # this only happens when Net is black_player serverside
        move = self.client.get_first_move()
        if move is None:
            # send the move that the opponent just made
            if self.board.last_move:
                self.client.write(self.move_to_char_move(self.board.last_move))
            # get the new move
            move, server_board, game_times = self.client.get_message()
        return [self.char_move_to_move(move)]
