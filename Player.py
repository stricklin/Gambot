from State import Board
from MoveGenerator import MoveGenerator
import random
import socket
import time


class Player:
    def __init__(self, board: Board, is_white: bool, depth=0, testing=False):
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
        if not self.testing:
            random.shuffle(best_moves)
        return best_moves[0]

    # TODO: make a net player
    # TODO: make a iteritive deepening alpha-beta player with a time limit
    # TODO: add TT


class Human(Player):
    def __init__(self, board: Board, is_white: bool):
        Player.__init__(self, board, is_white)

    def get_moves(self):
        # get all the moves
        moves = MoveGenerator(self.board).get_moves()
        move_count = len(moves)
        selected_move = ""
        for i in range(move_count):
            print(str(i) + ". " + MoveGenerator.move_to_char_move(moves[i]) + " " + str(moves[i]))
        while not selected_move.isdigit() or int(selected_move) >= move_count:
            selected_move = input("Choose which numbered move you would like to take: ")
        return [moves[int(selected_move)]]


class Random(Player):
    def __init__(self, board: Board, is_white: bool):
        Player.__init__(self, board, is_white)

    def get_moves(self):
        assert self.is_white == self.board.whites_turn
        moves = MoveGenerator(self.board).get_moves()
        # the 0 and [0] are to comply with gemoves in other player classes
        return moves


class Negamax(Player):
    def __init__(self, board: Board, is_white: bool, depth: int, testing=False):
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

    def negamax(self, depth: int):
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
    def __init__(self, board: Board, is_white: bool, depth: int, testing=False):
        Player.__init__(self, board, is_white, depth, testing)

    def get_moves(self):
        assert self.is_white == self.board.whites_turn
        best_moves = []
        # TODO: vals is for debug
        vals = []
        # initalize max_val to lowest possible
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
            non_alpha_beta_moves, negamax_val, negamax_vals = Negamax(self.board, self.is_white, self.depth, True).get_moves()
            assert set(non_alpha_beta_moves) == set(best_moves)
        if self.testing:
            return best_moves, max_val, vals
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
    def __init__(self, board: Board, is_white: bool, username: str, password: str, offer: bool):
        Player.__init__(self, board, is_white)
        self.username = username
        self.password = password
        self.host = "imcs.svcs.cs.pdx.edu"
        self.port = 3589
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logfile_name = "net_logs/" + str(time.strftime("%c"))

        # make connection
        self.sock.connect((self.host, self.port))
        # verify connection
        welcome = self.read_line()
        if welcome != "100 imcs 2.5":
            print("wrong version of server")
            exit()
        # login or register
        if not self.login():
            self.register()

        if offer:
            self.offer()
        else:
            self.accept()

    def __del__(self):
        self.sock.close()

    def write(self, message):
        sockfile = self.sock.makefile(mode="w", newline="\n")
        sockfile.write(message + "\n")
        sockfile.close()
        self.log(message)

    def read_line(self):
        return self.read_lines(1)[0]

    def read_lines(self, n):
        lines = []
        sockfile = self.sock.makefile(mode="r", newline="\r\n")
        for line in range(n):
            lines.append(sockfile.readline().strip("\r\n"))
        for line in lines:
            self.log(line)
        return lines

    def read_move(self):
        # read in block
        message_block = self.read_lines(4)
        # parse block
        char_move = message_block[0].split()[1]
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

    def log(self, text):
        logfile = open(self.logfile_name, mode="a")
        logfile.write(text + "\n")
        logfile.close()

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
        if self.is_white:
            self.write("offer b")
        else:
            self.write("offer w")
            offerline_gamestart_firstbord = self.read_lines(5)
            #prelude = self.read_lines(4)

    def accept(self):
        self.write("list")
        # todo: getting the lines this way will probably not work, because the games are probably sent with the accept line all at once
        number_of_games = self.read_line.split()[2]
        # wait until there are games
        while number_of_games == 0:
            time.sleep(5)
            self.write("list")
            number_of_games = self.read_lines().split()[2]
        # read the games
        games = []
        for game in range(len(number_of_games)):
            games.append(self.read_lines())
        # take out the games offering the wrong side
        for game in games:
            if self.is_white:
                # TODO: none of this has run, it could all be wrong
                if game.split()[2] != "B":
                    games.remove(game)
            else:
                if game.split()[2] != "W":
                    games.remove(game)
        if games:
            game_index = games[0].split()[0]
            self.write("accept " + game_index)
        else:
            # try again
            time.sleep(5)
            self.accept()

    def get_moves(self):
        # send the move that the opponent just made
        self.write(MoveGenerator.move_to_char_move(self.board.last_move))
        # get the new move
        move = self.read_move()
        return [move]

    def char_move_to_move(self, char_move):
        src, dest = MoveGenerator.char_move_to_src_dest(char_move)
        moves = MoveGenerator(self.board).get_moves()
        for move in moves:
            if src == move[0] and dest == move[1]:
                return move
        assert False


