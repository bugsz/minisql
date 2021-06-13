from IndexManager.indexDS import *
from IndexManager.BPTree import BPTree, BPTreeNode
from utils import utils

class IndexManager:
    def __init__(self):
        pass

    @classmethod
    def insert(cls, index_id, position, value):
        """
            插入值为value/物理位置为position=(record_id,page_id)的record
        """
        header = headerMap.get(index_id)
        if header == None:
            header = get_header_from_file(index_id)
        root = get_node(index_id, header.root)
        BPTree.insert(header.order, root, position, value)
    
    @classmethod
    def delete(cls, index_id, value):
        """
            删除值为value的record
            成功返回1，未找到返回-1
        """
        header = headerMap.get(index_id)
        if header == None:
            header == get_header_from_file(index_id)
        root = get_node(index_id, header.root)
        return BPTree.delete(header.order, root, value)

    @classmethod
    def find_single(cls, index_id, value):
        """
            查询值等于value的record
            成功返回位置元组(record_id, page_id)，未找到返回None
        """
        header = headerMap.get(index_id)
        if header == None:
            header == get_header_from_file(index_id)
        root = get_node(index_id, header.root)
        leafNode, pos = BPTree.find(root, value)
        if leafNode != None and leafNode.key[pos] == value:
            return leafNode.pointer[pos]
        else:
            return None

    @classmethod
    def find_range(cls, index_id, lower, upper):
        """
            查询值处于区间[lower,upper]的record
            返回list,组成元素为位置元组
        """
        header = headerMap.get(index_id)
        if header == None:
            header == get_header_from_file(index_id)
        root = get_node(index_id, header.root)
        leafNode, pos = BPTree.find(root, value)
        ret = []
        if leafNode == None:
            return ret
        while leafNode != None:
            k = 0
            while k < leafNode.size and leafNode.key[k] <= upper:
                ret.append(leafNode.pointer[k])
                k += 1
            if k == leafNode.size:
                leafNode = get_node(leafNode.index_id, leafNode.next)
            else:
                break
        return ret