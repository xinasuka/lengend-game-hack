import lang
import os.path
import json
import struct
import logging
import threading
from tkinter import *
from tkinter import messagebox, Entry
from tkinter import filedialog
from typing import Dict, Any

from playsound import playsound

# 日誌等級
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

# 全局遊戲數據
game_data = {}
app_title=""
# 存檔文件位置(R1存檔1, R2存檔2, R3存檔3)
save_file_path = ""
# 遊戲數據文件位置(Z.dat)
zdata_file_path = ""

# 設定主角開局屬性
# 從data.json中加載屬性地址
char_attributes_address = {}
char_attributes_value: Dict[str, int] = {}

# 中毒除數(遊戲算法數值，不在存檔中)
zdata_venom_divisor_address = 0x3600B
zdata_venom_divisor_value = 0x01
zdata_venom_divisor_desc = ""

# 武功(區分大小寫)
# 從data.json中加載武功地址
martial_arts_names = {}
# 武功最大數
char_martial_maxcount = 10
# 武功種類起始地址和步進
char_martial_type_start_address = 0x3C2
char_martial_type_address_step = 0x02
char_martial_type_list: [int] = []
# 武功等級起始地址和步進
# 武功等級: 0x8503 10級 (註：short是逆序寫入 little endian)
char_martial_tier_start_address = 0x3D6
char_martial_tier_address_step = 0x02
char_martial_tier_list: [int] = []

# 隊友
# 從data.json中加載隊友地址
team_members_names = {}
team_members_maxcount = 6
team_members_start_address = 0x18
team_members_address_step = 0x02
team_members_list: [str] = []
team_members_desc = ""

# 主窗口
root = None


# 武功等級轉換(從經驗值到級別)
def martial_ladder_from_tier(tier):
    return tier // 100 + 1


# 武功等級轉換(從級別到經驗值)
def martial_tier_from_ladder(ladder):
    tier = (int(ladder) - 1) * 100 + 1
    return tier


# 武功名稱轉換(從數值到名稱)
def martial_name_from_type(type):
    martial_arts_key = "0x{:02X}".format(type)
    return martial_arts_names[martial_arts_key]


# 武功名稱轉換(從名稱到數值)
def martial_type_from_name(name):
    for key, val in martial_arts_names.items():
        if val == name:
            return int(key, 16)
    return 0x00


# 主函數，不用在乎函數定義順序
def main_entry_point():
    play_sound()
    # 取得上回存檔位置
    retrieve_game_data()
    show_main_window()


def char_window_btn_refresh():
    retrieve_character()

    # 重設屬性
    for key, val in char_attributes_value.items():
        input = root.input_attrs[key]
        reset_char_item(input, val)

    # 重設武功列表
    for x in range(0, char_martial_maxcount):
        type = char_martial_type_list[x]
        tier = char_martial_tier_list[x]
        input = root.input_martial[x]
        reset_martial_list_item(input, type, tier)

    # 重設隊友列表
    for x in range(0, team_members_maxcount):
        member = team_members_list[x]
        input = root.input_team[x]
        reset_team_list_member(input, member)

    # 重置中毒除數
    reset_data_item(root.input_venom_divisor, zdata_venom_divisor_value)

    root.label_status.set(lang.TXT_SAVE_REFRESHED)


# 重置單個屬性
def reset_char_item(input, text):
    input.delete(0, END)
    input.insert(0, text)


# 重置單個武功
def reset_martial_list_item(mp, type, tier):
    name = martial_name_from_type(type)
    text = martial_ladder_from_tier(tier)
    options = mp[0]
    options.set(name)
    input = mp[1]
    input.delete(0, END)
    input.insert(0, text)

# 重置單個隊友
def reset_team_list_member(mp, member):
    options = mp
    options.set(member)

# 重置單個數據
def reset_data_item(input, text):
    input.delete(0, END)
    input.insert(0, text)


# 取得單個屬性值
def retrieve_char_item(input):
    value = input.get()
    return int(value)


# 取得單個武功的值
def retrieve_martial_list_item(mp):
    options = mp[0]
    name = martial_type_from_name(options.get())
    input = mp[1]
    text = martial_tier_from_ladder(input.get())
    return name, text

# 取得單個隊友名字
def retrieve_team_list_member(mp):
    options = mp
    name = options.get()
    return name

