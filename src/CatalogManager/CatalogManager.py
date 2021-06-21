from CatalogManager.metaDS import *
from BufferManager.BufferManager import BufferManager
from BufferManager.bufferDS import PageHeader, PageData
from utils import utils

class CatalogManager:
    def __init__(self):
        pass

    table_dict = {}
    index_dict = {}

    @classmethod
    def initialize(cls):
        """
        启动程序时调用
        """
        if BufferManager.create_file("meta1.db") == 0:
            CM_IO.update_header(MetaType.table, MetaHeader(-1, 0, 0, 272, 30))
        if BufferManager.create_file("meta2.db") == 0:
            CM_IO.update_header(MetaType.attr, MetaHeader(-1, 0, 0, 255, 32))
        if BufferManager.create_file("meta3.db") == 0:
            CM_IO.update_header(MetaType.index, MetaHeader(-1, 0, 0, 268, 30))
        header = CM_IO.get_header_from_file(MetaType.table)
        cnt = 0
        page_id = 1
        while cnt < header.record_num:
            for i in range(header.page_capacity):
                record = CM_IO.decode_page(MetaType.table, page_id, i)
                if record != None:
                    cls.table_dict[record.table_name] = (page_id - 1) * 30 + i
                    cnt += 1
            page_id += 1
        header = CM_IO.get_header_from_file(MetaType.index)
        cnt = 0
        page_id = 1
        while cnt < header.record_num:
            for i in range(header.page_capacity):
                record = CM_IO.decode_page(MetaType.index, page_id, i)
                if record != None:
                    cls.index_dict[record.index_name] = (page_id - 1) * 30 + i
                    cnt += 1
            page_id += 1

    @classmethod
    def get_table_id(cls, table_name):
        return cls.table_dict[table_name]

    @classmethod
    def get_index_id(cls, index_name):
        return cls.index_dict[index_name]

    @classmethod
    def table_exist(cls, table_name) -> bool:
        return cls.table_dict.get(table_name) != None
            
    @classmethod
    def index_exist(cls, index_name) -> bool:
        return cls.index_dict.get(index_name) != None

    @classmethod
    def attr_exist(cls, table_name, attr_name) -> bool:
        if not cls.table_exist(table_name):
            return False
        table = CM_IO.decode_page(MetaType.table, cls.table_dict[table_name] // 30 + 1, cls.table_dict[table_name] % 30)
        for i in range(table.attr_num):
            record = CM_IO.decode_page(MetaType.attr, table.attr_page_id, i)
            if record.attr_name == attr_name:
                return True
        return False

    @classmethod
    def attr_unique(cls, table_name, attr_name) -> bool:
        if not cls.table_exist(table_name):
            return False
        table = CM_IO.decode_page(MetaType.table, cls.table_dict[table_name] // 30 + 1, cls.table_dict[table_name] % 30)
        for i in range(table.attr_num):
            record = CM_IO.decode_page(MetaType.attr, table.attr_page_id, i)
            if record.attr_name == attr_name:
                return record.unique
        return False

    @classmethod
    def get_attrs_type(cls, table_name):
        """
        插入时做类型检查用
        返回(attr_name, attr_type, attr_length)的列表
        """
        table = CM_IO.decode_page(MetaType.table, cls.table_dict[table_name] // 30 + 1, cls.table_dict[table_name] % 30)
        ret = []
        for i in range(table.attr_num):
            record = CM_IO.decode_page(MetaType.attr, table.attr_page_id, i)
            type = utils.VALUETYPE.INT
            length = 4
            if record.attr_type > 1:
                type = utils.VALUETYPE.CHAR
                length = record.attr_type - 1
            elif record.attr_type == 1:
                type = utils.VALUETYPE.FLOAT
            ret.append((record.attr_name, type, length))
        return ret

    @classmethod
    def create_table(cls, table_name, attr_num, pk_id, attrs):
        """
        : param 表名，属性个数，主键（0~31），属性列表
                attrs包含4元组(attr_name, attr_type, attr_length(in bytes), unique)
                attr_type:  class VALUETYPE
        """
        header = CM_IO.headerMap.get(MetaType.table)
        if header == None:
            header = CM_IO.get_header_from_file(MetaType.table)
        page_id, pos = CM_IO.get_free_pos(MetaType.table)
        record = MetaTable(header.page_capacity * (page_id - 1) + pos, pk_id, CM_IO.get_free_pos(MetaType.attr)[0], attr_num, table_name, True)
        CM_IO.update_page(MetaType.table, page_id, pos, record)
        header.record_num += 1
        CM_IO.update_header(MetaType.table, header)
        cls.table_dict[record.table_name] = record.table_id

        header = CM_IO.headerMap.get(MetaType.attr)
        if header == None:
            header = CM_IO.get_header_from_file(MetaType.attr)
        record_len = 1
        data = b''
        for i in range(attr_num):
            type = 0
            record_len += 4
            if attrs[i][1] == utils.VALUETYPE.FLOAT:
                type = 1
            elif attrs[i][1] == utils.VALUETYPE.CHAR:
                type = attrs[i][2] + 1
                record_len += attrs[i][2] - 4
            data += utils.int_to_byte(type)
            attr = MetaAttr(attrs[i][0], type, -1, attrs[i][3])
            CM_IO.update_page(MetaType.attr, record.attr_page_id, i, attr)

        BufferManager.create_file("record" + str(record.table_id) + ".db")
        data = utils.int_to_byte(0) + utils.int_to_byte(record_len) +\
               utils.int_to_byte((utils.PAGE_SIZE - 4) // record_len) + utils.int_to_byte(attr_num) + data
        BufferManager.set_header("record" + str(record.table_id) + ".db", PageHeader(-1, 0, data))

    @classmethod
    def create_index(cls, index_name, table_name, attr_name):
        """
        可能要由API手动做一下insert，这里访问不到record
        """
        header = CM_IO.headerMap.get(MetaType.index)
        if header == None:
            header = CM_IO.get_header_from_file(MetaType.index)
        page_id, pos = CM_IO.get_free_pos(MetaType.index)
        table_id = cls.get_table_id(table_name)
        attr_id, attr_type = cls.get_attr_id(table_id, attr_name)
        record = MetaIndex(header.page_capacity * (page_id - 1) + pos, index_name, table_id, attr_id, True)
        CM_IO.update_page(MetaType.index, page_id, pos, record)
        cls.index_dict[record.index_name] = record.index_id
        header.record_num += 1
        CM_IO.update_header(MetaType.index, header)
        BufferManager.create_file("index" + str(record.index_id) + ".db")
        attr_len = 4 if attr_type < 2 else attr_type - 1
        order = min(400, (utils.PAGE_SIZE - 4) // attr_len)
        BufferManager.set_header("index" + str(record.index_id) + ".db", PageHeader(-1, 0, utils.int_to_byte(record.index_id)\
                                                                                        + utils.int_to_byte(table_id)\
                                                                                        + utils.int_to_byte(attr_id)\
                                                                                        + utils.int_to_byte(attr_type)\
                                                                                        + utils.int_to_byte(order)\
                                                                                        + utils.int_to_byte(1)))
        BufferManager.create_page("index" + str(record.index_id) + ".db")
        BufferManager.set_page("index" + str(record.index_id) + ".db", 1, PageData(-1, utils.bool_to_byte(True)\
                                                                                   + utils.bool_to_byte(True)\
                                                                                   + utils.int_to_byte(-1)\
                                                                                   + utils.int_to_byte(0)))

    @classmethod
    def drop_table(cls, table_name):
        page_id = cls.table_dict[table_name] // 30 + 1
        record_id = cls.table_dict[table_name] % 30
        table = CM_IO.decode_page(MetaType.table, page_id, record_id)
        table.valid = False
        CM_IO.update_page(MetaType.table, page_id, record_id, table)
        header = CM_IO.headerMap.get(MetaType.table)
        header.record_num -= 1
        CM_IO.update_header(MetaType.table, header)
        page = CM_IO.pageMap.get((MetaType.table, page_id))
        if page.next_free_page == -1:
            CM_IO.free_page(MetaType.table, page_id)
        del cls.table_dict[table_name]
        CM_IO.free_page(MetaType.attr, table.attr_page_id)
        BufferManager.remove_file("record" + str(table.table_id) + ".db")

    @classmethod
    def drop_index(cls, index_name):
        page_id = cls.index_dict[index_name] // 30 + 1
        record_id = cls.index_dict[index_name] % 30
        index = CM_IO.decode_page(MetaType.index, page_id, record_id)
        index.valid = False
        CM_IO.update_page(MetaType.index, page_id, record_id, index)
        header = CM_IO.headerMap.get(MetaType.index)
        header.record_num -= 1
        CM_IO.update_header(MetaType.index, header)
        page = CM_IO.pageMap.get((MetaType.index, page_id))
        if page.next_free_page == -1:
            CM_IO.free_page(MetaType.index, page_id)
        del cls.index_dict[index_name]
        BufferManager.remove_file("index" + str(index.index_id) + ".db")

    @classmethod
    def find_indexes(cls, table_name):
        """
        插入/删除时同步更新index用
        返回二元组(index_id, attr_name)的列表
        """
        table_id = cls.get_table_id(table_name)
        table = CM_IO.decode_page(MetaType.table, table_id // 30 + 1, table_id % 30)
        ret = []
        for i in cls.index_dict:
            page_id = cls.index_dict[i] // 30 + 1
            record_id = cls.index_dict[i] % 30
            index = CM_IO.decode_page(MetaType.index, page_id, record_id)
            if index.table_id == table_id:
                attr = CM_IO.decode_page(MetaType.attr, table.attr_page_id, index.attr_id)
                ret.append((index.index_id, attr.attr_name))
        return ret

    @classmethod
    def get_attr_id(cls, table_id, attr_name):
        table = CM_IO.decode_page(MetaType.table, table_id // 30 + 1, table_id % 30)
        for i in range(table.attr_num):
            attr = CM_IO.decode_page(MetaType.attr, table.attr_page_id, i)
            if attr.attr_name == attr_name:
                return (i, attr.attr_type)
        return (-1, -1)