import os
from BufferManager.bufferDS import PageData, PageHeader, LRUReplacer
from BufferManager.bufferDS import BufferBlock
from utils import utils
from collections import deque
import random
MAX_BUFFER_BLOCKS = 100
PAGE_SIZE = 8192


class BufferManager:
    # TODO 添加新page以及更新header
    def __init__(self) -> None:
        pass

    buffer_blocks = []
    LRU_replacer = deque()
    replacer_len = 0
    # LRUReplacer(MAX_BUFFER_BLOCKS)

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
        if block is None:
            return 

        if block.pin_count == 0:
            cls.LRU_replacer.remove(block)
            cls.replacer_len -= 1

        block.pin_count += 1

    @classmethod
    def unpin(cls, file_name, page_id):
        """
            减少一次pin计数，这一般会在对某个block结束操作的时候调用
        """
        block = cls._search_buffer_block(file_name, page_id)
        if block is None:
            return 

        if block.pin_count > 0:
            block.pin_count -= 1
        else:
            cls.LRU_replacer.append(block)
            cls.replacer_len == 1

    @classmethod
    def flush_buffer(cls):
        """
            把dirty block写入磁盘，不踢出缓冲区
        """
        for block in cls.buffer_blocks:
            if block.dirty == True:
                cls.write_back_to_file(block.file_name, block.page_id)
                block.dirty = False

    @classmethod
    def kick_out_victim_LRU(cls):
        """
            通过LRU机制将block踢出缓冲区
            如果没有能踢出的，就随机踢出一个
            :return bool, LRU_replacer是否为空
        """
        flag = True
        if cls.replacer_len == 0:
            print("No block can be replaced!")
            rand_idx = random.randint(0, MAX_BUFFER_BLOCKS-1)
            victim_block = cls.buffer_blocks[rand_idx]
            # 如果没有block可以被替换该怎么办
            # 那就随机unpin一个
            flag = False
        else:
            victim_block = cls.LRU_replacer.popleft()
            cls.replacer_len -= 1

        print("kick out victim page_id = {}".format(victim_block.page_id))

        if victim_block.dirty == True:
            cls.write_back_to_file(
                victim_block.file_name, victim_block.page_id)

        cls.buffer_blocks.remove(victim_block)
        return flag

    @classmethod
    def set_page(cls, file_name, page_id, new_page):
        block = cls._search_buffer_block(file_name, page_id)
        if block is None:
            return 

        block.page = new_page
        block.dirty = True

    @classmethod
    def fetch_page(cls, file_name, page_id) -> PageData:
        """
            对外暴露的接口
            访问一个page
            1. 如果该页在buffer里面，直接返回
            2. 如果该页不在buffer里面且buffer非满，则读到buffer里面
            3. 如果该页不在buffer里面且buffer满了，则找到一个victim，移除后进行步骤2.
            :return : PageData
        """

        block_from_buffer = cls._search_buffer_block(file_name, page_id)
        if block_from_buffer is not None:
            return block_from_buffer.page
        elif len(cls.buffer_blocks) < MAX_BUFFER_BLOCKS:
            # 如果该页不在buffer内且buffer非满
            print(file_name, page_id)
            page_data = cls._fetch_page_from_file(file_name, page_id)
            block = BufferBlock(page_data, file_name, page_id)
            cls.buffer_blocks.append(block)

            cls.LRU_replacer.append(block)
            cls.replacer_len += 1

            # TODO 接下来要干什么
            return page_data
        else:
            # 踢出一个victim
            status = cls.kick_out_victim_LRU()
            return (cls.fetch_page(file_name, page_id))

    @classmethod
    def _fetch_page_from_file(cls, file_name, page_id):
        """
            不对外暴露的接口
            从磁盘读取指定的page，并返回
            :return : PageData
        """
        page_offset = page_id * PAGE_SIZE

        with open(file_name, "rb+") as f:
            f.seek(page_offset)
            page_data = f.read(PAGE_SIZE)
            next_free_page = utils.byte_to_int(page_data[0:4])
            page_bytearray = bytearray(page_data[4:8192])
            return PageData(next_free_page, page_bytearray)
            # TODO 还要具体考虑

    @classmethod
    def write_back_to_file(cls, file_name, page_id):
        """
            将block写回文件
            :param file_name: string 文件名
            :param page_id  : int 
        """

        block = cls._search_buffer_block(file_name, page_id)
        page_offset = page_id * PAGE_SIZE
        page_data = bytearray(
            b'\x00' * 8188) if block.page.data is None else block.page.data
        page_data = utils.int_to_byte(block.page.next_free_page) + page_data

        with open(file_name, "rb+") as f:
            f.seek(page_offset, 0)
            f.write(page_data)
            block.dirty = False

    @classmethod
    def _read_file_header(cls, file_name):
        """
            内部方法
            :return : PageHeader
        """
        with open(file_name, "rb+") as f:
            if f is None:
                return None
            header_data = f.read(PAGE_SIZE)
            page_header = PageHeader(utils.byte_to_int(header_data[0:4]),
                                     utils.byte_to_int(header_data[4:8]),
                                     utils.byte_to_int(
                                         header_data[8:PAGE_SIZE])
                                     )
            return page_header

    @classmethod
    def remove_block(cls, file_name, page_id, force=False):
        """
            将指定block踢出，该block应当在buffer内且没有被pin
            如果要强制移除，将force属性置为True
            如果block是dirty的，那么先写回
            如果没找到block，那就返回false
            :param force : bool, 是否强制移除
        """
        block = cls._search_buffer_block(file_name, page_id)
        if block is None or (block.pin_count > 0 and force == False):
            return False
        if block.dirty == True:
            cls.write_back_to_file(file_name, page_id)
        cls.buffer_blocks.remove(block)
        return True

    @classmethod
    def remove_file(cls, file_name):
        """
            删除文件，同时删除buffer中所有与其相关的block
            该删除是强制的
        """
        page_header = cls._read_file_header(file_name)
        for i in range(page_header.size):
            cls.remove_block(file_name, i+1, force=True)
        os.remove(os.path.join(utils.DB_BASE_FOLDER, file_name))

    @classmethod
    def force_clear_buffer(cls):
        """
            强制清空buffer，不管其有没有被pin
            这一般在退出程序的时候使用
        """
        for block_idx in range(len(cls.buffer_blocks)-1, -1, -1):
            block = cls.buffer_blocks[block_idx]
            if block.dirty == True:
                cls.write_back_to_file(block.file_name, block.page_id)
            cls.buffer_blocks.remove(block)
if __name__ == "__main__":
    pass
