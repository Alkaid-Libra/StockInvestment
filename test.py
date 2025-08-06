import akshare as ak # type: ignore
import pandas as pd
import time
import datetime
import matplotlib.pyplot as plt # type: ignore
import ta # type: ignore

plt.rcParams['font.family'] = 'SimHei'  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

# 股票代码（示例为平安银行）
stock_code = "000001"
market = "sz"

# 获取历史行情数据（可配合定时轮询）
def get_stock_data(code, adjust="qfq"):
    df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20250101", adjust=adjust)
    df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量']] # 涨跌幅 换手率
    df.columns = ['date', 'open', 'close', 'high', 'low', 'volume']
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)
    # print(df)
    return df

# 添加常用技术指标
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

# 简单策略逻辑判断
def generate_signal(df):
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

# 主函数（实时或定时运行）
def run_analysis():
    df = get_stock_data(stock_code)
    df = add_indicators(df)
    
    signal = generate_signal(df)
    print(f"\n🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 分析信号：\n{signal}")

    # 可视化
    plt.figure(figsize=(14, 6))
    plt.plot(df.index[-60:], df['close'][-60:], label="收盘价", color="black")
    plt.plot(df.index[-60:], df['ma5'][-60:], label="MA5", linestyle="--", color="blue")
    plt.plot(df.index[-60:], df['ma20'][-60:], label="MA20", linestyle="--", color="orange")
    plt.fill_between(df.index[-60:], df['boll_upper'][-60:], df['boll_lower'][-60:], color='gray', alpha=0.2, label="布林带")
    plt.legend()
    plt.title(f"{stock_code} 技术指标盯盘图")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_analysis()