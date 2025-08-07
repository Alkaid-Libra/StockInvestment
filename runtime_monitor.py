import akshare as ak # type: ignore
from datetime import datetime, timedelta, time
import pandas as pd
from function import get_minute_macdfs, show_popup
import matplotlib.pyplot as plt # type: ignore
from load_config_function import load_watch_dict, add_stocks_interactively, save_watch_dict
import time as t
import ctypes

# watch_list_a = ['600619', '002364', '002130', '002837'] # 海立股份 中恒电气 沃尔核材
# watch_dict_a = {
#     '600619': '海立股份',
#     '002364': '中恒电气',
#     '002130': '沃尔核材',
#     '002837': '英维克'
# }

print("waite for loading...")
watch_dict_a = load_watch_dict()
# print("当前监控股票：", watch_dict_a)
# choice = input("是否新增股票？(y/n): ").strip().lower()
# if choice == 'y':
#     watch_dict_a = add_stocks_interactively(watch_dict_a)
#     save_watch_dict(watch_dict_a)

# print("最终监控股票：", watch_dict_a)

# 获取最近交易日
trade_dates_df = ak.tool_trade_date_hist_sina()
trade_dates_df["trade_date"] = pd.to_datetime(trade_dates_df["trade_date"]).dt.date

# 找到今天之前的最后一个交易日
today = datetime.now().date()
last_trade_date = max(date for date in trade_dates_df["trade_date"] if date < today)
last2_trade_date = max(date for date in trade_dates_df["trade_date"] if date < last_trade_date)
# print("上一个交易日是：", last_trade_date)
# print("上二个交易日是：", last2_trade_date)

# 获取当前时分秒
# now_time = datetime.now().time()

# # 设置开始和结束时间
# start = f"{last_trade_date} 09:30:00"
# # end = f"{last_trade_date} 15:00:00"
# end = datetime.combine(last_trade_date, now_time)
# start2 = f"{last2_trade_date} 09:30:00"
# end2 = datetime.combine(last2_trade_date, now_time)
# print(end)

