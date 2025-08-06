import akshare as ak # type: ignore
import pandas as pd
import time
from datetime import datetime

# 设置监控的4只股票
# watch_list = ['000858', '600519', '002475', '300750']  # 茅台、五粮液、立讯、宁德时代
watch_list = ['600392', '600619', '002558', '002837', '002364', '002130'] 
exchange_map = lambda code: 'sh' if code.startswith('6') else 'sz'

# 计算指标函数
def add_indicators(df):
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma10'] = df['close'].rolling(window=10).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['diff'] = ema12 - ema26
    df['dea'] = df['diff'].ewm(span=9, adjust=False).mean()
    df['macd'] = 2 * (df['diff'] - df['dea'])  # MACD柱子
    df['volume_ma5'] = df['volume'].rolling(window=5).mean()
    return df

# 判断逻辑函数
def generate_signal(df):
    signal = ""
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # 均线金叉死叉
    if latest['ma5'] > latest['ma10'] and prev['ma5'] <= prev['ma10']:
        signal += "🟢 均线金叉，关注回踩买入机会\n"
    elif latest['ma5'] < latest['ma10'] and prev['ma5'] >= prev['ma10']:
        signal += "🔴 均线死叉，考虑卖出或降低仓位\n"

    # MACD金叉死叉
    if latest['diff'] > latest['dea'] and prev['diff'] <= prev['dea']:
        signal += "🟢 MACD金叉，买入信号\n"
    elif latest['diff'] < latest['dea'] and prev['diff'] >= prev['dea']:
        signal += "🔴 MACD死叉，卖出信号\n"

    # 成交量分析
    if latest['volume'] > 1.5 * latest['volume_ma5']:
        signal += "📈 放量上涨，主力可能进场\n"
    elif latest['volume'] < 0.8 * latest['volume_ma5']:
        signal += "📉 缩量回踩，可能是洗盘\n"

    return signal or "无明显信号\n"

# 实时监控主逻辑
def monitor():
    while True:
        print("\n=====================================================")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        for code in watch_list:
            full_code = f"{exchange_map(code)}{code}"
            try:
                df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq").iloc[-60:]
                df.rename(columns={"日期": "date", "开盘": "open", "收盘": "close", "最高": "high",
                                   "最低": "low", "成交量": "volume"}, inplace=True)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                df = add_indicators(df)
                signal = generate_signal(df)
                print(f"{code} ⬇️\n{signal}")
            except Exception as e:
                print(f"{code} 加载失败：{e}")
        print("-----------------------------------------------------")
        time.sleep(60)

if __name__ == "__main__":
    monitor()