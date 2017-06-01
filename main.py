import State
import Player
import argparse
import time
# TODO: interitive deepening
# TODO: evaluator, change piece values for what phase the game is in. position: pawn structure, attacks/gaurding, xrays
# double pawn worth less
# isolated pawn worth less
# egde pawn worth less
# passed pawns worth more
# advanced pawns worth more
# keeping the king and queen back towards the homerow
# singular extention
# TODO: Transposition table
# TODO: pondering
# TODO: opening book


class Game:
    def __init__(self, board, white, black, display=True):
        self.board = board
        self.white = white
        self.black = black
        self.display = display
        self.game_start = None
        self.game_end = None
        self.white_time = None
        self.black_time = None

    def play_game(self,):
        self.game_start = time.time()
        self.white_time = 0
        self.black_time = 0
        while not self.board.winner:
            self.take_move(self.white)
            if not self.board.winner:
                self.take_move(self.black)
        self.end_game()

    def take_move(self, player):
            start = time.time()
            move = player.get_move()
            # show the board state and the move about to be applied
            self.print_board_and_move(move)
            # move might be None if game is over
            # TODO: this doesnt seem right, I bet I could get rid of checking if moves exist
            if move:
                self.board.apply_move(move)
            # save the last move applied for net player to send to server
            self.board.last_move = move
            stop = time.time()
            turn_duration = stop - start
            if player.is_white:
                self.white_time += turn_duration
            else:
                self.black_time += turn_duration
            self.print_time(turn_duration)

    def end_game(self):
        # apply one last move in case the game was won locally
        if self.board.winner is not "draw":
            if self.board.whites_turn:
                self.take_move(self.white)
            else:
                self.take_move(self.black)
        self.game_end = time.time()
        if self.display:
            print "winner: " + self.board.winner
            print "Total time: " + str(self.game_end - self.game_start)
            print "White's total time: " + str(self.white_time)
            print "Blacks's total time: " + str(self.black_time)

    def print_board_and_move(self, move):
        if self.display:
            self.board.print_char_state()
            print move

    def print_time(self, turn_duration):
        if self.display:
            print "Time: " + str(turn_duration)
            print


def make_player(arguments, board, is_white, testing):
    player = None
    player_type = get_arg_value(arguments, "pt")
    net_player = False
    assert player_type in ["h", "r", "nega", "id", "net"]
    # to pick the write type
    player_type_lookup = {"h": Player.Human,
                          "r": Player.Random,
                          "nega": Player.Negamax,
                          "id": Player.IterativeDeepening,
                          "net": Player.Net
                          }
    if player_type in ["h", "r"]:
        player = player_type_lookup[player_type](board, is_white, testing)
    elif player_type in ["nega"]:
        depth = int(get_arg_value(arguments, "d"))
        if "ab" in arguments:
            player = player_type_lookup[player_type](board, is_white, depth, True, testing)
        else:
            player = player_type_lookup[player_type](board, is_white, depth, False, testing)
    elif player_type in ["id"]:
            time_limit = int(get_arg_value(arguments, "t"))
            player = player_type_lookup[player_type](board, is_white, time_limit, testing)
    elif player_type in ["net"]:
            net_player = True
            username = get_arg_value(arguments, "u")
            password = get_arg_value(arguments, "p")
            game_type = get_arg_value(arguments, "gt")
            game_id = get_arg_value(arguments, "gid")
            if not game_id:
                player = player_type_lookup[player_type](board=board, is_white=is_white,
                                                         username=username, password=password, game_type=game_type)
            else:
                player = player_type_lookup[player_type](board=board, is_white=is_white,
                                                         username=username, password=password,
                                                         game_type=game_type, game_id=game_id)
    assert player
    return player, net_player


def get_arg_value(arguments, flag, delimiter=":"):
    """
    Will get a value of the first argument from a list of arguments prefixed with flag
    
    example: 
            get_arg_value([pt:nega, ab, d:5,], "pt",) returns the string "nega"
            get_arg_value([pt:nega, ab, d:5,], "d",) returns the string "5"
            get_arg_value([foo_bar], "foo, "_") returns the string "bar"
    :param arguments: The list of arguments
    :param flag: The flag for the argument
    :param delimiter: The delimiter separating the flag from the value. defaults to ":"
    :return: The value of the argument as a string, or None if the flag is not found
    """
    # Find argument
    arg_index = None
    for index in range(len(arguments)):
        if flag + delimiter in arguments[index]:
            arg_index = index
            break
    # If the argument is not found, return None
    if arg_index is None:
        return None
    # Get the argument and take off the flag
    arg = arguments[arg_index]
    val = arg.split(delimiter)[1]
    return val


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Play minichess!")
    # todo: rewrite this shinanagins
    players_description = """
    a player can only have one type. both a white_player and black_player player are required
    
    types include:
    h                                                       human player
    r                                                       random player
    nega <depth>                                            vanilla negamax player
    ab <depth>                                              alpha-beta negamax player
    net <username> <password> <offer/accept> <game number>  network player
    
    examples:
    -w r -b nega:5         
    starts a game with a white_player random player and a black_player network player
                           
    -w ab:3 -b net:myusername:mypassword
    starts a game with a white_player alpha-beta player and a black_player network player
    """

    players = parser.add_argument_group("players")
    parser.add_argument("-t", "--testing", action="store_true")
    players.add_argument("-w", "--white", nargs="+", required=True)
    players.add_argument("-b", "--black", nargs="+", required=True)
    parser.add_argument("-f", "--file", nargs=1, required=False,
                        help="File containing optional starting state")
    args = parser.parse_args()

    # read in a state from a file or load the starting state
    if args.file and args.white[0] != "net" and args.black[0] != "net":
        state = State.read_file(args.file)
        state = State.Board(state)
    else:
        state = State.Board(["0 W",
                             "kqbnr",
                             "ppppp",
                             ".....",
                             ".....",
                             "PPPPP",
                             "RNBQK"])
    if "net" in args.white or "net" in args.black:
        if "net" in args.white and "net" in args.black:
            exit("unable to have 2 net players")
        offerer, net_display1 = make_player(args.white, state, True, args.testing)
        other, net_display2 = make_player(args.black, state, True, args.testing)
        if offerer.is_white:
            white_player = offerer
            other.is_white = False
            black_player = other
        else:
            black_player = offerer
            other.is_white = True
            white_player = other

    else:
        # set up players
        white_player, net_display1 = make_player(args.white, state, True, args.testing)
        black_player, net_display2 = make_player(args.black, state, False, args.testing)

    net_display = (net_display1 or net_display2)

    game = Game(state, white_player, black_player, not net_display)
    game.play_game()

