class Square:
    def __init__(self, cordinates, piece):
        self.cords = cordinates
        self.row = cordinates[0]
        self.col = cordinates[1]
        self.piece = piece

    def __cmp__(self, other):
        difference = self.row - other.row
        if difference == 0:
            difference = self.col - other.col
            if difference == 0:
                difference = ord(self.piece) - ord(other.piece)
        return difference

    def __hash__(self):
        return self.row ** 2 * self.col ** 3 * ord(self.piece)
