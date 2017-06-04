import numpy as np


class ZobristGenerator:
    def __init__(self, row_count, col_count, piece_count, filename):
        self.row_count = row_count
        self.col_count = col_count
        self.piece_count = piece_count
        self.total = self.row_count * self.col_count * self.piece_count
        self.filename = filename

    def generate_zobrist_key(self):
        key = np.random.randint(2 ** 32 - 1, size=(self.row_count, self.col_count, self.piece_count), dtype="uint32")
        while len(np.unique(key)) != self.total:
            key = np.random.randint(2 ** 32 - 1, size=(self.row_count, self.col_count, self.piece_count), dtype="uint32")

        np.save(self.filename, key)

if __name__ == "__main__":
    zobrist_generator = ZobristGenerator(6, 5, 13, "zobrist_key")
    zobrist_generator.generate_zobrist_key()
