
class MetaHeader:
    def __init__(self, first_free_page, size, table_num, record_length, page_capacity) -> None:
        """
          header单独占用一个page
        : param first_free_page: int, 0-3    文件中第一个可用页，初始值为-1
        : param size           : int, 4-7    该文件中有几个page
        : param record         : int, 8-11   该数据库中有几条记录
        : param record_length  : int, 12-15  
        : param page_capacity  : int, 16-19  
        """
        self.first_free_page = first_free_page
        self.size = size
        self.table_num = table_num
        self.record_length = record_length
        self.page_capacity = page_capacity

class MetaPagedData:
    def __init__(self, next_free_page, data) -> None:
        """
        : param next_free_page: int, 0-3     若为可用页，设为下一个可用页的number；若不可用，置为-1
        : param data          : byte,4-4095  数据区，只储存整数条记录，用0填满剩余的地方
        """
        self.next_free_page = next_free_page
        self.data = data
