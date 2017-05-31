import socket
import time


class Client:

    def __init__(self):
        self.host = "imcs.svcs.cs.pdx.edu"
        self.port = 3589
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logfile_name = "net_logs/" + str(time.strftime("%c"))
        self.first_move = None
        self.is_white = None
        # make connection
        self.sock.connect((self.host, self.port))
        welcome = self.read_line()
        if welcome != "100 imcs 2.5":
            print "wrong version of server"
            exit()

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

    def get_message(self):
        # read in block
        message_block = self.read_lines(11)
        # parse block
        move = message_block[0]
        # handle gameover
        if "=" in move:
            game_over = move.split()
            if game_over[1] == "W":
                return 'w', None, None
            elif game_over[1] == "B":
                return 'b', None, None
            else:
                return 'd', None, None
        board = message_block[2].split("\n")
        game_times = message_block[3]
        # return info
        return move, board, game_times

    def get_first_move(self):
        temp = self.first_move
        self.first_move = None
        return temp

    def get_games(self):
        # new sockfiles are created here to escape logging unneeded things like:
        #   asking for games and not getting any
        # the game list that includes the game returned is manually logged at the end
        self.log("list")
        games = []
        while not games:
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
                    games.append(line)
            sockfile.close()
        for game in games:
            self.log(game)
        return games

    def log(self, text):
        logfile = open(self.logfile_name, mode="a")
        logfile.write(text + "\n")
        logfile.close()
        print text

    def login(self, username, password):
        self.write("me " + username + " " + password)
        reply = self.read_line()
        return reply.startswith("201")

    def register(self, username, password):
        self.write("register " + username + " " + password)
        reply = self.read_line()
        if not reply.startswith("202"):
            exit("problems registering " + self.username + " with password " + self.password)

    def offer(self):
        self.write("offer")
        self.start(True)
        return self.is_white

    def accept(self, game_number):
        self.write("accept " + game_number)
        self.start(False)
        return self.is_white

    def start(self, offer):
        sockfile = self.sock.makefile(mode="r")
        lines = [sockfile.readline().strip("\r\n")]
        # determine what color I am
        if offer:
            line = sockfile.readline().strip("\r\n")
            lines.append(line)
        else:
            line = lines[0]
        # if a game is accepted and you are white_player server side
        if "105" in line:
            lines += self.white_start(sockfile)
        # if a game is accepted and you are black_player server side
        elif "106" in line:
            lines += self.black_start(sockfile)
        sockfile.close()
        for line in lines:
            self.log(line)
        if self.is_white is None:
            exit("Something went wrong, game was not offered")

    def white_start(self, sockfile):
        # start when white_player serverside
        self.is_white = True
        lines = []
        for counter in range(10):
            line = sockfile.readline().strip("\r\n")
            lines.append(line)
        return lines

    def black_start(self, sockfile):
        # start when black_player serverside
        self.is_white = False
        lines = []
        for counter in range(11):
            line = sockfile.readline().strip("\r\n")
            lines.append(line)
        self.first_move = lines[0]
        return lines
