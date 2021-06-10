from interpreterDS import ReturnValue, ACTIONTYPE, CONDITION
from ply import yacc, lex
import interpreterDS as interpreterDS


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
    '''exp_create : CREATE TABLE COLUMN_OR_TABLE LPAREN columns RPAREN END
                  | CREATE INDEX COLUMN_OR_TABLE ON COLUMN_OR_TABLE LPAREN COLUMN_OR_TABLE RPAREN END'''
    global return_value
    if p[2] in ['table', "TABLE"]:
        return_value.action_type = ACTIONTYPE.CREATE_TABLE
        return_value.table_name = p[3]

    elif p[2] in ['index', 'index']:
        return_value.action_type = ACTIONTYPE.CREATE_INDEX
        return_value.index_name = p[3]
    else:
        print("Invalid command {}".format(p[2]))
    
    # TODO create

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
    '''exp_execfile : EXECFILE'''

def p_error(p):
    if p:
        print("Syntax error at {}".format(p))
    else:
        print("Syntax error!")
    parser.restart()

def pr(return_value):
    print(return_value)

while True:
    data = input("minisql>")
    # print(data)
    parser = yacc.yacc()
    res = parser.parse(data)
    # print(return_value.action_type)