import State
import Player
import argparse
import time
# TODO: ab Transposition table
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
        # remember who won before last moves are applied
        winner = self.board.winner
        # apply one last move in case the game was won locally
        if self.board.winner != "draw":
            if self.board.whites_turn:
                self.take_move(self.white)
            else:
                self.take_move(self.black)
        self.game_end = time.time()
        if self.display:
            print "winner: " + winner
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
    elif player_type in ["nega", "id"]:
        if "ab" in arguments:
            ab_pruning = True
        else:
            ab_pruning = False
        if "tt" in arguments:
            use_t_table = True
        else:
            use_t_table = False
        if player_type == "nega":
            depth = int(get_arg_value(arguments, "d"))
            player = player_type_lookup[player_type](board=board, is_white=is_white, max_depth=depth,
                                                     ab_pruning=ab_pruning, use_t_table=use_t_table, testing=testing)
        elif player_type == "id":
            time_limit = int(get_arg_value(arguments, "tl"))
            player = player_type_lookup[player_type](board=board, is_white=is_white, ab_pruning=ab_pruning,
                                                     time_limit=time_limit, t_table=use_t_table, testing=testing)
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
    players_description = """
    game types include:
    -p adds pawn evaluation
    -t runs in testing mode
    player types include:
    pt:h                                                                 human player
    pt:r                                                                 random player
    pt:nega ab d:<max_depth>                                                negamax player
    pt:net u:<username> p:<password> gt:<offer/accept> gid:<game id>     network player
    
    examples:
    -t -p -w pt:r -b pt:nega d:5         
    starts a game with a white_player random player and a black_player negamax player
    with testing and pawn evaluation turned on
                           
    -w pt:nega ab d:3 -b pt:net u:myusername p:mypassword gt:accept gn:12345
    starts a game with a white_player alpha-beta player of max_depth 3 
    and a black network player that will accept the game with id 12345
    """

    players = parser.add_argument_group("players")
    parser.add_argument("-t", "--testing", action="store_true")
    parser.add_argument("-p", "--pawn_evaluation", action="store_true")
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
                             "RNBQK"], args.pawn_evaluation)
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

