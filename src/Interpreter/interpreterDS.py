class ReturnValue:
    action_type = None  # 返回值类型
    condition = []      # where条件，如果为空就说明没有。如果有，则是一个三元组(lvalue, comparator, rvalue)的列表
    column_data = []    # 插入的值，如果为空说明没有。如果有，则是一个多元列表，在create的时候储存字段名，其他时候储存插入的东西
    value_type = []     # 插入值的类型，只在create里使用。如果有，是一个二元组（type，length）的列表
    unique = []			# 是否唯一，只在create里使用。每个元素对应的unique情况
    pk = []				# 主键是哪几个，只在create里使用。只储存主键

    column_name = None
    table_name = None
    index_name = None
    attr_name = None