# 取得單個數據值
def retrieve_data_item(input):
    value = input.get()
    return int(value)

def char_window_btn_write():
    global char_attributes_value
    global zdata_venom_divisor_value

    # 讀取全部屬性
    for key, val in char_attributes_value.items():
        input = root.input_attrs[key]
        char_attributes_value[key] = retrieve_char_item(input)

    # 讀取武功列表
    for x in range(0, char_martial_maxcount):
        input = root.input_martial[x]
        (type, tier) = retrieve_martial_list_item(input)
        char_martial_type_list[x] = type
        char_martial_tier_list[x] = tier
        # logging.debug("武功%d種類 %s 經驗 %s" % (x+1, '0x{:02X}'.format(type), hex(tier)))

    # 讀取隊友列表
    for x in range(0, team_members_maxcount):
        input = root.input_team[x]
        member = retrieve_team_list_member(input)
        team_members_list[x] = member

    # 讀取中毒除數
    zdata_venom_divisor_value = retrieve_data_item(root.input_venom_divisor)

    # 寫入存檔
    rewrite_character()
    root.label_status.set(lang.TXT_SAVE_WRITEN)


def char_window_btn_close():
    global root
    root.destroy()
    show_main_window()


# 生成人物單個屬性輸入框
def create_sub_character_input(parent_pane, desc, text, desc_width=6, text_width=6):
    pane = Frame(parent_pane)
    pane.pack(fill=X, expand=True, padx=10, pady=2)
    label = Label(pane, text=desc, width=desc_width)
    label.pack(side=LEFT, fill=BOTH, expand=True)
    input = Entry(pane, width=text_width)
    input.pack(side=RIGHT, fill=BOTH, expand=True)
    input.insert(0, text)
    return input


# 生成人物單個武功輸入框
def create_sub_martial_input(parent_pane, type, tier, type_width=10, tier_width=10):
    pane = Frame(parent_pane)
    pane.pack(fill=X, expand=True, padx=10, pady=2)
    # 讓武功成為選擇列表，而不是輸入
    '''
    input_type = Entry(pane)
    input_type.pack(side=LEFT, fill=BOTH, expand=True)
    input_type.insert(0, type)
    '''
    options = StringVar(root)
    options.set(type)
    # [value for value in martial_arts_names.values()]
    dp = OptionMenu(pane, options, *martial_arts_names.values())
    dp.config(width=type_width)
    dp.pack(side=LEFT, fill=BOTH, expand=True)

    input_tier = Entry(pane, width=tier_width)
    input_tier.pack(side=RIGHT, fill=BOTH, expand=True)
    input_tier.insert(0, tier)
    return options, input_tier

# 生成單個隊友列表
def create_sub_team_menu(parent_pane, member, width=10):
    pane = Frame(parent_pane)
    pane.pack(fill=X, expand=True, padx=10, pady=2)
    options = StringVar(root)
    options.set(member)
    dp = OptionMenu(pane, options, *team_members_names.keys())
    dp.config(width=width)
    dp.pack(side=TOP, fill=BOTH, expand=True)
    return options

