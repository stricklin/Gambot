from Square import Square


class PieceList:
    def __init__(self):
        self.pieces_by_type = {
            "K": [],
            "P": [],
            "B": [],
            "R": [],
            "Q": [],
            "N": [],
        }
        self.ordering = ["K", "P", "B", "R", "Q", "N"]

    def add(self, square):
        self.pieces_by_type[square.piece.upper()].append(square)

    def remove(self, square):
        self.pieces_by_type[square.piece.upper()].remove(square)

    def get_pieces(self, specified_type=None):
        pieces = []
        if specified_type:
            pieces += self.pieces_by_type[specified_type]
        else:
            for piece_type in self.ordering:
                pieces += self.pieces_by_type[piece_type]
        return pieces

