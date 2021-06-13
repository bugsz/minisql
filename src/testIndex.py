from IndexManager.IndexManager import IndexManager as IM
import os

with open("index1.db", "wb") as f:
    f.write(int(-1).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(1).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(1).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(1).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(1).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(0).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(3).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(1).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(b'\x00' * 8160)
    f.write(int(-1).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(bool(True).to_bytes(length = 1, byteorder = 'big', signed=True))
    f.write(bool(True).to_bytes(length = 1, byteorder = 'big', signed=True))
    f.write(int(-1).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(0).to_bytes(length = 4, byteorder = 'big', signed=True))

IM.insert(1, (1, 1), 1)
IM.insert(1, (2, 2), 2)
IM.insert(1, (3, 3), 3)
IM.insert(1, (4, 4), 4)

print(IM.find_single(1, 5))
print(IM.find_single(1, 3))
print(IM.find_range(1, 2, 2))
print(IM.find_range(1, -100, 100))

print(IM.delete(1, 2))
print(IM.delete(1, 2))
print(IM.find_range(1, 2, 2))