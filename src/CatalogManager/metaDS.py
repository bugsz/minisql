from enum import Enum
from utils import utils
from BufferManager.BufferManager import BufferManager
from BufferManager.bufferDS import PageHeader, PageData

class MetaType(Enum):
    table = 1
    attr = 2
    index = 3

class MetaHeader:
    def __init__(self, first_free_page, size, record_num, record_length, page_capacity) -> None:
        """
          header单独占用一个page
        : param first_free_page: int, 0-3    文件中第一个可用页，初始值为-1
        : param size           : int, 4-7    该文件中有几个page
        : param record_num     : int, 8-11   该数据库中有几条记录
        : param record_length  : int, 12-15  
        : param page_capacity  : int, 16-19  
        """
        self.first_free_page = first_free_page
        self.size = size
        self.record_num = record_num
        self.record_length = record_length
        self.page_capacity = page_capacity

# MetaPage is the same as PageData, so not defined
# class MetaPage:
#     def __init__(self, next_free_page, data) -> None:
#         """
#         : param next_free_page: int, 0-3     若为可用页，设为下一个可用页的number；若不可用，置为-1
#         : param data          : byte,4-8191  数据区，只储存整数条记录，用0填满剩余的地方
#         """
#         self.next_free_page = next_free_page
#         self.data = data

class MetaTable:
    def __init__(self, table_id, pk_id, attr_page_id, attr_num, table_name, valid):
        """
          至多存放30个/page
        : param table_id    : int , 0-3
        : param pk_id       : int , 4-7      主键的attr_id
        : param attr_page_id: int , 8-11
        : param attr_num    : int , 12-15  
        : param table_name  : char, 16-270
        : param valid       : bool, 271
        """
        self.table_id = table_id
        self.pk_id = pk_id
        self.attr_page_id = attr_page_id
        self.attr_num = attr_num
        self.table_name = table_name
        self.attrs = []
        self.valid = valid

class MetaAttr:
    def __init__(self, attr_name, attr_type, index_id, unique):
        """
          至多存放32个/page
          将属于一个table的attr存放在同一个page里，因此省略了table_id
        : param attr_name: char, 0-245 
        : param attr_type: int , 246-249
        : param index_id : int , 250-253
        : param unique   : bool, 254
        """
        self.attr_name = attr_name
        self.attr_type = attr_type
        self.index_id = index_id
        self.unique = unique

class MetaIndex:
    def __init__(self, index_id, index_name, table_id, attr_id, valid):
        """
          32/page
        : param index_id  : int , 0-3
        : param index_name: char, 4-258
        : param table_id  : int , 259-262
        : param attr_id   : int , 263-266
        : param valid     : bool, 267
        """
        self.index_id = index_id
        self.index_name = index_name
        self.table_id = table_id
        self.attr_id = attr_id

