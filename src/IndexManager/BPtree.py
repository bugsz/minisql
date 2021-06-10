from IndexMananger.indexDS import BPTreeNode
from BufferManager.BufferManager import BufferManager

def get_node_from_file(index_id, page_id) -> BPTreeNode:
    pageData = BufferManager.fetch_page(index_id + ".db", page_id) 
    # TODO: 文件名称待确定
    isRoot = utils.byte_to_bool(pageData.data[0])
    isLeaf = utils.byte_to_bool(pageData.data[1])
    father = utils.byte_to_int(pageData.data[2:5])
    previous = utils.byte_to_int(pageData.data[6:9])
    nxt = utils.byte_to_int(pageData.data[10:13])
    size = utils.byte_to_int(pageData.data[14:17])
    pointer = []
    for i in range(size):
        st = 18 + i * 8
        pointer.append((utils.byte_to_int(pageData.data[st:st + 3]), utils.byte_to_int(pageData.data[st+4:st+7])))
    key = []
    # TODO: 添加索引值的种类
    return BPTreeNode(pageData.next_free_page, isRoot, isLeaf, father, previous, nxt, size, pointer, key)

def binary_find(ls, val) -> int:
    if ls == [] or ls[len(ls) - 1] < val:
        return len(ls)
    l = 0
    r = len - 1
    ret = len - 1
    while l <= r:
        mid = (l + r) // 2
        if ls[mid] >= val:
            ret = mid
            r = mid - 1
        else:
            l = mid + 1
    return ret

class BPTree:
    def __init__():
        pass

    @classmethod
    def insert(cls, header, rootNode, position, value) -> [page_id, BPTreeNode]:
        """
            向该子树中插入值为value/物理位置为position=(rid,pid)的record
            返回split后新增Node, 未split则为None
        """
        p = binary_find(rootNode.key[0:size - (0 if rootNode.isLeaf else 1)], value)
        if rootNode.is_leaf:
            rootNode.key.insert(p, value)
            rootNode.pointer.insert(p, position)
            rootNode.size = rootNode.size + 1
        else:
            if child[p] == None:
                child[p] = get_node_from_file(header.index_id, rootNode.pointer[p][1])
            page_id, newNode = insert(header, child[p], position, value)
            if newNode != None:
                rootNode.key[p] = rootNode.child[p].max_key() #TODO
                rootNode.key.insert(p + 1, newNode.max_key())
                rootNode.pointer.insert(p + 1, (0, page_id))
                rootNode.child.insert(p + 1, newNode)
                rootNode.size = rootNode.size + 1
        if rootNode.size <= rootNode.order:
            return [0, None]
        rootNode, retNode = _split(rootNode)
        # TODO: page_id传的真麻烦 回去再开一个类        


    @classmethod
    def delete(cls, header, rootNode, value) -> int:
        pass

    @classmethod
    def find(cls, rootNode, value) -> BPTreeNode:
        pass

    @classmethod
    def _split(cls, rootNode) -> [BPTreeNode, BPTreeNode]:
        pass

    @classmethod
    def _merge(cls, rootNode):
        pass