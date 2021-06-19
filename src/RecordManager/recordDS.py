from utils import utils
from BufferManager.BufferManager import BufferManager
from BufferManager.bufferDS import PageHeader, PageData

class RecordHeader:
    def __init__(self, first_free_page, size, record_num, record_length, page_capacity, attr_num, attr_types) -> None:
        """
          Header单独占据一个Page
        : param first_free_page: int, 0-3    文件中第一个可用页，起始为-1
        : param size           : int, 4-7    当前page数量
        : param record_num     : int, 8-11   当前record数量
        : param record_length  : int, 12-15  一条record的长度
        : param page_capacity  : int, 16-19  page中可容纳record的数目
        : param attr_num       : int, 20-23  参数数目
        : param attr_types     : int, 24-23+4*num   0:int / 1:float / other:char(x-1)
        """
        self.first_free_page = first_free_page
        self.size = size
        self.record_num = record_num
        self.record_length = record_length
        self.page_capacity = page_capacity
        self.attr_num = attr_num
        self.attr_types = attr_types

# class RecordPage:
#     def __init__(self, next_free_page, data) -> None:
#         """
#         : param next_free_page: int, 0-3     若为可用页，设为下一个可用页的位置；若不可用，置为-1
#         : param data          : byte, 4-     数据区，储存至多page_capacity条记录，用0填满剩余的地方
#                                              存储格式为[next_free_record, record_content]组成的元组，长度为record_length + 4
#         """
#         self.next_free_page = next_free_page
#         self.data = data

class Record:
    def __init__(self, valid, value):
        """
        : param valid: bool, 0
        : param value: list
        """
        self.valid = valid
        self.value = value

