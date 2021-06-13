class BPTreeNode:
    def __init__(self, index_id, page_id, is_root, is_leaf, next, size, pointer, key) -> None:
        self.index_id = index_id
        self.page_id = page_id
        self.is_root = is_root
        self.is_leaf = is_leaf
        self.next = next
        self.size = size
        self.pointer = pointer
        self.key = key
        self.child = [None] * size

    def max_key(self):
        return self.key[self.size - 1]