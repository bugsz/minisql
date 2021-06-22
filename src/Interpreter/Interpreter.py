from BufferManager.BufferManager import BufferManager
from CatalogManager.CatalogManager import CatalogManager
import os
from utils.utils import ACTIONTYPE, CONDITION, VALUETYPE, COMPARATOR, print_dbg_info, float_to_byte, byte_to_float
from Interpreter.InterpreterDS import ReturnValue
from RecordManager import RecordManager
from ply import yacc, lex
from API.API import API 
from prettytable import PrettyTable
import time


tokens = (
    # Token for fixed statement
    "LPAREN",    # (
    "RPAREN",    # )

    "CREATE",
    "DROP",
    "SELECT",
    "INSERT",
    "DELETE",
    "QUIT",
    "EXECFILE",

    "TABLE",
    "PK",        # primary key
    "INDEX",

    "ON",
    "FROM",
    "WHERE",
    "INTO",
    'VALUES',
    "AND",
    "STAR",
    "COMMA",
    "UNIQUE",
    "INT",
    "CHAR",
    "FLOAT",
    "PRIMARY",
    "KEY",

    "END",

    # Token for variable inputs
    "COLUMN_OR_TABLE",
    "COMPARATOR",
)


# TODO 大小写不敏感的匹配
t_LPAREN = r"\("
t_RPAREN = r"\)"

t_CREATE = r"CREATE|create"
t_DROP   = r"DROP|drop"
t_SELECT = r"SELECT|select"
t_INSERT = r"INSERT|insert"
t_DELETE = r"DELETE|delete"
t_QUIT   = r"QUIT|quit"
t_EXECFILE=r"EXECFILE|execfile"

t_TABLE  = r"TABLE|table"
t_PK     = r"PK|pk"    # TODO 
t_PRIMARY= r"PRIMARY|primary"
t_KEY    = r"KEY|key"
t_INDEX  = r"INDEX|index"

t_ON     = r"ON|on"
t_FROM   = r"FROM|from"
t_WHERE  = r"WHERE|where"
t_INTO   = r"INTO|into" 
t_VALUES = r"VALUES|values"
t_AND    = r"AND|and"
t_COMMA  = r","

t_STAR   = r"\*"
t_END    = r";"
t_UNIQUE = r"UNIQUE|unique"

t_COMPARATOR = r"[<>=]{1,2}"



def t_COLUMN_OR_TABLE(t):
    r"[\"_\'a-zA-Z0-9/.-]+"
    if t.value.upper() in tokens:
        t.type = t.value.upper()
    # TODO
    return t

def t_newline(t):
    r'\n+'
    pass


t_ignore = " \t"

def t_error(t):
    print("Illegal character {}".format(t.value[0]))
    t.lexer.skip(1)

lexer = lex.lex()


test_lex = "insert into t1 values"
test_lex = "where a<>1 and b < 1"
test_lex = "select * from t1 where a = '1' and b = 1"
lexer.input(test_lex)
'''
while True:
    tok = lexer.token()
    if not tok: break
    print(tok)
'''

# ---------- Up: lex, Down: parse ---------------

condition = []
# column_data = interpreterDS.ColumnData()
column_data = []
return_value = ReturnValue()
execfile = 0
execfile_name = ""

def reset():
    global return_value
    return_value = ReturnValue()

def p_expression_start(p):
    '''expression : exp_drop
                  | exp_select
                  | exp_delete
                  | exp_create
                  | exp_insert
                  | exp_quit
                  | exp_execfile'''

def p_expression_create(p):
    '''exp_create : CREATE TABLE COLUMN_OR_TABLE LPAREN exp_create_columns RPAREN END
                  | CREATE INDEX COLUMN_OR_TABLE ON COLUMN_OR_TABLE LPAREN COLUMN_OR_TABLE RPAREN END'''
    global return_value
    if p[2] in ['table', "TABLE"]:
        return_value.action_type = ACTIONTYPE.CREATE_TABLE
        return_value.table_name = p[3]
        
        if check_create_table(return_value):
            API.api_create_table(return_value)
            print("Successfully create table {}".format(return_value.table_name))

    elif p[2] in ['index', 'index']:
        return_value.action_type = ACTIONTYPE.CREATE_INDEX
        return_value.index_name = p[3]
        return_value.table_name = p[5]
        return_value.attr_name = p[7]

        if check_create_index(return_value):
            API.api_create_index(return_value)
            print("Successfully create index {} on attribute {}".format(return_value.index_name, return_value.attr_name))

    else:
        print("Invalid command {}".format(p[2])) 
        raise SyntaxError
    

def p_expression_create_columns(p):
    '''exp_create_columns : exp_create_valid_column
                          | exp_create_valid_column COMMA exp_create_columns'''
    pass

