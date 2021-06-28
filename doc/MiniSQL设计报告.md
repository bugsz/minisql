![](.\figure\31.png)

#                                     **MiniSQL设计报告**

| 姓名   | 学号       | 分工                                           | 联系方式    |
| ------ | ---------- | ---------------------------------------------- | ----------- |
| 苏哲   |            | interpreter, buffer manager, api               |             |
| 陈新宇 |            | record manager, index manager, catalog manager |             |
| 王荣浩 | 3170100140 | 系统测试，编写报告                             | 18561226609 |

[toc]

## **1 实验目的**

设计并实现一个精简型单用户SQL引擎(DBMS)MiniSQL，允许用户通过字符界面输入SQL语句实现表的建立/删除；索引的建立/删除以及表记录的插入/删除/查找。

通过对MiniSQL的设计与实现，提高学生的系统编程能力，加深对数据库系统原理的理解。

## **2 需求概述**

### **2.1 数据类型**

只要求支持三种基本数据类型：int，char(n)，float，其中char(n)满足 1 <= n <= 255 。

### **2.2 表定义**

一个表最多可以定义32个属性，各属性可以指定是否为unique；支持单属性的主键定义。

### **2.3 索引的建立和删除**

对于表的主属性自动建立B+树索引，对于声明为unique的属性可以通过SQL语句由用户指定建立/删除B+树索引（因此，所有的B+树索引都是单属性单值的）。

### **2.4 查找记录**

可以通过指定用and连接的多个条件进行查询，支持等值查询和区间查询。

### **2.5 插入和删除记录**

支持每次一条记录的插入操作；支持每次一条或多条记录的删除操作。

## **3 语法说明**

MiniSQL支持标准的SQL语句格式，每一条SQL语句以分号结尾，一条SQL语句可写在一行或多行。为简化编程，要求所有的关键字都为小写。在以下语句的语法说明中，用黑体显示的部分表示语句中的原始字符串，如**create**就严格的表示字符串“create”，否则含有特殊的含义，如表名并不是表示字符串 “表名”，而是表示表的名称。

- **创建表**

  ```sql
  create table 表名（
  	列名1 类型1，
  	列名1 类型1，
  	...
  	列名1 类型1，
  	primary key(列名)
  ）；
  ```

  其中，属性声明后可加上关键字unique。声明为primary key的属性必须声明为unique，否则会报错“Primary key <primary key attribute name\> should be unique!”.

  创建表成功会打印以下内容

  ```
  Successfully create table <table name>
  Execute time: <float number>s
  ```

  创建表失败会打印报错信息。

- **删除表**

  ```sql
  drop table 表名；
  ```

  删除表成功，打印以下内容

  ```
  Successfully drop table <table name>
  Execute time: <float number>s
  ```

  删除不存在的表会报错

  ```
  Table does not exist!
  Execute time: <float number>s
  ```

- **创建索引**

  ```sql
  create index 索引名 on 表名（列名）；
  ```

  MiniSQL自动对主键属性建立索引。对其他属性建立索引成功打印以下信息

  ```
  Successfully create index <index name> on attrubute <attribute name>
  Execute time: <float number>s
  ```

  建立索引失败打印报错信息。

- **删除索引**

  ```sql
  drop index 索引名；
  ```

  删除索引成功打印如下信息

  ```
  Execute time: <float number>s
  ```

  删除索引失败打印报错信息

- **选择语句**

  ```sql
  select * from 表名；
  select * from 表名 where 条件；
  ```

  其中，条件语法格式为

  ```
  列 operator 值 and 列 operator 值 and 列 operator 值
  ```

  operator为=,<>,<,>,<=,>=

  选择记录成功，打印一个包含数据记录的table，并打印以下信息

  ```
  <integer> row(s) affected
  Execute time: <float number>s
  ```

  <img src=".\figure\1.png" style="zoom:75%;" />

  选择记录为空，打印如下信息

  ```
  No column selected
  Execute time: <float number>s
  ```

  选择记录出现错误，打印报错信息

- **插入记录**

```sql
insert into 表名 values(值1，值2，...,值n);
```

​	插入记录成功显示以下内容

```
<integer> row(s) affected
Execute time: <float number>s
```

​	插入记录失败打印报错信息

- **删除记录**

  ```sql
  delete from 表名；
  delete from 表名 where 条件；
  ```

  删除记录成功输出以下信息

  ```
  <integer> row(s) affected
  Execute time: <float number>s
  ```

  删除记录失败打印报错信息

- **退出MiniSQL系统**

  MiniSQL有两种执行方式：命令行和脚本文件模式。

  退出命令行模式时，在命令行输入

  ```sql
  quit;
  ```

  MiniSQL退出系统，并打印如下信息

  ```
  Finish executing, bye...
  ```

- **执行SQL脚本文件**

  MiniSQL执行脚本文件语法如下所示

  ```sql
  execfile <path to file>;
  ```

  如果脚本文件末尾包含退出指令

  ```sql
  quit;
  ```

  那么当MiniSQL读取到这行代码时，系统结束运行并退出。如果该指令后还有其他MiniSQL语句，那么系统不执行这些语句。

## **4 系统设计**

### **4.1 系统体系结构**

MiniSQL系统体系结构参考了实验指导书的要求，如下图所示。

<img src=".\figure\12.png" style="zoom:67%;" />

### **4.2 Interpreter**

#### **4.2.1 功能**

+ Interpreter模块直接与用户交互，主要实现以下功能：
  + 程序流程控制，即 `启动并初始化 -> "接收命令、处理命令、显示命令结果" 循环 -> 退出`流程。
  + 接收并解释用户输入的命令，生成命令的内部数据结构表示，同时检查命令的语法正确性和语义正确性，对正确的命令调用API层提供的函数执行并显示执行结果，对不正确的命令显示错误信息。

#### **4.2.2 语句解析**

我们使用词法分析工具lex和语法分析工具yacc对输入的语句进行解析，分析过程分为两步：词法分析和语法分析。

