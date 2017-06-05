from collections import deque


class TTable:
    """
    a transposition table holds states that have already been calculated
    """
    def __init__(self, max_size=1024):
        self.max_size = max_size
        self.entrys_by_zob_hash = {}
        self.zob_hashes_by_depth = {}
        self.current_size = 0
        self.smallest_depth = 100

    def try_to_add(self, entry):
        """
        trys to add entry
        :param entry: the entry to try to add
        :return: None
        """
        # if same entry with smaller depth is present, replace that entry
        if entry.zob_hash in self.entrys_by_zob_hash:
            present_entry = self.entrys_by_zob_hash[entry.zob_hash]
            if entry.depth > present_entry.depth:
                self.remove(present_entry)
                self.add(entry)
            return
        # if there is room in the table
        if self.current_size < self.max_size:
            self.add(entry)
        # if entry is of a deeper depth
        elif entry.depth >= self.smallest_depth:
            self.remove_oldest_shallowest()
            self.add(entry)

    def add(self, entry):
        """
        adds entry
        :param entry: the entry to add
        :return: None
        """
        self.entrys_by_zob_hash[entry.zob_hash] = entry
        self.current_size += 1
        if entry.depth in self.zob_hashes_by_depth.keys():
            self.zob_hashes_by_depth[entry.depth].append(entry.zob_hash)
        else:
            self.zob_hashes_by_depth[entry.depth] = deque([entry.zob_hash])
            if entry.depth < self.smallest_depth:
                self.smallest_depth = entry.depth

    def remove(self, entry):
        """
        removes an entry
        :param entry: the entry to remove
        :return: None
        """
        # remove from hashes by depth
        self.zob_hashes_by_depth[entry.depth].remove(entry.zob_hash)
        # if it was the last entry of that depth, remove that depth
        if not self.zob_hashes_by_depth[entry.depth]:
            self.zob_hashes_by_depth.pop(entry.depth)
            self.smallest_depth = min(self.zob_hashes_by_depth.keys())
        # remove from entries by hash
        self.entrys_by_zob_hash.pop(entry.zob_hash)
        self.current_size -= 1

    def remove_oldest_shallowest(self):
        """
        removes the oldest shallowest entry
        :return: None
        """
        # get the the oldest smallest entry
        smallest_depth_queue = self.zob_hashes_by_depth[self.smallest_depth]
        oldest_smallest_hash = smallest_depth_queue[0]
        oldest_smallest = self.entrys_by_zob_hash[oldest_smallest_hash]
        # remove the oldest smallest entry
        self.remove(oldest_smallest)

    def get_entry(self, zob_hash):
        """
        gets an entry
        :param zob_hash: the hash of the entry to get
        :return: the entry with hash zob_hash
        """
        return self.entrys_by_zob_hash.get(zob_hash)
