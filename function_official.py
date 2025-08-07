import akshare as ak # type: ignore
import pandas as pd
import datetime
import numpy as np
from datetime import datetime, timedelta
from ta.trend import MACD, SMAIndicator # type: ignore
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt # type: ignore
import ctypes
import time as t

# 存储每个消息的上次弹出时间（内容作为 key）
last_popup_times = {}
# 弹窗函数（仅限 Windows）
def show_popup(message, title="提醒", cooldown=3600):
    current_time = t.time()
    # 获取该消息的上次弹出时间
    last_time = last_popup_times.get(message, 0)
    # 如果距离上次弹窗小于 cooldown 秒，就不弹
    if current_time - last_time < cooldown:
        return
    # 弹窗
    ctypes.windll.user32.MessageBoxW(0, message, title, 0)
    
    # 记录这次弹窗时间
    last_popup_times[message] = current_time


def get_realtime_macdfs(stock_code: str) -> float:
    # 1. 获取历史收盘价
    end_date = datetime.datetime.now().strftime("%Y%m%d")
    start_date = (datetime.datetime.now() - datetime.timedelta(days=45)).strftime("%Y%m%d")
    hist_df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
    
    if hist_df.empty:
        raise ValueError(f"未获取到历史数据: {stock_code}")
    
    close_prices = hist_df["收盘"].tolist()

    # 2. 获取当前实时价格
    realtime_df = ak.stock_zh_a_spot_em()
    realtime_price_row = realtime_df[realtime_df["代码"] == stock_code]
    if realtime_price_row.empty:
        raise ValueError(f"未找到实时数据: {stock_code}")
    
    realtime_price = float(realtime_price_row["最新价"].values[0])
    close_prices.append(realtime_price)

    # 3. 计算 MACD（默认 12,26,9）
    close_series = pd.Series(close_prices)
    ema12 = close_series.ewm(span=12, adjust=False).mean()
    ema26 = close_series.ewm(span=26, adjust=False).mean()
    dif = ema12 - ema26
    dea = dif.ewm(span=9, adjust=False).mean()
    macd = (dif - dea) * 2  # MACDFS = (DIFF - DEA) * 2

    latest_macdfs = macd.iloc[-1]
    return float(latest_macdfs)

def get_minute_macdfs(stock_code: str):
    """
    获取某只股票最近的1分钟级MACDFS值，并提供交叉信号、趋势判断、建议等
    """
    try:
        # 假设你现在时间是 14:30
        end_time = datetime.now()
        # start_time = end_time - timedelta(minutes=60)

        # start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
        today = pd.Timestamp.now().strftime("%Y-%m-%d")
        start_str = f"{today} 09:30:00"
        # end_str = f"{today} 13:35:00"
        # 获取最近240条1分钟K线数据（约1个交易日）
        df = ak.stock_zh_a_hist_min_em(symbol=stock_code, start_date=start_str, end_date=end_str,period="1", adjust="")
        # print(df)

        if df.empty or '收盘' not in df.columns:
            print("数据获取失败或格式异常，可能已收盘")
            return None

        close_prices = df['收盘'].astype(float)

        # 计算MACD指标
        ema12 = close_prices.ewm(span=12, adjust=False).mean()
        ema26 = close_prices.ewm(span=26, adjust=False).mean()
        diff = ema12 - ema26
        dea = diff.ewm(span=9, adjust=False).mean()
        macdfs = 2 * (diff - dea)  # MACDFS = (DIF - DEA) * 2

        latest_dif = diff.iloc[-1]
        prev_dif = diff.iloc[-2]
        latest_dea = dea.iloc[-1]
        prev_dea = dea.iloc[-2]
        latest_macdfs = macdfs.iloc[-1]
        prev_macdfs = macdfs.iloc[-2]

        # 是否金叉/死叉
        is_golden_cross = prev_dif < prev_dea and latest_dif > latest_dea
        is_dead_cross = prev_dif > prev_dea and latest_dif < latest_dea

        # 趋势穿越0轴
        cross_zero_up = prev_dif < 0 and latest_dif > 0
        cross_zero_down = prev_dif > 0 and latest_dif < 0

        # 趋势增强/减弱（MACDFS放大/缩小）
        macdfs_diff = latest_macdfs - prev_macdfs
        macdfs_strength = "增强" if abs(latest_macdfs) > abs(prev_macdfs) else "减弱"

        # 建议
        if is_golden_cross:
            suggestion = "出现金叉"
        elif is_dead_cross:
            suggestion = "出现死叉"
        elif latest_macdfs > 0:
            suggestion = "偏多持有"
        else:
            suggestion = "偏空观望"

        # 找局部高点（价格）
        high_indices = argrelextrema(close_prices.values, np.greater, order=15)[0]
        # print(high_indices)
        # 找局部低点
        low_indices = argrelextrema(close_prices.values, np.less, order=15)[0]
        # print(low_indices)
        # 顶背离检测：价格创新高，DIF未创新高
        if len(high_indices) >= 2:
            last = high_indices[-1]
            prev = high_indices[-2]
            if close_prices.iloc[last] * 0.9 > close_prices.iloc[prev] and diff.iloc[last] < diff.iloc[prev]:
                print("⚠️ 顶背离出现：价格创新高，但DIF未创新高")
                # ctypes.windll.user32.MessageBoxW(0, "顶背离出现：价格创新高，但DIF未创新高", "顶背离", 0)
                show_popup("顶背离出现：价格创新高，但DIF未创新高", f"{stock_code}：顶背离")

        # 底背离检测：价格创新低，DIF未创新低
        if len(low_indices) >= 2:
            last = low_indices[-1]
            prev = low_indices[-2]
            if close_prices.iloc[last] * 1.1 < close_prices.iloc[prev] and diff.iloc[last] > diff.iloc[prev]:
                print("⚠️ 底背离出现：价格创新低，但DIF未创新低")
                ctypes.windll.user32.MessageBoxW(0, "底背离出现：价格创新低，但DIF未创新低", "底背离", 0)
                show_popup("底背离出现：价格创新低，但DIF未创新低", f"{stock_code}：底背离")

        # 打印分析
        result = {
            "MACDFS": round(latest_macdfs, 6),
            "\n出现MACDFS金叉": is_golden_cross,
            "\n出现MACDFS死叉": is_dead_cross,
            "\nDIF上穿0": cross_zero_up,
            "\nDIF下穿0": cross_zero_down,
            "\n趋势变化": macdfs_strength,
            "\nMACDFS变化": round(macdfs_diff, 6),
            "\nMACDFS指标建议": suggestion
        }

        return result

    except Exception as e:
        print(f"异常：{e}")
        return None
    


