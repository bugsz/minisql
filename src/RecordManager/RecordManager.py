from RecordManager.recordDS import *
from utils import utils

class RecordManager:
    def __init__(self):
        pass

    @classmethod
    def insert(cls, table_id, values):
        """
        values按序存储attrs的值
        类型检查由API和catalog完成
        返回值包含record_id/page_id，便于索引的插入
        """
        header = RM_IO.headerMap.get(table_id)
        if header == None:
            header = RM_IO.get_header_from_file(table_id)
        page_id, pos = RM_IO.get_free_pos(table_id)
        record = Record(True, values)
        RM_IO.update_page(table_id, page_id, pos, record)
        header.record_num += 1
        RM_IO.update_header(table_id, header)
        return (pos, page_id)

    @classmethod
    def delete(cls, table_id, condition = None, candidates = None):
        """
        CONDITION类的lvalue设为attr_id
        condition之间为and关系
        若条件中存在可被索引加速项，则将索引查询返回的record位置作为candidate传入
        此时这些条件不再出现在condition中
        下同
        返回值与select相同，用于维护index
        """
        header = RM_IO.headerMap.get(table_id)
        if header == None:
            header = RM_IO.get_header_from_file(table_id)
        deleted = []
        if candidates != None:
            for i in candidates:
                record = RM_IO.decode_page(table_id, i[1], i[0])
                if condition == None or cls.__match(record, condition):
                    cls.__delete_item(table_id, i[1], i[0], record)
                    deleted.append(record.value)
        else:
            cnt = 0
            page_id = 1
            while cnt < header.record_num:
                for i in range(header.page_capacity):
                    record = RM_IO.decode_page(table_id, page_id, i)
                    if record != None:
                        cnt += 1
                        if condition == None or cls.__match(record, condition):
                            cls.__delete_item(table_id, page_id, i, record)
                            deleted.append(record.value)
                page_id += 1
        header.record_num -= len(deleted)
        RM_IO.update_header(table_id, header)
        return deleted
                    
    @classmethod
    def select(cls, table_id, condition = None, candidates = None):
        """
        目前只支持select *
        解析索引查找结果也使用这个接口(condition = None)
        """
        header = RM_IO.headerMap.get(table_id)
        if header == None:
            header = RM_IO.get_header_from_file(table_id)
        ret = []
        if candidates != None:
            for i in candidates:
                record = RM_IO.decode_page(table_id, i[1], i[0])
                if condition == None or cls.__match(record, condition):
                    ret.append(record.value)
        else:
            cnt = 0
            page_id = 1
            while cnt < header.record_num:
                for i in range(header.page_capacity):
                    record = RM_IO.decode_page(table_id, page_id, i)
                    if record != None:
                        cnt += 1
                        if condition == None or cls.__match(record, condition):
                            ret.append(record.value)
                page_id += 1
        return ret
                    
    @classmethod
    def select_all_attrs(cls, table_id, attr_id):
        """
        返回(position, value)的list
        """
        header = RM_IO.headerMap.get(table_id)
        if header == None:
            header = RM_IO.get_header_from_file(table_id)
        ret = []
        cnt = 0
        page_id = 1
        while cnt < header.record_num:
            for i in range(header.page_capacity):
                record = RM_IO.decode_page(table_id, page_id, i)
                if record != None:
                    cnt += 1
                    ret.append(((i, page_id), record.value[attr_id]))
            page_id += 1
        return ret

    @classmethod
    def attr_value_exist(cls, table_id, attr_id, value) -> bool:
        header = RM_IO.headerMap.get(table_id)
        if header == None:
            header = RM_IO.get_header_from_file(table_id)
        cnt = 0
        page_id = 1
        while cnt < header.record_num:
            for i in range(header.page_capacity):
                record = RM_IO.decode_page(table_id, page_id, i)
                if record != None:
                    cnt += 1
                    if record.value[attr_id] == value:
                        return True
            page_id += 1
        return False

    @classmethod
    def __delete_item(cls, table_id, page_id, record_id, record):
        record.valid = False
        RM_IO.update_page(table_id, page_id, record_id, record)
        page = RM_IO.pageMap.get((table_id, page_id))
        if page.next_free_page == -1:
            RM_IO.free_page(table_id, page_id)

    @classmethod
    def __match(cls, record, condition) -> bool:
        for i in condition:
            if i.comparator == utils.COMPARATOR.EQUAL and record.value[i.lvalue] != i.rvalue:
                return False
            elif i.comparator == utils.COMPARATOR.NONEQUAL and record.value[i.lvalue] == i.rvalue:
                return False
            elif i.comparator == utils.COMPARATOR.GREATER_EQUAL and record.value[i.lvalue] < i.rvalue:
                return False
            elif i.comparator == utils.COMPARATOR.LESS_EQUAL and record.value[i.lvalue] > i.rvalue:
                return False
            elif i.comparator == utils.COMPARATOR.GREATER and record.value[i.lvalue] <= i.rvalue:
                return False
            elif i.comparator == utils.COMPARATOR.LESS and record.value[i.lvalue] >= i.rvalue:
                return False
        return True