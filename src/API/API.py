from typing import List
from CatalogManager.CatalogManager import CatalogManager
from RecordManager.RecordManager import RecordManager
from IndexManager.IndexManager import IndexManager
from BufferManager.BufferManager import BufferManager

class API:

    @classmethod
    def api_create_table(cls, create_value):
        '''
            如成功，输出执行成功信息
            如失败，告诉原因

            table合法性的检查已经在interpreter检查过了
            我们目前只支持单属性primary key
        '''
        
        table_name = create_value.table_name
        attr_num = len(create_value.column_data)
        attrs = [ (create_value.column_data[i], create_value.value_type[i][0], create_value.unique[i][1]) for i in range(attr_num)]

        pk_id = 0
        for i in range(attr_num):
            if create_value.column_data[i] == create_value.pk[0]:
                pk_id = i
                break

        ret = CatalogManager.create_table(table_name, attr_num, pk_id, attrs)

        return ret

    @classmethod
    def api_create_index(cls, create_value):
        '''
            如成功，输出执行成功信息
            如失败，告诉原因
        '''

        table_name = create_value.table_name
        index_name = create_value.index_name
        attr_name = create_value.attr_name
        index_id = CatalogManager.get_index_id(index_name)
        table_id = CatalogManager.get_table_id(table_name)

        # 查询所有元组
        selected = cls.api_select(create_value)

        # 创建索引文件
        CatalogManager.create_index(index_name, table_name, attr_name)

        

        # 把所有数据添加进bptree内
        for tuple in selected:
            position = None
            value = None
            IndexManager.insert(index_id, position, value)
            # TODO


    @classmethod
    def api_drop_table(cls, table_name):
        CatalogManager.drop_table(table_name)


    @classmethod
    def api_drop_index(cls, index_name):
        CatalogManager.drop_index(index_name)

    @classmethod
    def api_select(select_value) -> List:
        '''
            函数中将attr转换成了id形式
            保证所有attr都存在
            : return select_result
        '''
        
        candidate_condition = [] # TODO 等api
        for condition in select_value.condition:
            condition.lvalue = CatalogManager.get_attr_id(condition.lvalue)
            

        table_id = CatalogManager.get_table_id(select_value.table_name)
        select_result = RecordManager.select(table_id, condition = select_value.condition)
        return select_result

    @classmethod
    def api_delete(delete_value) -> int:
        '''
            函数中将attr转换成了id形式
            保证所有attr都存在
            : return delete_num
        '''

        # TODO candidate：我只知道attr的属性怎么对应上index_id
        for condition in delete_value.condition:
            condition.lvalue = CatalogManager.get_attr_id(condition.lvalue)

        table_id = CatalogManager.get_table_id(delete_value.table_name)
        delete_num = RecordManager.delete(table_id, delete_value.condition)
        return delete_num

    @classmethod
    def api_insert(insert_value):
        '''
            若该语句执行成功，则输出执行成功信息；
            若失败，必须告诉用户失败的原因
        '''

        # TODO 需要更新index
        table_id = CatalogManager.get_table_id(insert_value.table_name)
        (pos, page_id) = RecordManager.insert(table_id, insert_value.columm_data)

    @classmethod
    def api_quit():
        BufferManager.flush_buffer()