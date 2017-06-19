Gambot: a minichess player

Gambot runs best with pypy, but it can also be ran with  just python.
python ./main.py -p -t -w pt:net u:username p:password gt:offer -b pt:id etl:2 ltl:9
Will start a game with:
    -p, pawn promotion turned on
    -t, testing turned on
    -w, the white player
        pt:net, a player of type net
            u:username, the username used to sign onto the server
            p:password, the password used to sign onto the server
            gt:offer, the game type (can be offer or accept)
    -b, the black player
        pt:id, a player of type iteritive deepening
        etl:2, a early time limit of 2 seconds
        ltl:9, late time limit of 9 seconds
If you run ./main.py help more options should be given

The pricipal components of Gambot can be found in Board.py and Player.py.
The respective responsibilites of these components are to hold the game state
and to modify it. All of the other components support these two.

Board.py holds the game state. It uses piece lists for both sides and a dict
with all of the squares in it for quick access to squares. There are functions
for applying moves and undoing moves with the undo information store in a stack.
All of the information and mechanisms needed for board evaluation is also
contained here. This consists of material values for pieces and added pawn
formation values. It also contains the Zobrist keyring for creating hash values
of its states.

main.py interprets comand line arguments, creates a board and players, then
runs the game until completion by having the players take alternating turns.

Square.py contains the class Square which consists of cordinates and a piece
value. It's used for representing game pieces, board squares, and moves.

Move.py contains the class Move. A Move is just a container for two squares,
src and dest.

PieceLists.py constains the class PieceList. A PieceList contains a dict that
maps piece types to lists of pieces, this cuts out iterating through the piece
lists to get the wanted pieces and allows the pieces to be returned in a sorted
order.

Undo.py contains the class Undo. A Undo is just a container for the two squares
modified when a board applys a move and the value of the board before the move
was applied. This makes undoing moves very simple.

Player.py contains all of the player classes. The base class Player holds the
variables common to all the other players and functions that translate between
the internal move representation and the standard chess format. The common
variables are: board, is_white and testing. Board is the game state, is_white
is a boolean flag indicating which side this player is, and testing is a flag
indicating if the test functions should be run or not. If testing is turned on,
the best_moves chosen by the derived players are not shuffled and instead the
first move is chosen. Making the game deterministic made debugging much easier.

The Human Player allows for a human to play the game. All the moves are
generated and listed, then the human is prompted to choose one.

The Random Player generates all moves and passes them all to the base player
to be shuffled, thus producing random moves.

The Negamax player uses negamax search to find moves that produce the best
value. It has the options of using alphabeta pruning or transposition tables,
but right now using transposition tables and alphabeta pruning at the same
time results in bad moves being chosen. Either one by itself produces the right
moves. When testing is turned on it makes sure that undo returns the board to
the right state and that alphabeta pruning produces the same moves as regular
negamax

The IterativeDeepening player creates deeper and deeper negamax players until
time runs out to choose the best moves. There are options to set a early time
limit and a late time limit so that the first 10 moves of the game only use the
early time limit.

The Net Player contains a Client that allows it to talk to the chess server.
It sends the last move that was made and then gets the new move from the
server.

TTable.py contains the class TTable. A TTable is two dicts, one that maps
depths to queues of Zobrist hashes and another that maps Zobrist hashes to
entries. Having both of these allows for the oldest shallowest entry to get
removed when the TTable is full and a deeper entry is trying to get stored.

TTableEntry.py contains the class TTableEntry. A TTableEntry is a vaule, a
depth, a zobrist_hash, a flag for alphabeta pruning, and a bound for alphabeta
pruning.

tests.py is where all of the unittests live. They are a major boon when doing
major refactoring.

The biggest problem in my program is alphabeta pruning with TTables turned on
doesn't work.