# 顯示人物屬性窗口
def show_character_window():
    global root
    root = Tk()
    root.title(lang.TITLE_CHAR_DATA)
    root.resizable(0, 0)

    # paned window
    pane = Frame(root)
    pane.pack(fill=BOTH, expand=True, padx=0, pady=0)

    # 左側人物數據
    pane_char = LabelFrame(pane, text=lang.TXT_CHAR_DATA)
    pane_char.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

    # 右側面板
    pane_right = Frame(pane)
    pane_right.pack(side=RIGHT, fill=Y, expand=True, padx=10, pady=10)

    # 中間面板
    pane_middle = Frame(pane)
    pane_middle.pack(side=RIGHT, fill=Y, expand=True, padx=10, pady=10)

    # 右側上方隊友列表
    pane_team = LabelFrame(pane_right, text=lang.TXT_MEMBER_LST)
    pane_team.pack(side=TOP, fill=BOTH, expand=True, padx=0, pady=(0, 2))

    # 右側下方關於隊友的說明
    pane_team_desc = LabelFrame(pane_right, text=lang.TXT_MEMBER_DESC)
    pane_team_desc.pack(side=BOTTOM, fill=BOTH, expand=True, padx=0, pady=(2, 0))

    # 中側上方武功列表
    pane_martial = LabelFrame(pane_middle, text=lang.TXT_ATTACK_LST)
    pane_martial.pack(side=TOP, fill=X, expand=True, padx=0, pady=(0, 2))

    # 中側下放毒性增強
    pane_venom = LabelFrame(pane_middle, text=lang.TXT_VENOM_ENHANCE)
    pane_venom.pack(side=BOTTOM, fill=BOTH, expand=True, padx=0, pady=(2, 0))

    # 每一個輸入框都變成root的一個屬性，方面後面取值
    root.input_attrs = {}
    for key, val in char_attributes_value.items():
        input = create_sub_character_input(pane_char, key, val)
        root.input_attrs[key] = input

    # 右側武功列表
    pane = Frame(pane_martial)
    pane.pack(fill=X, expand=True, padx=10, pady=2)
    label = Label(pane, text=lang.TXT_ATTACK, width=6)
    label.pack(side=LEFT, fill=BOTH, expand=True)
    label = Label(pane, text=lang.TXT_LEVEL, width=6)
    label.pack(side=RIGHT, fill=BOTH, expand=True)

    pane = Frame(pane_martial)
    pane.pack(fill=X, expand=True)
    # 10種武功(返回:選擇武功, 等級輸入框)
    root.input_martial = []
    for x in range(0, char_martial_maxcount):
        type = char_martial_type_list[x]
        tier = char_martial_tier_list[x]
        input = create_sub_martial_input(pane, martial_name_from_type(type), martial_ladder_from_tier(tier))
        root.input_martial.append(input)

    # 右側隊友列表
    pane = Frame(pane_team)
    pane.pack(fill=X, expand=True)
    root.input_team = []
    for x in range(0, team_members_maxcount):
        member = team_members_list[x]
        input = create_sub_team_menu(pane, member)
        root.input_team.append(input)

    # 關於隊友的說明
    msg = Message(pane_team_desc, text=team_members_desc)
    msg.pack(side=TOP, fill=BOTH, anchor=W, expand=True)

    # 毒性增強設定
    label = Label(pane_venom, text=zdata_venom_divisor_desc)
    label.pack(side=TOP, fill=BOTH, expand=True)
    input = create_sub_character_input(pane_venom, lang.TXT_VENOM_DIVISOR, zdata_venom_divisor_value)
    root.input_venom_divisor = input

    # 下側按鈕
    pane = Frame(root)
    pane.pack(fill=X, expand=False, padx=10, pady=10)

    label_status = StringVar()
    label_status.set(lang.TXT_SAVE_LOADED)
    label = Label(pane, textvariable=label_status)
    label.pack(side=LEFT, fill=BOTH, expand=True)
    root.label_status = label_status

    # 返回，写入，刷新
    btn = Button(pane, text=lang.BTN_RETURN, command=char_window_btn_close)
    btn.pack(side=RIGHT, fill=BOTH, expand=True, padx=4)
    btn = Button(pane, text=lang.BTN_WRITE, command=char_window_btn_write)
    btn.pack(side=RIGHT, fill=BOTH, expand=True, padx=4)
    btn = Button(pane, text=lang.BTN_REFRESH, command=char_window_btn_refresh)
    btn.pack(side=RIGHT, fill=BOTH, expand=True, padx=4)

    root.update_idletasks()  # Update "requested size" from geometry manager
    root.geometry("+%d+%d" % ((root.winfo_screenwidth() - root.winfo_reqwidth()) / 2,
                              (root.winfo_screenheight() - root.winfo_reqheight()) / 2))
    root.mainloop()


# 關閉主窗口
def main_window_btn_close():
    global root
    root.destroy()


# 讀取存檔文件
def main_window_btn_read():
    err = ""
    save_path = root.input_save_path.get()
    if not os.path.exists(save_path):
        err = lang.ERR_SAVE_NOT_EXIST
        root.input_save_status.set(err)
        logging.error(err)
        return
    root.input_save_status.set(err)

    zdata_path = root.input_zdata_path.get()
    if not os.path.exists(zdata_path):
        err = lang.ERR_DATA_NOT_EXIST
        root.input_zdata_status.set(err)
        logging.error(err)
        return
    root.input_zdata_status.set(err)

    # 保存存檔目錄
    dump_save_path(save_path, zdata_path)
    retrieve_character()

    # 打開人物窗口
    main_window_btn_close()
    show_character_window()


