from utils import utils
from IndexMananger.BPTree import BPTreeNode
from BufferManager.BufferManager import BufferManager
from BufferManager.bufferDS import PageHeader, PageData

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
        : param root           : int, 28-31  root的pid  
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
        : param is_root       : bool, 4
        : param is_leaf       : bool, 5
        : param next          : int, 6-9           索引序后一个节点pid(非叶节点置0)
        : param size          : int, 10-13         当前pointer数目
        : param pointer       : int, 14-13+8*size  以元组[record_id, page_id]存储(非叶节点record_id置0)
        : param key           : int                存储各child的分界值
        """
        self.next_free_page = next_free_page
        self.is_root = is_root
        self.is_leaf = is_leaf
        self.next = next
        self.size = size
        self.pointer = pointer
        self.key = key

headerMap ={} # index_id:IndexHeader
pageMap = {} # (index_id, page_id):IndexPage

def get_header_from_file(index_id) -> IndexHeader:
    pageHeader = BufferManager.get_header("index" + index_id + ".db")
    table_id = utils.byte_to_int(pageHeader.data[4:8])
    attr_id = utils.byte_to_int(pageHeader.data[8:12])
    attr_type = utils.byte_to_int(pageHeader.data[12:16])
    order = utils.byte_to_int(pageHeader.data[16:20])
    root = utils.byte_to_int(pageHeader.data[20:24])
    headerMap[index_id] = IndexHeader(pageHeader.first_free_page, pageHeader.size, index_id, table_id, attr_id, attr_type, order, root)
    return headerMap[index_id]

def get_page_from_file(index_id, page_id) -> IndexPage:
    pageData = BufferManager.fetch_page("index" + index_id + ".db", page_id)
    isRoot = utils.byte_to_bool(pageData.data[0])
    isLeaf = utils.byte_to_bool(pageData.data[1])
    nxt = utils.byte_to_int(pageData.data[2:6])
    size = utils.byte_to_int(pageData.data[6:10])
    pointer = []
    for i in range(size):
        st = 10 + i * 8
        pointer.append((utils.byte_to_int(pageData.data[st:st + 4]), utils.byte_to_int(pageData.data[st+4:st+8])))
    header = headerMap.get(index_id)
    if header == None:
        header = get_header_from_file(index_id)
    key = []
    st = 10 + size * 8
    for i in range(size):
        if header.attr_type == 0:
            key.append(utils.byte_to_int(pageData.data[st:st + 4]))
            st += 4
        elif header.attr_type == 1:
            key.append(utils.byte_to_float(pageData.data[st:st + 4]))
            st += 4
        else:
            key.append(utils.byte_to_str(pageData.data[st: st + header.attr_type - 1]))
            st += header.attr_type - 1
    pageMap[(index_id, page_id)] = IndexPage(pageData.next_free_page, isRoot, isLeaf, nxt, size, pointer, key)
    return pageMap[(index_id, page_id)]

def write_header(index_id, header):
    data = b''
    data += utils.int_to_byte(index_id)
    data += utils.int_to_byte(header.table_id)
    data += utils.int_to_byte(header.attr_id)
    data += utils.int_to_byte(header.attr_type)
    data += utils.int_to_byte(header.order)
    data += utils.int_to_byte(header.root)
    BufferManager.set_header(file_name, PageHeader(header.first_free_page, header.size, data))

def write_page(index_id, page_id, page):
    data = b''
    data += utils.bool_to_byte(page.is_root)
    data += utils.bool_to_byte(page.is_leaf)
    data += utils.int_to_byte(page.next)
    data += utils.int_to_byte(page.size)
    for i in range(page.size):
        data += utils.int_to_byte(page.pointer[i][0])
        data += utils.int_to_byte(page.pointer[i][1])
    header = headerMap.get(index_id)
    if header == None:
        header = get_header_from_file(index_id)
    for i in range(page.size):
        if header.attr_type == 0:
            data += utils.int_to_byte(page.key[i])
        elif header.attr_type == 1:
            data += utils.float_to_byte(page.key[i])
        else:
            data += utils.str_to_byte(page.key[i])
    BufferManager.set_page("index" + index_id + ".db", page_id, PageData(page.next_free_page, data))

def get_node(index_id, page_id) -> BPTreeNode:
    if page_id == -1:
        return None
    page = pageMap.get((index_id, page_id))
    if page == None:
        page = get_page_from_file(index_id, page_id)
    return BPTreeNode(index_id, page_id, page.is_root, page.is_leaf, page.next, page.size, page.pointer, page.key)

def get_new_page_id(index_id) -> int:
    header = headerMap.get(index_id)
    if header == None:
        header = get_header_from_file(index_id)
    if header.first_free_page == -1:
        BufferManager.create_page("index" + index_id + ".db")
        return header.size + 1
    page = pageMap.get((index_id, header.first_free_page))
    if page == None:
        page = get_page_from_file((index_id, header.first_free_page))
    ret = header.first_free_page
    header.first_free_page = page.next_free_page
    page.next_free_page = -1
    write_header(index_id, header)
    write_page(index_id, ret, page)
    return ret

def update_page(node) -> None:
    page = pageMap.get((node.index_id, node.page_id))
    if page == None:
        page = get_page_from_file(node.index_id, node.page_id)
    page.is_root = node.is_root
    page.is_leaf = node.is_leaf
    page.next = node.next
    page.size = node.size
    page.pointer = node.pointer
    page.key = node.key
    pageMap[(node.index_id, node.page_id)] = page
    write_page(node.index_id, node.page_id, page)

def free_page(node) -> None:
    page = pageMap.get((node.index_id, node.page_id))
    if page == None:
        page = get_page_from_file(node.index_id, node.page_id)
    header = headerMap.get(node.index_id)
    if header == None:
        header = get_header_from_file(node.index_id)
    page.next_free_page = header.first_free_page
    header.first_free_page = node.page_id
    write_page(node.index_id, node.page_id, page)
    write_header(node.index_id, header)

def update_header(index_id, val, op):
    header = headerMap.get(index_id)
    if header == None:
        header = get_header_from_file(index_id)
    if op == 0:
        header.size += val
    else:
        header.root = val
    headerMap[index_id] = header
    write_header(index_id, header)