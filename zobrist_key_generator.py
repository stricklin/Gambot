import numpy as np


class ZobristGenerator:
    def __init__(self, row_count, col_count, piece_count, square_key_filename, player_key_filename):
        self.row_count = row_count
        self.col_count = col_count
        self.piece_count = piece_count
        self.total = self.row_count * self.col_count * self.piece_count
        self.square_key_filename = square_key_filename
        self.player_key_filename = player_key_filename

    def generate_zobrist_key(self):
        player_key = np.random.randint(2 ** 32 - 1, size=2, dtype="uint32")
        square_key = np.random.randint(2 ** 32 - 1, size=(self.row_count, self.col_count, self.piece_count), dtype="uint32")
        while len(np.unique(square_key)) != self.total:
            square_key = np.random.randint(2 ** 32 - 1, size=(self.row_count, self.col_count, self.piece_count), dtype="uint32")

        np.save(self.square_key_filename, square_key)
        np.save(self.player_key_filename, player_key)

if __name__ == "__main__":
    zobrist_generator = ZobristGenerator(6, 5, 13, "zobrist_square_key", "zobrist_player_key")
    zobrist_generator.generate_zobrist_key()
