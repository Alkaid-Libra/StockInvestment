import json
import os
import akshare as ak # type: ignore

watch_file = 'watch_dict.json'

def load_watch_dict():
    if not os.path.exists(watch_file) or os.path.getsize(watch_file) == 0:
        return {}
    with open(watch_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_watch_dict(watch_dict):
    with open(watch_file, 'w', encoding='utf-8') as f:
        json.dump(watch_dict, f, ensure_ascii=False, indent=2)

def main():
    watch_dict = load_watch_dict()

    while True:
        print("\n当前关注列表：")
        for code, name in watch_dict.items():
            print(f"{code}: {name}")

        print("\n选项：")
        print("1. 添加股票")
        print("2. 删除股票")
        print("3. 退出")

        choice = input("请选择操作：").strip()
        if choice == '1':
            code = input("请输入股票代码：").strip()
            # name = input("请输入股票名称：").strip()
            stock_individual_info_em_df = ak.stock_individual_info_em(symbol=code)
            stock_name = stock_individual_info_em_df.loc[stock_individual_info_em_df["item"] == "股票简称", "value"].values[0]
            watch_dict[code] = stock_name
            save_watch_dict(watch_dict)
            print("已添加")
        elif choice == '2':
            code = input("请输入要删除的股票代码：").strip()
            if code in watch_dict:
                del watch_dict[code]
                save_watch_dict(watch_dict)
                print("已删除")
            else:
                print("股票代码不存在")
        elif choice == '3':
            break
        else:
            print("无效选项")

if __name__ == "__main__":
    main()