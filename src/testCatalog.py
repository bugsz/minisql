from CatalogManager.CatalogManager import CatalogManager as CM
from BufferManager.BufferManager import BufferManager as BM
from utils import utils

CM.initialize()
CM.create_table("FK", 2, 0, [("a", utils.VALUETYPE.INT, 4, True), ("b", utils.VALUETYPE.CHAR, 2, False)])
CM.create_index("off", "FK", "a")
print(CM.get_table_id("FK"))
print(CM.get_index_id("off"))
print(CM.table_exist("sadsadas"))
print(CM.attr_exist("FK", "b"))
print(CM.attr_unique("FK", "a"))
print(CM.get_attrs_type("FK"))
print(CM.find_indexes("FK"))
print(CM.get_attr_id(0, "b"))
BM.force_clear_buffer()