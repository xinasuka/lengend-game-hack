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


with open("data.json", "w") as f:
    json.dump(game_data, f, ensure_ascii=True)

print("Done.")