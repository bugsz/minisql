class BufferBlock:
    def __init__(self, page, file_name, page_id) -> None:
        """
            :param page     : PageData,
            :param pin_count: int,      该block被访问次数
            :param dirty    : bool,     是否被修改过
        """
        # TODO: 应该用什么初始化
        self.dirty = False
        self.pin_count = 0
        self.file_name = file_name
        self.page_id = page_id
        self.page = page

class PageHeader:
    def __init__(self, first_free_page, size, data) -> None:
        """
            :param first_free_page: int, 0-3  文件中第一个可用页
            :param size           : int, 4-7  文件中当前有几个page
            :param data           : byte[], 8-8191 ,数据
        """
        self.first_free_page = first_free_page
        self.size = size
        self.data = data

    def set_first_free_page(self, page_id):
        self.first_free_page = page_id

class PageData:
    def __init__(self, next_free_page, data) -> None:
        self.next_free_page = next_free_page
        self.data = data

'''
class LinkedListNode:
    def __init__(self, block_data) -> None:
        """
        :param block_data: BufferBlock类型
        """
        self.block_data = block_data
        self.previous = None
        self.next = None


class LRUReplacer:
    def __init__(self, MAX_BUFFER_BLOCKS) -> None:
        """
            用双向链表实现的支持LRU替换的buffer block
            每次新的 pin_count=0 的block出现的时候，就将其加入队首
            每次踢出的时候，只需要从队尾取出来就行了
        """
        self.__head = None
        self.__rear = None

    def is_empty(self):
        return self.__head == None

    def insert_head(self, buffer_block):
        """
            在链表头新增一个节点
        """
        new_node = LinkedListNode(buffer_block)
        if self.is_empty():
            self.__head = new_node
            self.__rear = new_node
        else:
            new_node.next = self.__head
            self.__head.previous = new_node
            self.__head = new_node

    def pop_rear(self):
        """
            在链表尾取出一个节点，但不删除
            :return : BufferBlock
        """
        if self.is_empty():
            return None
        return self.__rear
    
    def remove_rear(self):
        """
            删除链表尾部的元素
        """
        if self.is_empty():
            return False
        if self.__head == self.__rear:
            self._head = None
            self._rear = None
            return True
        self.__rear.previous.next = None
        self.__rear = self.__rear.previous
'''