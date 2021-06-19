from RecordManager.RecordManager import RecordManager as RM
from CatalogManager.CatalogManager import CatalogManager as CM
from BufferManager.BufferManager import BufferManager as BM
from utils import utils

CM.initialize()
CM.create_table("FK", 2, 0, [("a", utils.VALUETYPE.INT, 4, True), ("b", utils.VALUETYPE.CHAR, 2, False)])
RM.insert(0, [1, "1"])
RM.insert(0, [2, "2"])
RM.insert(0, [3, "3"])
RM.insert(0, [4, "4"])
print(RM.insert(0, [11, "11"]))
print(RM.select(0, [utils.CONDITION(0, "=", 2)]))
print(RM.select(0, [utils.CONDITION(1, ">=", "1")]))
print(RM.delete(0, [utils.CONDITION(0, ">", 3)]))
print(RM.delete(0, [utils.CONDITION(0, ">", 3)]))
BM.force_clear_buffer()