# yesterday = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
# start = yesterday + " 09:30:00"
# end = yesterday + " 15:00:00"
while True:
    # 获取当前时分秒
    now_time = datetime.now().time()
    # 设置开始和结束时间
    start = f"{last_trade_date} 09:30:00"
    # end = f"{last_trade_date} 15:00:00"
    end = datetime.combine(last_trade_date, now_time)
    start2 = f"{last2_trade_date} 09:30:00"
    end2 = datetime.combine(last2_trade_date, now_time)

    for code, name in watch_dict_a.items():
        print("=============================")
        print("时间：", now_time.strftime("%H:%M:%S"))
        print("名称：", name)
        df = ak.stock_zh_a_hist_min_em(
            symbol=code, 
            start_date=start,
            end_date=end,
            period="5",  # 每分钟数据
            adjust=""  # 不复权
        )
        # print(df)
        # 计算总成交量
        total_volume = df["成交量"].sum()
        # print(f"{last_trade_date} 昨日此时总成交量为: {total_volume}")
        df2 = ak.stock_zh_a_hist_min_em(
            symbol=code,
            start_date=start2,
            end_date=end2,
            period="5",  # 每分钟数据
            adjust=""  # 不复权
        )
        # print(df)
        # 计算总成交量
        total_volume2 = df2["成交量"].sum()
        # print(f"{last2_trade_date} 昨二日此时总成交量为: {total_volume2}")

        # 行情报价
        stock_bid_ask_em_df = ak.stock_bid_ask_em(symbol=code)
        # print(stock_bid_ask_em_df)
        current_volume = stock_bid_ask_em_df.loc[stock_bid_ask_em_df["item"] == "总手", "value"].values[0]
        # print(current_volume)

        # print("end:", end)
        # print("end2: ", end2)
        # print(current_volume)
        # print(total_volume)

        # 量能变化关系
        if current_volume > total_volume * 1.5:
            volume_result = "明显放量"
        elif current_volume < total_volume * 0.8:
            volume_result = "明显缩量"
        elif current_volume > total_volume * 1.1 and current_volume > total_volume2 * 1.1:
            volume_result = "有所放量"
        elif current_volume < total_volume * 0.9 and current_volume < total_volume2 * 0.9:
            volume_result = "有所缩量"
        else:
            volume_result = "平量"

        # print(volume_result)

        # stock_bid_ask_em_df = ak.stock_bid_ask_em(symbol="600619")
        # print(stock_bid_ask_em_df)
        # 昨日收盘价
        last_close = stock_bid_ask_em_df[stock_bid_ask_em_df['item'] == "昨收"]['value'].values[0]

        current_price = stock_bid_ask_em_df[stock_bid_ask_em_df['item'] == "最新"]['value'].values[0]
        most_high_price = stock_bid_ask_em_df[stock_bid_ask_em_df['item'] == "最高"]['value'].values[0]
        # print(last_close)

        current_up = stock_bid_ask_em_df[stock_bid_ask_em_df['item'] == "涨幅"]['value'].values[0]
        # print(current_up['value'].values[0])
        print("当前股价涨幅：", current_up, "%")

        df_35 = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=(today - timedelta(days=35)).strftime("%Y%m%d"), end_date=today.strftime("%Y%m%d"), adjust="qfq")
        # print(df_35)
        df_35_filter = df_35[["日期", "收盘"]]
        ma5 = df_35_filter.tail(5)["收盘"].mean()
        ma10 = df_35_filter.tail(10)["收盘"].mean()
        ma20 = df_35_filter.tail(20)["收盘"].mean()
        # print("ma5:", ma5)
        # print("ma10:", ma10)
        # print("ma20:", ma20)

        # print(ma5)
        if volume_result == "明显放量":
            if current_up > 2:
                print("量价关系：放量大涨!")
            elif 0 < current_up <= 2:
                print("量价关系：放量但涨不多，可能滞涨，注意回调!")
            elif -0.5 < current_up <= 0:
                print("量价关系：放量微跌，可能滞涨，注意风险！")
            elif current_up <= -0.5:
                print("量价关系：放巨量下跌，必须减仓，亏损也要减，或者等第二天反包!")
                # ctypes.windll.user32.MessageBoxW(0, "必须减仓，亏损也要减，或者等第二天反包!", "放巨量下跌", 0)
                show_popup("必须减仓，亏损也要减，或者等第二天反包!", f"{name}：放巨量下跌")
            if last_close > ma5 and current_price < ma5:
                print("\t已跌破5日线，当天跑最好!")
                # ctypes.windll.user32.MessageBoxW(0, "不要犹豫了，必须减仓!", "放巨量下跌", 0)
                show_popup("已跌破5日线，当天跑最好!", f"{name}：放巨量下跌")
            if last_close > ma10 and current_price < ma10:
                print("\t放量跌破10日线，不要犹豫了，必须减仓!")
                # ctypes.windll.user32.MessageBoxW(0, "不要犹豫了，必须减仓!", "放巨量下跌", 0)
                show_popup("放量跌破10日线，不要犹豫了，必须减仓!", f"{name}：放巨量下跌")
            if last_close < ma5 and current_price > ma5:
                print("\t放量突破5日线")
                # ctypes.windll.user32.MessageBoxW(0, "放量突破5日线", "明显放量", 0)
                show_popup("放量突破5日线", f"{name}：明显放量")
            if last_close < ma10 and current_price > ma10:
                print("\t放量突破10日线")
                # ctypes.windll.user32.MessageBoxW(0, "放量突破10日线", "明显放量", 0)
                show_popup("放量突破10日线", f"{name}：明显放量")
            
        elif volume_result == "有所放量":
            if current_up > 0:
                print("量价关系：放量上涨，健康上涨!")
            else:
                print("量价关系：放量下跌，注意观察!")
                if current_price >= ma5:
                    print("\t在5日线上方")
                else:
                    if last_close < ma5:
                        print("\t在5日线下方")
                    else:
                        print("\t跌破5日线，危险下跌，可看明天能否反包")
                        show_popup("跌破5日线，危险下跌，可看明天能否反包", f"{name}：有所放量")
                    if current_price >= ma10:
                        print("\t在10日线上方")
                    else:
                        if last_close < ma10:
                            print("\t在10日线下方")
                        else:
                            print("\t跌破10日线，明显撤离点")
                            # ctypes.windll.user32.MessageBoxW(0, "在10日线下方，明显撤离点", "有所放量", 0)
                            show_popup("跌破10日线，明显撤离点", f"{name}：有所放量")
            if last_close < ma5 and current_price > ma5:
                print("\t突破5日线")
                # ctypes.windll.user32.MessageBoxW(0, "突破5日线", "有所放量", 0)
                show_popup("突破5日线", f"{name}：有所放量")
            if last_close < ma10 and current_price > ma10:
                print("\t突破10日线")
                # ctypes.windll.user32.MessageBoxW(0, "突破10日线", "有所放量", 0)
                show_popup("突破10日线", f"{name}：有所放量")

        elif volume_result == "有所缩量":
            if current_up < 0:
                print("量价关系：缩量下跌，可能健康调整!")
                if last_close > ma5 and current_price < ma5:
                    print("\t跌破5日线，产生分歧，主动抛压不强，可看明天能否反包")
                    # ctypes.windll.user32.MessageBoxW(0, "跌破5日线，可看明天能否反包", "有所缩量", 0)
                    # show_popup("跌破5日线，产生分歧，主动抛压不强，可观望", f"{name}：有所缩量")
                if last_close > ma10 and current_price < ma10:
                    print("\t跌破10日线，有分歧")
            else:
                print("量价关系：缩量上涨，力量不足，可能诱多!")
        elif volume_result == "明显缩量":
            if current_up <= 0:
                print("量价关系：明显缩量下跌，可能筑底!")
                if last_close > ma5 and current_price < ma5:
                    print("\t跌破5日线，主动抛压不强，可观望")
                if last_close > ma10 and current_price < ma10:
                    print("\t跌破10日线，主动抛压不强")
            else:
                print("量价关系：明显缩量但上涨，力量严重不足!")
        elif volume_result == "平量":
            print("量价关系：平量，成交量变化不大！")
            if last_close > ma5 and current_price < ma5:
                print("\t跌破5日线，可看第二天能否反包")
            if last_close > ma10 and current_price < ma10:
                print("\t跌破10日线，明显撤离点")

        if (volume_result == "明显放量" or volume_result == "有所放量") and current_up > 0 and current_price < most_high_price:
            if (most_high_price - current_price) / last_close * 100 > 3:
                print("\t明显回落，危险, 可能滞涨或出货")
            if (most_high_price - current_price) / last_close * 100 > 4:
                # ctypes.windll.user32.MessageBoxW(0, "明显回落，危险, 可能滞涨或出货", "放量冲高回落", 0)
                show_popup("明显回落，危险, 可能滞涨或出货", f"{name}：放量冲高回落")

        # stock_zh_a_hist_min_em_df = ak.stock_zh_a_hist_min_em(symbol="000001", start_date="2025-08-04 09:30:00", end_date="2025-08-04 15:00:00", period="1", adjust="")
        # print(stock_zh_a_hist_min_em_df)
        # 确保时间列是时间格式
        stock_intraday_em_df = ak.stock_intraday_em(symbol=code)
        stock_intraday_em_df['时间'] = pd.to_datetime(stock_intraday_em_df['时间'], format='%H:%M:%S')
        # print(stock_intraday_em_df)

        trigger_1 = False
        trigger_2 = False
        # 9.40价格
        if time(9, 41, 0) >= now_time >= time(9, 40, 0):
        # if time(19, 41, 0) >= now_time >= time(9, 40, 0):
            price_0940_row = stock_intraday_em_df[stock_intraday_em_df['时间'] <= pd.to_datetime("09:40:00", format="%H:%M:%S")].iloc[-1]
            price_0940 = float(price_0940_row['成交价'])
            increase_0940 = (price_0940 - last_close) / last_close * 100
            # print(increase_0940)
            # print(price_0940)
            if increase_0940 > 5:
                trigger_1 = True
        # 10.00价格
        if time(10, 1, 0) >= now_time >= time(10, 00, 0):
        # if time(16, 1, 0) >= now_time >= time(16, 00, 0):
            price_1000_row = stock_intraday_em_df[stock_intraday_em_df['时间'] <= pd.to_datetime("10:00:00", format="%H:%M:%S")].iloc[-1]
            price_1000 = float(price_1000_row['成交价'])
            print(price_1000)
            increase_1000 = (price_1000 - last_close) / last_close * 100
            if increase_1000 > 7:
                trigger_2 = True
        if trigger_1 and trigger_2 and current_up > 6.5:
            print("好消息！很有可能马上涨停")
            # ctypes.windll.user32.MessageBoxW(0, "好消息！很有可能马上涨停", "开盘上攻", 0)
            show_popup("好消息！很有可能马上涨停", f"{name}：开盘上攻")
        elif current_up > 6.5:
            print("涨幅过高，适合卖出做T")
            # ctypes.windll.user32.MessageBoxW(0, "涨幅过高，适合卖出做T", "开盘上攻", 0)
            show_popup("涨幅过高，适合卖出做T", f"{name}：盘中上攻")
        elif -4 <= current_up < -2:
            print("\t跌幅超过-2%")

        elif current_price < -4:
            print("\t跌幅超过-4%")
            show_popup("跌幅超过-4%", f"{name}：大幅下跌")


    # stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20250804", end_date='20250804', adjust="")
    # print(stock_zh_a_hist_df)

        # =============================
        result = get_minute_macdfs(code)
        # 格式化打印
        # 假设 result 是你的结果字典
        always_show_keys = ["K", "D", "J", "信号"]  # 后4个字段
        filtered_items = []

        # 筛选前8个有效键值对（不含 always_show_keys 且值有效）
        for k, v in result.items():
            if k in always_show_keys:
                continue
            if v not in [-1, False, "", None]:
                filtered_items.append((k, v))
            if len(filtered_items) >= 8:
                break

        # 收集后4个键值对（始终显示）
        always_items = [(k, result.get(k, "")) for k in always_show_keys]

        # 对齐输出
        for i in range(max(len(filtered_items), len(always_items))):
            left = f"{filtered_items[i][0]}: {filtered_items[i][1]}" if i < len(filtered_items) else ""
            right = f"{always_items[i][0]}: {always_items[i][1]}" if i < len(always_items) else ""
            print(f"{left:<20} {right}")
            if right == "信号: 超买区间，可能回调" or right == "信号: 超卖区间，可能反弹":
                show_popup(f"{name}: {always_items[i][1]}", f"{name}：KDJ信号", 600)

        # =========== origin ============
        # macdfs_result = get_minute_macdfs(code)
        # if macdfs_result is not None:
        #     for k, v in macdfs_result.items():
        #         if v not in [-1, False, ""]:
        #         # if v not in [-1, False, False, False, "", -1, ""]:
        #             print(f"{k.strip()}: {v}")

    print("-----------------------------")
    print("......wait for the next......")
    print("-----------------------------")
    t.sleep(60)


input("任务执行完毕，按回车退出...")