+ 词法分析：lex通过正则匹配寻找符合规则的词，生成token
+ 语法分析：yacc接收lex传来的token，根据用户定义规则，使用LR分析法进行语法解析，具体细节不过多阐述

`ply`库是lex和yacc的Python实现，这个实现比其它语言的实现更加清晰易懂，让我们可以方便快速完成此工作。

#### **4.2.3 数据结构**

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
      attr_name = None
  ```

#### **4.2.4 相关错误**

##### **4.2.4.1 错误分类**

在minisql输入的语句中出现的错误可以分为以下几种：

+ 语法错误（不支持的数据类型或运算符，错误的关键词，括号不匹配等）
+ 定义错误（创建表格时出现重复定义，char的长度不在范围内，主键未定义等）
+ 标识符错误（不存在的表名，索引名，字段名等）
+ 值错误（插入参数和表的定义不匹配）
+ 索引建立在非unique属性上

##### **4.2.4.2 错误检测和处理**

+ 语法错误：检测到错误后，我们在`p_error`函数中输出错误行号和信息。
+ 定义错误：解析完成后，所有数据都被存到`return value`中。我们需要检测的有命名冲突，无主键定义，char长度不在范围内等。这些都比较好检测，在此不赘述。
+ 标识符错误：调用`CatalogManager`中提供的方法检测表格和索引等是否存在。如果不存在，给出提示。
+ 值错误：调用`CatalogManager`获取相关元属性，然后进行检测。
+ 属性建立在非unique属性上：调用`CatalogManager`获取相关元属性，然后进行检测。

#### **4.2.5 实现样例**

整个执行流程可以大致分为`语句解析->数据处理->错误检测->执行`四个阶段，以及循环输入读取，下面我们对这些进行简要介绍。

##### **4.2.5.1 循环输入读取**

+ 我们有一个全局变量`execfile`用于确定执行文件还是执行用户输入，并交由相对应函数处理
+ 两个函数的逻辑基本相同：一直读取输入，直到遇到`;`为止。然后将整个语句交由parser处理，并计算执行时间。
+ 由于逻辑较为简单，在此不做赘述。

##### **4.2.5.2 语句解析**

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

##### **4.2.5.3 数据处理**

词法和语法解析所获得的都只是字符串类型的数据，也有可能包含引号。因此，我们需要将这些数据转成相应的类型。

+ 对于create，我们只需要将匹配的char长度转换成int即可
+ 对于insert，我们首先从`CatalogManager`获取相关属性类型，然后根据这些结果进行转换。
+ 对于select和delete当中的条件`condition`，其包含lvalue, comparator, rvalue三个元素，分别对应元素名，比较运算符，元素值，我们在这里对元素值进行类型转换，方式与insert相同

**类型转换方案：**对于char，我们过滤引号；对于int和float，我们只要检测该字符串是否可以转换成相应类型即可。这可以通过`try...except`解决。大致代码如下

**float类型转换**：由于我们使用byte对float进行储存，这样就一定会带来精度的损失，给等号比较带来麻烦。因此，我们在处理过程中会将`rvalue`转换成byte再转换回来，这样保证相等的float数据转换过后仍然相等。

```python
	attrs = CatalogManager.get_attrs_type(table_name)
    # (attr_name, attr_type, attr_length)
    for condition in return_value.condition:
        attr_type = None
        for attr in attrs:
            if attr[0] == condition.lvalue:
                attr_type = attr[1]
        if attr_type == VALUETYPE.INT:
            try:
                condition.rvalue = int(condition.rvalue)
            except:
                ...  
        elif attr_type == VALUETYPE.FLOAT:
            try:
                condition.rvalue = float(condition.rvalue)
                condition.rvalue = byte_to_float(float_to_byte(condition.rvalue))
            except:
                ...
        else:
            if ("'" not in condition.rvalue) and ("\"" not in condition.rvalue):
                print("You should use "" or '' to specify a string")
                return None
            condition.rvalue = condition.rvalue.strip("\"").strip("'")
```

##### **4.2.5.4 错误检测和处理**

+ 我们以`create table`为例说明，部分代码如下

  + 在这里，我们只展示了少部分的错误检测代码。首先，我们通过`CatalogManager`查找表格是否存在。然后，我们验证定义是否存在主键和主键是否在表格中。当然此后还有char长度检测，单主键检测等，但是以下代码并没有体现这些实现。

  ```python
  def check_create_table(return_value):
  
      if CatalogManager.attr_exist(return_value.table_name): 
          print("Table does not exist!")
          return False
  
      if len(return_value.pk) == 0:
          print("No primary key is specified!")
          return False
  
      for pk in return_value.pk:
          if pk not in return_value.column_data:
              print("Primary key is not in the table!")
              return False
  ```

##### **4.2.5.5 执行**

+ 执行阶段，我们调用API提供的接口执行操作，获取返回值并展现，在此仅提供简单代码示例，实现细节将在其他部分展现。

  ```python
  	if check_select(return_value):
          select_result = API.api_select(return_value)  # 调用API
  
          if len(select_result) == 0:
              print("No column selected")
              return 
  # --------------------- 输出 -----------------------------
          attrs = CatalogManager.get_attrs_type(p[4])
          attr_row = [attr[0] for attr in attrs]
          tb = PrettyTable()
          tb.field_names = attr_row
          for tuple in select_result:
              tb.add_row(tuple)
          print(tb)
          print("{} row(s) affected".format(len(select_result)))
  ```

#### **4.2.6 表格的输出**

+ 我们使用`PrettyTable`库输出`select`语句执行结果。
+ 库的使用方法非常简单，在此不做赘述

### **4.3 API**

Record Manager、Index Manager与Catalog Manager处于数据库整体架构的中间部分——它们通过Buffer Manager完成与文件的IO交互， 在内部处理数据，并向API层开放相应的接口。数据库的主要功能在这一层次实现。

三大Manager模块在文件处理方面非常相似，它们都从Buffer中获得基本单位大小的数据（称为page，8192Bytes），解码出有效数据，并将数据组织成有序状态写回。因此，我们提供抽象的文件数据处理模型（不同模块中的实现细节有所不同）。

以最简单的Record Manager为例：

```python
class RM_IO:
    def __init__(self):
        pass
	# 对已获取过的数据进行缓存，加速查询时间
    headerMap = {} # table_id:PageHeader
    pageMap = {} # (table_id, page_id):PageData

    # 从特定文件中获取header并解码
    @classmethod
    def get_header_from_file(cls, table_id) -> Header:
        
    # 从特定文件的page_id处获取page
    @classmethod
    def get_page_from_file(cls, table_id, page_id) -> Page:
        
    # 从page中解码第record_id条记录
    @classmethod
    def decode_page(cls, table_id, page_id, record_id):   

    # 更新page/header   
    @classmethod
    def update_header(cls, table_id, header):
    @classmethod
    def update_page(cls, table_id, page_id, record_id, content) -> None:
    
    # 查询表中可插入记录的位置
    @classmethod
    def get_free_pos(cls, table_id):
    
    # 将页面标记为free(可插入)，维护表的free page链表
    @classmethod
    def free_page(cls, table_id, page_id) -> None:
        pass
    
    # 私有接口，将数据编码为二进制，供update page调用
    @classmethod
    def __encode_page(cls, table_id, page_id, record_id, content):
        
    # 私有接口，向Buffer Mananger申请一个空白page
    @classmethod
    def __get_new_page_id(cls, table_id) -> int:
        pass
        
    # 私有接口，将修改过的数据写回Buffer
    @classmethod
    def __write_header(cls, table_id, header):
    @classmethod
    def __write_page(cls, table_id, page_id, page):
