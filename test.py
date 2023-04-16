
import sys
import json
import binascii
import encodings
import zhconv
from tkinter import *
from tkinter import ttk

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

def test_json_file2():
    with open("data_local.json", "r") as f:
        game_data = json.load(f)
        print(game_data["battle_events"])
        battle_events = game_data["battle_events"]

    # clear file
    with open("t.dat", 'w') as output:
        output.close()

    for battle in battle_events:
        title = battle["title"]
        description = battle["description"]
        check = battle["check"]
        overlays = battle["overlays"]
        print("title %s\ndesc %s" %(title, description))

        for overlay in overlays:
            for key, val in overlay.items():
                val = val.replace(" ","").replace("\n","")
                print("\toverlay: %s: %s" %(key, val))

                byte_data = binascii.unhexlify(val)
                print("bytes: %s" % byte_data)
                with open("t.dat", 'ab+') as output:
                    output.write(byte_data)

        print("\tcheck: %s: %s" %(check["pos"], check["val"]))
'''

'''
def test_byte_convert():
    n = 10
    b = bytearray(n)
    b[:] = [0x20] * n
    print(b)

def test_table():

    ws = Tk()
    ws.title('PythonGuides')
    ws.geometry('500x500')
    ws['bg'] = '#AC99F2'

    game_frame = Frame(ws)
    game_frame.pack()

    my_game = ttk.Treeview(game_frame)
    my_game['columns'] = ('player_id', 'player_name', 'player_Rank', 'player_states', 'player_city')

    my_game.column("#0", width=0, stretch=NO)
    my_game.column("player_id", anchor=CENTER, width=80)
    my_game.column("player_name", anchor=CENTER, width=80)
    my_game.column("player_Rank", anchor=CENTER, width=80)
    my_game.column("player_states", anchor=CENTER, width=80)
    my_game.column("player_city", anchor=CENTER, width=80)

    my_game.heading("#0", text="", anchor=CENTER)
    my_game.heading("player_id", text="Id", anchor=CENTER)
    my_game.heading("player_name", text="Name", anchor=CENTER)
    my_game.heading("player_Rank", text="Rank", anchor=CENTER)
    my_game.heading("player_states", text="States", anchor=CENTER)
    my_game.heading("player_city", text="States", anchor=CENTER)

    my_game.insert(parent='', index='end', iid=0, text='', values=('1', 'Ninja', '101', 'Oklahoma', 'Moore'))
    my_game.insert(parent='', index='end', iid=1, text='', values=('2', 'Ranger', '102', 'Wisconsin', 'Green Bay'))
    my_game.insert(parent='', index='end', iid=2, text='', values=('3', 'Deamon', '103', 'California', 'Placentia'))
    my_game.insert(parent='', index='end', iid=3, text='', values=('4', 'Dragon', '104', 'New York', 'White Plains'))
    my_game.insert(parent='', index='end', iid=4, text='', values=('5', 'CrissCross', '105', 'California', 'San Diego'))
    my_game.insert(parent='', index='end', iid=5, text='', values=('6', 'ZaqueriBlack', '106', 'Wisconsin ', 'TONY'))

    my_game.pack()

    ws.mainloop()

def test_tkinter_list():
    root = Tk()
    root.title('Listbox')

    langs = ('Java', 'C#', 'C', 'C++', 'Python', 'Go', 'JavaScript', 'PHP', 'Swift')

    var = Variable(value=langs)

    listbox = Listbox(root, listvariable=var, height=6, selectmode=EXTENDED)
    listbox.pack(expand=True, fill=BOTH)

    root.mainloop()

def test_tkinter_checkbox():
    root = Tk()

    on_image = PhotoImage(width=36, height=18)
    off_image = PhotoImage(width=36, height=18)
    on_image.put(("green",), to=(1, 1, 17, 17))
    off_image.put(("red",), to=(18, 1, 35, 17))

    var1 = IntVar(value=1)
    var2 = IntVar(value=0)
    cb1 = Checkbutton(root, image=off_image, selectimage=on_image, indicatoron=False,
                         onvalue=1, offvalue=0, variable=var1)
    cb2 = Checkbutton(root, image=off_image, selectimage=on_image, indicatoron=False,
                         onvalue=1, offvalue=0, variable=var2)

    cb1.pack(padx=20, pady=10)
    cb2.pack(padx=20, pady=10)

    root.mainloop()

def test_decode():
    # initializing string
    str = "正是妖仙寻隐处"
    strb = "正是妖仙尋隱處"

    # encoding string
    str_enc = str.encode(encoding='utf-8')

    # printing the encoded string
    print("The encoded string in base64 format is : ", )
    print(str_enc)

    # printing the original decoded string
    print("The decoded string is : ", )
    print(str_enc.decode('big5', 'strict'))

def test_decode2():
    utf8_str = "正是妖仙寻隐处"
    print(zhconv.convert(utf8_str, 'zh-tw'))


if __name__ == '__main__':
    #test_json_file2()
    #test_tkinter_checkbox()
    test_decode2()

