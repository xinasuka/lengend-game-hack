import json

'''
convert data_local.json -> data.json
convert ascii to unicode
'''
game_data = {}

with open("data_local.json", "r") as f:
    game_data = json.load(f)


with open("data.json", "w") as f:
    json.dump(game_data, f, ensure_ascii=True)

print("Done.")