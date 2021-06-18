from CatalogManager import CatalogManager

def api_create_table(create_value):
    '''
        如成功，输出执行成功信息
        如失败，告诉原因

        table合法性的检查已经在interpreter检查过了
    '''
    
    table_name = create_value.table_name
    attr_num = len(create_value.column_data)
    attrs = [ (create_value.column_data[i], create_value.value_type[i], create_value.unique[i]) for i in range(attr_num)]

    pk_id = 0 # TODO

    ret = CatalogManager.create_table(table_name, attr_num, pk_id, attrs)


def api_create_index(create_value):
    '''
        如成功，输出执行成功信息
        如失败，告诉原因
    '''

    ret = CatalogManager.create_index(create_value.index_name, create_value.table_name, create_value.attr_name)



def api_drop_table(table_name):
    '''
        如成功，输出执行成功信息
        如失败，告诉原因
    '''

    ret = CatalogManager.drop_table(table_name)
    pass

def api_drop_index(index_name):
    '''
        如成功，输出执行成功信息
        如失败，告诉原因
    '''

    ret = CatalogManager.drop_index(index_name)
    pass

def api_select(select_value):
    '''
        若该语句执行成功且查询结果不为空，则按行输出查询结果，第一行为属性名，其余每一行表示一条记录；若查询结果为空，则输出信息告诉用户查询结果为空；
        若失败，必须告诉用户失败的原因
    '''
    pass

def api_delete(delete_value):
    '''
        若该语句执行成功，则输出执行成功信息，其中包括删除的记录数；
        若失败，必须告诉用户失败的原因
    '''
    pass

def api_insert(insert_value):
    '''
        若该语句执行成功，则输出执行成功信息；
        若失败，必须告诉用户失败的原因
    '''
    pass

