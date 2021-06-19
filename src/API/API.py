from CatalogManager.CatalogManager import CatalogManager
from RecordManager.RecordManager import RecordManager

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

        ret = CatalogManager.create_index(create_value.index_name, create_value.table_name, create_value.attr_name)

        return ret


    @classmethod
    def api_drop_table(cls, table_name):
        CatalogManager.drop_table(table_name)


    @classmethod
    def api_drop_index(cls, index_name):
        CatalogManager.drop_index(index_name)

    @classmethod
    def api_select(select_value):
        '''
            TODO
        '''
        for condition in select_value.condition:
            condition.lvalue = CatalogManager.get_attr_id(condition.lvalue)
        
        table_id = CatalogManager.get_table_id(select_value.table_name)
        select_result = RecordManager.select(table_id, condition = select_value.condition)
        return select_result

    @classmethod
    def api_delete(delete_value):
        '''
            函数中将attr转换成了id形式
        '''
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
        table_id = CatalogManager.get_table_id(insert_value.table_name)
        (pos, page_id) = RecordManager.insert(table_id, insert_value.columm_data)