class RecordHeader:
    def __init__(self, first_free_page, size, record_num, record_length, page_capacity) -> None:
        """
          Header单独占据一个Page
        : param first_free_page: int, 0-3    文件中第一个可用页，起始为-1
        : param size           : int, 4-7    当前page数量
        : param record_num     : int, 8-11   当前record数量
        : param record_length  : int, 12-15  一条record的长度
        : param page_capacity  : int, 16-19  page中可容纳record的数目
        """
        self.first_free_page = first_free_page
        self.size = size
        self.record_num = record_num
        self.record_length = record_length
        self.page_capacity = page_capacity 

class RecordPage:
    def __init__(self, next_free_page, data) -> None:
        """
        : param next_free_page: int, 0-3     若为可用页，设为下一个可用页的位置；若不可用，置为-1
        : param data          : byte, 4-     数据区，储存至多page_capacity条记录，用0填满剩余的地方
                                             存储格式为[next_free_record, record_content]组成的元组，长度为record_length + 4
        """
        self.next_free_page = next_free_page
        self.data = data