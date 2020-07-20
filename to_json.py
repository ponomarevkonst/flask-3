import data
import json

for val in data.__dict__:
    if val[0] != "_":
        with open("data/" +val + ".json", "w") as f:
            json.dump(getattr(data, val), f, ensure_ascii=False)