# 生成通用單個屬性輸入框
def create_sub_path_input(parent_pane, desc, text, btn_command):
    pane = Frame(parent_pane)
    pane.pack(fill=X, expand=True, padx=10, pady=2)

    pane_info = Frame(pane)
    pane_info.pack(side=TOP, fill=X, expand=True)

    label = Label(pane_info, text=desc)
    label.pack(side=LEFT, anchor=NW)

    # 提示文件狀態
    label_status = StringVar()
    label_status.set("")
    label = Label(pane_info, textvariable=label_status)
    label.pack(side=RIGHT)

    pane = Frame(pane)
    pane.pack(side=BOTTOM, fill=X, expand=True)

    input = Entry(pane)
    input.pack(side=LEFT, fill=BOTH, expand=True)
    input.insert(0, text)

    btn = Button(pane, text=lang.BTN_SELECT, width=8, command=btn_command)
    btn.pack(side=RIGHT, fill=X, expand=False, padx=4)

    return label_status, input


# 選擇存檔文件位置
def main_window_select_save_file():
    global save_file_path
    path = filedialog.askopenfilename(defaultextension=".grp", multiple=False, title=lang.TITLE_SAVE_PATH_SEL)
    if not path:
        return
    save_file_path = path
    root.input_save_path.delete(0, END)
    root.input_save_path.insert(0, save_file_path)
    # 保存存檔目錄
    dump_save_path(save_file_path, zdata_file_path)


# 選擇數據文件位置
def main_window_select_zdata_file():
    global zdata_file_path
    path = filedialog.askopenfilename(defaultextension=".dat", multiple=False, title=lang.TITLE_DATA_PATH_SEL)
    if not path:
        return
    zdata_file_path = path
    root.input_zdata_path.delete(0, END)
    root.input_zdata_path.insert(0, zdata_file_path)
    # 保存存檔目錄
    dump_save_path(save_file_path, zdata_file_path)


# 顯示存檔窗口
def show_main_window():
    global root
    root = Tk()
    root.title(app_title)

    '''
    root.minsize(width=400, height=0) 
    root.maxsize(width=300, height=300)
    '''
    root.resizable(0, 0)

    img = PhotoImage(file='img/logo.png')
    Label(root, image=img).pack(fill=BOTH, expand=True)

    pane = Frame(root)
    pane.pack(fill=X, expand=True, padx=5, pady=(5, 5))

    # 返回(文件狀態,文件路徑)
    input: Entry
    (status, input) = create_sub_path_input(pane, lang.TXT_SAVE_PATH, save_file_path, main_window_select_save_file)
    root.input_save_path = input
    root.input_save_status = status

    # 返回(文件狀態,文件路徑)
    (status, input) = create_sub_path_input(pane, lang.TXT_DATA_PATH, zdata_file_path, main_window_select_zdata_file)
    root.input_zdata_path = input
    root.input_zdata_status = status

    pane = Frame(root)
    pane.pack(fill=X, expand=True, padx=5, pady=(5, 10))

    label = Label(pane, text="© 2022-2023 Charles Liu.")
    label.pack(side=LEFT, anchor=NW, expand=False, padx=(10, 2))

    pane = Frame(pane)
    pane.pack(side=RIGHT, fill=X, expand=False, padx=10)

    btn = Button(pane, text=lang.BTN_READ, width=8, command=main_window_btn_read)
    btn.pack(side=LEFT, fill=BOTH, expand=True, padx=4)

    btn = Button(pane, text=lang.BTN_CLOSE, width=8, command=main_window_btn_close)
    btn.pack(side=RIGHT, fill=BOTH, expand=True, padx=4)

    root.update_idletasks()  # Update "requested size" from geometry manager
    root.geometry("+%d+%d" % ((root.winfo_screenwidth() - root.winfo_reqwidth()) / 2,
                              (root.winfo_screenheight() - root.winfo_reqheight()) / 2))
    root.mainloop()


# 播放音樂
def play_sound():
    threading.Thread(target=playsound, args=('snd/sound.mp3',), daemon=True).start()


