import State
import MoveGenerator
import Player
import argparse


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--white", nargs=1, required=True)
    parser.add_argument("-b", "--black", nargs=1, required=True)
    parser.add_argument("-f", "--file", nargs=1, required=False,
                        help="File containing optional starting board,")
    args = parser.parse_args()

    # for setting up players
    player_type_lookup = {"r": Player.Random}


    # TODO: we will need to set the depth of the player

    # read in a board from a file or load the starting board
    if args.file:
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
    # set up players
    white = player_type_lookup[args.white[0]](board, True)
    black = player_type_lookup[args.black[0]](board, False)

    board.print_char_state()
    while not board.winner:
        move = white.get_move()
        print(move)
        print()
        board.apply_move(move, True)
        board.print_char_state()
        print()
        if not board.winner:
            move = black.get_move()
            print(move)
            print()
            board.apply_move(move, False)
            board.print_char_state()
            print()
    print("winner: " + board.winner)
