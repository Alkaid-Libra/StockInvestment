import json
import os

WATCH_FILE = "watch_dict.json"

# 尝试读取已有的 watch_dict
def load_watch_dict():
    # if not os.path.exists(WATCH_FILE) or os.path.getsize(WATCH_FILE) == 0:
    #     watch_dict_a = {}
    if os.path.exists(WATCH_FILE):
        with open(WATCH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# 保存 watch_dict 到文件
def save_watch_dict(watch_dict):
    with open(WATCH_FILE, "w", encoding="utf-8") as f:
        json.dump(watch_dict, f, ensure_ascii=False, indent=2)

# 增加股票的方法
def add_stocks_interactively(watch_dict):
    print("请输入股票代码和名称（例如 000001 平安银行），输入 q 退出：")
    while True:
        line = input(">>> ").strip()
        if line.lower() == 'q':
            break
        parts = line.split()
        if len(parts) != 2:
            print("格式错误，应为：股票代码 股票名称")
            continue
        code, name = parts
        watch_dict[code] = name
    return watch_dict