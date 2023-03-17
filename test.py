
import sys

import encodings



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
