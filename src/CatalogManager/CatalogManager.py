from metaDS import *  # TODO
from BufferManager.BufferManager import BufferManager

class CatalogManager:
    def __init__(self):
        pass

    @classmethod
    def initialize():
        """
        启动程序时调用
        """
        if BufferManager.create_file("meta1.db") == 0:
            CM_IO.update_header(MetaType.table, MetaHeader(-1, 0, 0, 272, 30))
        if BufferManager.create_file("meta2.db") == 0:
            CM_IO.update_header(MetaType.attr, MetaHeader(-1, 0, 0, 255, 32))
        if BufferManager.create_file("meta3.db") == 0:
            CM_IO.update_header(MetaType.index, MetaHeader(-1, 0, 0, 268, 30))

    @classmethod
    def create_table(table_name, attr_num, pk_id, attrs) -> int:
        """
        : param 表名，属性个数，主键（0~31），属性列表
                attrs包含3元组(attr_name, attr_type, unique)
                attr_type:  0:int / 1:float / other:char(x-1)
        : return 0:success / 1:pk is not unique 
        """
        if not attrs[pk_id][2]:
            return 1
        header = CM_IO.headerMap.get(MetaType.table)
        if header == None:
            header = CM_IO.get_header_from_file(MetaType.table)
        page_id = CM_IO.get_new_page_id(MetaType.table)
        record = None
        for i in range(header.page_capacity):
            record = CM_IO.decode_page(MetaType.table, page_id, i)
            if record.valid:
                break
        record.valid = True
        record.table_id = header.page_capacity * page_id + i
        record.pk_id = pk_id
        record.attr_page_id = CM_IO.get_new_page_id(MetaType.attr)
        record.attr_num = attr_num
        record.table_name = table_name
        #TODO
        page = CM_IO.encode_page(MetaType.table, page_id, i, record)
        CM_IO.write_page(MetaType.table, page_id, page)
        return 0

    @classmethod
    def create_index(index_name, table_name, attr_name):
        """
        : return  0:success / 1: attr is not unique
        可能要由API手动做一下insert，这里访问不到record
        """
        pass

    @classmethod
    def __create_attr():
        pass

    @classmethod
    def drop_table(table_name): # TODO: 会失败吗？
        pass

    @classmethod
    def drop_index(index_name):
        pass