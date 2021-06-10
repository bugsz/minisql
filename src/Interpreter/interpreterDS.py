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
    # TODO 不知道这部分需不需要
    column_name = None
    table_name = None
    index_name = None

class ACTIONTYPE:
    INSERT = 1
    CREATE_TABLE = 2
    CREATE_INDEX = 3
    DROP_TABLE = 4
    DROP_INDEX = 5
    SELECT_STAR = 6
    DELETE = 7

class COMPARATOR:
    EQUAL = 1  # =
    NONEQUAL = 2  # !=
    GREATER_EQUAL = 3  # >=
    LESS_EQUAL = 4  # <=
    GREATER = 5
    LESS = 6

class CONDITION:
    comparator_mapping = {
        "=" : COMPARATOR.EQUAL,
        "<>": COMPARATOR.NONEQUAL,
        ">=": COMPARATOR.GREATER_EQUAL,
        "<=": COMPARATOR.LESS_EQUAL,
        ">" : COMPARATOR.GREATER,
        "<" : COMPARATOR.LESS
    }
    def __init__(self, lvalue, comparator, rvalue):
        self.lvalue = lvalue
        self.rvalue = rvalue
        self.comparator = self.comparator_mapping[comparator]

    def tuple(self):
        return (self.lvalue, self.comparator, self.rvalue)

    def __eq__(self, that) -> bool:
        if isinstance(that, self.__class__):
            return self.tuple() == that.tuple()
        raise NotImplementedError


    @classmethod 
    def valid(cls, input):
        return input in cls.comparator_mapping.keys()

            

class ColumnStack:
    stack = []
    stack_ptr = 0
    def push(self):
        ret = self.stack[self.stack_ptr]
        self.stack_ptr -= 1
        return ret