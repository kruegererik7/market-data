"""Daily total-return table for sector and asset-class ETFs.

Uses dividend-adjusted closes from Yahoo Finance (via yfinance), so every
figure is a total return. 3/5/10-year returns are annualized.
Output: data/returns.csv
"""
import os

import pandas as pd
import yfinance as yf

SECTORS = {
    "XLE": "Energy",
    "XLK": "Technology",
    "XLV": "Health Care",
    "XLB": "Materials",
    "XLI": "Industrials",
    "XLP": "Consumer Staples",
    "XLRE": "Real Estate",
    "XLC": "Communication Services",
    "XLF": "Financials",
    "XLY": "Consumer Discretionary",
    "XLU": "Utilities",
}

ASSETS = {
    "SPY": "US Large Cap",
    "IJH": "US Mid Cap",
    "IWM": "US Small Cap",
    "EFA": "Intl Developed",
    "EEM": "Emerging Markets",
    "AGG": "US Aggregate Bond",
    "TLT": "Long Treasury (20+ yr)",
    "TIP": "TIPS",
    "HYG": "High Yield",
    "BNDX": "Intl Bonds (USD hedged)",
    "BIL": "Cash (T-Bills)",
    "VNQ": "REITs",
    "DBC": "Commodities",
    "GLD": "Gold",
}


def price_on_or_before(s, date):
    """Last available price on or before a date (handles weekends/holidays)."""
    s = s.loc[:date]
    return s.iloc[-1] if len(s) else None


def calc_return(s, end_price, start_date, years=None):
    """Total return from start_date to the as-of date, in percent.
    Returns None if the fund doesn't have enough history."""
    if s.index[0] > start_date:
        return None
    start_price = price_on_or_before(s, start_date)
    if start_price is None or start_price == 0:
        return None
    growth = end_price / start_price
    if years:
        growth = growth ** (1 / years)
    return round((growth - 1) * 100, 2)


def main():
    tickers = list(SECTORS) + list(ASSETS)
    start = pd.Timestamp.today().normalize() - pd.DateOffset(years=10, months=1)

    data = yf.download(
        tickers,
        start=start.strftime("%Y-%m-%d"),
        auto_adjust=True,  # adjusts for dividends and splits -> total return
        progress=False,
    )["Close"]

    # As-of date = most recent day where every ticker has a price
    as_of = data.dropna(how="any").index[-1]
    ytd_base = pd.Timestamp(year=as_of.year - 1, month=12, day=31)

    rows = []
    for group, names in (("Sector", SECTORS), ("Asset Class", ASSETS)):
        for ticker, name in names.items():
            s = data[ticker].dropna()
            end = s.loc[as_of]
            rows.append({
                "group": group,
                "ticker": ticker,
                "name": name,
                "as_of": as_of.strftime("%Y-%m-%d"),
                "ytd": calc_return(s, end, ytd_base),
                "3m": calc_return(s, end, as_of - pd.DateOffset(months=3)),
                "6m": calc_return(s, end, as_of - pd.DateOffset(months=6)),
                "3y_ann": calc_return(s, end, as_of - pd.DateOffset(years=3), 3),
                "5y_ann": calc_return(s, end, as_of - pd.DateOffset(years=5), 5),
                "10y_ann": calc_return(s, end, as_of - pd.DateOffset(years=10), 10),
            })

    df = pd.DataFrame(rows).sort_values(
        ["group", "ytd"], ascending=[False, False]  # Sectors first, then by YTD
    )
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/returns.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
