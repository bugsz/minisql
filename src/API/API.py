from typing import List
from CatalogManager.CatalogManager import CatalogManager
from RecordManager.RecordManager import RecordManager
from IndexManager.IndexManager import IndexManager
from BufferManager.BufferManager import BufferManager

class API:
    @classmethod
    def api_initialize(cls):
        CatalogManager.initialize()

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
        attrs = [ (create_value.column_data[i], create_value.value_type[i][0], create_value.value_type[i][1], create_value.unique[i]) for i in range(attr_num)]

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
        attr_id = CatalogManager.get_attr_id(table_id, attr_name)

        # 查询所有元组
        selected = RecordManager.select_all_attrs(table_id, attr_id)

        # 创建索引文件
        CatalogManager.create_index(index_name, table_name, attr_name)
        
        attrs = CatalogManager.get_attrs_type(table_name)
        attr_id = 0
        for i in len(attrs):
            if attrs[i][0] == attr_name:
                attr_id = i
                break

        # 把所有数据添加进bptree内 
        for tuple in selected:
            position = tuple[0]
            value = tuple[1]
            IndexManager.insert(index_id, position, value)


    @classmethod
    def api_drop_table(cls, table_name):
        CatalogManager.drop_table(table_name)


    @classmethod
    def api_drop_index(cls, index_name):
        CatalogManager.drop_index(index_name)

    @classmethod
    def api_select(cls, select_value) -> List:
        '''
            函数中将attr转换成了id形式
            保证所有attr都存在
            : return select_result
        '''

        # 在查找的时候，只需要找一个index就行了
        candidate_tuple = None
        # 查找表中存在的index，
        # 形式为（index_id, attr_name)
        index_list = CatalogManager.find_indexes(select_value.table_name)
        for condition in select_value.condition:
            for index in index_list:
                if index[1] == condition.lvalue:
                    candidate_tuple = IndexManager.find_by_condition(index[0], condition)
                    select_value.condition.remove(condition)
                    break
                if candidate_tuple is not None:
                    break

        table_id = CatalogManager.get_table_id(select_value.table_name)

        for condition in select_value.condition:
            condition.lvalue = CatalogManager.get_attr_id(table_id, condition.lvalue)[0]
  

        # 可以利用index进行加速
        select_result = RecordManager.select(table_id, condition = select_value.condition, candidates = candidate_tuple)

        return select_result

    @classmethod
    def api_delete(cls, delete_value) -> int:
        '''
            函数中将attr转换成了id形式
            保证所有attr都存在
            : return delete_num
        '''
        # 在查找的时候，只需要找一个index就行了
        candidate_tuple = None
        table_id = CatalogManager.get_table_id(delete_value.table_name)
        # 查找表中存在的index，
        # 形式为（index_id, attr_name)
        index_list = CatalogManager.find_indexes(delete_value.table_name)
        for condition in delete_value.condition:
            for index in index_list:
                if index[1] == condition.lvalue:
                    candidate_tuple = IndexManager.find_by_condition(index[0], condition)
                    delete_value.condition.remove(condition)
                    break
                if candidate_tuple is not None:
                    break
        
        for condition in delete_value.condition:
            condition.lvalue = CatalogManager.get_attr_id(table_id, condition.lvalue)[0]

        table_id = CatalogManager.get_table_id(delete_value.table_name)
        delete_num = RecordManager.delete(table_id, condition = delete_value.condition, candidates= candidate_tuple)

        return delete_num

    @classmethod
    def api_insert(cls, insert_value):
        '''
            若该语句执行成功，则输出执行成功信息；
            若失败，必须告诉用户失败的原因
        '''
        table_name = insert_value.table_name
        table_id = CatalogManager.get_table_id(table_name)
        
        # 插入记录
        (record_id, page_id) = RecordManager.insert(table_id, insert_value.column_data)

        # 更新索引
        indexes = CatalogManager.find_indexes(table_name)
        attrs = CatalogManager.get_attrs_type(table_name)
        # print(attrs)
        for i in range(len(attrs)):
            for index in indexes:
                if attrs[i][0] == index[1]:
                    IndexManager.insert(index[0], (record_id, page_id), insert_value.column_data[i])

    @classmethod
    def api_quit():
        BufferManager.flush_buffer()