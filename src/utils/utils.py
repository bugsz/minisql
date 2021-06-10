
from sys import getsizeof
from struct import pack, unpack

PAGE_SIZE = 8192
DB_BASE_FOLDER = ""




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
    return unpack("f", byte)



if __name__ == "__main__":
    import sys
    a = "123"
    b = str_to_byte(a)
    print(b, getsizeof(b))
    d = str_to_byte("1234")
    print(d, getsizeof(d))
    c = byte_to_str(b)
    print(c, sys.getsizeof(c))

    e = 1.414
    f = float_to_byte(e)
    g = byte_to_float(f)
    print(e, f, g)