class CM_IO:
    def __init__(self):
        pass

    headerMap = {} # meta_type:MetaHeader
    pageMap = {} # (meta_type, page_id):MetaPage

    @classmethod
    def get_header_from_file(cls, meta_type) -> MetaHeader:
        header = BufferManager.get_header("meta" + str(meta_type.value) + ".db")
        record_num = utils.byte_to_int(header.data[0:4])
        record_length = utils.byte_to_int(header.data[4:8])
        page_capacity = utils.byte_to_int(header.data[8:12])
        cls.headerMap[meta_type] = MetaHeader(header.first_free_page, header.size, record_num, record_length, page_capacity)
        return cls.headerMap[meta_type]

    @classmethod
    def get_page_from_file(cls, meta_type, page_id) -> MetaPage:
        pageData = BufferManager.fetch_page("meta" + str(meta_type.value) + ".db", page_id)
        cls.pageMap[(meta_type, page_id)] = pageData
        return cls.pageMap[(meta_type, page_id)]

    @classmethod
    def write_header(cls, meta_type, header):
        data = b''
        data += utils.int_to_byte(header.record_num)
        data += utils.int_to_byte(header.record_length)
        data += utils.int_to_byte(header.page_capacity)
        BufferManager.set_header("meta" + str(meta_type.value) + ".db", PageHeader(header.first_free_page, header.size, data))

    @classmethod
    def write_page(cls, meta_type, page_id, page):
        # if page.next_free_page > 0:
        #     page.data = b'\x00' * 8188
        BufferManager.set_page("meta" + str(meta_type.value) + ".db", page_id, page)

    @classmethod
    def decode_page(cls, meta_type, page_id, record_id):
        page = cls.pageMap.get((meta_type, page_id))
        if page == None:
            page = cls.get_page_from_file(meta_type, page_id)
        if meta_type == MetaType.table:
            pos = record_id * 272
            table_id = utils.byte_to_int(page.data[pos:pos+4])
            pk_id = utils.byte_to_int(page.data[pos+4:pos+8])
            attr_page_id = utils.byte_to_int(page.data[pos+8:pos+12])
            attr_num = utils.byte_to_int(page.data[pos+12:pos+16])
            table_name = utils.byte_to_str(page.data[pos+16:pos+271])
            valid = utils.byte_to_bool(page.data[pos+271])
            if not valid:
                return None
            else:
                return MetaTable(table_id, pk_id, attr_page_id, attr_num, table_name, valid)
        elif meta_type == MetaType.attr:
            pos = record_id * 255
            attr_name = utils.byte_to_str(page.data[pos:pos+246])
            attr_type = utils.byte_to_int(page.data[pos+246:pos+250])
            index_id = utils.byte_to_int(page.data[pos+250:pos+254])
            unique = utils.byte_to_bool(page.data[pos+254])
            return MetaAttr(attr_name, attr_type, index_id, unique)
        else:
            pos = record_id * 268
            index_id = utils.byte_to_int(page.data[pos:pos+4])
            index_name = utils.byte_to_str(page.data[pos+4:pos+259])
            table_id = utils.byte_to_int(page.data[pos+259:pos+263])
            attr_id = utils.byte_to_int(page.data[pos+263:pos+267])
            valid = utils.byte_to_bool(page.data[pos+267])
            if not valid:
                return None
            else:
                return MetaIndex(index_id, index_name, table_id, attr_id, valid)
    
    @classmethod
    def encode_page(cls, meta_type, page_id, record_id, content):
        page = cls.pageMap.get((meta_type, page_id))
        if page == None:
            page = cls.get_page_from_file(meta_type, page_id)
        data = b''
        if meta_type == MetaType.table:
            data += utils.int_to_byte(content.table_id)
            data += utils.int_to_byte(content.pk_id)
            data += utils.int_to_byte(content.attr_page_id)
            data += utils.int_to_byte(content.attr_num)
            data += utils.str_to_byte(content.table_name)
            data += utils.bool_to_byte(content.valid)
            page.data[record_id * 272: (record_id + 1) * 272] = data
            return page
        elif meta_type == MetaType.attr:
            data += utils.str_to_byte(content.attr_name)
            data += utils.int_to_byte(content.attr_type)
            data += utils.int_to_byte(content.index_id)
            data += utils.bool_to_byte(content.unique)
            page.data[record_id * 255: (record_id + 1) * 255] = data
            return page
        else:
            data += utils.int_to_byte(content.index_id)
            data += utils.str_to_byte(content.index_name)
            data += utils.int_to_byte(content.table_id)
            data += utils.int_to_byte(content.attr_id)
            data += utils.bool_to_byte(content.valid)
            page.data[record_id * 268: (record_id + 1) * 268] = data
            return page
            
    @classmethod
    def get_new_page_id(cls, meta_type) -> int:
        header = cls.headerMap.get(meta_type)
        if header == None:
            header = cls.get_header_from_file(meta_type)
        if header.first_free_page == -1:
            BufferManager.create_page("meta" + str(meta_type.value) + ".db")
            return header.size + 1
        return header.first_free_page

    @classmethod
    def update_page(cls, meta_type, page_id, record_id, content) -> None:
        page = cls.encode_page(meta_type, page_id, record_id, content)
        cls.pageMap[(meta_type, page_id)] = page
        cls.write_page(meta_type, page_id, page)

    @classmethod
    def free_record(cls, meta_type, page_id, record_id):
        pass

    @classmethod
    def free_page(cls, meta_type, page_id) -> None:
        page = cls.pageMap.get((meta_type, page_id))
        if page == None:
            page = cls.get_page_from_file(meta_type, page_id)
        header = cls.headerMap.get(meta_type)
        if header == None:
            header = cls.get_header_from_file(meta_type)
        page.next_free_page = header.first_free_page
        header.first_free_page = page_id
        cls.write_page(meta_type, page_id, page)
        cls.write_header(meta_type, header)

    @classmethod
    def update_header(cls, meta_type, header):
        cls.headerMap[meta_type] = header
        cls.write_header(meta_type, header)