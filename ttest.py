import akshare as ak # type: ignore
import pandas as pd
import time
from datetime import datetime
# df = ak.stock_zh_a_hist(symbol="000001", period="daily", adjust="qfq")
# print(df)
# start = "2025-08-05 09:30:00"
# end = "2025-08-05 11:20:07.579538"
# df = ak.stock_zh_a_hist_min_em(
#     symbol="000001", 
#     start_date=start,
#     end_date=end,
#     period="5",  # 每分钟数据
#     adjust=""  # 不复权
# )
# # print(df)
# # 计算总成交量
# total_volume = df["成交量"].sum()
# print(total_volume)

# now_time = datetime.now().time()
# today = datetime.now().date()
# trade_dates_df = ak.tool_trade_date_hist_sina()
# trade_dates_df["trade_date"] = pd.to_datetime(trade_dates_df["trade_date"]).dt.date
# last_trade_date = max(date for date in trade_dates_df["trade_date"] if date < today)
# start = f"{last_trade_date} 09:30:00"
# end2 = datetime.combine(last_trade_date, now_time)
# print(now_time)
# print(end2)
# df = ak.stock_zh_a_hist_min_em(
#     symbol="000001", 
#     start_date=start,
#     end_date=end2,
#     period="5",  # 每分钟数据
#     adjust=""  # 不复权
# )
# # print(df)
# # 计算总成交量
# total_volume = df["成交量"].sum()
# print(total_volume)

# # 获取上证指数实时行情
# df_sz = ak.stock_zh_index_spot()

# # 找出上证指数或其它重要指数的数据
# df_sz[df_sz["名称"] == "上证指数"][["最新价", "成交量", "成交额"]]