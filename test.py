
import sys
import json

import encodings
from tkinter import *
def remove_trailing_zeros(byte_array):
    """
    Removes trailing zeros from a byte array.

    :param byte_array: The byte array to remove trailing zeros from.
    :type byte_array: bytes
    :return: The byte array without trailing zeros.
    :rtype: bytes
    """
    i = len(byte_array) - 1
    while i >= 0 and byte_array[i] == 0:
        i -= 1
    return byte_array[:i + 1]

def test_big5():
    # print(encodings.aliases.aliases)

    chr = "小蝦米"
    # big5_string = utf8_string.encode('big5')
    # print(big5_string)
    print(b"\xa4p".decode("big5"))

    with open("t.dat", 'w+b') as f:
        f.write(chr.encode("big5_tw"))

    big5_string = b'\xa7A\xa6n\xabH\xac\xdc\xbc\xd0\xa5\xba\xbd\xf4'
    decoded_string = big5_string.decode('big5')
    print(decoded_string)

    # string to truncate
    s = '一二三四'

    # encode the string to bytes
    b = s.encode('utf-8')
    print(b)

    # slice the bytes object to truncate
    truncated_b = b[:6]
    print(truncated_b)

    # decode the bytes object back to string
    truncated_s = truncated_b.decode('utf-8')
    print(truncated_s)

    byte_array = b'\x01\x02\x03\x00\x00\x00'
    new_byte_array = remove_trailing_zeros(byte_array)
    print(new_byte_array)  # b'\x01\x02\x03'

def test_json_file():
    with open("data_local.json", "r") as f:
        game_data = json.load(f)
        print(game_data["map_positions"])
        map_positions = game_data["map_positions"]
        for key, val in map_positions.items():
            #print("%s -> %s" %(key, val))
            inner_lambda = lambda x: int(x, 16) if not isinstance(x, int) else x
            x, y = map(inner_lambda, val.strip("()").split(","))
            print("%s: %d %d" %(key, x, y))
            map_positions[key] = (x, y)

    with open("test.json", "w") as f:
        # prevent json from transforming chars to unicode
        json.dump(game_data, f, ensure_ascii=True)

if __name__ == '__main__':
    n = 10
    b = bytearray(n)
    b[:] = [0x20] * n
    print(b)