# 讀取全局數據文件
def retrieve_game_data():
    # Read data from file
    global game_data
    global app_title
    global save_file_path
    global zdata_file_path
    global char_attributes_address
    global martial_arts_names
    global zdata_venom_divisor_address
    global zdata_venom_divisor_desc
    global char_martial_type_start_address
    global char_martial_type_address_step
    global char_martial_tier_start_address
    global char_martial_tier_address_step
    global char_martial_maxcount
    global team_members_names
    global team_members_maxcount
    global team_members_start_address
    global team_members_address_step
    global team_members_desc

    char_attributes_address = {}
    martial_arts_names = {}
    team_members_names = {}
    app_title = ""
    zdata_file_path = ""
    save_file_path = ""

    with open("data.json", "r") as f:
        game_data = json.load(f)
        if "app_title" in game_data:
            app_title = game_data["app_title"]
        if "save_file_path" in game_data:
            save_file_path = game_data["save_file_path"]
        if "zdata_file_path" in game_data:
            zdata_file_path = game_data["zdata_file_path"]
        if "char_attributes_address" in game_data:
            char_attributes_address = game_data["char_attributes_address"]
        if "martial_arts_names" in game_data:
            martial_arts_names = game_data["martial_arts_names"]
        if "team_members_names" in game_data:
            team_members_names = game_data["team_members_names"]

        for key, val in char_attributes_address.items():
            # 第一次加載的是16進製文字，進行了整形轉換，重新寫入data.json
            # 第二次加載的就是int了，不需要再轉換
            if isinstance(val, int):
                char_attributes_address[key] = val
            else:
                char_attributes_address[key] = int(val, 16)

        for key, val in team_members_names.items():
            # 第一次加載的是16進製文字，進行了整形轉換，重新寫入data.json
            # 第二次加載的就是int了，不需要再轉換
            if isinstance(val, int):
                team_members_names[key] = val
            else:
                team_members_names[key] = int(val, 16)

        char_martial_type_start_address = int(game_data["char_martial_type_start_address"], 16)
        char_martial_type_address_step = int(game_data["char_martial_type_address_step"], 16)
        char_martial_tier_start_address = int(game_data["char_martial_tier_start_address"], 16)
        char_martial_tier_address_step = int(game_data["char_martial_tier_address_step"], 16)
        char_martial_maxcount = int(game_data["char_martial_maxcount"])
        team_members_start_address = int(game_data["team_members_start_address"], 16)
        team_members_address_step = int(game_data["team_members_address_step"], 16)
        team_members_maxcount = int(game_data["team_members_maxcount"])
        team_members_desc = game_data["team_members_desc"]
        zdata_venom_divisor_address = int(game_data["zdata_venom_divisor_address"], 16)
        zdata_venom_divisor_desc = game_data["zdata_venom_divisor_desc"]


# 寫入全局數據文件
# 若想修改原始遊戲編輯數據
# 修改data_local.json文件，然後執行python convert_data.py
# 把data_local.json轉換成data.json unicode化
# 不要直接改data.json
def dump_save_path(save_path, zdata_path):
    # Write data to file
    global game_data
    game_data["save_file_path"] = save_path
    game_data["zdata_file_path"] = zdata_path
    with open("data.json", "w") as f:
        # prevent json from transforming chars to unicode
        json.dump(game_data, f, ensure_ascii=True)


