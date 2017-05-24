import State
import Player
import argparse
import time


def make_player(arguments, board, is_white):
    player = None
    player_type = arguments[0]
    net_display = False
    assert player_type in ["h", "r", "nega", "ab", "net"]
    # to pick the write type
    player_type_lookup = {"h": Player.Human,
                          "r": Player.Random,
                          "nega": Player.Negamax,
                          "ab": Player.AlphaBeta,
                          "net": Player.Net
                          }
    # no arguments needed
    if player_type in ["h", "r"]:
        player = player_type_lookup[player_type](board, is_white)
    # depth needed, testing optional
    elif player_type in ["nega", "ab"]:
        if len(arguments) == 2:
            depth = int(arguments[1])
            player = player_type_lookup[player_type](board, is_white, depth)
        elif len(arguments) == 3:
            depth = int(arguments[1])
            testing = arguments[2] == "True"
            player = player_type_lookup[player_type](board, is_white, depth, testing)
    elif player_type in ["net"]:
            net_display = True
            username = arguments[1]
            password = arguments[2]
            game_type = arguments[3]
            if len(arguments) == 4:
                player = player_type_lookup[player_type](board, is_white, username, password, game_type)
            if len(arguments) == 5:
                game_number = arguments[4]
                player = player_type_lookup[player_type](board, is_white, username, password, game_type, game_number)
    assert player
    return player, net_display


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Play minichess!")
    players_description = """
    a player can only have one type. both a white and black player are required
    
    types include:
    h                                                       human player
    r                                                       random player
    nega <depth>                                            vanilla negamax player
    ab <depth>                                              alpha-beta negamax player
    net <username> <password> <offer/accept> <game number>  network player
    
    examples:
    -w r -b nega:5         
    starts a game with a white random player and a black network player
                           
    -w ab:3 -b net:myusername:mypassword
    starts a game with a white alpha-beta player and a black network player
    """

    players = parser.add_argument_group("players")
    players.add_argument("-w", "--white", nargs="+", required=True)
    players.add_argument("-b", "--black", nargs="+", required=True)
    parser.add_argument("-f", "--file", nargs=1, required=False,
                        help="File containing optional starting board")
    args = parser.parse_args()

    # read in a board from a file or load the starting board
    if args.file and args.white[0] != "net" and args.black[0] != "net":
        board = State.read_file(args.file)
        board = State.Board(board)
    else:
        board = State.Board(["0 W",
                             "kqbnr",
                             "ppppp",
                             ".....",
                             ".....",
                             "PPPPP",
                             "RNBQK"])
    if "net" in args.white or "net" in args.black:
        if "net" in args.white and "net" in args.black:
            exit("unable to have 2 net players")
        offerer, net_display1 = make_player(args.white, board, True)
        other, net_display2 = make_player(args.black, board, True)
        if offerer.is_white:
            white = offerer
            other.is_white = False
            black = other
        else:
            black = offerer
            other.is_white = True
            white = other

    else:
        # set up players
        white, net_display1 = make_player(args.white, board, True)
        black, net_display2 = make_player(args.black, board, False)
    white_time = 0
    black_time = 0

    net_display = net_display1 or net_display2
    game_start = time.time()
    while not board.winner:
        start = time.time()
        move = white.get_move()
        if not net_display:
            board.print_char_state()
            print move
        if move:
            board.apply_move(move)
        # save the last  move applied so that net players can grab it
        board.last_move = move
        stop = time.time()
        white_time += stop - start
        if not net_display:
            print "Time: " + str(stop - start)
            print
        if not board.winner:
            start = time.time()
            move = black.get_move()
            if not net_display:
                board.print_char_state()
                print move
            if move:
                board.apply_move(move)
            # save the last  move applied so that net players can grab it
            board.last_move = move
            stop = time.time()
            black_time += stop - start
            if not net_display:
                print "Time: " + str(stop - start)
                print
    # try one last move in case I won first
    if board.whites_turn:
        move = white.get_move()
        if move:
            board.apply_move(move)
    else:
        move = black.get_move()
        if move:
            board.apply_move(move)

    game_stop = time.time()
    if not net_display:
        print "winner: " + board.winner
        print "Total time: " + str(game_stop - game_start)
        print "White's time: " + str(white_time)
        print "Blacks's time: " + str(black_time)
