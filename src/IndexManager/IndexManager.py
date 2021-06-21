from IndexManager.indexDS import BM_IO as IO
from IndexManager.BPtree import BPTree
from utils import utils

class IndexManager:
    def __init__(self):
        pass

    @classmethod
    def init(cls, index_id):
        IO.update_header(index_id, 1, 0)

    @classmethod
    def insert(cls, index_id, position, value):
        """
            插入值为value/物理位置为position=(record_id,page_id)的record
        """
        header = IO.headerMap.get(index_id)
        if header == None:
            header = IO.get_header_from_file(index_id)
        root = IO.get_node(index_id, header.root)
        BPTree.insert(header.order, root, position, value)
    
    @classmethod
    def delete(cls, index_id, value):
        """
            删除值为value的record
            成功返回1，未找到返回-1
        """
        header = IO.headerMap.get(index_id)
        if header == None:
            header = IO.get_header_from_file(index_id)
        root = IO.get_node(index_id, header.root)
        return BPTree.delete(header.order, root, value)

    @classmethod
    def find_by_condition(cls, index_id, condition):
        """
        基于单一condition查询record
        返回list,组成元素为位置元组
        """
        # print("BM find")
        if condition.comparator == utils.COMPARATOR.EQUAL:
            ret = cls.find_single(index_id, condition.rvalue)
            return [] if ret == None else [ret]
        elif condition.comparator == utils.COMPARATOR.GREATER:
            return cls.__find_range(index_id, condition.rvalue, None, False, False)
        elif condition.comparator == utils.COMPARATOR.GREATER_EQUAL:
            return cls.__find_range(index_id, condition.rvalue, None, True, False)
        elif condition.comparator == utils.COMPARATOR.LESS:
            return cls.__find_range(index_id, None, condition.rvalue, False, False)
        elif condition.comparator == utils.COMPARATOR.LESS_EQUAL:
            return cls.__find_range(index_id, None, condition.rvalue, False, True)

    @classmethod
    def find_single(cls, index_id, value):
        """
            查询值等于value的record
            成功返回位置元组(record_id, page_id)，未找到返回None
        """
        header = IO.headerMap.get(index_id)
        if header == None:
            header = IO.get_header_from_file(index_id)
        root = IO.get_node(index_id, header.root)
        leafNode, pos = BPTree.find(root, value)
        if leafNode != None and leafNode.key[pos] == value:
            return leafNode.pointer[pos]
        else:
            return None

    @classmethod
    def __find_range(cls, index_id, lower, upper, includeL, includeR):
        """
            查询值处于区间[lower,upper]的record
            返回list,组成元素为位置元组
        """
        # print("find range")
        header = IO.headerMap.get(index_id)
        if header == None:
            header = IO.get_header_from_file(index_id)
        root = IO.get_node(index_id, header.root)
        leafNode, k = BPTree.find(root, lower)
        # print("BM INFO: {}, {}".format(leafNode.key, leafNode.key[k]))
        ret = []
        if leafNode == None:
            return ret
        if not includeL and lower == leafNode.key[k]:
            k += 1
            if k == leafNode.size:
                leafNode = IO.get_node(index_id, leafNode.next)
                k = 0
        while leafNode != None:
            while k < leafNode.size and (upper == None or includeR and leafNode.key[k] <= upper or not includeR and leafNode.key[k] < upper):
                ret.append(leafNode.pointer[k])
                k += 1
            if k == leafNode.size:
                leafNode = IO.get_node(leafNode.index_id, leafNode.next)
                k = 0
            else:
                break
        return ret