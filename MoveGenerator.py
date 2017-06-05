from Move import Move


class MoveGenerator:
    def __init__(self, board):
        """
        makes all legal moves for the side on move
        :param board: the board to make moves for
        """
        self.board = board
        self.pieces = self.get_all_pieces()
        self.moves = []
        self.get_moves(self.pieces)

    def get_all_pieces(self):
        """
        :return: the pieces of the side on move
        """
        if self.board.whites_turn:
            return self.board.white_piece_list.get_pieces()
        else:
            return self.board.black_piece_list.get_pieces()

    def get_all_moves(self):
        """
        makes all moves and adds them to self.moves
        :return: None
        """
        self.get_moves(self.get_all_pieces())

    def get_moves(self, pieces):
        """
        makes all moves for the pieces specified and adds the moves to self.move
        :param pieces: the pieces specified
        :return: None
        """
        for piece in pieces:
            self.find_pieces_moves(piece)

    def find_pieces_moves(self, src):
        """
        makes all moves for the piece specified and adds the moves to self.move
        :param src: the piece
        :return: None
        """
        piece_type = src.piece.upper()

        # add the moves based on what kind of src it is
        if piece_type == "P":
            # set the forward direction
            if self.board.whites_turn:
                f = -1
            else:
                f = 1
            self.scan(src, src, f, -1, True, True, True)
            self.scan(src, src, f, 0, True, False, False)
            self.scan(src, src, f, 1, True, True, True)

        elif piece_type == "N":
            self.symscan(src, src, 2, 1, True, True)
            self.symscan(src, src, 1, 2, True, True)

        elif piece_type == "B":
            self.symscan(src, src, 1, 1, False, True)
            self.symscan(src, src, 0, 1, True, False)

        elif piece_type == "R":
            self.symscan(src, src, 0, 1, False, True)

        elif piece_type == "Q":
            self.symscan(src, src, 0, 1, False, True)
            self.symscan(src, src, 1, 1, False, True)

        elif piece_type == "K":
            self.symscan(src, src, 0, 1, True, True)
            self.symscan(src, src, 1, 1, True, True)

    def scan(self, src, intermediate, row_change, col_change, short, can_capture, must_capture=False):
        """
        looks at all the squares projected in the direction to search for valid moves
        valid moves are added to self.move
        :param src: the starting square, never changes because moves produced need a valid starting square
        :param intermediate: a square used to walk the board
        :param row_change: the change in rows
        :param col_change: the change in cols
        :param short: if the scan should continue in the direction
        :param can_capture: if the scan allows capturing moves
        :param must_capture: if the scan requires capturing moves
        :return: None
        """
        # make sure that the intermediate square is on the board
        if not self.check_bounds(intermediate, row_change, col_change):
            return
        dest_cords = (intermediate.row + row_change, intermediate.col + col_change)
        dest = self.board.dict_board[dest_cords]
        if dest.is_empty() and not must_capture:
            self.moves.append(Move(src, dest))
        else:
            # if the square is occupied the scan can stop
            short = True
        if not dest.is_empty():
            # if the dest has a enemy piece
            if src.piece.isupper() != dest.piece.isupper():
                if can_capture:
                    # if this scan allows capuring, add this move
                    self.moves.append(Move(src, dest))
        if not short:
            # recurse if scan not over
            self.scan(src, dest, row_change, col_change, short, can_capture, must_capture)

    def check_bounds(self, src, row_change, col_change):
        """
        checks if a square is on the board
        :param src: the starting square
        :param row_change: the change in rows
        :param col_change: the change in columns
        :return: True if square on board, False otherwise
        """
        r = src.row + row_change
        c = src.col + col_change
        if r < 0 or r >= self.board.row_count:
            return False
        if c < 0 or c >= self.board.col_count:
            return False
        return True

    def symscan(self, src, intermediate, row_change, col_change, short, can_capture, must_capture=False):
        """
        looks at all the squares projected in 4 directions to search for valid moves
        valid moves are added to self.move
        :param src: the starting square, never changes because moves produced need a valid starting square
        :param intermediate: a square used to walk the board
        :param row_change: the change in rows
        :param col_change: the change in cols
        :param short: if the scan should continue in the direction
        :param can_capture: if the scan allows capturing moves
        :param must_capture: if the scan requires capturing moves
        :return: None
        """
        # row_change and col_change are swapped and negated to get 4 directions
        self.scan(src, intermediate, row_change, col_change, short, can_capture, must_capture)
        self.scan(src, intermediate, -col_change, row_change, short, can_capture, must_capture)
        self.scan(src, intermediate, -row_change, -col_change, short, can_capture, must_capture)
        self.scan(src, intermediate, col_change, -row_change, short, can_capture, must_capture)
