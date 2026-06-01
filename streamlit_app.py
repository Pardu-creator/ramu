from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


BASE_DIR = Path(__file__).resolve().parent
COMPANY_FILE = BASE_DIR / "nifty500_companies.csv"
CLIENT_FILE = BASE_DIR / "stock_clients.csv"
MUTUAL_FUND_FILE = BASE_DIR / "mutual_funds.csv"
WATCHLIST_FILE = BASE_DIR / "watchlist.json"

VALID_RANGES = ["1D", "5D", "1M", "3M", "1Y"]
FALLBACK_STOCKS = {
    "RELIANCE": {"company_name": "Reliance Industries Limited", "ticker": "RELIANCE.NS", "clients": {}},
    "TCS": {"company_name": "Tata Consultancy Services Limited", "ticker": "TCS.NS", "clients": {}},
    "INFY": {"company_name": "Infosys Limited", "ticker": "INFY.NS", "clients": {}},
    "HDFCBANK": {"company_name": "HDFC Bank Limited", "ticker": "HDFCBANK.NS", "clients": {}},
    "ICICIBANK": {"company_name": "ICICI Bank Limited", "ticker": "ICICIBANK.NS", "clients": {}},
    "SBIN": {"company_name": "State Bank of India", "ticker": "SBIN.NS", "clients": {}},
    "LT": {"company_name": "Larsen & Toubro Limited", "ticker": "LT.NS", "clients": {}},
    "ITC": {"company_name": "ITC Limited", "ticker": "ITC.NS", "clients": {}},
}


st.set_page_config(page_title="Stock Intelligence", page_icon=":chart_with_upwards_trend:", layout="wide")