def p_expression_create_valid_column(p):
    '''exp_create_valid_column : exp_create_valid_char
                               | exp_create_valid_int
                               | exp_create_valid_float
                               | exp_create_valid_pk'''
    pass

def p_expression_create_pk(p):
    '''exp_create_valid_pk : PRIMARY KEY LPAREN exp_pk RPAREN'''
    pass

def p_expression_pk(p):
    '''exp_pk : COLUMN_OR_TABLE
              | COLUMN_OR_TABLE COMMA exp_pk'''
    return_value.pk.append(p[1])

def p_expression_create_valid_char(p):
    '''exp_create_valid_char : COLUMN_OR_TABLE CHAR LPAREN COLUMN_OR_TABLE RPAREN UNIQUE
                               | COLUMN_OR_TABLE CHAR LPAREN COLUMN_OR_TABLE RPAREN'''
    if not str.isnumeric(p[4]):
        print("[Error] String length should be a number!")
        raise SyntaxError
    return_value.value_type.append((VALUETYPE.CHAR, int(p[4])))
    return_value.column_data.append(p[1])
    return_value.unique.append(len(p) == 7)

    # print("char variable {}".format(p[1]))

def p_expression_create_valid_int(p):
    '''exp_create_valid_int : COLUMN_OR_TABLE INT
                            | COLUMN_OR_TABLE INT UNIQUE'''
    global return_value
    return_value.value_type.append((VALUETYPE.INT, 0))
    return_value.column_data.append(p[1])
    return_value.unique.append(len(p) == 4)

    # print("int variable {}".format(p[1]))

def p_expression_create_valid_float(p):
    '''exp_create_valid_float : COLUMN_OR_TABLE FLOAT
                              | COLUMN_OR_TABLE FLOAT UNIQUE'''
    global return_value
    return_value.value_type.append((VALUETYPE.FLOAT, 0))
    return_value.column_data.append(p[1])
    return_value.unique.append(len(p) == 4)

    # print("float variable {}".format(p[1]))


def p_expression_drop(p):
    '''exp_drop : DROP TABLE COLUMN_OR_TABLE END 
                | DROP INDEX COLUMN_OR_TABLE END'''

    global return_value
    if p[2] in ['table', "TABLE"]:
        return_value.action_type = ACTIONTYPE.DROP_TABLE
        return_value.table_name = p[3]

        if check_drop_table(return_value):
            API.api_drop_table(return_value.table_name)
            print("Successfully drop table {}".format(p[3]))
        
    elif p[2] in ['index', "INDEX"]:
        return_value.action_type = ACTIONTYPE.DROP_INDEX
        return_value.index_name = p[3]

        if check_drop_index(return_value):
            API.api_drop_index(return_value.index_name)

    else:
        print("invalid command {}".format(p[2]))
        return 

def p_expression_select(p):
    '''exp_select : SELECT STAR FROM COLUMN_OR_TABLE END
                  | SELECT STAR FROM COLUMN_OR_TABLE exp_condition'''
    global return_value
    return_value.action_type = ACTIONTYPE.SELECT_STAR
    return_value.table_name = p[4]
    
    # print_dbg_info(return_value)

    if check_select(return_value):
        select_result = API.api_select(return_value)

        if len(select_result) == 0:
            print("No column selected")
            return 

        attrs = CatalogManager.get_attrs_type(p[4])
        attr_row = [attr[0] for attr in attrs]
        tb = PrettyTable()
        tb.field_names = attr_row
        for tuple in select_result:
            tb.add_row(tuple)
        print(tb)
        print("{} row(s) affected".format(len(select_result)))


def p_expression_delete(p):
    '''exp_delete : DELETE FROM COLUMN_OR_TABLE END
                  | DELETE FROM COLUMN_OR_TABLE exp_condition'''
    global return_value
    return_value.action_type = ACTIONTYPE.DELETE
    return_value.table_name = p[3]

    if check_delete(return_value):
        delete_num = API.api_delete(return_value)
        print("{} row(s) affected".format(len(delete_num)))

def p_expression_insert(p):
    '''exp_insert : INSERT INTO COLUMN_OR_TABLE exp_insert_line'''
    global return_value
    global column_data

    return_value.return_type = ACTIONTYPE.INSERT
    return_value.table_name = p[3]
    return_value.column_data.reverse()

    if check_insert(return_value):
        API.api_insert(return_value)
        print("1 row(s) affected")


def p_expression_insert_line(p):
    '''exp_insert_line : VALUES LPAREN columns RPAREN END'''

def p_expression_columns(p):
    '''columns : COLUMN_OR_TABLE
               | COLUMN_OR_TABLE COMMA columns'''
    # 这个是倒序进入的
    global return_value
    return_value.column_data.append(p[1])

