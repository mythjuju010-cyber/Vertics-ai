import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="VERTICS AI - AI Trading Made Easy", page_icon="📈", layout="wide")

st.title("📈 VERTICS AI")
st.subheader("AI trading made easy")
st.write("Live market data • AI signals • Smart dashboard")

# Sidebar
st.sidebar.header("⚙️ Settings")
symbol = st.sidebar.selectbox("Choose Asset", ["BTC-USD", "ETH-USD", "EURUSD=X", "AAPL", "TSLA", "GBPUSD=X", "XAUUSD=X"], index=0)
period = st.sidebar.selectbox("Timeframe", ["1d", "5d", "1mo", "3mo", "6mo", "1y"], index=2)
risk = st.sidebar.slider("Risk Level", 1, 10, 5)
balance = st.sidebar.number_input("Account Balance ($)", value=1000.0)

if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

# Load data
@st.cache_data(ttl=60)
def load_data(sym, per):
    df = yf.download(sym, period=per, interval="1d", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

try:
    df = load_data(symbol, period)
    if df.empty:
        st.error("No data found. Try another asset.")
        st.stop()

    # Indicators
    df['SMA20'] = df['Close'].rolling(20).mean()
    df['SMA50'] = df['Close'].rolling(50).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    last_price = float(df['Close'].iloc[-1])
    prev_price = float(df['Close'].iloc[-2])
    change = ((last_price - prev_price) / prev_price) * 100
    rsi = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50

    # AI Signal Logic
    if rsi < 30:
        signal = "🟢 STRONG BUY"
        color = "green"
    elif rsi < 45:
        signal = "🟢 BUY"
        color = "green"
    elif rsi > 70:
        signal = "🔴 STRONG SELL"
        color = "red"
    elif rsi > 55:
        signal = "🔴 SELL"
        color = "red"
    else:
        signal = "🟡 HOLD"
        color = "orange"

    # Top metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"{symbol} Price", f"${last_price:,.2f}", f"{change:+.2f}%")
    c2.metric("RSI (14)", f"{rsi:.1f}")
    c3.metric("AI Signal", signal)
    c4.metric("Suggested Lot", f"${balance * risk / 100:,.0f}")

    st.markdown(f"### AI Verdict: :{color}[{signal}]")

    # Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='blue', width=1), name="SMA 20"))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='orange', width=1), name="SMA 50"))
    fig.update_layout(height=450, xaxis_rangeslider_visible=False, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # Table
    st.subheader("📊 Recent Data")
    st.dataframe(df.tail(10).sort_index(ascending=False), use_container_width=True)

    st.info(f"💡 VERTICS AI Analysis for {symbol}: Price is ${last_price:,.2f}. RSI is {rsi:.1f}. If RSI is below 30, market is oversold (good to buy). If above 70, overbought (good to sell). Always use stop-loss!")

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.write("Try refreshing or choosing another asset.")

st.markdown("---")
st.caption("VERTICS AI • Built for traders • Not financial advice. Trade responsibly.")
