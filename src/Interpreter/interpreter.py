import os
from interpreterDS import VALUETYPE
from interpreterDS import ReturnValue, ACTIONTYPE, CONDITION
from ply import yacc, lex


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
    r'[a-zA-Z0-9/.-]+'
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
test_lex = "select * from t1 where a = 1 and b = 1"
lexer.input(test_lex)
while True:
    tok = lexer.token()
    if not tok: break
    print(tok)


# ---------- Up: lex, Down: parse ---------------

condition = []
# column_data = interpreterDS.ColumnData()
column_data = []
return_value = ReturnValue()
execfile = 0
execfile_name = ""

def reset():
    global condition, column_data, return_value
    condition = []
    column_data = []
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
            pass
            # TODO API.api_create_table()

    elif p[2] in ['index', 'index']:
        return_value.action_type = ACTIONTYPE.CREATE_INDEX
        return_value.index_name = p[3]
        if check_create_index(return_value):
            pass
            # TODO API.api_create_index
    else:
        print("Invalid command {}".format(p[2])) 
    

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
        print("[Error] String length should be a number")
        raise SyntaxError
    return_value.value_type.append((VALUETYPE.CHAR, int(p[4])))
    return_value.column_data.append(p[1])
    return_value.unique.append(len(p) == 7)

    print("char variable {}".format(p[1]))

def p_expression_create_valid_int(p):
    '''exp_create_valid_int : COLUMN_OR_TABLE INT
                            | COLUMN_OR_TABLE INT UNIQUE'''
    global return_value
    return_value.value_type.append((VALUETYPE.FLOAT, 0))
    return_value.column_data.append(p[1])
    return_value.unique.append(len(p) == 4)

    print("int variable {}".format(p[1]))
    pass

def p_expression_create_valid_float(p):
    '''exp_create_valid_float : COLUMN_OR_TABLE FLOAT
                              | COLUMN_OR_TABLE FLOAT UNIQUE'''
    global return_value
    return_value.value_type.append((VALUETYPE.FLOAT, 0))
    return_value.column_data.append(p[1])
    return_value.unique.append(len(p) == 4)

    print("float variable {}".format(p[1]))


def p_expression_drop(p):
    '''exp_drop : DROP TABLE COLUMN_OR_TABLE 
                | DROP INDEX COLUMN_OR_TABLE'''

    global return_value
    if p[2] in ['table', "TABLE"]:
        return_value.action_type = ACTIONTYPE.DROP_TABLE
        return_value.table_name = p[3]
        # TODO drop_table
        pass
    elif p[2] in ['index', "INDEX"]:
        return_value.action_type = ACTIONTYPE.DROP_INDEX
        return_value.index_name = p[3]
        # TODO drop_index
        pass
    else:
        print("invalid command {}".format(p[2]))
        return 

def p_expression_select(p):
    '''exp_select : SELECT STAR FROM COLUMN_OR_TABLE END
                  | SELECT STAR FROM COLUMN_OR_TABLE exp_condition'''
    global return_value
    return_value.action_type = ACTIONTYPE.SELECT_STAR
    return_value.table_name = p[4]
    # TODO select api

def p_expression_delete(p):
    '''exp_delete : DELETE FROM COLUMN_OR_TABLE END
                  | DELETE FROM COLUMN_OR_TABLE exp_condition'''
    global return_value
    return_value.action_type = ACTIONTYPE.DELETE
    return_value.table_name = p[3]
    # TODO delete api
    pass

def p_expression_insert(p):
    '''exp_insert : INSERT INTO COLUMN_OR_TABLE exp_insert_line'''
    global return_value
    global column_data

    return_value.return_type = ACTIONTYPE.INSERT
    return_value.values.append(column_data)
    # TODO insert API


def p_expression_insert_line(p):
    '''exp_insert_line : VALUES LPAREN columns RPAREN END'''

def p_expression_columns(p):
    '''columns : COLUMN_OR_TABLE
               | COLUMN_OR_TABLE COMMA columns'''
    # 这个是倒序进入的
    column_data.append(p[1])

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
    print("Bye")
    # TODO 处理quit的事项
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

def check_create_table(return_value):
    
    print(return_value.pk)
    if len(return_value.pk) == 0:
        print("No primary key is specified!")
        return False

    print(return_value.column_data)
    for pk in return_value.pk:
        if pk not in return_value.column_data:
            print("Primary key is not in the table!")
            return False
    
    print(return_value.column_data)
    if len(set(return_value.column_data)) != len(return_value.column_data):
        print("Detect duplicate keys!")
        return False

    print(return_value.value_type)
    for val_type in return_value.value_type:
        if val_type[0] == VALUETYPE.CHAR:
            if val_type[1] > 255 or val_type[1] < 0:
                print("Invalid char definition!")
                return False
    
    for (i, col) in enumerate(return_value.column_data):
        if col in return_value.pk and return_value.unique[i] != True:
            print("Primary key {} should be unique!".format(col))
            return False

    return True


def check_create_index(return_value):
    pass

parser = yacc.yacc()

def interpret():
    global execfile, execfile_name
    
    while True:
        if execfile == 0:
            data = input("minisql>")
            reset()
            while ";" not in data:
                data = data + input()
            # print(data)
            
            res = parser.parse(data)
        
        else:
            if not os.path.exists(execfile_name):
                print("File does not exist!")
                return -1

            with open(execfile_name, "r") as f:
                while True:
                    data = ""
                    new_line = f.readline()
                    if not new_line:
                        return 0
                    
                    reset()
                    while ";" not in data:
                        if not new_line:
                            print("No end token found!")
                            return -1
                        data += new_line
                        new_line = f.readline()

                    print(data)
                    res = parser.parse(data)                    

interpret()              