```

该模块接受数据块page，输出Manager需要的格式化数据，充当文件系统之上的过渡模块。这样，我们在编写代码时可以更加专注于处理逻辑，将IO交互与数据处理分离开来。

### **4.4 Catalog Manager**

#### **4.4.1 基本功能**

Catalog Manager管理数据库中所有的表、属性与索引，实际上是维护了数据库中特殊的三张表，我们称之为元数据（meta）。主要功能有：

+ 支持数据表的新建与删除，记录表的基本属性（表名、关联属性、主键等等），支持使用表名查询表的详细信息；
+ 支持表内属性的同步新建/删除，记录属性的基本值以及查询；
+ 支持索引的新建/删除/查询；
+ 完成相关文件的创建与header初始化。

模块接口如下：

```python
class CatalogManager:
    def __init__(self):
        pass
	# 数据库中表和索引的数目相对较少，因此可以直接全部存放在缓存中
    table_dict = {}
    index_dict = {}

    @classmethod
    def initialize(cls):
        """
        启动程序时调用
        如果meta文件不存在则创建空表
        若存在则读入缓存中
        """
	# 查询基本信息接口
    @classmethod
    def get_table_id(cls, table_name):
    @classmethod
    def get_index_id(cls, index_name):
    @classmethod
    def table_exist(cls, table_name) -> bool:
    @classmethod
    def index_exist(cls, index_name) -> bool:
	@classmethod
    def attr_exist(cls, table_name, attr_name) -> bool:
    @classmethod
    def attr_unique(cls, table_name, attr_name) -> bool:

    @classmethod
    def get_attrs_type(cls, table_name):
        """
        插入时做类型检查用
        返回(attr_name, attr_type, attr_length)的列表
        """
	# 创建接口
    @classmethod
    def create_table(cls, table_name, attr_num, pk_id, attrs):
    @classmethod
    def create_index(cls, index_name, table_name, attr_name):
    
    # 删除接口
    @classmethod
    def drop_table(cls, table_name):
    @classmethod
    def drop_index(cls, index_name):

    @classmethod
    def find_indexes(cls, table_name):
        """
        插入/删除时，同步更新索引使用
        返回该表上的所有索引
        """
```

#### **4.4.2 数据结构**

```python
class MetaType(Enum):
    table = 1
    attr = 2
    index = 3

class MetaHeader:
    def __init__(self, first_free_page, size, record_num, record_length, page_capacity) -> None:
        """
          header单独占用一个page
        : param first_free_page: int, 0-3    文件中第一个可用页，初始值为-1
        : param size           : int, 4-7    该文件中有几个page
        : param record_num     : int, 8-11   该数据库中有几条记录
        : param record_length  : int, 12-15  
        : param page_capacity  : int, 16-19  
        """
        self.first_free_page = first_free_page
        self.size = size
        self.record_num = record_num
        self.record_length = record_length
        self.page_capacity = page_capacity

class MetaTable:
    def __init__(self, table_id, pk_id, attr_page_id, attr_num, table_name, valid):
        """
          至多存放30个/page
        : param table_id    : int , 0-3
        : param pk_id       : int , 4-7      主键的attr_id
        : param attr_page_id: int , 8-11
        : param attr_num    : int , 12-15  
        : param table_name  : char, 16-270
        : param valid       : bool, 271
        """
        self.table_id = table_id
        self.pk_id = pk_id
        self.attr_page_id = attr_page_id
        self.attr_num = attr_num
        self.table_name = table_name
        self.valid = valid

class MetaAttr:
    def __init__(self, attr_name, attr_type, index_id, unique):
        """
          至多存放32个/page
          将属于一个table的attr存放在同一个page里，因此省略了table_id
        : param attr_name: char, 0-245 
        : param attr_type: int , 246-249
        : param index_id : int , 250-253
        : param unique   : bool, 254
        """
        self.attr_name = attr_name
        self.attr_type = attr_type
        self.index_id = index_id
        self.unique = unique

class MetaIndex:
    def __init__(self, index_id, index_name, table_id, attr_id, valid):
        """
          至多存放30个/page
        : param index_id  : int , 0-3
        : param index_name: char, 4-258
        : param table_id  : int , 259-262
        : param attr_id   : int , 263-266
        : param valid     : bool, 267
        """
        self.index_id = index_id
        self.index_name = index_name
        self.table_id = table_id
        self.attr_id = attr_id
        self.valid = valid
