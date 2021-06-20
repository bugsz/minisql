
from sys import getsizeof
from struct import pack, unpack

PAGE_SIZE = 8192
DB_FILE_FOLDER = "DBFiles"

class ACTIONTYPE:
    INSERT = 1
    CREATE_TABLE = 2
    CREATE_INDEX = 3
    DROP_TABLE = 4
    DROP_INDEX = 5
    SELECT_STAR = 6
    DELETE = 7

class COMPARATOR:
    EQUAL = 1  # =
    NONEQUAL = 2  # !=
    GREATER_EQUAL = 3  # >=
    LESS_EQUAL = 4  # <=
    GREATER = 5
    LESS = 6

class CONDITION:
    comparator_mapping = {
        "=" : COMPARATOR.EQUAL,
        "<>": COMPARATOR.NONEQUAL,
        ">=": COMPARATOR.GREATER_EQUAL,
        "<=": COMPARATOR.LESS_EQUAL,
        ">" : COMPARATOR.GREATER,
        "<" : COMPARATOR.LESS
    }
    def __init__(self, lvalue, comparator, rvalue):
        self.lvalue = lvalue
        self.rvalue = rvalue
        self.comparator = self.comparator_mapping[comparator]

    def tuple(self):
        return (self.lvalue, self.comparator, self.rvalue)

    def __eq__(self, that) -> bool:
        if isinstance(that, self.__class__):
            return self.tuple() == that.tuple()
        raise NotImplementedError


    @classmethod 
    def valid(cls, input):
        return input in cls.comparator_mapping.keys()

class VALUETYPE:
    INT = 1
    CHAR = 2
    FLOAT = 3


def str_to_byte(str):
    return str.encode("ascii")

def byte_to_str(byte):
    return byte.decode("ascii")

def int_to_byte(integer):
    if integer is None:
        integer = 0
    return int(integer).to_bytes(length=4, byteorder="big", signed=True)

def byte_to_int(byte):
    i = int().from_bytes(byte, byteorder="big", signed=True)
    return i

def bool_to_byte(bool):
    return int(bool).to_bytes(length=1, byteorder="big", signed=True)

def byte_to_bool(byte):
    return int().from_bytes(byte, byteorder="big", signed=True)

def float_to_byte(float):
    return pack("f", float)

def byte_to_float(byte):
    return unpack("f", byte)[0]



if __name__ == "__main__":
    import sys
    a = "'2'"
    b = str_to_byte(a)
    c = byte_to_str(b)
    print(a, b, c)