class RM_IO:
    def __init__(self):
        pass

    headerMap = {} # table_id:RecordHeader
    pageMap = {} # (table_id, page_id):PageData

    @classmethod
    def get_header_from_file(cls, table_id) -> RecordHeader:
        header = BufferManager.get_header("record" + str(table_id) + ".db")
        record_num = utils.byte_to_int(header.data[0:4])
        record_length = utils.byte_to_int(header.data[4:8])
        page_capacity = utils.byte_to_int(header.data[8:12])
        attr_num = utils.byte_to_int(header.data[12:16])
        attr_types = []
        for i in range(attr_num):
            attr_types.append(utils.byte_to_int(header.data[16+4*i:20+4*i]))
        cls.headerMap[table_id] = RecordHeader(header.first_free_page, header.size, record_num, record_length, page_capacity, attr_num, attr_types)
        return cls.headerMap[table_id]

    @classmethod
    def get_page_from_file(cls, table_id, page_id):
        pageData = BufferManager.fetch_page("record" + str(table_id) + ".db", page_id)
        cls.pageMap[(table_id, page_id)] = pageData
        return cls.pageMap[(table_id, page_id)]

    @classmethod
    def __write_header(cls, table_id, header):
        data = b''
        data += utils.int_to_byte(header.record_num)
        data += utils.int_to_byte(header.record_length)
        data += utils.int_to_byte(header.page_capacity)
        data += utils.int_to_byte(header.attr_num)
        for i in range(header.attr_num):
            data += utils.int_to_byte(header.attr_types[i])
        BufferManager.set_header("record" + str(table_id) + ".db", PageHeader(header.first_free_page, header.size, data))

    @classmethod
    def __write_page(cls, table_id, page_id, page):
        BufferManager.set_page("record" + str(table_id) + ".db", page_id, page)

    @classmethod
    def decode_page(cls, table_id, page_id, record_id):
        page = cls.pageMap.get((table_id, page_id))
        if page == None:
            page = cls.get_page_from_file(table_id, page_id)
        header = cls.headerMap.get(table_id)
        if header == None:
            header = cls.get_header_from_file(table_id)
        pos = record_id * header.record_length
        valid = utils.byte_to_bool(page.data[pos:pos+1])
        pos += 1
        if not valid:
            return None
        else:
            value = []
            for i in range(header.attr_num):
                type = header.attr_types[i]
                if type == 0:
                    value.append(utils.byte_to_int(page.data[pos:pos+4]))
                    pos += 4
                elif type == 1:
                    value.append(utils.byte_to_float(page.data[pos:pos+4]))
                    pos += 4
                else:
                    str = utils.byte_to_str(page.data[pos:pos+type-1])
                    str = str.rstrip('\x00')
                    value.append(str)
                    pos += type - 1
            return Record(valid, value)
    
    @classmethod
    def __encode_page(cls, table_id, page_id, record_id, content):
        page = cls.pageMap.get((table_id, page_id))
        if page == None:
            page = cls.get_page_from_file(table_id, page_id)
        header = cls.headerMap.get(table_id)
        if header == None:
            header = cls.get_header_from_file(table_id)
        data = b''
        data += utils.bool_to_byte(content.valid)
        for i in range(header.attr_num):
            type = header.attr_types[i]
            if type == 0:
                data += utils.int_to_byte(content.value[i])
            elif type == 1:
                data += utils.float_to_byte(content.value[i])
            else:
                data += utils.str_to_byte(content.value[i])
                data += b'\x00' * (type - 1 - len(content.value[i]))
        page.data[record_id * header.record_length: (record_id + 1) * header.record_length] = data
        return page
            
    @classmethod
    def get_free_pos(cls, table_id):
        header = cls.headerMap.get(table_id)
        if header == None:
            header = cls.get_header_from_file(table_id)
        if header.first_free_page == -1:
            return (cls.__get_new_page_id(table_id), 0)
        pos = None
        cnt = 0
        for i in range(header.page_capacity):
            record = cls.decode_page(table_id, header.first_free_page, i)
            if not record.valid:
                cnt += 1
                pos = i
        if cnt > 1:
            return (header.first_free_page, pos)
        page = cls.pageMap.get((table_id, header.first_free_page))
        if page == None:
            page = cls.get_page_from_file(table_id, header.first_free_page)
        ret = header.first_free_page
        header.first_free_page = page.next_free_page
        page.next_free_page = -1
        cls.pageMap[(table_id, page_id)] = page
        cls.__write_page(table_id, header.size, page)
        cls.update_header(table_id, header)
        return (ret, pos)

    @classmethod
    def __get_new_page_id(cls, table_id) -> int:
        header = cls.headerMap.get(table_id)
        if header == None:
            header = cls.get_header_from_file(table_id)
        BufferManager.create_page("record" + str(table_id) + ".db")
        header.size += 1
        if header.page_capacity > 1:
            page = cls.get_page_from_file(table_id, header.size)
            page.next_free_page = header.first_free_page
            header.first_free_page = header.size
            cls.pageMap[(table_id, page_id)] = page
            cls.__write_page(table_id, header.size, page)
        cls.update_header(table_id, header)
        return header.size

    @classmethod
    def update_page(cls, table_id, page_id, record_id, content) -> None:
        page = cls.__encode_page(table_id, page_id, record_id, content)
        cls.pageMap[(table_id, page_id)] = page
        cls.__write_page(table_id, page_id, page)

    @classmethod
    def free_page(cls, table_id, page_id) -> None:
        """
        从一个满的页中删除时，调用此函数以标记页中存在空位置
        """
        page = cls.pageMap.get((table_id, page_id))
        if page == None:
            page = cls.get_page_from_file(table_id, page_id)
        header = cls.headerMap.get(table_id)
        if header == None:
            header = cls.get_header_from_file(table_id)
        page.next_free_page = header.first_free_page
        header.first_free_page = page_id
        cls.__write_page(table_id, page_id, page)
        cls.__write_header(table_id, header)

    @classmethod
    def update_header(cls, table_id, header):
        cls.headerMap[table_id] = header
        cls.__write_header(table_id, header)