st.markdown(
    """
    <style>
      .main .block-container { padding-top: 1.4rem; padding-bottom: 2rem; }
      [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #d8e0ea;
        border-radius: 8px;
        padding: 0.8rem 1rem;
      }
      .subtle { color: #64748b; margin-top: -0.35rem; }
      .stock-title { color: #152033; font-size: 1.85rem; font-weight: 750; margin: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)


def normalize_symbol(symbol: str) -> str:
    return symbol.upper().strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(mode="r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


@st.cache_data(show_spinner=False)
def load_stocks() -> dict[str, dict[str, Any]]:
    companies: dict[str, dict[str, Any]] = {}

    for row in read_csv(COMPANY_FILE):
        symbol = normalize_symbol(row.get("company_symbol", ""))
        if symbol:
            companies[symbol] = {
                "company_name": row.get("company_name", "").strip(),
                "ticker": row.get("ticker", "").strip(),
                "clients": {},
            }

    for row in read_csv(CLIENT_FILE):
        symbol = normalize_symbol(row.get("company_symbol", ""))
        if symbol not in companies:
            continue
        client_name = row.get("client_name", "").strip()
        client_ticker = row.get("client_ticker", "").strip()
        if client_name and client_ticker:
            companies[symbol]["clients"][client_name] = client_ticker

    return companies or FALLBACK_STOCKS


@st.cache_data(show_spinner=False)
def load_mutual_funds() -> pd.DataFrame:
    if not MUTUAL_FUND_FILE.exists():
        return pd.DataFrame(columns=["scheme_code", "amc", "category", "scheme_name", "nav", "nav_date"])
    funds = pd.read_csv(MUTUAL_FUND_FILE, dtype={"scheme_code": str})
    funds["nav"] = pd.to_numeric(funds["nav"], errors="coerce")
    return funds


def load_watchlist() -> list[str]:
    if not WATCHLIST_FILE.exists():
        return []
    try:
        data = json.loads(WATCHLIST_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return [normalize_symbol(item) for item in data if isinstance(item, str) and item.strip()] if isinstance(data, list) else []


def save_watchlist(watchlist: list[str]) -> None:
    unique_symbols = sorted(set(normalize_symbol(item) for item in watchlist if item.strip()))
    WATCHLIST_FILE.write_text(json.dumps(unique_symbols, indent=2), encoding="utf-8")


def get_chart_settings(range_key: str) -> dict[str, str]:
    settings = {
        "1D": {"period": "1d", "interval": "5m"},
        "5D": {"period": "5d", "interval": "15m"},
        "1M": {"period": "1mo", "interval": "1d"},
        "3M": {"period": "3mo", "interval": "1d"},
        "1Y": {"period": "1y", "interval": "1d"},
    }
    return settings.get(range_key.upper(), settings["1D"])


@st.cache_data(ttl=90, show_spinner=False)
def get_live_quote(ticker: str) -> dict[str, Any]:
    quote = {
        "price": None,
        "previous_close": None,
        "change": None,
        "change_percent": None,
        "currency": "INR",
        "market_state": None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        stock = yf.Ticker(ticker)
        fast_info = stock.fast_info
        price = fast_info.get("last_price")
        previous_close = fast_info.get("previous_close")
        currency = fast_info.get("currency")
        market_state = fast_info.get("market_state")

        if not price:
            history = stock.history(period="5d", interval="5m")
            if not history.empty:
                price = float(history["Close"].iloc[-1])
                previous_close = previous_close or float(history["Close"].iloc[0])

        if price:
            quote["price"] = round(float(price), 2)
        if previous_close:
            quote["previous_close"] = round(float(previous_close), 2)
        if quote["price"] is not None and quote["previous_close"]:
            change = quote["price"] - quote["previous_close"]
            quote["change"] = round(change, 2)
            quote["change_percent"] = round((change / quote["previous_close"]) * 100, 2)
        if currency:
            quote["currency"] = currency
        if market_state:
            quote["market_state"] = market_state
    except Exception:
        pass
    return quote


@st.cache_data(ttl=90, show_spinner=False)
def get_chart_data(ticker: str, range_key: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    try:
        settings = get_chart_settings(range_key)
        history = yf.Ticker(ticker).history(period=settings["period"], interval=settings["interval"])
        if history.empty:
            history = yf.Ticker(ticker).history(period="1mo", interval="1d")
    except Exception:
        history = pd.DataFrame()

    if history.empty:
        return pd.DataFrame(), {}

    chart = history.tail(90).reset_index()
    chart = chart.rename(columns={chart.columns[0]: "time"})
    chart["time"] = pd.to_datetime(chart["time"]).dt.tz_localize(None)
    first_close = float(chart["Close"].iloc[0])
    last_close = float(chart["Close"].iloc[-1])
    change = round(last_close - first_close, 2)

    return chart, {
        "open": round(float(chart["Open"].iloc[0]), 2),
        "high": round(float(chart["High"].max()), 2),
        "low": round(float(chart["Low"].min()), 2),
        "close": round(last_close, 2),
        "change": change,
        "change_percent": round((change / first_close) * 100, 2) if first_close else 0,
        "volume": int(chart["Volume"].sum()) if "Volume" in chart else 0,
    }


@st.cache_data(ttl=600, show_spinner=False)
def get_news(stock: str) -> list[dict[str, str]]:
    try:
        query = quote_plus(f"{stock} stock market india")
        request = Request(f"https://news.google.com/rss/search?q={query}", headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=10) as response:
            root = ET.fromstring(response.read())
        items = []
        for item in root.findall("./channel/item")[:6]:
            title = item.findtext("title", default="").strip()
            link = item.findtext("link", default="").strip()
            if title and link:
                items.append({"title": title, "link": link})
        return items
    except Exception:
        return []


def stock_table(stocks: dict[str, dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "symbol": symbol,
                "company_name": stock["company_name"],
                "ticker": stock["ticker"],
                "client_count": len(stock["clients"]),
            }
            for symbol, stock in sorted(stocks.items())
        ]
    )


def format_money(value: Any, currency: str = "INR") -> str:
    if not isinstance(value, (int, float)):
        return "--"
    prefix = "Rs" if currency == "INR" else currency
    return f"{prefix} {value:,.2f}"


def format_volume(value: Any) -> str:
    if not isinstance(value, (int, float)):
        return "--"
    if value >= 10_000_000:
        return f"{value / 10_000_000:.2f} Cr"
    if value >= 100_000:
        return f"{value / 100_000:.2f} L"
    return f"{value:,.0f}"


def render_price_chart(chart: pd.DataFrame, title: str) -> None:
    if chart.empty:
        st.info("No chart data was available for this range.")
        return
    rising = chart["Close"].iloc[-1] >= chart["Close"].iloc[0]
    line_color = "#0f766e" if rising else "#b42318"
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=chart["time"],
            y=chart["Close"],
            mode="lines",
            line={"color": line_color, "width": 2.5},
            fill="tozeroy",
            fillcolor="rgba(15, 118, 110, 0.10)" if rising else "rgba(180, 35, 24, 0.08)",
            hovertemplate="%{x}<br>Close: Rs %{y:,.2f}<extra></extra>",
            name="Close",
        )
    )
    figure.update_layout(
        title=title,
        height=420,
        margin={"l": 10, "r": 10, "t": 46, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        xaxis={"showgrid": False},
        yaxis={"gridcolor": "#e7edf5", "tickprefix": "Rs "},
    )
    st.plotly_chart(figure, width="stretch")


def main() -> None:
    stocks = load_stocks()
    stocks_df = stock_table(stocks)
    watchlist = load_watchlist()

    st.title("Stock Intelligence")
    st.caption("Indian equities dashboard with quotes, charts, news, watchlist, and mutual fund search.")

    with st.sidebar:
        st.header("Controls")
        search_query = st.text_input("Search stocks", placeholder="Symbol, company, or ticker")
        client_only = st.checkbox("Only stocks with listed clients")
        range_key = st.segmented_control("Chart range", VALID_RANGES, default="1D")

        filtered = stocks_df.copy()
        if search_query:
            query = search_query.strip().lower()
            filtered = filtered[
                filtered["symbol"].str.lower().str.contains(query, regex=False)
                | filtered["company_name"].str.lower().str.contains(query, regex=False)
                | filtered["ticker"].str.lower().str.contains(query, regex=False)
            ]
        if client_only:
            filtered = filtered[filtered["client_count"] > 0]
        if filtered.empty:
            st.warning("No matching stocks found.")
            filtered = stocks_df

        selected_symbol = st.selectbox(
            "Selected stock",
            filtered["symbol"].tolist(),
            format_func=lambda symbol: f"{symbol} - {stocks[symbol]['company_name']}",
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Refresh", width="stretch"):
                get_live_quote.clear()
                get_chart_data.clear()
                get_news.clear()
                st.rerun()
        with col_b:
            if selected_symbol in watchlist:
                if st.button("Remove", width="stretch"):
                    save_watchlist([item for item in watchlist if item != selected_symbol])
                    st.rerun()
            elif st.button("Watch", width="stretch"):
                save_watchlist(watchlist + [selected_symbol])
                st.rerun()

    stock = stocks[selected_symbol]
    quote = get_live_quote(stock["ticker"])
    chart, stats = get_chart_data(stock["ticker"], range_key)

    st.markdown(f"<p class='stock-title'>{stock['company_name']}</p>", unsafe_allow_html=True)
    st.markdown(
        f"<p class='subtle'>{selected_symbol} - {stock['ticker']} - {quote.get('market_state') or 'Market state unavailable'}</p>",
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(5)
    metric_cols[0].metric("Price", format_money(quote["price"], quote["currency"]))
    metric_cols[1].metric(
        "Quote change",
        format_money(quote["change"], quote["currency"]),
        f"{quote['change_percent']}%" if isinstance(quote["change_percent"], (int, float)) else None,
    )
    metric_cols[2].metric("Range high", format_money(stats.get("high")))
    metric_cols[3].metric("Range low", format_money(stats.get("low")))
    metric_cols[4].metric("Volume", format_volume(stats.get("volume")))

    render_price_chart(chart, f"{selected_symbol} price trend - {range_key}")

    tab_overview, tab_clients, tab_screener, tab_funds, tab_news = st.tabs(
        ["Overview", "Listed Clients", "Stock Screener", "Mutual Funds", "Market News"]
    )

    with tab_overview:
        st.subheader("Range stats")
        st.dataframe(
            pd.DataFrame(
                [
                    {"Metric": "Open", "Value": format_money(stats.get("open"))},
                    {"Metric": "Close", "Value": format_money(stats.get("close"))},
                    {"Metric": "High", "Value": format_money(stats.get("high"))},
                    {"Metric": "Low", "Value": format_money(stats.get("low"))},
                    {"Metric": "Range change", "Value": f"{stats.get('change', '--')} ({stats.get('change_percent', '--')}%)"},
                    {"Metric": "Client links", "Value": str(len(stock["clients"]))},
                ]
            ),
            width="stretch",
            hide_index=True,
        )
        if not watchlist:
            st.info("No stocks are on the watchlist yet.")
        else:
            watched = stocks_df[stocks_df["symbol"].isin(watchlist)][["symbol", "company_name", "ticker"]]
            st.dataframe(watched, width="stretch", hide_index=True)

    with tab_clients:
        clients = stock["clients"]
        if not clients:
            st.info("No verified listed clients are available for this stock.")
        else:
            rows = []
            for client_name, client_ticker in clients.items():
                client_quote = get_live_quote(client_ticker)
                rows.append(
                    {
                        "Client": client_name,
                        "Ticker": client_ticker,
                        "Price": format_money(client_quote["price"], client_quote["currency"]),
                        "Change %": client_quote["change_percent"],
                    }
                )
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    with tab_screener:
        st.dataframe(filtered.head(100), width="stretch", hide_index=True)

    with tab_funds:
        funds = load_mutual_funds()
        fund_query = st.text_input("Search AMC, scheme, category, or code")
        if fund_query and not funds.empty:
            query = fund_query.strip().lower()
            funds = funds[
                funds["scheme_code"].str.lower().str.contains(query, regex=False)
                | funds["scheme_name"].str.lower().str.contains(query, regex=False)
                | funds["amc"].str.lower().str.contains(query, regex=False)
                | funds["category"].str.lower().str.contains(query, regex=False)
            ]
        if funds.empty:
            st.info("Add mutual_funds.csv to this folder to enable mutual fund search.")
        else:
            st.caption(f"{len(funds):,} matching funds")
            st.dataframe(funds.head(100), width="stretch", hide_index=True)

    with tab_news:
        news = get_news(selected_symbol)
        if not news:
            st.info("No headlines were available right now.")
        for item in news:
            st.markdown(f"[{item['title']}]({item['link']})")

    st.caption("Market data is provided by Yahoo Finance through yfinance. News is loaded from Google News RSS.")


if __name__ == "__main__":
    main()
