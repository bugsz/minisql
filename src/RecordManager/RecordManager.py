from RecordManager.recordDS import *
from utils.utils import *

class RecordManager:
    def __init__(self):
        pass

    @classmethod
    def insert(cls, table_id, values):
        """
        values按序存储attrs的值
        类型检查由API和catalog完成
        """
        pass

    @classmethod
    def delete(cls, table_id, condition = None):
        pass

    @classmethod
    def select(cls, table_id, condition = None):
        """
        返回值包含每条record的page_id/record_id/value，便于索引的插入
        """
        pass

    @classmethod
    def find_single(cls, page_id, record_id):
        """
        支持索引查找用
        """
        pass