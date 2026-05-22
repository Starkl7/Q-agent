"""
pipeline.py — fetch SEC EDGAR fundamentals for the 30-stock equity universe.

Outputs:
  MyProjects/data/edgar/fundamentals_annual.csv   — annual (10-K) data
  MyProjects/data/edgar/fundamentals_quarterly.csv — quarterly (10-Q) data (if --quarterly flag)

Usage:
  cd ~/Documents/Q-agent && source venv/bin/activate
  python infrastructure/edgar/pipeline.py
  python infrastructure/edgar/pipeline.py --quarterly   # also fetch quarterly
  python infrastructure/edgar/pipeline.py --tickers AAPL MSFT  # subset
"""

import argparse
import time
from pathlib import Path

import os

import edgar
import pandas as pd

# SEC EDGAR requires a user-agent identity ("Name email@domain"). Set the
# SEC_EDGAR_IDENTITY env var to your own before running, or edit the fallback.
# Using a real identity that you control is required by SEC policy.
IDENTITY = os.environ.get("SEC_EDGAR_IDENTITY", "Your Name your.email@example.com")

EQUITY_UNIVERSE = [
    "AAPL", "AMGN", "AXP", "BA", "CAT", "CRM",
    "CSCO", "CVX", "DIS", "DOW", "GS", "HD",
    "HON", "IBM", "INTC", "JNJ", "JPM", "KO",
    "MCD", "MMM", "MRK", "MSFT", "NKE", "PG",
    "TRV", "UNH", "V", "VZ", "WBA", "WMT",
]

# Standard concepts to extract (subset that's broadly available across companies)
INCOME_CONCEPTS = [
    "Revenue",
    "GrossProfit",
    "OperatingIncomeLoss",
    "NetIncome",
    "SharesFullyDilutedAverage",
]
BALANCE_CONCEPTS = [
    "Assets",
    "Liabilities",
    "AllEquityBalance",
    "LongTermDebt",
    "CashAndMarketableSecurities",
]
CASHFLOW_CONCEPTS = [
    "NetCashFromOperatingActivities",
    "CapitalExpenses",
]

ALL_CONCEPTS = INCOME_CONCEPTS + BALANCE_CONCEPTS + CASHFLOW_CONCEPTS


def extract_metrics(df: pd.DataFrame, period_tag: str) -> list[dict]:
    """Pull standard_concept values from a statement DataFrame for all periods.

    Income/CF statements tag columns as '2025-09-27 (FY)'; balance sheets use '2025-09-27'.
    Both are handled here.
    """
    import re
    date_re = re.compile(r"^\d{4}-\d{2}-\d{2}")
    if period_tag:
        period_cols = [c for c in df.columns if f"({period_tag})" in c]
    else:
        period_cols = [c for c in df.columns if date_re.match(c)]
    rows = []
    for _, row in df[df["standard_concept"].notna()].iterrows():
        concept = row["standard_concept"]
        if concept not in ALL_CONCEPTS:
            continue
        for col in period_cols:
            val = row.get(col)
            if pd.notna(val):
                period_date = col.split(" ")[0]  # "2025-09-27 (FY)" → "2025-09-27"
                rows.append({"standard_concept": concept, "period": period_date, "value": val})
    return rows


def fetch_ticker(ticker: str, include_quarterly: bool) -> list[dict]:
    """Return list of metric dicts for one ticker. Returns [] on any error."""
    try:
        company = edgar.Company(ticker)
        records = []

        # Annual (10-K)
        fin = company.get_financials()
        for stmt_fn, tag in [
            (fin.income_statement, "FY"),
            (fin.balance_sheet, ""),   # balance sheet uses plain date columns
            (fin.cash_flow_statement, "FY"),
        ]:
            try:
                df = stmt_fn().to_dataframe()
                for r in extract_metrics(df, tag):
                    r["ticker"] = ticker
                    r["period_type"] = "annual"
                    records.append(r)
            except Exception:
                pass

        if include_quarterly:
            # 10-Q: fetch last 4 quarters
            filings = company.get_filings(form="10-Q")
            for filing in filings.latest(4):
                try:
                    f_fin = filing.financials
                    if f_fin is None:
                        continue
                    for stmt_fn, tag in [
                        (f_fin.income_statement, "Q"),
                        (f_fin.balance_sheet, ""),
                        (f_fin.cash_flow_statement, "Q"),
                    ]:
                        try:
                            df = stmt_fn().to_dataframe()
                            for r in extract_metrics(df, tag):
                                r["ticker"] = ticker
                                r["period_type"] = "quarterly"
                                records.append(r)
                        except Exception:
                            pass
                except Exception:
                    pass

        return records
    except Exception as exc:
        print(f"  [WARN] {ticker}: {exc}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Fetch EDGAR fundamentals for the 30-stock equity universe")
    parser.add_argument("--quarterly", action="store_true", help="Also fetch quarterly (10-Q) data")
    parser.add_argument("--tickers", nargs="+", default=EQUITY_UNIVERSE, help="Override universe")
    args = parser.parse_args()

    edgar.set_identity(IDENTITY)

    # __file__ = .../QuantConnect/infrastructure/edgar/pipeline.py → walk up 3 levels to workspace root
    out_dir = Path(__file__).resolve().parents[2] / "MyProjects" / "data" / "edgar"
    out_dir.mkdir(parents=True, exist_ok=True)

    all_records = []
    for i, ticker in enumerate(args.tickers):
        print(f"[{i+1}/{len(args.tickers)}] {ticker}...")
        records = fetch_ticker(ticker, args.quarterly)
        all_records.extend(records)
        if i < len(args.tickers) - 1:
            time.sleep(0.2)  # polite to EDGAR (max 10 req/s)

    if not all_records:
        print("No records fetched.")
        return

    df = pd.DataFrame(all_records)

    annual = df[df["period_type"] == "annual"].drop(columns="period_type")
    annual_wide = (
        annual.drop_duplicates(["ticker", "period", "standard_concept"])
        .pivot_table(index=["ticker", "period"], columns="standard_concept", values="value")
        .reset_index()
        .sort_values(["ticker", "period"])
    )
    annual_path = out_dir / "fundamentals_annual.csv"
    annual_wide.to_csv(annual_path, index=False)
    print(f"\nAnnual data saved: {annual_path} ({len(annual_wide)} rows)")

    if args.quarterly:
        quarterly = df[df["period_type"] == "quarterly"].drop(columns="period_type")
        quarterly_wide = (
            quarterly.drop_duplicates(["ticker", "period", "standard_concept"])
            .pivot_table(index=["ticker", "period"], columns="standard_concept", values="value")
            .reset_index()
            .sort_values(["ticker", "period"])
        )
        q_path = out_dir / "fundamentals_quarterly.csv"
        quarterly_wide.to_csv(q_path, index=False)
        print(f"Quarterly data saved: {q_path} ({len(quarterly_wide)} rows)")


if __name__ == "__main__":
    main()
