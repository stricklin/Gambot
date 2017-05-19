from State import Board
from MoveGenerator import MoveGenerator
import random
import socket
import time
import copy


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

    # TODO: make a net player
    # TODO: make a iteritive deepening alpha-beta player with a time limit
    # TODO: add TT


class Human(Player):
    def __init__(self, board, is_white):
        Player.__init__(self, board, is_white)

    def get_moves(self):
        # get all the moves
        moves = MoveGenerator(self.board).get_moves()
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
        moves = MoveGenerator(self.board).get_moves()
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
        moves = MoveGenerator(self.board).get_moves()
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
        moves = MoveGenerator(self.board).get_moves()
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
        moves = MoveGenerator(self.board).get_moves()
        if not moves:
            self.board.lose()
            return None
        alpha = -10000
        beta = 10000
        for move in moves:
            # apply move
            captured_piece, promoted_piece = self.board.apply_move(move)
            # get the value of this move
            # this is the widest window possible for alpha beta
            val = - self.alphabeta(self.depth, alpha, beta)
            # if this is a better move, remember it
            # the better move is the smallest value because its the value of the opponents turn
            if val > alpha:
                alpha = val
                best_moves = [move]
                if self.testing:
                    vals = [val]
            # if more than one move is best, keep them all
            elif val == alpha:
                best_moves.append(move)
                if self.testing:
                    vals.append(val)
            # keep track of the worst value seen
            if val < beta:
                beta = val
            # undo move
            self.board.undo_move(move, captured_piece, promoted_piece)
        if self.testing:
            # make sure that negamax and alpha beta are returning the same values
            negamax_moves, negamax_val, negamax_vals = Negamax(self.board, self.is_white, self.depth, True).get_moves()
            assert set(negamax_moves) == set(best_moves)
        if self.testing:
            return best_moves, alpha, vals
        return best_moves

    def alphabeta(self, depth, alpha, beta):
        # check if the game is done or depth is reached
        if depth <= 0 or self.board.winner:
            return self.board.value
        moves = MoveGenerator(self.board).get_moves()
        # get value of the first one to initalize max_val todo: I'm pretty sure this is why we do it
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
    def __init__(self, board, is_white, username, password, game_type):
        Player.__init__(self, board, is_white)
        self.username = username
        self.password = password
        self.host = "imcs.svcs.cs.pdx.edu"
        self.port = 3589
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logfile_name = "net_logs/" + str(time.strftime("%c"))
        self.game_type = game_type
        self.first_move = None

        # make connection
        self.sock.connect((self.host, self.port))
        # verify connection
        welcome = self.read_line()
        if welcome != "100 imcs 2.5":
            print "wrong version of server"
            exit()
        # login or register
        if not self.login():
            self.register()

        if "offer" in game_type:
            self.offer()
        else:
            self.accept()

    def __del__(self):
        self.sock.close()

    def write(self, message):
        sockfile = self.sock.makefile(mode="w")
        sockfile.write(message + "\n")
        sockfile.close()
        self.log(message)

    def read_line(self):
        return self.read_lines(1)[0]

    def read_lines(self, n):
        lines = []
        sockfile = self.sock.makefile(mode="r")
        for line in range(n):
            lines.append(sockfile.readline().strip("\r\n"))
        for line in lines:
            self.log(line)
        return lines

    def read_move(self):
        # read in block
        message_block = self.read_lines(11)
        # parse block
        char_move = message_block[0]
        # handle gameover
        if "=" in char_move:
            game_over = char_move.split()
            if game_over[1] == "W":
                self.board.win("white")
            elif game_over[1] == "B":
                self.board.win("black")
            else:
                self.board.draw()
            move = None
            return move
        board = message_block[2].split("\n")
        time = message_block[3]
        # check board
        foo = self.board.get_char_state()
        # todo: this check is in the wrong spot. its happening after the non net player makes a move
        # todo: so the board looks wrong.
        #assert set(board) == set(self.board.get_char_state())
        # update time
        # todo: update time
        # return move
        move = self.char_move_to_move(char_move)
        return move

    def read_games(self):
        # new sockfiles are created here to escape logging unneeded things like:
        #   asking for games and not getting any
        #   asking for games and only getting the wrong type
        # the game list that includes the game returned is manually logged at the end
        self.log("list")
        games = []
        while not games:
            # for logging
            original_games = []

            # ask for games
            sockfile = self.sock.makefile(mode="w")
            sockfile.write("list" + "\n")
            sockfile.close()

            # read games
            sockfile = self.sock.makefile(mode="r")
            line = None
            while line != '.':
                line = sockfile.readline().strip("\r\n")
                if "available" not in line and "." not in line:
                    original_games.append(line)
            sockfile.close()
            games = copy.deepcopy(original_games)

            # remove games of wrong type
            for game in games:
                if self.is_white:
                    foo = game.split()[2]
                    if game.split()[2] != "W":
                        games.remove(game)
                else:
                    if game.split()[2] != "B":
                        games.remove(game)
        for game in original_games:
            self.log(game)
        return games

    def log(self, text):
        logfile = open(self.logfile_name, mode="a")
        logfile.write(text + "\n")
        logfile.close()
        print text

    def login(self):
        self.write("me " + self.username + " " + self.password)
        reply = self.read_line()
        return reply.startswith("201")

    def register(self):
        self.write("register " + self.username + " " + self.password)
        reply = self.read_line()
        if not reply.startswith("202"):
            exit("problems registering " + self.username + " with password " + self.password)

    def offer(self):
        """
        This function makes an offer of a game
        offer x will offer a game where the offerer plays side x
        here it is flipped because the net player presents different sides to the program and the outside
        :return: 
        """
        if self.game_type == "offer?":
            self.write("offer")
            sockfile = self.sock.makefile(mode="r", newline="\r\n")
            lines = [sockfile.readline().strip("\r\n")]
            # determine what color I am
            line = sockfile.readline().strip("\r\n")
            lines.append(line)
            # if a game is accepted and you are white
            if "106" in line:
                self.is_white = True
                prelude_size = 3
            # if a game is accepted and you are black
            else:
                self.is_white = False
                prelude_size = 12
            for counter in range(prelude_size):
                line = sockfile.readline().strip("\r\n")
                lines.append(line)
            if self.is_white:
                self.first_move = self.char_move_to_move(lines[10])
            sockfile.close()
            for line in lines:
                self.log(line)
        # for offering black
        elif not self.is_white:
            self.write("offer w")
            prelude = self.read_lines(5)
        # for offering white
        else:
            self.write("offer b")
            # this prelude includes the first move
            prelude = self.read_lines(6)
            # todo: explain why the below is needed
            self.first_move = self.char_move_to_move(prelude[2])

    def accept(self):
        # read the games
        games = self.read_games()
        game_number = games[0].split()[0]
        self.write("accept " + game_number)
        if not self.is_white:
            prelude = self.read_lines(11)
        else:
            # this prelude includes the first move
            prelude = self.read_lines(12)
            self.first_move = self.char_move_to_move(prelude[1])

    def get_moves(self):
        # this only happens when Net is white
        if self.first_move:
            move = self.first_move
            self.first_move = None
        else:
            # send the move that the opponent just made
            if self.board.last_move:
                self.write(MoveGenerator.move_to_char_move(self.board.last_move))
            # get the new move
            move = self.read_move()
        return [move]

    def char_move_to_move(self, char_move):
        if char_move == '':
            return None
        char_move = char_move.split()[1]
        src, dest = MoveGenerator.char_move_to_src_dest(char_move)
        moves = MoveGenerator(self.board).get_moves()
        for move in moves:
            if src == move[0] and dest == move[1]:
                return move
        assert False


