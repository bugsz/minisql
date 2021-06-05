from bufferDS import BufferBlock
import utils
from collections import deque
MAX_BUFFER_BLOCKS = 150
PAGE_SIZE = 8192


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
        


    # def remove(self, file_name, page_id):
    #     block = BufferManager._search_buffer_block(file_name, page_id)



class BufferManager:

    curr_buffer_blocks = 0
    buffer_blocks = []

    LRU_replacer = deque(MAX_BUFFER_BLOCKS)
    # LRUReplacer(MAX_BUFFER_BLOCKS)

    def __init__(self) -> None:
        """
            对内为block，对外为page，两者是一个东西
        """
        pass

    @classmethod
    def _search_buffer_block(cls, file_name, page_id) -> BufferBlock:
        """
            不对外暴露的接口
            根据filename和page搜寻缓冲区是否存在该block
            如果没有，就返回None
            :param file_name: 文件名
            :param page_id  : 文件中的offset
            :return BufferBlock
        """
        for buffer_block in cls.buffer_blocks:
            if buffer_block.file_name == file_name and buffer_block.page_id == page_id:
                return buffer_block

        return None

    @classmethod
    def mark_dirty(cls, file_name, page_id):
        block = cls._search_buffer_block(file_name, page_id)
        if block != None:
            block.dirty = True

    @classmethod
    def pin(cls, file_name, page_id):
        """
            添加一次pin计数，这一般会在对某个block进行操作的时候调用
            :param file_name: string
            :param page_id  : int
        """
        block = cls._search_buffer_block(file_name, page_id)
        if block is not None:
            block.pin_count += 1

    @classmethod
    def unpin(cls, file_name, page_id):
        """
            减少一次pin计数，这一般会在对某个block结束操作的时候调用
        """
        block = cls._search_buffer_block(file_name, page_id)
        if block is not None:
            block.pin_count -= 1

    @classmethod
    def flush_page(cls):
        """
            把block写入磁盘
            pin计数不为0的不能被踢出
        """


    @classmethod
    def _fetch_page_from_file(file_name, page_id):
        """
            不对外暴露的接口
            从磁盘读取指定的page
        """
        page_offset = page_id * PAGE_SIZE

        with open(file_name, "rb+") as f:
            f.seek(page_offset)
            page_data = f.read(PAGE_SIZE)
            next_free_page = utils.byte_to_int(page_data[0:4])
            page_bytearray = bytearray(page_data[4:8192])
            # TODO 还要具体考虑

    @classmethod
    def kick_out_victim_LRU(cls):
        if cls.LRU_replacer.empty():
            print("No block can be replaced!")
            # TODO 如果没有block可以被替换该怎么办
            return None
        else:
            victim = cls.LRU_replacer.popleft()
            if victim.dirty == True:
                # TODO 写回
                pass
            return victim

    @classmethod
    def fetch_page(cls, file_name, page_id):
        """
            访问一个page
            1. 如果该页在buffer里面，直接返回
            2. 如果该页不在buffer里面且buffer非满，则读到buffer里面
            3. 如果该页不在buffer里面且buffer满了，则找到一个victim，移除后进行步骤2.
        """

        block_from_buffer = cls._search_buffer_block(file_name, page_id)
        if block_from_buffer is not None:
            return block_from_buffer
        elif cls.curr_buffer_blocks < MAX_BUFFER_BLOCKS:
            block = BufferBlock(cls._fetch_page_from_buffer())
            # TODO 接下来要干什么

            return block
        else:
            # 寻找一个victim
            block = cls.kick_out_victim()
            return(cls.fetch_page())
    
    @classmethod
    def write_back_to_file(cls, file_name, page_id, block):
        """
            将block写回文件
            :param file_name: string 文件名
            :param page_id  : int 
            :param block    : BufferBlock 写回的block
        """
        page_offset = page_id * PAGE_SIZE
        page_data = bytearray(b'\x00' * 8188)
        page_data = utils.int_to_byte(block.next_free_page) + page_data

        with open(file_name, "rb+") as f:
            f.seek(page_offset, 0)
            f.write(page_data)
            # TODO 取消dirty标志

    @classmethod
    def remove_block(cls, block):
        """
            将指定block踢出
            如果block是dirty的，那么先写回
        """