def p_expression_condition(p):
    '''exp_condition : WHERE exp_all_conditions END'''

def p_expression_all_conditions(p):
    '''exp_all_conditions : COLUMN_OR_TABLE COMPARATOR COLUMN_OR_TABLE
                          | COLUMN_OR_TABLE COMPARATOR COLUMN_OR_TABLE AND exp_all_conditions'''

    if not CONDITION.valid(p[2]):
        print("Invalid operator type {}".format(p[2]))
        return 
    
    global return_value
    return_value.condition.append(CONDITION(p[1], p[2], p[3]))

def p_expression_quit(p):
    '''exp_quit : QUIT'''
    # API.api_quit()
    # print("Bye")
    raise InterruptedError
    
    exit(0)

def p_expression_execfile(p):
    '''exp_execfile : EXECFILE COLUMN_OR_TABLE END'''
    global execfile, execfile_name
    execfile = 1
    execfile_name = p[2]
    # print(execfile, execfile_name)


def p_error(p):
    if p:
        print("Syntax error at {}".format(p))
    else:
        print("Syntax error!")
    parser.restart()

def check_delete(return_value):
    '''
        同时把char的'去掉
    '''
    table_name = return_value.table_name
    if not CatalogManager.table_exist(table_name):
        print("Table does not exist!")
        return False
    
    for condition in return_value.condition:
        if not CatalogManager.attr_exist(table_name, condition.lvalue):
            print("Attribute {} does not exist!".format(condition.lvalue))
            return False
    
    return_value = condition_rvalue_decode(return_value)
    if return_value is None:
        return False
    
    return True

def check_select(return_value):
    """
        同时把char的'去掉
    """
    table_name = return_value.table_name
    if not CatalogManager.table_exist(table_name):
        print("Table does not exist!")
        return False

    for condition in return_value.condition:
        if not CatalogManager.attr_exist(table_name, condition.lvalue):
            print("Attribute {} does not exist!".format(condition.lvalue))
            return False
        # condition.rvalue = condition.rvalue.strip("'").strip("\"")
    
    return_value = condition_rvalue_decode(return_value)
    if return_value is None:
        return False
    
    return True

def check_create_table(return_value):
    # print(return_value.column_data)
    if CatalogManager.attr_exist(return_value.table_name, return_value.attr_name):
        print("Table does not exist!")
        return False

    # print(return_value.pk)
    if len(return_value.pk) == 0:
        print("No primary key is specified!")
        return False

    # print(return_value.column_data)
    for pk in return_value.pk:
        if pk not in return_value.column_data:
            print("Primary key is not in the table!")
            return False
    
    # print(return_value.column_data)
    if len(set(return_value.column_data)) != len(return_value.column_data):
        print("Detect duplicate keys!")
        return False

    # print(return_value.value_type)
    for val_type in return_value.value_type:
        if val_type[0] == VALUETYPE.CHAR:
            if val_type[1] > 255 or val_type[1] < 0:
                print("Invalid char definition!")
                return False

    if len(return_value.pk) != 1:
        print("We only support primary key that only contains one attribute!")
        return False
    
    
    for (i, col) in enumerate(return_value.column_data):
        if col in return_value.pk and return_value.unique[i] != True:
            print("Primary key {} should be unique!".format(col))
            return False

    return True


def check_create_index(return_value):
    # print(return_value.attr_name)
    
    if not CatalogManager.attr_exist(return_value.table_name, return_value.attr_name):
        print("Attribute name {} does not exist!")
        return False
        
    if CatalogManager.index_exist(return_value.index_name):
        print("Index name {} has already existed!".format(return_value.index_name))
        return False

    if not CatalogManager.attr_unique(return_value.table_name, return_value.attr_name):
        print("Attribute should be unique!")
        return False

    return True

def check_drop_table(return_value):
    if not CatalogManager.table_exist(return_value.table_name):
        print("Table does not exist!")
        return False

    return True

def check_drop_index(return_value):
    if not CatalogManager.index_exist(return_value.index_name):
        print("Index does not exist!")
        return False

    return True

def condition_rvalue_decode(return_value):
    table_name = return_value.table_name
    attrs = CatalogManager.get_attrs_type(table_name)
    # (attr_name, attr_type, attr_length)
    for condition in return_value.condition:
        attr_type = None
        for attr in attrs:
            if attr[0] == condition.lvalue:
                attr_type = attr[1]
            if attr_type is not None:
                break
        if attr_type == VALUETYPE.INT:
            try:
                condition.rvalue = int(condition.rvalue)
            except:
                print("Rvalue of condition should be INT for attr {}".format(attr.lvalue))
                return None
            
        
        elif attr_type == VALUETYPE.FLOAT:
            try:
                condition.rvalue = float(condition.rvalue)
                condition.rvalue = byte_to_float(float_to_byte(condition.rvalue))
                # print(condition.rvalue)
            except:
                print("Rvalue of condition should be FLOAT for attr {}".format(attr.lvalue))
                return None

        else:
            if ("'" not in condition.rvalue) and ("\"" not in condition.rvalue):
                print("You should use "" or '' to specify a string")
                return None
            condition.rvalue = condition.rvalue.strip("\"").strip("'")

    return return_value


