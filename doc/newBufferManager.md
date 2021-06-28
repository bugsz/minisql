## BufferManager

### 1. 功能

+ Buffer Manager负责缓冲区的管理，主要功能有：
  + 根据需要，读取指定的数据到系统缓冲区或将缓冲区中的数据写出到文件
  + 实现缓冲区的替换算法，当缓冲区满时选择合适的页进行替换
  + 记录缓冲区中各页的状态，如是否被修改过等
  + 提供缓冲区页的pin功能，及锁定缓冲区的页，不允许替换出去
+ 在本项目中，考虑到一条记录最大的长度大致为$32*255 = 8160$，**我们使用8kB的页大小与磁盘交互**

### 2. 数据结构

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


### 3. 部分重要的实现细节

#### 3.1 页缓冲区

+ 对于从文件中读取的页，我们使用两个类进行储存：`PageHeader`和`PageData`。前者储存文件头，后者储存文件的具体内容。

+ `BufferBlock`类为缓冲区块的核心数据结构，除了有从文件中读取的页以外，同时添加了pin计数和dirty位
+ 我们一开始使用`list`储存缓冲区区块，但是这样子每次在缓冲区中查找相关区块时间复杂度会比较高。为了进一步提升缓冲区的访问性能，我们使用Python的`dict`类型进行储存，该结构通过对key进行hash，可以将随机访问复杂度降低到常数级别。具体来说，储存的键值对为`(file_name, page_id) :  BufferBlock`。

#### 3.2 页的替换策略

+ 我们使用LRU策略进行页替换，具体实现细节如下。
+ 我们建立一个LRU替换列表，这是一个FIFO队列，按照进入的时间先后储存。每当有新的块被读入缓冲区，或是该页被读取，或者pin计数刚减到0，我们就将其`(file_name, page_id)`的key放入队列中；如果该页被pin，那么我们就将其移出LRU列表。

#### 3.3 文件缓冲区

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





