from IndexManager.indexDS import IO
from IndexManager.BPTreeNode import BPTreeNode
import copy

def binary_find(ls, val) -> int:
    if ls == [] or ls[len(ls) - 1] < val:
        return len(ls)
    l = 0
    r = len(ls) - 1
    ret = len(ls) - 1
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
    def insert(cls, order, rootNode, position, value) -> BPTreeNode:
        """
            向该子树中插入值为value/物理位置为position=(rid,pid)的record
            返回split后新增Node, 未split则为None
        """
        p = binary_find(rootNode.key[0:rootNode.size - (0 if rootNode.is_leaf else 1)], value)
        if rootNode.is_leaf:
            rootNode.key.insert(p, value)
            rootNode.pointer.insert(p, position)
            rootNode.size = rootNode.size + 1
            IO.update_page(rootNode)
        else:
            if rootNode.child[p] == None:
                rootNode.child[p] = IO.get_node(rootNode.index_id, rootNode.pointer[p][1])
            newNode = cls.insert(order, rootNode.child[p], position, value)
            if newNode != None:
                rootNode.key[p] = rootNode.child[p].max_key()
                rootNode.key.insert(p + 1, newNode.max_key())
                rootNode.pointer.insert(p + 1, (0, newNode.page_id))
                rootNode.child.insert(p + 1, newNode)
                rootNode.size = rootNode.size + 1
                IO.update_page(rootNode)
        if rootNode.size <= order:
            return None
        rootNode, retNode = cls.__split(rootNode)
        if not rootNode.is_root:
            return retNode
        newNode = BPTreeNode(rootNode.index_id, IO.get_new_page_id(rootNode.index_id), True, False, -1, 2, [], [])
        retNode.is_root = False
        rootNode.is_root = False
        newNode.pointer = [(0, rootNode.page_id), (0, retNode.page_id)]
        newNode.key = [rootNode.max_key(), retNode.max_key()]
        newNode.child = [rootNode, retNode]
        IO.update_page(newNode)
        IO.update_page(retNode)
        IO.update_page(rootNode)
        IO.update_header(newNode.index_id, 1, 0)
        IO.update_header(newNode.index_id, newNode.page_id, 1)
        return None

    @classmethod
    def delete(cls, order, rootNode, value) -> int:
        p = binary_find(rootNode.key, value)
        if p == len(rootNode.key):
            return -1
        if rootNode.is_leaf:
            if rootNode.key[p] != value:
                return -1
            del rootNode.key[p]
            del rootNode.pointer[p]
            rootNode.size = rootNode.size - 1
            IO.update_page(rootNode)
            return 1
        if rootNode.child[p] == None:
            rootNode.child[p] = IO.get_node(rootNode.index_id, rootNode.pointer[p][1])
        ret = cls.delete(order, rootNode.child[p], value)
        if ret == 1:
            if rootNode.child[p].size < order // 2:
                neighbor = p - 1 if p > 0 else 1
                if rootNode.child[neighbor] == None:
                    rootNode.child[neighbor] = IO.get_node(rootNode.index_id, rootNode.pointer[neighbor][1])
                if rootNode.child[neighbor].size > order // 2:
                    cls.__transfer(rootNode.child[neighbor], rootNode.child[p], -1 if p > 0 else 1)
                    rootNode.key[neighbor] = rootNode.child[neighbor].max_key()
                else:
                    if p == 0:
                        p, neighbor = neighbor, p
                    cls.__merge(rootNode.child[neighbor], rootNode.child[p])
                    del rootNode.key[p]
                    del rootNode.pointer[p]
                    rootNode.child[p] = None
                    rootNode.size = rootNode.size - 1
                    p = neighbor
            rootNode.key[p] = rootNode.child[p].max_key()
            if rootNode.is_root and rootNode.size == 1:
                rootNode.child[p].is_root = True
                IO.update_page(rootNode.child[p])
                IO.update_header(rootNode.index_id, -1, 0)
                IO.update_header(rootNode.index_id, rootNode.pointer[p][1], 1)
                IO.free_page(rootNode)
            else:
                IO.update_page(rootNode)
        return ret        

    @classmethod
    def find(cls, rootNode, value) -> [BPTreeNode, int]:
        """
            在子树中查找值最接近value(>=)的record
            返回leafNode以及该记录位置
        """
        p = binary_find(rootNode.key, value)
        if p == len(rootNode.key):
            return [None, -1]
        if rootNode.is_leaf:
            return [rootNode, p]
        if rootNode.child[p] == None:
            rootNode.child[p] = IO.get_node(rootNode.index_id, rootNode.pointer[p][1])
        return cls.find(rootNode.child[p], value)

    @classmethod
    def __split(cls, rootNode) -> [BPTreeNode, BPTreeNode]:
        mid = rootNode.size // 2
        retNode = copy.deepcopy(rootNode)                   # retNode is the right one while rootNode stays left
        retNode.page_id = IO.get_new_page_id(rootNode.index_id)
        if retNode.is_leaf:
            rootNode.next = retNode.page_id
        rootNode.size = mid
        retNode.size = retNode.size - mid
        rootNode.pointer = rootNode.pointer[0:mid]
        retNode.pointer = retNode.pointer[mid:]
        rootNode.key = rootNode.key[0:mid]
        retNode.key = retNode.key[mid:]
        rootNode.child = rootNode.child[0:mid]
        retNode.child = retNode.child[mid:]
        IO.update_page(rootNode)
        IO.update_page(retNode)
        IO.update_header(rootNode.index_id, 1, 0)
        return [rootNode, retNode]

    @classmethod
    def __transfer(cls, srcNode, desNode, op):
        if op < 0:
            desNode.pointer.insert(0, srcNode.pointer[srcNode.size - 1])
            desNode.key.insert(0, srcNode.key[srcNode.size - 1])
            desNode.child.insert(0, srcNode.child[srcNode.size - 1])
            desNode.size += 1
            del srcNode.pointer[srcNode.size - 1]
            del srcNode.key[srcNode.size - 1]
            del srcNode.child[srcNode.size - 1]
            srcNode.size -= 1
        else:
            desNode.pointer.append(srcNode.pointer[0])
            desNode.key.append(srcNode.key[0])
            desNode.child.append(srcNode.child[0])
            desNode.size = desNode.size + 1
            del srcNode.pointer[0]
            del srcNode.key[0]
            del srcNode.child[0]
            srcNode.size = srcNode.size - 1
        IO.update_page(srcNode)
        IO.update_page(desNode)
            
    @classmethod
    def __merge(cls, leftNode, rightNode):
        if rightNode.is_leaf:
            leftNode.next = rightNode.next
        leftNode.size += rightNode.size
        leftNode.key += rightNode.key
        leftNode.pointer += rightNode.pointer
        leftNode.child += rightNode.child
        IO.update_page(leftNode)
        IO.free_page(rightNode)
        IO.update_header(leftNode.index_id, -1, 0)