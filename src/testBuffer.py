import os
from utils import utils
from BufferManager.bufferDS import PageData, PageHeader
from BufferManager.BufferManager import BufferManager
FILENAME = "test_1.db"
def create_file():
    
    page_data = []

    if os.path.exists(FILENAME):
        return 
    
    FILE_PAGE = 160

    for i in range(FILE_PAGE):
        page_data.append(utils.int_to_byte(i) + bytearray(b'\00' * 8188))
        print("First 12 bytes of Page data {} is {}".format(i, page_data[i][0:11]))
    
    page_header = utils.int_to_byte(1) + utils.int_to_byte(FILE_PAGE) + bytearray(b'\x01'*8184)
    with open(FILENAME, "wb") as f:
        f.write(page_header)
        for i in range(FILE_PAGE):
            f.write(page_data[i])

def test_buffer():
    create_file()

    bm = BufferManager()
    # print(len(bm.buffer_blocks))
    print(len(BufferManager.buffer_blocks))

    pageheader = BufferManager._read_file_header(FILENAME)
    print(pageheader.size)

    for i in range(pageheader.size):
        pagedata = BufferManager.fetch_page(FILENAME, i+1)
        if i+1 <= 80:
            BufferManager.pin(FILENAME, i+1)

        print("page no.{}, next_free_page: {}".format(i+1, pagedata.next_free_page))
        print("current buffer blocks: {}".format(len(bm.buffer_blocks)))
        print("total buffer blocks used: {}, replacer length: {}".format(len(BufferManager.buffer_blocks), BufferManager.replacer_len))

    for i in range(pageheader.size):
        # block = BufferManager._search_buffer_block(FILENAME, i+1)
        # page_data = block.page
        page = bytearray(b'\xff' * 8184)
        new_page_data = PageData(4, page)
        BufferManager.set_page(FILENAME, i+1, new_page_data)
        
    BufferManager.flush_buffer()
    for i in range(pageheader.size):
        block = BufferManager._search_buffer_block(FILENAME, i+1)
        if block is not None:
            print("block id: {}, page_data: {}".format(i+1, block.page.data[0:12]))
    
    BufferManager.remove_file(FILENAME)
    print(len(BufferManager.buffer_blocks))

"""
    已测试：
        fetch_page
        pin
        kick_out_victim_LRU
        remove_file
        set_page
        _search_buffer_block
        _read_file_header
        write_back_to_file
"""
        
    

test_buffer()