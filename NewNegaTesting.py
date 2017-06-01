import State
from main import Game
import Player

if __name__ == "__main__":
    state = State.Board(["0 W",
                         "kqbnr",
                         "ppppp",
                         ".....",
                         ".....",
                         "PPPPP",
                         "RNBQK"])
    white = Player.NewNegamax(state, True, 2, False, True)
    black = Player.NewNegamax(state, False, 2, True, True)

    game = Game(state, white, black)
    game.play_game()
