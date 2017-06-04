from TTableEntry import TTableEntry
from collections import deque


class TTable:
    def __init__(self, max_size=1024):
        self.max_size = max_size
        self.entrys_by_zob_hash = {}
        self.zob_hashes_by_depth = {}
        self.current_size = 0
        self.smallest_depth = 100

    def try_to_add(self, entry):
        # if entry already present, don't add again
        if entry.zob_hash in self.entrys_by_zob_hash:
            return
        if self.current_size < self.max_size:
            self.add(entry)
        elif entry.depth >= self.smallest_depth:
            self.remove_smallest()
            self.add(entry)

    def add(self, entry):
        self.entrys_by_zob_hash[entry.zob_hash] = entry
        self.current_size += 1
        if entry.depth in self.zob_hashes_by_depth.keys():
            self.zob_hashes_by_depth[entry.depth].append(entry.zob_hash)
        else:
            self.zob_hashes_by_depth[entry.depth] = deque([entry.zob_hash])
            if entry.depth < self.smallest_depth:
                self.smallest_depth = entry.depth

    def remove_smallest(self):
        # get the hash of the oldest smallest entry and remove hashes by depth
        smallest_depth_queue = self.zob_hashes_by_depth[self.smallest_depth]
        hash_to_remove = smallest_depth_queue.popleft()
        # remove the oldest smallest entry
        removed_entry = self.entrys_by_zob_hash.pop(hash_to_remove)
        # update size
        self.current_size -= 1
        # update smallest depth if needed
        if not self.zob_hashes_by_depth[self.smallest_depth]:
            self.zob_hashes_by_depth.pop(self.smallest_depth)
            self.smallest_depth = min(self.zob_hashes_by_depth.keys())

    def get_entry(self, zob_hash):
        return self.entrys_by_zob_hash.get(zob_hash)
