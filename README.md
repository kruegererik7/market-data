# market-data

Daily total-return snapshot for a set of sector and asset-class ETFs.

A [GitHub Actions workflow](.github/workflows/daily-returns.yml) runs on
weekday mornings (11:00 UTC, after all major markets have closed for the
day) and on manual dispatch. It executes [`update_returns.py`](update_returns.py),
which pulls dividend-adjusted closing prices from Yahoo Finance (via
`yfinance`) for:

- **Sectors**: the 11 S&P 500 sector SPDR ETFs (XLE, XLK, XLV, XLB, XLI,
  XLP, XLRE, XLC, XLF, XLY, XLU)
- **Asset classes**: a mix of equity, bond, and alternative ETFs (SPY, IJH,
  IWM, EFA, EEM, AGG, TLT, TIP, HYG, BNDX, BIL, VNQ, DBC, GLD)

For each ticker it computes YTD, 3-month, and 6-month total return, plus
annualized 3/5/10-year total returns, and writes the result to
[`data/returns.csv`](data/returns.csv), which the workflow commits back to
the repo automatically.

## Running locally

```bash
pip install yfinance pandas
python update_returns.py
```
