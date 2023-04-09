import json
import struct

'''
convert data_local.json -> data.json
convert ascii to unicode
'''
game_data = {}

with open("data_local.json", "r") as f:
    game_data = json.load(f)
    map_positions = game_data["map_positions"]
    for key, val in map_positions.items():
        # print("%s -> %s" %(key, val))
        # 轉換地圖坐標為數字，並且調整為正確字節順序
        inner_lambda = lambda x: int(x, 16) if not isinstance(x, int) else x
        x, y = map(inner_lambda, val.strip("()").split(","))
        x_bytes = struct.pack(">H", x)
        y_bytes = struct.pack(">H", y)
        x = struct.unpack("<H", x_bytes)[0]
        y = struct.unpack("<H", y_bytes)[0]
        #print("%s: %d %d" % (key, x, y))
        map_positions[key] = (x, y)

    # 重写战斗事件
    battle_events = game_data["battle_events"]
    for battle in battle_events:
        check = battle["check"]
        overlays = battle["overlays"]
        for overlay in overlays:
            # 重写overlay的值
            for key, val in overlay.items():
                val = val.replace(" ","").replace("\n","")
                overlay[key] = val

        # 重写check的值
        pos = check["pos"]
        check["pos"] = int(pos, 16)
        val = check["val"]
        val = val.replace(" ", "").replace("\n", "")
        check["val"] = val

with open("data.json", "w") as f:
    json.dump(game_data, f, ensure_ascii=True)

print("Done.")