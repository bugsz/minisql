class IndexHeader:
    def __init__(self, first_free_page, size, index_id, table_id, attr_id, order, root) -> None:
        """
          header单独占用一个page
        : param first_free_page: int, 0-3    文件中第一个可用页，初始值为-1
        : param size           : int, 4-7    该文件中有几个page
        : param index_id       : int, 8-11   索引序号
        : param table_id       : int, 12-15  对应表序号
        : param attr_id        : int, 16-19  对应表属性序号  
        : param order          : int, 16-19  B+树的阶数  
        : param root           : int, 16-19  root的pid  
        """
        self.first_free_page = first_free_page
        self.size = size
        self.index_id = index_id
        self.table_id = table_id
        self.attr_id = attr_id
        self.order = order
        self.root = root

class BPTreeNode:
    def __init__(self, next_free_page, is_root, is_leaf, father, previous, next, size, pointer, key) -> None:
        """
          每个B+树节点单独占用一个page
        : param next_free_page: int, 0-3           若为可用页，设为下一个可用页的位置；若不可用，置为-1
        : param is_root       : bool, 4
        : param is_leaf       : bool, 5
        : param father        : int, 6-9           父节点pid
        : param previous      : int, 10-13         索引序前一个节点pid(非叶节点置0)
        : param next          : int, 14-17         索引序后一个节点pid(非叶节点置0)
        : param size          : int, 18-21         当前pointer数目
        : param pointer       : int, 22-21+8*size  以元组[record_id, page_id]存储(非叶节点record_id置0)
        : param key           : int                存储各child的分界值
        """
        self.next_free_page = next_free_page
        self.is_root = is_root
        self.is_leaf = is_leaf
        self.father = father
        self.previous = previous
        self.next = next
        self.size = size
        self.pointer = pointer
        self.key = key