def check_insert(return_value):

    # print(type(return_value.table_name))
    try:
        attrs = CatalogManager.get_attrs_type(return_value.table_name)
    except KeyError:
        print("Table not found!")
        return False

    if len(attrs) != len(return_value.column_data):
        print("Inserted element number {} does not match attribute number of table {}".format(len(return_value.column_data), len(attrs)))
        return False
    
    # print(attrs)
    
    # 检测数据类型是否匹配
    for i in range(len(attrs)):
        (attr_name, attr_type, attr_length) = attrs[i]

        insert_data = return_value.column_data[i]

        if ("'" in insert_data) or ("\"" in insert_data):
            return_value.column_data[i] = return_value.column_data[i].strip("'").strip("\"")
            # print(return_value.column_data[i])
            if attr_type != VALUETYPE.CHAR:
                print("Value type CHAR does not match on column {}".format(attr_name))
                return False
            if len(return_value.column_data[i]) > attr_length:
                print("Value {} of type char has more characters than specified!".format(return_value.column_data[i]))
                return False
            continue

        if str.isnumeric(insert_data):
            # int or float
            if attr_type == VALUETYPE.INT:
                return_value.column_data[i] = int(insert_data)
                # print(type(return_value.column_data[i]))
                continue
            if attr_type == VALUETYPE.FLOAT:
                return_value.column_data[i] = float(insert_data)
                # print(type(return_value.column_data[i]))
                continue
            if attr_type == VALUETYPE.CHAR:
                print("Please use '' to specify a string")
                return False
            continue

        if "." in insert_data:
            try:
                float_number = float(insert_data)
                
                if attr_type == VALUETYPE.FLOAT:
                    return_value.column_data[i] = float_number
                    continue
                
                if attr_type == VALUETYPE.INT:
                    print("Cannot insert float number to int attribute!")
                    return False

                if attr_type == VALUETYPE.CHAR:
                    print("Please use '' to specify a string")
                    return False
                continue
        

            except ValueError:
                print("Please use '' to specify a string")
                return False

    if not check_unique(return_value, attrs):
        return False
    
    return True        

def check_unique(return_value, attrs):
    # 利用索引进行优化查询
    table_name = return_value.table_name
    # print(attrs)
    
    # print_dbg_info(unique_value)   
    # 检测是否unique
    for i in range(len(attrs)):
        unique_value = ReturnValue()
        unique_value.table_name = table_name
        attr_name = attrs[i][0]
        # (attr_name, attr_type, attr_length)
        if not CatalogManager.attr_unique(table_name, attr_name):
            continue
        condition_rvalue = return_value.column_data[i]
        condition_comparator = "="
        condition_lvalue = attr_name
        # print(condition_lvalue, condition_comparator, condition_rvalue)
        unique_value.condition.append(CONDITION(condition_lvalue, condition_comparator, condition_rvalue))
        data_tuple = API.api_select(unique_value)
        if len(data_tuple) != 0:
            print("Inserted data on attribute {} should be unique!".format(attr_name))
            return False

    return True

parser = yacc.yacc()

def execute_user_input():
    reset()
    data = input("minisql>")
    while ";" not in data:
        data = data + input()
    data = data.strip("\n")
    print(data)
    
    start_time = time.time()
    res = parser.parse(data)
    end_time = time.time()
    print("Execute time: {:.2f}s".format(end_time-start_time))
    # print(BufferManager.buffer_blocks)

def execute_file():
    global execfile, execfile_name
    if not os.path.exists(execfile_name):
        print("File does not exist!")
        return -1

    with open(execfile_name, "r") as f:
        while True:
            data = ""
            new_line = f.readline()
            if not new_line:
                print("Detect empty line, quit...")
                return 0
            
            reset()
            while ";" not in data:
                if not new_line:
                    print("No end token found!")
                    return -1
                data += new_line
                if ";" in new_line:
                    break
                new_line = f.readline()
            data = data.strip("\n")
            print(data)
            parser.parse(data)


def Interpret():
    API.api_initialize()
    global execfile, execfile_name
    execfile = 0
    
    while True:
        if execfile == 0:
            reset()
            execute_user_input()
        else:
            start_time = time.time()
            res = execute_file()
            end_time = time.time()
            print("Execute time: {:.2f}s".format(end_time-start_time))
            if res == -1:
                return 
            execfile = 0                                    