```

由于meta文件是特化的表，MetaHeader和record完全一致。而meta文件对应的三种record类型则如上所示。record_length、page_capacity等属性可直接计算得出。

存储属性的MetaAttr略有不同。考虑到表与属性是一个一对多的关系，且访问属性必须经过表的查询。如果将属性也视为普通的记录存储，则要在MetaTable中存储多个指针指向每个属性，带来很大的开销。因此我们牺牲了一点空间利用率，将单张表的所有属性存储在一个page中，这样只需要进行一次寻址便可以找到所有的属性。

#### **4.4.3 实现细节**

Catalog Manager的执行方式与Record也基本一致，只是需要在修改meta时同步维护存储文件实体。以create table为例：

```python
def create_table(cls, table_name, attr_num, pk_id, attrs):
        #向metaTable表中插入一条record

        BufferManager.create_file("record" + str(record.table_id) + ".db")
        data = utils.int_to_byte(0) + utils.int_to_byte(record_len) +\
               utils.int_to_byte((utils.PAGE_SIZE - 4) // record_len) + utils.int_to_byte(attr_num) + data
        BufferManager.set_header("record" + str(record.table_id) + ".db", PageHeader(-1, 0, data))
```

由于文件更新是与Buffer交互，所以务必在程序结束时写回所有buffer，保证数据的一致性。

### **4.5 Record Manager**

#### **4.5.1 基本功能**

Record Manager管理所有表中的数据项，主要功能有：

+ 数据项的插入、删除与检索；
+ 逻辑检查接口，比如检查数据项是否违反unique声明。

模块接口如下：

```python
class RecordManager:
    def __init__(self):
        pass

    @classmethod
    def insert(cls, table_id, values):
        """
        values按序存储各个属性的值
        类型检查交由API层完成
        返回值包含record的文件位置，便于索引的维护
        """

    @classmethod
    def delete(cls, table_id, condition = None, candidates = None):
        """
        condition之间为and关系
        若条件中存在可被索引加速项，则将索引查询返回的record位置作为candidate传入
        此时这些条件不再出现在condition中
        返回值为删除record文件位置的列表，便于索引的维护
        """
                    
    @classmethod
    def select(cls, table_id, condition = None, candidates = None):
        """
        参数/返回值定义与delete相似
        """

    @classmethod
    def attr_value_exist(cls, table_id, attr_id, value) -> bool:
        """
        检查某一属性值是否出现过
        为API检查unique声明提供接口
        """
```

#### **4.5.2 数据结构**

```python
class RecordHeader:
    def __init__(self, first_free_page, size, record_num, record_length, page_capacity, attr_num, attr_types) -> None:
        """
        : param first_free_page: int, 0-3    文件中第一个可用页，起始为-1
        : param size           : int, 4-7    当前page数量
        : param record_num     : int, 8-11   当前record数量
        : param record_length  : int, 12-15  一条record的长度
        : param page_capacity  : int, 16-19  page中可容纳record的数目
        : param attr_num       : int, 20-23  参数数目
        : param attr_types     : int, 24-23+4*num   0:int / 1:float / other:char(x-1)
        """
class Record:
    def __init__(self, valid, value):
        """
        : param valid: bool, 0  标记record是否被删除
        : param value: list
        """
```

Header中，record_length/attr_num/attr_types都在创建表时确定，不再更改。page_capacity可以由页面容量除以记录长度得出。

Record在删除时只执行“懒惰操作”，即将valid置为0以节省时间，插入新record时覆盖即可。

#### **4.5.3 实现细节**

Record Manager的函数执行流程大同小异：

+ 遍历所有record位置，跳过标记为not valid项
+ 对于每个record，检查其是否满足条件
  + 若满足，执行相关操作（删除或输出信息）
+ 如果枚举属性可被索引加速，则枚举范围从整张表缩小为candidate。

以select为例：

```python
def select(cls, table_id, condition = None, candidates = None):
        header = RM_IO.headerMap.get(table_id)
        if header == None:
            header = RM_IO.get_header_from_file(table_id)
        ret = []
        if candidates != None: # 枚举candidate
            for i in candidates:
                record = RM_IO.decode_page(table_id, i[1], i[0])
                if condition == None or cls.__match(record, condition):
                    ret.append(record.value)
        else:  # 枚举全局
            cnt = 0
            page_id = 1
            while cnt < header.record_num:
                for i in range(header.page_capacity):
                    record = RM_IO.decode_page(table_id, page_id, i)
                    if record != None:
                        cnt += 1
                        if condition == None or cls.__match(record, condition):
                            ret.append(record.value)
                page_id += 1
        return ret
```

### **4.6 Index Manager**

#### **4.6.1 基本功能**

Index Manager管理数据库中的索引，以B+树的形式组织。主要功能有：

+ 在索引中插入/删除数据项
+ 条件查询满足要求的数据

接口如下：

```python
class IndexManager:
    def __init__(self):
        pass

    @classmethod
    def insert(cls, index_id, position, value):
        """
            插入值为value/物理位置为position=(record_id,page_id)的record
        """
    
    @classmethod
    def delete(cls, index_id, value):
        """
            删除值为value的record
            成功返回1，未找到返回-1
        """

    @classmethod
    def find_by_condition(cls, index_id, condition):
        """
        基于单一condition查询record
        返回组成元素为位置元组的list
        """

    @classmethod
    def find_single(cls, index_id, value):
        """
            查询值等于value的record
            成功返回位置元组(record_id, page_id)，未找到返回None
        """

    @classmethod
    def __find_range(cls, index_id, lower, upper, includeL, includeR):
        """
            查询值处于区间[lower,upper]的record
            includeL与includeR表示区间开闭
            由find_by_condition调用
        """
```

#### **4.6.2 数据结构**

索引中的基本元素为b+树节点：

```python
class BPTreeNode:
    def __init__(self, index_id, page_id, is_root, is_leaf, next, size, pointer, key) -> None:
        """
          每个B+树节点单独占用一个page
        : param next          : 索引序后一个节点pid(非叶节点置0)
        : param size          : 当前pointer数目
        : param pointer       : 以元组(record_id, page_id)存储(非叶节点record_id置0)
        : param key           : 存储各child的最大值
        """
        self.index_id = index_id
        self.page_id = page_id
        self.is_root = is_root
        self.is_leaf = is_leaf
        self.next = next
        self.size = size
        self.pointer = pointer
        self.key = key
        self.child = [None] * size
      
class IndexHeader:
    def __init__(self, first_free_page, size, table_id, attr_id, attr_type, order, root) -> None:
        """
          header单独占用一个page
        : param first_free_page: int, 0-3    文件中第一个可用页，初始值为-1
        : param size           : int, 4-7    该文件中有几个page
        notused index_id       : int, 8-11   索引序号
        : param table_id       : int, 12-15  对应表序号
        : param attr_id        : int, 16-19  对应表属性序号  
        : param attr_type      : int, 20-23  0:int, 1:float, else char(type - 1)
        : param order          : int, 24-27  B+树的阶数  
        : param root           : int, 28-31  root的page_id  
        """
        self.first_free_page = first_free_page
        self.size = size
        self.table_id = table_id
        self.attr_id = attr_id
        self.attr_type = attr_type
        self.order = order
        self.root = root

class IndexPage:
    def __init__(self, next_free_page, is_root, is_leaf, next, size, pointer, key) -> None:
        """
          每个B+树节点单独占用一个page
        : param next_free_page: int, 0-3           若为可用页，设为下一个可用页的位置；若不可用，置为-1
        """
        self.next_free_page = next_free_page
        self.is_root = is_root
        self.is_leaf = is_leaf
        self.next = next
        self.size = size
        self.pointer = pointer
        self.key = key
```

每个节点大小都为一个page，因此我们特化了它的page结构。B+树节点中的child列表存储其子节点，我们只实例化并读取需要访问的子节点，其他的则以占位符None代替，减少单次操作读入节点的数目。

#### **4.6.3 实现细节**

index的维护操作通过调用B+树实现：

```python
class BPTree:
    def __init__():
        pass

    @classmethod
    def insert(cls, order, rootNode, position, value) -> BPTreeNode:
        """
            向该子树中插入值为value/物理位置为position=(rid,pid)的record
            返回split后新增Node, 未split则为None
        """
        
    @classmethod
    def delete(cls, order, rootNode, value) -> int:
        """
        返回删除是否成功的flag
        """

    @classmethod
    def find(cls, rootNode, value):
        """
            在子树中查找值最接近value(>=)的record，便于区间查询
            返回leafNode以及该记录在leafNode.child中的位置
            :return : (BPTreeNode, int)
        """

    @classmethod
    def __split(cls, rootNode):
        """
        	供insert调用，将size大于order的节点分为等大的两个节点
            :return (BPTreeNode, BPTreeNode)
        """

    @classmethod
    def __transfer(cls, srcNode, desNode, op):
        """
        	供delete调用，将desNode中的一个child转移给srcNode
        	它们必须有共同的父节点且相邻，op表示它们的相对位置关系
        """
            
    @classmethod
    def __merge(cls, leftNode, rightNode):
        """
        	供delete调用，合并两个size均不满order/2的两个相邻节点
        	返回值存储在leftNode中，rightNode被销毁
        """
```

插入时遵循如下策略：

+ 在key中二分查找，找到value应当插入的位置；
+ 若当前节点为leaf，则直接插入位置信息；否则，申请对应child节点递归执行，如果child插入结果返回了新节点（child执行了split），将其插入到child后方；
+ 检查当前节点的size，若超过order限制，将该节点分裂，
  + 若当前节点不是root，返回新节点；
  + 若当前节点是root，申请一个空白节点作为新的root，分裂出的两个节点成为他的child。修改header中的root。

删除时遵循如下策略：

+ 在key中二分查找，找到value应当存在的位置；若key都比value小则返回notFound；
+ 若当前节点为leaf，则直接删除位置信息；否则，申请对应child节点递归执行；
+ 返回之后，父节点检查child的size，若不满order的一半，则指定一个相邻的child（称为neighbor）；由于父节点不为leaf，所以size>=2，neighbor一定存在：
  + 若neighbor的size也不满order的一半，则将这两个节点合并；
  + 若neighbor的size超出order的一半，则从中转移孙子节点给child。

可以看出，删除的时间复杂度为$O(logN)$，可以加速对record的枚举。

查找函数的定义比较特殊，它返回大于等于给定value的第一条记录，这是为了方便实现区间查找。

find_single函数需要在调用find之后再判断值是否相等。

find_range函数通过find找到第一条符合要求的记录，再利用叶节点的next指针快速地按序遍历记录。具体实现可以参见源码。

#### **4.6.4 备注**

在测试中我们发现，B+树的效率与order有着密切的关系，order太小会显著增加树的深度，而order太大会令单个节点的读取与修改变得缓慢。我们最初采取与record类似的策略，通过page大小计算可存放child的个数作为order，但在索引单int值时测试表现远不如order较小时。综合考虑之后，我们为order设置了400的上限。

索引有加速查询的作用，但是过多的索引会增加更新的开销——每插入/删除一条记录，都要更新与之相关的所有index文件。因此建立索引是否能加快执行需要做trade off，根据实际情况确定。对于需要大量查询的属性——比如，在声明表中某属性为unique后插入大量数据——我们建议对其进行索引，对于主键建立的默认索引表现就比较良好。

### **4.7 Buffer Manager**

#### **4.7.1. 功能**

+ Buffer Manager负责缓冲区的管理，主要功能有：
  + 根据需要，读取指定的数据到系统缓冲区或将缓冲区中的数据写出到文件
  + 实现缓冲区的替换算法，当缓冲区满时选择合适的页进行替换
  + 记录缓冲区中各页的状态，如是否被修改过等
  + 提供缓冲区页的pin功能，及锁定缓冲区的页，不允许替换出去
+ 在本项目中，考虑到一条记录最大的长度大致为$32*255 = 8160$，**我们使用8kB的页大小与磁盘交互**

#### **4.7.2. 数据结构**

+ 主要的数据结构有`LRU_replacer`, `BufferBlock`, `PageHeader`, `PageData`，定义如下

  ```python
  LRU_replacer = deque()  # 使用一个双向队列进行LRU块的储存
  class BufferBlock:
      def __init__(self, page, file_name, page_id) -> None:
          """
              :param page     : PageData,
              :param pin_count: int,      该block被访问次数
              :param dirty    : bool,     是否被修改过
          """
          self.dirty = False
          self.pin_count = 0
          self.page = page
  
  class PageHeader:
      def __init__(self, first_free_page, size, data) -> None:
          """
              :param first_free_page: int, 0-3  文件中第一个可用页
              :param size           : int, 4-7  文件中当前有几个page
              :param data           : byte[], 8-8191 ,数据
          """
          self.first_free_page = first_free_page
          self.size = size
          self.data = data
  
      def set_first_free_page(self, page_id):
          self.first_free_page = page_id
  
  class PageData:
      def __init__(self, next_free_page, data) -> None:
          self.next_free_page = next_free_page
          self.data = data
  ```

#### **4.7.3. 部分重要的实现细节**

##### **4.7.3.1 页缓冲区**

+ 对于从文件中读取的页，我们使用两个类进行储存：`PageHeader`和`PageData`。前者储存文件头，后者储存文件的具体内容。

+ `BufferBlock`类为缓冲区块的核心数据结构，除了有从文件中读取的页以外，同时添加了pin计数和dirty位
+ 我们一开始使用`list`储存缓冲区区块，但是这样子每次在缓冲区中查找相关区块时间复杂度会比较高。为了进一步提升缓冲区的访问性能，我们使用Python的`dict`类型进行储存，该结构通过对key进行hash，可以将随机访问复杂度降低到常数级别。具体来说，储存的键值对为`(file_name, page_id) :  BufferBlock`。

##### **4.7.3.2 页的替换策略**

+ 我们使用LRU策略进行页替换，具体实现细节如下。
+ 我们建立一个LRU替换列表，这是一个FIFO队列，按照进入的时间先后储存。每当有新的块被读入缓冲区，或是该页被读取，或者pin计数刚减到0，我们就将其`(file_name, page_id)`的key放入队列中；如果该页被pin，那么我们就将其移出LRU列表。

##### **4.7.3.3 文件缓冲区**

+ 考虑到大规模操作时对于文件的频繁读写可能影响性能，我们采用了文件缓冲区的策略。

+ 该缓冲区的具体实现细节基本和页缓冲区相同。我们维护一个`file_buffer_blocks`的字典来储存文件名和打开文件流的对应关系，当相关请求涉及到文件操作时，我们会先在该结构中查询是否有已经打开的文件流。如果已经打开，那么直接返回；如果没有打开，那就通过操作系统交互获取文件流，放到内存中后再返回。

+ 因为Python的文件写入机制包含缓冲区，因此在每次写入操作之后都需要调用`flush`函数清空缓冲区。

+ 由于文件的量较少，LRU机制对于效率提升较小，因此我们采用随机替换策略。

+ 核心函数和简单使用样例如下：

  ```python
  	@classmethod
      def fetch_file_stream(cls, file_name):
          """
              在保证文件已经存在的情况下返回一个文件流
          """
          file_stream = None
          if file_name in cls.file_blocks:			# 如果存在于缓冲区，就直接返回
              return cls.file_blocks[file_name]
          else:										# 如果不存在
              if os.path.exists(os.path.join(utils.DB_FILE_FOLDER, file_name)): # 如果文件存在，直接与系统交互
                  file_stream = open(os.path.join(utils.DB_FILE_FOLDER, file_name), "rb+")
  
              else:															  # 如果没有，创建文件
                  file_stream = open(os.path.join(utils.DB_FILE_FOLDER, file_name), "wb+")
                  file_stream.close()
                  file_stream = open(os.path.join(utils.DB_FILE_FOLDER, file_name), "rb+")
  
              if cls.file_block_len > MAX_BUFFER_BLOCKS:						  # 使用随机替换策略
                  del_id = None
                  for f in cls.file_blocks:
                      file_block = cls.file_blocks[f]
                      file_block.flush()
                      file_block.close()
                      del_id = f
                      break
  
                  cls.file_block_len -= 1
                  del cls.file_blocks[del_id]
  
              cls.file_blocks[file_name] = file_stream
              cls.file_block_len += 1
  
              return file_stream
       
  	@classmethod
      def create_page(cls, file_name) -> PageData:
          """
              在文件全满的时候创建一个新页
              返回PageData类型
              :param file_name : string
              :return PageData
          """
          file_header = cls._read_file_header(file_name)
          page_id = file_header.size + 1
  
          data = bytearray(b"\xff\xff\xff\xff" + b"\x00" * 8188)
          fstream = cls.fetch_file_stream(file_name)
          fstream.seek(PAGE_SIZE*page_id, 0)
          fstream.write(data)
          fstream.flush()
          
          return cls.fetch_page(file_name, page_id)
  ```

### **4.8 DB Files**

MiniSQL运行过程中的记录数据文件，索引文件，meta文件都存储在./src/DBFiles文件夹中。

系统启动之后，DBFiles文件夹中自动建立三个meta.db文件，分别存储元表、元属性、元索引信息。文件存储byte数组，包含一个header文件头和各个表、属性、索引的信息。

![](.\figure\13.png)

系统运行过程中，建立record.db和index.db文件，存储数据信息。

![](.\figure\14.png)

## **5 系统测试**

### **5.1 测试思路**

首先对MiniSQL系统的命令行输入和脚本文件输入基本语法进行测试。

然后使用命令行模式测试错误代码输出。

之后编写代码生成大量测试数据，对MiniSQL系统进行压力测试。

### **5.2 测试内容**

#### **5.2.1 命令行基本语法**

- **创建表**

```sql
# 测试代码
create table student(
    sno char(8) unique,
    sname char(16) unique,
    sage int,
    sgender char(1),
    primary key (sno)
);
```

**预期结果：**打印以下信息

```sql
Successfully create table student
Execute time: <float number>s
```

**执行结果：**

![](.\figure\2.png)

**测试状态：**通过

- **插入记录**

```sql
# 测试代码
insert into student values('12345678','wy',22,'M');
insert into student values('12345679','wz',22,'M');
insert into student values('12345680','ya',23,'M');
insert into student values('12345681','yb',23,'M');
insert into student values('12345682','yc',22,'M');
insert into student values('12345683','yd',22,'F');
insert into student values('12345684','ye',24,'F');
insert into student values('12345685','yf',24,'F');
insert into student values('12345686','yg',22,'F');
insert into student values('12345687','yh',22,'F');
```

**预期结果：**打印以下信息

```sql
1 row(s) affected
Execute time: <float number>s
1 row(s) affected
Execute time: <float number>s
1 row(s) affected
Execute time: <float number>s
1 row(s) affected
Execute time: <float number>s
1 row(s) affected
Execute time: <float number>s
1 row(s) affected
Execute time: <float number>s
1 row(s) affected
Execute time: <float number>s
1 row(s) affected
Execute time: <float number>s
1 row(s) affected
Execute time: <float number>s
1 row(s) affected
Execute time: <float number>s
```

**执行结果：**

<img src=".\figure\3.png" style="zoom:67%;" />

**测试状态：**通过

- **删除记录**

```sql
# 测试代码
delete from student where sno='12345680';
```

**预期结果：**打印以下信息

```sql
1 row(s) affected
Execute time: <float number>s
```

**执行结果：**

![](.\figure\4.png)

**测试状态：**通过

- **创建索引**

```sql
# 测试代码
create index studentidx on student (sname);
```

**预期结果：**打印以下信息

```sql
Successfully create index studentidx on attribute sname
Execute time: <float number>s
```

**执行结果：**

![](.\figure\5.png)

**测试状态：**通过

- **选择**

```sql
# 测试代码
# 选择1
select * from student;
# 选择2
select * from student where sno='12345682';
# 选择3
select * from student where sage=23 and sgender='M';
# 选择4
select * from student where sname='yg';
```

**预期结果：**打印以下信息

```sql
# 选择1
```

| sno      | sname | sage | sgender |
| -------- | ----- | ---- | ------- |
| 12345678 | wy    | 22   | M       |
| 12345679 | wz    | 22   | M       |
| 12345681 | yb    | 23   | M       |
| 12345682 | yc    | 22   | M       |
| 12345683 | yd    | 22   | F       |
| 12345684 | ye    | 24   | F       |
| 12345685 | yf    | 24   | F       |
| 12345686 | yg    | 22   | F       |
| 12345687 | yh    | 22   | F       |

```sql
9 row(s) affected
Execute time: <float number>s
```

```sql
# 选择2
```

| sno      | sname | sage | sgender |
| -------- | ----- | ---- | ------- |
| 12345682 | yc    | 22   | M       |

```sql
1 row(s) affected
Execute time: <float number>s
```

```sql
# 选择3
```

| sno      | sname | sage | sgender |
| -------- | ----- | ---- | ------- |
| 12345681 | yb    | 23   | M       |

```sql
1 row(s) affected
Execute time: <float number>s
```

```sql
# 选择4
```

| sno      | sname | sage | sgender |
| -------- | ----- | ---- | ------- |
| 12345686 | yg    | 22   | F       |

```sql
1 row(s) affected
Execute time: <float number>s
```

**执行结果：**

<img src=".\figure\6.png" style="zoom:67%;" />

**测试状态：**通过

- **删除索引**

```sql
# 测试代码
drop index studentidx;
```

**预期结果：**打印以下信息

```sql
Execute time: <float number>s
```

**执行结果：**

![](.\figure\7.png)

**测试状态：**通过

- **删除表**

```sql
# 测试代码
drop table student;
```

**预期结果：**打印以下信息

```sql
Successfully drop table student
Execute time: <float number>s
```

**执行结果：**

![](.\figure\8.png)

**测试状态：**通过

- **退出系统**

```sql
# 测试代码
quit;
```

**预期结果：**打印以下信息

```sql
Finish executing, bye...
```

**执行结果：**

![](.\figure\9.png)

**测试状态：**通过

#### **5.2.2 脚本文件基本语法**

**测试文件：**

```sql
# ./src/testCode.txt

create table student(
    sno char(8) unique,
    sname char(16) unique,
    sage int,
    sgender char(1),
    primary key (sno)
);
insert into student values('12345678','wy',22,'M');
insert into student values('12345679','wz',22,'M');
insert into student values('12345680','ya',23,'M');
insert into student values('12345681','yb',23,'M');
insert into student values('12345682','yc',22,'M');
insert into student values('12345683','yd',22,'F');
insert into student values('12345684','ye',24,'F');
insert into student values('12345685','yf',24,'F');
insert into student values('12345686','yg',22,'F');
insert into student values('12345687','yh',22,'F');
delete from student where sno='12345680';
create index studentidx on student (sname);
select * from student;
select * from student where sno='12345682';
select * from student where sage=23 and sgender='M';
select * from student where sname='yg';
drop index studentidx;
drop table student;
quit;
```

**测试代码：**

```sql
execfile testCode.txt;
```

**输出结果：**

<img src=".\figure\10.png" style="zoom:67%;" />

<img src=".\figure\11.png" alt="11" style="zoom:85%;" />

**测试状态：**通过

#### **5.2.3 错误处理**

##### **5.2.3.1 定义错误**

- 重复定义表格属性名称

```sql
# 测试代码
create table student(
    sno char(8) unique,
    sname char(16) unique,
    sname int,
    sgender char(1),
    primary key (sno)
);
```

**预期结果：**打印以下信息

```sql
Detect duplicate keys!
Execute time: <float number>s
```

**执行结果：**

<img src=".\figure\15.png" style="zoom:67%;" />

**测试状态：**通过

- char长度超过255或小于1

```sql
# 测试代码
create table student(
    sno char(0) unique,
    sname char(256) unique,
    sage int,
    sgender char(1),
    primary key (sno)
);
```

**预期结果：**打印以下信息

```sql
Invalid char definition!
Execute time: <float number>s
```

**执行结果：**

<img src=".\figure\16.png" style="zoom:80%;" />

**测试状态：**通过

- 未定义主键

```sql
# 测试代码
create table student(
    sno char(8) unique,
    sname char(16) unique,
    sage int,
    sgender char(1)
);
```

**预期结果：**打印以下信息

```sql
No primary key is specified!
Execute time: <float number>s
```

**执行结果：**

<img src=".\figure\17.png" style="zoom:75%;" />

**测试状态：**通过

##### **5.2.3.2 语法错误**

- 不支持的数据类型

```sql
# 测试代码
create table student(
    sno char(8) unique,
    sname char(16) unique,
    sage double,
    sgender char(1),
    primary key(sno)
);
```

**预期结果：**打印以下信息

```sql
Syntax error at LexToken(<token type>,<invalid syntax>,<position>,<position>)
Execute time: <float number>s
```

**执行结果：**

<img src=".\figure\18.png" style="zoom:75%;" />

**测试状态：**通过

- 关键词错误

```sql
# 测试代码
create table student(
    sno char(8) unique,
    sname chararacter(16) unique,
    sage double,
    sgender char(1),
    primary key(sno)
);
```

**预期结果：**打印以下信息

```sql
Syntax error at LexToken(<token type>,<invalid syntax>,<position>,<position>)
Execute time: <float number>s
```

**执行结果：**

<img src=".\figure\19.png" style="zoom:75%;" />

**测试状态：**通过

- 括号不匹配

```sql
# 测试代码
create table student(
    sno char(8) unique,
    sname char(16) unique,
    sage int,
    sgender char(1),
    primary key(sno);
```

**预期结果：**打印以下信息

```sql
Syntax error at LexToken(<token type>,<invalid syntax>,<position>,<position>)
Execute time: <float number>s
```

**执行结果：**

<img src=".\figure\20.png" style="zoom:75%;" />

**测试状态：**通过

##### **5.2.3.3 标识符错误**

- 对不存在的表进行操作

```sql
# 测试代码
create table student(
    sno char(8) unique,
    sname char(16) unique,
    sage int,
    sgender char(1),
    primary key (sno)
);
insert into student2 values('12345678','wy',22,'M');
```

**预期结果：**打印以下信息

```sql
Table not found!
Execute time: <float number>s
```

**执行结果：**

<img src=".\figure\21.png" style="zoom:75%;" />

**测试状态：**通过

- 对不存在的索引进行i操作

```sql
# 测试代码
create index studentidx on student (sname);
drop index studentidx2;
```

**预期结果：**打印以下信息

```sql
Index does not exist!
Execute time: <float number>s
```

**执行结果：**

<img src=".\figure\22.png" style="zoom:75%;" />

**测试状态：**通过

- 对不存在的属性进行操作

```sql
# 测试代码
create table student(
    sno char(8) unique,
    sname char(16) unique,
    sage int,
    sgender char(1),
    primary key (sno)
);
insert into student values('12345678','wy',22,'M');
insert into student values('12345679','wz',22,'M');
insert into student values('12345680','ya',23,'M');
delete from student where sgrade='senior';
```

**预期结果：**打印以下信息

```sql
Attribute <non-existing attribute name> does not exist!
Execute time: 0.00s
```

**执行结果：**

<img src=".\figure\23.png" style="zoom:75%;" />

**测试状态：**通过

##### **5.2.3.4 值错误**

- 插入参数和表头属性定义不匹配

```sql
# 测试代码
create table student(
    sno char(8) unique,
    sname char(16) unique,
    sage int,
    sgender char(1),
    primary key (sno)
);
insert into student values('wy',22,'12345678','M');
```

**预期结果：**打印以下信息

```sql
Please use '' to specify a string
Execute time: <float number>s
```

**执行结果：**

<img src=".\figure\24.png" style="zoom:75%;" />

**测试状态：**通过

##### **5.2.3.5 索引建立在非unique属性上**

```sql
# 测试代码
create table student(
    sno char(8) unique,
    sname char(16) unique,
    sage int,
    sgender char(1),
    primary key (sno)
);
create index studentGender on student(sgender);
```

**预期结果：**打印以下信息

```sql
Attribute should be unique!
Execute time: <float number>s
```

**执行结果：**

<img src=".\figure\25.png" style="zoom:75%;" />

**测试状态：**通过

#### **5.2.4 压力测试**

##### **5.2.4.1 插入10,000条记录**

**测试文件：**

./src/pressureTest/insertion.txt

该文件创建了一个表，并向该表内插入了10,000条记录

```sql
# 测试代码
execfile ./pressureTest/insertion.txt;
```

**执行结果：**

由于输出较多，因此只展示最终结果如下图所示

<img src=".\figure\26.png" style="zoom:75%;" />

<img src=".\figure\27.png" style="zoom:75%;" />

index0.db是对主键建立的索引文件

**测试状态：**通过

##### **5.2.4.2 选择10,000条记录**

**测试文件：**

./src/pressureTest/selection.txt

该文件创建了一个表，并向该表内插入了10,000条记录

```sql
# 测试代码
execfile ./pressureTest/selection.txt;
```

**执行结果：**

由于输出较多，因此只展示最终结果如下图所示

<img src=".\figure\28.png" style="zoom:75%;" />

<img src=".\figure\29.png" style="zoom:75%;" />

index0.db是对主键建立的索引文件

**测试状态：**通过

##### **5.2.4.3 删除10,000条记录**

**测试文件：**

./src/pressureTest/deletion.txt

该文件创建了一个表，并向该表内插入了10,000条记录

```sql
# 测试代码
execfile ./pressureTest/deletion.txt;
```

**执行结果：**

由于输出较多，因此只展示最终结果如下图所示

<img src=".\figure\30.png" style="zoom:75%;" />

**测试状态：**通过