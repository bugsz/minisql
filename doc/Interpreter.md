## Interpreter

### 功能

+ Interpreter模块直接与用户交互，主要实现以下功能：
  + 程序流程控制，即 `启动并初始化 -> "接收命令、处理命令、显示命令结果" 循环 -> 退出`流程。
  + 接收并解释用户输入的命令，生成命令的内部数据结构表示，同时检查命令的语法正确性和语义正确性，对正确的命令调用API层提供的函数执行并显示执行结果，对不正确的命令显示错误信息。

### 语句解析

我们使用词法分析工具lex和语法分析工具yacc对输入的语句进行解析，分析过程分为两步：词法分析和语法分析。

+ 词法分析：lex通过正则匹配寻找符合规则的词，生成token
+ 语法分析：yacc接收lex传来的token，根据用户定义规则，使用LR分析法进行语法解析，具体细节不过多阐述

`ply`库是lex和yacc的Python实现，这个实现比其它语言的实现更加清晰易懂，让我们可以方便快速完成此工作。



### 数据结构

+ 每条语句的解析结果都会储存到一个`ReturnValue`类中，该类储存了所有相关信息。具体结构如下：

  ```python
  class ReturnValue:
      action_type = None  # 返回值类型
      condition = []      # where条件，如果为空就说明没有。如果有，则是一个三元组(lvalue, comparator, rvalue)的列表
      column_data = []    # 插入的值，如果为空说明没有。如果有，则是一个多元列表，在create的时候储存字段名，其他时候储存插						  入的东西
      value_type = []     # 插入值的类型，只在create里使用。如果有，是一个二元组（type，length）的列表
      unique = []			# 是否唯一，只在create里使用。每个元素对应的unique情况
      pk = []				# 主键是哪几个，只在create里使用。只储存主键
  
      column_name = None
      table_name = None
      index_name = None
  ```

  



### 错误处理

在minisql输入的语句中出现的错误可以分为以下几种：

+ 语法错误（不支持的数据类型或运算符，错误的关键词，括号不匹配等）

+ 定义错误（创建表格时出现重复定义，char的长度不在范围内，主键未定义等）

+ 标识符错误（不存在的表名，索引名，字段名等）

+ 值错误（插入参数和表的定义不匹配）

+ 索引建立在非unique属性上

  

+ 不过，由于这其中绝大多数错误都需要查询元数据才能确定，因此将会交给API进行处理，在Interpreter中处理的只有前两个错误。
  + 对于所有的语法错误，我们不给出具体问题，只会输出错误的行号和错误关键词
  + 对于定义错误，我们会给出具体问题的说明



### 实现样例

#### 语句解析

+ 我们以`select * from table_name where xxx`的解析过程为例进行分析
  + 我们首先通过词法匹配得到不同的token，然后再进行语法匹配。首先在第一个函数之内匹配是否有 `select * from`，如果有`where`条件，就会进入下一个匹配函数执行。第二个匹配函数匹配`where`和`;`截止符。第三个匹配函数递归匹配所有的条件。部分代码如下。

```python
t_SELECT = r"SELECT|select" # 词法分析token，正则匹配select
def t_COLUMN_OR_TABLE(t):	# 词法分析token，正则匹配表名字，
    r'[a-zA-Z0-9/.-]+'
    if t.value.upper() in tokens: # 防止匹配到已有的token
        t.type = t.value.upper()
    return t

# --------------- up: lex, down: yacc -----------------

def p_expression_select(p):												# 语法分析，BNF形式匹配
    '''exp_select : SELECT STAR FROM COLUMN_OR_TABLE END				
                  | SELECT STAR FROM COLUMN_OR_TABLE exp_condition'''	# 或者直接结束，或者有条件
    global return_value
    return_value.action_type = ACTIONTYPE.SELECT_STAR
    return_value.table_name = p[4]
    
def p_expression_condition(p):											# where 条件，我们支持无限条件
    '''exp_condition : WHERE exp_all_conditions END'''

def p_expression_all_conditions(p):										# 条件主体，从右往左添加匹配到的条件
    '''exp_all_conditions : COLUMN_OR_TABLE COMPARATOR COLUMN_OR_TABLE
                          | COLUMN_OR_TABLE COMPARATOR COLUMN_OR_TABLE AND exp_all_conditions'''

    if not CONDITION.valid(p[2]):
        print("Invalid operator type {}".format(p[2]))
        return 
    
    global return_value
    return_value.condition.append(CONDITION(p[1], p[2], p[3]))
```



#### 错误处理

+ 语法错误：检测到错误后，我们在`p_error`函数中输出错误行号和信息。
+ 定义错误：解析完成后，所有数据都被存到`return value`中，因此这非常好检测，在此不赘述。

