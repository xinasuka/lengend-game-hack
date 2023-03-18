
import sys

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


if __name__ == '__main__':
    # print(encodings.aliases.aliases)

    chr = "小蝦米"
    #big5_string = utf8_string.encode('big5')
    #print(big5_string)
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

