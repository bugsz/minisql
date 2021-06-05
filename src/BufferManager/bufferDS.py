class BufferBlock:
    def __init__(self, page_data, file_name, page_id) -> None:
        """
            :param page_data: 一页的数据
            :param pin_count: 该block被访问次数
            :param dirty    : 是否被修改过
        """
        # TODO: 应该用什么初始化
        self.dirty = False
        self.pin_count = 0
        self.file_name = file_name
        self.page_id = page_id
        self.data = page_data

