# Managers

Record Manager、Index Manager与Catalog Manager处于数据库整体架构的中间部分——它们通过Buffer Manager完成与文件的IO交互， 在内部处理数据，并向API层开放相应的接口。数据库的主要功能在这一层次实现。

## 文件数据组织

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

## Record Manager

### 基本功能

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

### 数据结构

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

### 实现细节

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

## Catalog Manager

### 基本功能

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

### 数据结构

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

### 实现细节

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

## Index Manager

### 基本功能

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

### 数据结构

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

### 实现细节

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

### 备注

在测试中我们发现，B+树的效率与order有着密切的关系，order太小会显著增加树的深度，而order太大会令单个节点的读取与修改变得缓慢。我们最初采取与record类似的策略，通过page大小计算可存放child的个数作为order，但在索引单int值时测试表现远不如order较小时。综合考虑之后，我们为order设置了400的上限。

索引有加速查询的作用，但是过多的索引会增加更新的开销——每插入/删除一条记录，都要更新与之相关的所有index文件。因此建立索引是否能加快执行需要做trade off，根据实际情况确定。对于需要大量查询的属性——比如，在声明表中某属性为unique后插入大量数据——我们建议对其进行索引，对于主键建立的默认索引表现就比较良好。

