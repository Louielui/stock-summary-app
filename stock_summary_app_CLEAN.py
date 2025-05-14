import streamlit as st
import datetime
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 使用者輸入股票代碼與 Put 模擬口數
st.set_page_config(page_title="單股分析板", layout="centered")
st.title(":bar_chart: 單股即時分析")
symbol = st.text_input("輸入股票代碼（例如：TD.TO / AAPL）", value="TD.TO").upper()
put_lots = st.number_input("輸入 Put 模擬口數", min_value=1, max_value=20, value=5, step=1)
exp_date = st.date_input("模擬履約日期", value=datetime.date.today() + datetime.timedelta(days=30))

if symbol:
    ticker = yf.Ticker(symbol)
    try:
        info = ticker.info
        data = ticker.history(period="6mo")
        current = data["Close"].iloc[-1]
        change = round(current - data["Close"].iloc[-2], 2)
        change_pct = round((change / data["Close"].iloc[-2]) * 100, 2)

        st.markdown(f"_Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")

        st.header("[ 即時報價 ]")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("股價", f"${current:.2f}", f"{change_pct}%")
            st.text(f"成交量: {int(data['Volume'].iloc[-1]):,}")
        with col2:
            st.text(f"開盤: ${data['Open'].iloc[-1]:.2f}")
            st.text(f"昨收: ${data['Close'].iloc[-2]:.2f}")

        st.divider()
        st.header("[ 技術指標圖表 ]")

        ma20_series = data['Close'].rolling(window=20).mean()
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi_series = 100 - (100 / (1 + rs))

        exp12 = data['Close'].ewm(span=12, adjust=False).mean()
        exp26 = data['Close'].ewm(span=26, adjust=False).mean()
        macd_line = exp12 - exp26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()

        low_min = data['Low'].rolling(window=9).min()
        high_max = data['High'].rolling(window=9).max()
        rsv = (data['Close'] - low_min) / (high_max - low_min) * 100
        k_line = rsv.ewm(com=2).mean()
        d_line = k_line.ewm(com=2).mean()

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(data.index, data['Close'], label='Close Price')
        ax.plot(ma20_series, label='MA20', linestyle='--')
        ax.set_title(f"{symbol} 股價與 MA20")
        ax.legend()
        st.pyplot(fig)

        fig2, ax2 = plt.subplots(figsize=(10, 2))
        ax2.plot(rsi_series, label="RSI", color="orange")
        ax2.axhline(70, color='red', linestyle='--')
        ax2.axhline(30, color='green', linestyle='--')
        ax2.set_title("RSI 指標")
        st.pyplot(fig2)

        fig3, ax3 = plt.subplots(figsize=(10, 2))
        ax3.plot(macd_line, label='MACD', color='blue')
        ax3.plot(signal_line, label='Signal', color='red', linestyle='--')
        ax3.axhline(0, color='gray', linestyle=':')
        ax3.set_title("MACD 指標")
        ax3.legend()
        st.pyplot(fig3)

        fig4, ax4 = plt.subplots(figsize=(10, 2))
        ax4.plot(k_line, label='K', color='green')
        ax4.plot(d_line, label='D', color='purple')
        ax4.axhline(80, color='red', linestyle='--')
        ax4.axhline(20, color='blue', linestyle='--')
        ax4.set_title("KD 指標")
        ax4.legend()
        st.pyplot(fig4)

        rsi = rsi_series.iloc[-1]
        ma20 = ma20_series.iloc[-1]
        macd_trend = "多方趨勢" if current > ma20 else "盤整/偏空"

        st.text(f"MA20: ${ma20:.2f}    RSI: {rsi:.1f}    MACD: {macd_trend}")

        st.divider()
        st.header("[ 期權模擬：多履約價賣出 Put ]")

        put_rows = []
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        for pct in [0.95, 0.975, 1.0, 1.025]:
            strike_price = round(current * pct, 2)
            premium = round(1.0 + (1.05 - pct) * 3.5, 2)
            capital_req = strike_price * 100 * put_lots * 0.8
            total_income = premium * 100 * put_lots
            return_rate = total_income / capital_req * 100
            put_rows.append({
                "日期": today_str,
                "履約日": exp_date.strftime("%Y-%m-%d"),
                "履約價": f"${strike_price}",
                "權利金": f"${premium}",
                f"總收入({put_lots}口)": f"${total_income:.0f}",
                "保證金需求": f"${capital_req:,.0f}",
                "報酬率": f"{return_rate:.2f}%"
            })

        st.table(pd.DataFrame(put_rows))

        st.divider()
        st.header("[ AI 建議 ]")

        try:
            ai_comment = ""
            summary_score = 0

            # RSI 分析
            if rsi > 70:
                ai_comment += f"🔺 RSI > 70：{symbol} 處於超買區，可能出現拉回修正，建議保守觀望或分批停利。\n"
                summary_score -= 1
            elif rsi < 30:
                ai_comment += f"🔻 RSI < 30：{symbol} 處於超賣區，技術面可能反彈，Put Sell 策略具吸引力。\n"
                summary_score += 1
            else:
                ai_comment += f"➤ RSI 在中性區 ({rsi:.1f})，觀察是否轉強或失守 MA20 (${ma20:.2f})。\n"

            # MACD 分析
            macd_diff = macd_line.iloc[-1] - signal_line.iloc[-1]
            if macd_diff > 0 and macd_line.iloc[-1] > 0:
                ai_comment += "✅ MACD 處於多頭排列，趨勢偏多。\n"
                summary_score += 1
            elif macd_diff < 0 and macd_line.iloc[-1] < 0:
                ai_comment += "⚠️ MACD 處於空頭排列，建議保守操作。\n"
                summary_score -= 1
            else:
                ai_comment += "🔄 MACD 處於轉折點附近，需觀察方向明朗化。\n"

            # KD 指標分析
            k_val = k_line.iloc[-1]
            d_val = d_line.iloc[-1]
            if k_val > 80 and d_val > 80:
                ai_comment += "🔺 KD 高檔鈍化，短線漲多須防回落。\n"
                summary_score -= 1
            elif k_val < 20 and d_val < 20:
                ai_comment += "🔻 KD 低檔鈍化，可能進入反彈階段，可考慮進場。\n"
                summary_score += 1
            else:
                ai_comment += f"➤ KD 中性 (K={k_val:.1f}, D={d_val:.1f})，等待轉折明確訊號。\n"

            # MA 趨勢分析
            if current > ma20:
                ai_comment += "📈 價格站上 MA20，技術面維持偏多格局。\n"
                summary_score += 1
            else:
                ai_comment += "📉 價格低於 MA20，短線弱勢，建議保守。\n"
                summary_score -= 1

            st.info(ai_comment)

            # 綜合策略建議
            st.subheader("策略等級判斷：")
            if summary_score >= 2:
                st.success("✅ 綜合建議：積極建倉（偏多）")
            elif summary_score <= -2:
                st.error("⚠️ 綜合建議：保守觀望（偏空）")
            else:
                st.warning("➤ 綜合建議：中性偏觀望，留意轉折")

        except Exception as e:
            st.warning("⚠️ 無法進行 AI 分析，可能資料不足或格式異常。請確認股票代碼正確，並重新載入頁面。")
