class PieceList:
    """
    holds pieces for board in dicts for easy access
    orders pieces to produce better move ordering
    """
    def __init__(self):
        self.pieces_by_type = {
            "K": [],
            "P": [],
            "B": [],
            "R": [],
            "Q": [],
            "N": [],
        }
        # the pieces are ordered like this because I always want to make sure
        # that the king gets out of harms way first,
        # that pawns are considered second for pawn evaluation
        # and that knights are considered last because they are terrible
        self.ordering = ["K", "P", "B", "R", "Q", "N"]

    def add(self, square):
        """
        puts a piece into the piecelist
        :param square: the piece 
        :return: None
        """
        self.pieces_by_type[square.piece.upper()].append(square)

    def remove(self, square):
        """
        takes a piece out of the piecelist
        :param square: the piece 
        :return: None
        """
        self.pieces_by_type[square.piece.upper()].remove(square)

    def get_pieces(self, type=None):
        """
        gets a list of pieces
        :param type: the type of piece wanted, if type is None this means all piece types
        :return: a list of pieces
        """
        pieces = []
        if type:
            pieces += self.pieces_by_type[type]
        else:
            for piece_type in self.ordering:
                pieces += self.pieces_by_type[piece_type]
        return pieces

