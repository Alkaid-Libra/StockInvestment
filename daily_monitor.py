import akshare as ak # type: ignore
import pandas as pd
import matplotlib.pyplot as plt# type: ignore
from ta.trend import MACD, SMAIndicator# type: ignore
# from matplotlib.font_manager import FontProperties
from load_config_function import load_watch_dict
from datetime import datetime, timedelta
import ta # type: ignore
# font = FontProperties(fname=r"C:\\Windows\\Fonts\\simsun.ttc", size=12)

plt.rcParams['font.family'] = 'SimHei'  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

# ========== 参数区域 ==========
# stock_code = "000001"  # 平安银行
today = datetime.now().date()
# start_date = "20250101"
start_date = (today - timedelta(days=150)).strftime("%Y%m%d")
# end_date = "20250801"
end_date = today.strftime("%Y%m%d")
macd_cross_alert = True
sma_crossover_alert = True
# =============================

def get_stock_data(code, start, end):
    df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start, end_date=end, adjust="qfq")
    df.rename(columns={"日期": "date", "开盘": "open", "收盘": "close", "最高": "high", "最低": "low", "成交量": "volume"}, inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df = df.sort_index()
    return df

def add_indicators(df):
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()

    # MACD
    # macd = ta.trend.macd(df['close'])
    df['macd'] = ta.trend.macd(df['close']) # DIF 快线
    df['macd_signal'] = ta.trend.macd_signal(df['close']) # DEA 慢线
    df['macd_diff'] = ta.trend.macd_diff(df['close']) # MACD 柱子

    # RSI
    df['rsi14'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()

    # Bollinger Bands
    boll = ta.volatility.BollingerBands(df['close'], window=20)
    df['boll_upper'] = boll.bollinger_hband()
    df['boll_lower'] = boll.bollinger_lband()
    
    return df


def check_signals(df):
    latest = df.iloc[-1]
    signal = ""

    # 均线金叉死叉
    # if latest['ma5'] > latest['ma20'] and df.iloc[-2]['ma5'] <= df.iloc[-2]['ma20']:
    #     signal += "🟢 均线金叉，考虑买入\n"
    # elif latest['ma5'] < latest['ma20'] and df.iloc[-2]['ma5'] >= df.iloc[-2]['ma20']:
    #     signal += "🔴 均线死叉，考虑卖出\n"
    if latest['ma5'] > latest['ma10'] and df.iloc[-2]['ma5'] <= df.iloc[-2]['ma10']:
        signal += "🟢 均线金叉，考虑买入\n"
    elif latest['ma5'] < latest['ma10'] and df.iloc[-2]['ma5'] >= df.iloc[-2]['ma10']:
        signal += "🔴 均线死叉，考虑卖出\n"

    # MACD
    if latest['macd'] > latest['macd_signal'] and df.iloc[-2]['macd'] <= df.iloc[-2]['macd_signal']:
        signal += "🟢 MACD金叉\n"
    elif latest['macd'] < latest['macd_signal'] and df.iloc[-2]['macd'] >= df.iloc[-2]['macd_signal']:
        signal += "🔴 MACD死叉\n"

    # RSI
    if latest['rsi14'] < 30:
        signal += "🟢 RSI低于30，超卖区\n"
    elif latest['rsi14'] > 70:
        signal += "🔴 RSI高于70，超买区\n"

    # 布林带突破
    if latest['close'] > latest['boll_upper']:
        signal += "🔴 突破上轨，注意回调\n"
    elif latest['close'] < latest['boll_lower']:
        signal += "🟢 跌破下轨，可能反弹\n"

    return signal if signal else "⚪ 暂无明确信号"

def plot_chart(df,name):
    plt.figure(figsize=(14, 7))
    plt.plot(df.index[-60:], df['close'][-60:], label="收盘价", color="black")
    plt.plot(df.index[-60:], df['ma5'][-60:], label="MA5", linestyle="--", color="blue")
    plt.plot(df.index[-60:], df['ma20'][-60:], label="MA20", linestyle="--", color="orange")
    plt.fill_between(df.index[-60:], df['boll_upper'][-60:], df['boll_lower'][-60:], color='gray', alpha=0.2, label="布林带")
    # plt.legend()
    # plt.title(f"{stock_code} 技术指标盯盘图")
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()

    # plt.plot(df.index, df['close'], label='收盘价', color='black')
    # plt.plot(df.index, df['sma_5'], label='5日均线', color='blue', linestyle='--')
    # plt.plot(df.index, df['sma_20'], label='20日均线', color='orange', linestyle='--')
    plt.title(f"{name} 日k线分析图")
    # plt.title("A股盯盘分析图", fontproperties=font)
    # plt.legend(prop=font)
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("waite for loading...")
    watch_dict_a = load_watch_dict()
    for stock_code, name in watch_dict_a.items():
        data = get_stock_data(stock_code, start_date, end_date)
        data = add_indicators(data)
        signal = check_signals(data)
        print(f"\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 分析信号：\n{signal}")

        plot_chart(data, name)

    input("任务执行完毕，按回车退出...")
