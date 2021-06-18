from IndexManager.IndexManager import IndexManager as IM
import os

with open("index1.db", "rb") as f:
    f.write(int(-1).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(0).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(1).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(1).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(1).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(0).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(3).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(1).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(-1).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(bool(True).to_bytes(length = 1, byteorder = 'big', signed=True))
    f.write(bool(True).to_bytes(length = 1, byteorder = 'big', signed=True))
    f.write(int(-1).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.write(int(0).to_bytes(length = 4, byteorder = 'big', signed=True))
    f.close()

IM.insert(1, (1,1), 1)
IM.insert(1, (2,2), 2)
IM.insert(1, (3,3), 3)
IM.insert(1, (4,4), 4)
IM.insert(1, (5,5), 5)
IM.insert(1, (6,6), 6)
IM.insert(1, (7,7), 7)
IM.insert(1, (8,8), 8)
IM.insert(1, (9,9), 9)
IM.insert(1, (10,10), 10)
IM.delete(1, 1)
IM.delete(1, 2)
IM.delete(1, 3)
IM.delete(1, 4)
IM.delete(1, 5)
IM.delete(1, 6)
IM.delete(1, 7)
IM.delete(1, 8)
IM.delete(1, 9)
IM.delete(1, 10)
IM.insert(1, (11,11), 11)
IM.insert(1, (12,12), 12)
IM.insert(1, (13,13), 13)
IM.insert(1, (14,14), 14)
IM.insert(1, (15,15), 15)
IM.insert(1, (16,16), 16)
IM.insert(1, (17,17), 17)
IM.insert(1, (18,18), 18)
IM.insert(1, (19,19), 19)
IM.insert(1, (20,20), 20)
IM.delete(1, 11)
IM.delete(1, 12)
IM.delete(1, 13)
IM.delete(1, 14)
IM.delete(1, 15)
IM.delete(1, 16)
IM.delete(1, 17)
IM.delete(1, 18)
IM.delete(1, 19)
IM.delete(1, 20)
IM.insert(1, (21,21), 21)
IM.insert(1, (22,22), 22)
IM.insert(1, (23,23), 23)
IM.insert(1, (24,24), 24)
IM.insert(1, (25,25), 25)
IM.insert(1, (26,26), 26)
IM.insert(1, (27,27), 27)
IM.insert(1, (28,28), 28)
IM.insert(1, (29,29), 29)
IM.insert(1, (30,30), 30)
IM.delete(1, 21)
IM.delete(1, 22)
IM.delete(1, 23)
IM.delete(1, 24)
IM.delete(1, 25)
IM.delete(1, 26)
IM.delete(1, 27)
IM.delete(1, 28)
IM.delete(1, 29)
IM.delete(1, 30)
IM.insert(1, (31,31), 31)
IM.insert(1, (32,32), 32)
IM.insert(1, (33,33), 33)
IM.insert(1, (34,34), 34)
IM.insert(1, (35,35), 35)
IM.insert(1, (36,36), 36)
IM.insert(1, (37,37), 37)
IM.insert(1, (38,38), 38)
IM.insert(1, (39,39), 39)
IM.insert(1, (40,40), 40)
IM.delete(1, 31)
IM.delete(1, 32)
IM.delete(1, 33)
IM.delete(1, 34)
IM.delete(1, 35)
IM.delete(1, 36)
IM.delete(1, 37)
IM.delete(1, 38)
IM.delete(1, 39)
IM.delete(1, 40)
IM.insert(1, (41,41), 41)
IM.insert(1, (42,42), 42)
IM.insert(1, (43,43), 43)
IM.insert(1, (44,44), 44)
IM.insert(1, (45,45), 45)
IM.insert(1, (46,46), 46)
IM.insert(1, (47,47), 47)
IM.insert(1, (48,48), 48)
IM.insert(1, (49,49), 49)
IM.insert(1, (50,50), 50)
IM.delete(1, 41)
IM.delete(1, 42)
IM.delete(1, 43)
IM.delete(1, 44)
IM.delete(1, 45)
IM.delete(1, 46)
IM.delete(1, 47)
IM.delete(1, 48)
IM.delete(1, 49)
IM.delete(1, 50)
IM.insert(1, (51,51), 51)
IM.insert(1, (52,52), 52)
IM.insert(1, (53,53), 53)
IM.insert(1, (54,54), 54)
IM.insert(1, (55,55), 55)
IM.insert(1, (56,56), 56)
IM.insert(1, (57,57), 57)
IM.insert(1, (58,58), 58)
IM.insert(1, (59,59), 59)
IM.insert(1, (60,60), 60)
IM.delete(1, 51)
IM.delete(1, 52)
IM.delete(1, 53)
IM.delete(1, 54)
IM.delete(1, 55)
IM.delete(1, 56)
IM.delete(1, 57)
IM.delete(1, 58)
IM.delete(1, 59)
IM.delete(1, 60)
IM.insert(1, (61,61), 61)
IM.insert(1, (62,62), 62)
IM.insert(1, (63,63), 63)
IM.insert(1, (64,64), 64)
IM.insert(1, (65,65), 65)
IM.insert(1, (66,66), 66)
IM.insert(1, (67,67), 67)
IM.insert(1, (68,68), 68)
IM.insert(1, (69,69), 69)
IM.insert(1, (70,70), 70)
IM.delete(1, 61)
IM.delete(1, 62)
IM.delete(1, 63)
IM.delete(1, 64)
IM.delete(1, 65)
IM.delete(1, 66)
IM.delete(1, 67)
IM.delete(1, 68)
IM.delete(1, 69)
IM.delete(1, 70)
IM.insert(1, (71,71), 71)
IM.insert(1, (72,72), 72)
IM.insert(1, (73,73), 73)
IM.insert(1, (74,74), 74)
IM.insert(1, (75,75), 75)
IM.insert(1, (76,76), 76)
IM.insert(1, (77,77), 77)
IM.insert(1, (78,78), 78)
IM.insert(1, (79,79), 79)
IM.insert(1, (80,80), 80)
IM.delete(1, 71)
IM.delete(1, 72)
IM.delete(1, 73)
IM.delete(1, 74)
IM.delete(1, 75)
IM.delete(1, 76)
IM.delete(1, 77)
IM.delete(1, 78)
IM.delete(1, 79)
IM.delete(1, 80)
IM.insert(1, (81,81), 81)
IM.insert(1, (82,82), 82)
IM.insert(1, (83,83), 83)
IM.insert(1, (84,84), 84)
IM.insert(1, (85,85), 85)
IM.insert(1, (86,86), 86)
IM.insert(1, (87,87), 87)
IM.insert(1, (88,88), 88)
IM.insert(1, (89,89), 89)
IM.insert(1, (90,90), 90)
IM.delete(1, 81)
IM.delete(1, 82)
IM.delete(1, 83)
IM.delete(1, 84)
IM.delete(1, 85)
IM.delete(1, 86)
IM.delete(1, 87)
IM.delete(1, 88)
IM.delete(1, 89)
IM.delete(1, 90)
IM.insert(1, (91,91), 91)
IM.insert(1, (92,92), 92)
IM.insert(1, (93,93), 93)
IM.insert(1, (94,94), 94)
IM.insert(1, (95,95), 95)
IM.insert(1, (96,96), 96)
IM.insert(1, (97,97), 97)
IM.insert(1, (98,98), 98)
IM.insert(1, (99,99), 99)
IM.insert(1, (100,100), 100)
IM.delete(1, 91)
IM.delete(1, 92)
IM.delete(1, 93)
IM.delete(1, 94)
IM.delete(1, 95)
IM.delete(1, 96)
IM.delete(1, 97)
IM.delete(1, 98)
IM.delete(1, 99)
IM.delete(1, 100)
