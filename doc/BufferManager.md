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
          self.file_name = file_name
          self.page_id = page_id
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

  