# 讀取人物數據
def retrieve_character():
    global char_attributes_value
    global char_martial_type_list
    global char_martial_tier_list
    global team_members_list

    '''
    struct.unpack('<')
    the short integer is stored in little-endian byte-order(<). 
    If the short integer is stored in big-endian byte-order, 
    then we need to use > character in the format string instead of <.
    '''
    with open(save_file_path, mode='rb') as f:
        logging.debug("讀取人物數據 開始:")
        char_attributes_value = {}
        for key, val in char_attributes_address.items():
            address = char_attributes_address[key]
            value = read_file_byte(f, address, 2)
            char_attributes_value[key] = value
            logging.debug("讀取 -> %s: %d" % (key, value))

        logging.debug("讀取人物武功")
        char_martial_type_list.clear()
        char_martial_tier_list.clear()
        for x in range(0, char_martial_maxcount):
            address = char_martial_type_start_address + x * char_martial_type_address_step
            mtype = read_file_byte(f, address, char_martial_type_address_step)
            char_martial_type_list.append(mtype)
            address = char_martial_tier_start_address + x * char_martial_tier_address_step
            tier = read_file_byte(f, address, char_martial_tier_address_step)
            char_martial_tier_list.append(tier)
            logging.debug(
                "讀取 -> 武功%d: %s 等級 %s" % (x + 1, martial_name_from_type(mtype), martial_ladder_from_tier(tier)))

        logging.debug("讀取隊友列表")
        team_members_list.clear()
        for x in range(0, team_members_maxcount):
            address = team_members_start_address + x * team_members_address_step
            member = read_file_byte(f, address, team_members_address_step, unsigned=True) #註意：隊友數據是無符號short
            for key, value in team_members_names.items():
                if value == member:
                    logging.debug("讀取 -> 隊友%d: %s" % (x + 1, key))
                    team_members_list.append(key)
                    break

    logging.debug("讀取人物數據 完成.")

    logging.debug("讀取遊戲數據 開始:")
    global zdata_venom_divisor_value
    with open(zdata_file_path, mode='rb') as f:
        zdata_venom_divisor_value = read_file_byte(f, zdata_venom_divisor_address, 2)
        logging.debug("讀取 -> 中毒除數: %d" % zdata_venom_divisor_value)

    logging.debug("讀取遊戲數據 完成.")


# 從文件中讀取字節(金庸大部分數據都是short)
def read_file_byte(f, address, count, unsigned=False):
    f.seek(address)
    binary_data = f.read(count)
    fmt = '<h'  # short
    if count == 2:
        fmt = '<h'
    elif count == 4:
        fmt = '<i'  # integer
    else:
        return 0
    if unsigned:
        fmt = fmt.upper()
    val = struct.unpack(fmt, binary_data)[0]
    return val


# 向文件中寫入字節(金庸大部分數據都是short)
def write_file_byte(f, address, count, value, unsigned=False):
    if value < 0:
        return
    f.seek(address)
    fmt = 'h'  # short
    if count == 2:
        fmt = 'h'
    elif count == 4:
        fmt = 'i'  # integer
    if unsigned:
        fmt = fmt.upper()
    f.write(struct.pack(fmt, value))


# 重寫人物數據
def rewrite_character():
    logging.debug("重寫人物數據 開始:")
    with open(save_file_path, 'r+b') as f:
        # seek to the position where the value to be rewritten is
        # ?: boolean
        # h: short
        # l: long
        # i: int
        # f: float
        # q: long long int [1]

        logging.debug("重寫人物屬性")
        for key, val in char_attributes_address.items():
            address = char_attributes_address[key]
            value = char_attributes_value[key]
            logging.debug("重寫 -> %s: %d" % (key, value))
            write_file_byte(f, address, 2, value)

        logging.debug("重寫人物武功")
        for x in range(0, char_martial_maxcount):
            address = char_martial_type_start_address + x * char_martial_type_address_step
            mtype = char_martial_type_list[x]
            logging.debug("重寫 -> 武功%d: %s" % (x + 1, martial_name_from_type(mtype)))
            write_file_byte(f, address, char_martial_type_address_step, mtype)

            address = char_martial_tier_start_address + x * char_martial_tier_address_step
            tier = char_martial_tier_list[x]
            logging.debug("重寫 -> 武功%d 等級: %s" % (x + 1, martial_ladder_from_tier(tier)))
            write_file_byte(f, address, char_martial_tier_address_step, tier)

        logging.debug("重寫隊友列表")
        for x in range(0, team_members_maxcount):
            address = team_members_start_address + x * team_members_address_step
            member = team_members_list[x]
            value = team_members_names[member]
            logging.debug("重寫 -> 隊友%d : %s" % (x + 1, member))
            write_file_byte(f, address, team_members_address_step, value, unsigned=True) #註意：隊友數據是無符號short

    logging.debug("重寫人物數據 完成.")

    logging.debug("重寫遊戲數據 開始:")
    with open(zdata_file_path, 'r+b') as f:
        logging.debug("重寫 -> 中毒除數: %d" % zdata_venom_divisor_value)
        write_file_byte(f, zdata_venom_divisor_address, 2, zdata_venom_divisor_value)

    logging.debug("重寫遊戲數據 完成.")


# 全局主函數
if __name__ == '__main__':
    main_entry_point()