def get_minute_kdj(stock_code: str):
    """
    获取某只股票最近的1分钟级KDJ值，并提供交叉信号、趋势判断、建议等
    """
    try:
        # 时间设定
        end_time = datetime.now()
        today = pd.Timestamp.now().strftime("%Y-%m-%d")
        start_str = f"{today} 09:30:00"
        end_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

        # 获取1分钟K线数据
        df = ak.stock_zh_a_hist_min_em(symbol=stock_code, start_date=start_str, end_date=end_str, period="1", adjust="")
        if df.empty or "收盘" not in df.columns:
            print("数据获取失败或格式异常，可能已收盘")
            return None

        df["收盘"] = df["收盘"].astype(float)
        df["最高"] = df["最高"].astype(float)
        df["最低"] = df["最低"].astype(float)

        # 计算 KDJ
        low_list = df["最低"].rolling(window=9, min_periods=1).min()
        high_list = df["最高"].rolling(window=9, min_periods=1).max()
        rsv = (df["收盘"] - low_list) / (high_list - low_list) * 100

        df["K"] = rsv.ewm(com=2).mean()
        df["D"] = df["K"].ewm(com=2).mean()
        df["J"] = 3 * df["K"] - 2 * df["D"]

        latest_k = df["K"].iloc[-1]
        prev_k = df["K"].iloc[-2]
        latest_d = df["D"].iloc[-1]
        prev_d = df["D"].iloc[-2]
        latest_j = df["J"].iloc[-1]

        # 金叉 / 死叉判断
        is_golden_cross = prev_k < prev_d and latest_k > latest_d
        is_dead_cross = prev_k > prev_d and latest_k < latest_d

        # 趋势判断
        if latest_j > 80:
            signal = "超买区间，可能回调"
        elif latest_j < 20:
            signal = "超卖区间，可能反弹"
        elif is_golden_cross:
            signal = "出现KDJ金叉"
        elif is_dead_cross:
            signal = "出现KDJ死叉"
        else:
            signal = "中性震荡"

        # 返回结果
        result = {
            "K": round(latest_k, 2),
            "D": round(latest_d, 2),
            "J": round(latest_j, 2),
            "金叉": is_golden_cross,
            "死叉": is_dead_cross,
            "信号": signal
        }
        return result

    except Exception as e:
        print(f"KDJ计算异常: {e}")
        return None

def get_stock_data(code, start, end):
    df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start, end_date=end, adjust="qfq")
    df.rename(columns={"日期": "date", "开盘": "open", "收盘": "close", "最高": "high", "最低": "low", "成交量": "volume"}, inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df = df.sort_index()
    return df

def add_indicators(df):
    # MACD
    macd = MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()

    # 均线
    sma_short = SMAIndicator(df['close'], window=5)
    sma_long = SMAIndicator(df['close'], window=20)
    df['sma_5'] = sma_short.sma_indicator()
    df['sma_20'] = sma_long.sma_indicator()

    return df


macd_cross_alert = True
sma_crossover_alert = True

def check_signals(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # MACD 金叉提示
    if macd_cross_alert:
        if prev['macd'] < prev['macd_signal'] and latest['macd'] > latest['macd_signal']:
            print("📈 MACD 金叉：可能出现上涨机会")

    # 均线交叉提示
    if sma_crossover_alert:
        if prev['sma_5'] < prev['sma_20'] and latest['sma_5'] > latest['sma_20']:
            print("📊 均线金叉：短期均线向上突破长期均线")


plt.rcParams['font.family'] = 'SimHei'  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
def plot_chart(df):
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['close'], label='收盘价', color='black')
    plt.plot(df.index, df['sma_5'], label='5日均线', color='blue', linestyle='--')
    plt.plot(df.index, df['sma_20'], label='20日均线', color='orange', linestyle='--')
    plt.title("A股盯盘分析图")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()