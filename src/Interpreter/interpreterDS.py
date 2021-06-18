class ReturnValue:
    action_type = None  # 返回值类型
    condition = []      
    # where条件，如果为空就说明没有
    # 如果有，则是一个三元组(lvalue, comparator, rvalue)的列表
    column_data = []
    # 插入的值，如果为空说明没有
    # 如果有，则是一个多元数组
    value_type = []
    # 插入值的类型
    unique = []
    # 是否唯一
    pk = []
    # 主键是哪几个

    # TODO 不知道这部分需不需要
    column_name = None
    table_name = None
    index_name = None
    attr_name = None


class ColumnStack:
    stack = []
    stack_ptr = 0
    def push(self):
        ret = self.stack[self.stack_ptr]
        self.stack_ptr -= 1
        return ret