# WRDS-to-LEAN Data Pipeline

Pulls market data from [WRDS](https://wrds-www.wharton.upenn.edu/) (CRSP, Compustat, and more), converts it to [QuantConnect LEAN](https://github.com/QuantConnect/Lean) format, and publishes to `lean-data/` so local backtests and research notebooks have complete, clean data.

## What it produces

| Output | Source | Coverage |
|--------|--------|----------|
| Daily equity bars (OHLCV) | CRSP `dsf` | 1926–present |
| Split & dividend factor files | CRSP `dsedist` | full history |
| Ticker map files | CRSP `dsenames` | full history |
| DIA ETF constituent universe | CRSP `holdings` | 2002–present |
| GICS → Morningstar sector map | Compustat `company` | current |
| Point-in-time Piotroski F-scores | Compustat `funda` | 1950–present |
| FX and interest rates | FRB `fx_daily`, `rates_daily` | 1971–present |
| Fama-French factors | `ff.factors_daily`, `ff.fivefactors_daily` | 1926–present |
| Global factor panel | `contrib_global_factor.global_factor` | 1925–present |
| 13F ownership | `tr_13f.s34` | quarterly holdings |
| Financial ratios | `wrdsapps_finratio.firm_ratio` | precomputed ratios |
| Credit data | Markit CDS, TRACE | CDS and bond trade history |

All output lands in `lean-data/` in the exact directory/file structure LEAN expects for local backtests.

## Requirements

- Python 3.11+
- A WRDS account with access to CRSP and Compustat
- `~/.pgpass` entry for WRDS PostgreSQL (see [Credentials](#credentials))

```bash
pip install -r requirements.txt
```

## Credentials

WRDS uses PostgreSQL. Add your credentials to `~/.pgpass`:

```
wrds-pgdata.wharton.upenn.edu:9737:wrds:<your_username>:<your_password>
chmod 600 ~/.pgpass
```

### Multiple WRDS accounts

Copy `wrds_profiles.example.json` to `.wrds_profiles.json` (gitignored) and fill in your usernames:

```json
{
  "default_profile": "upenn",
  "profiles": {
    "upenn": {
      "username": "your_wrds_username",
      "hostname": "wrds-pgdata.wharton.upenn.edu",
      "port": 9737,
      "dbname": "wrds"
    }
  }
}
```

Pass `--profile <name>` to any pipeline script to select a profile, or set `WRDS_PROFILE=<name>` in the environment.

## Usage

```bash
# Daily equity bars (CRSP)
python scripts/run_pipeline.py                            # full universe
python scripts/run_pipeline.py --tickers AAPL MSFT        # specific tickers
python scripts/run_pipeline.py --start 1998-01-01 --end 2026-01-01
python scripts/run_pipeline.py --validate                  # compare against reference data

# ETF constituent universe (DIA)
python scripts/run_etf_pipeline.py
python scripts/run_etf_pipeline.py --start 2018-01-01 --end 2023-01-01

# Sector classification
python scripts/run_sector_pipeline.py
python scripts/run_sector_pipeline.py --include-dia-history

# Piotroski F-scores
python scripts/run_fundamentals_pipeline.py
python scripts/run_fundamentals_pipeline.py --tickers AAPL MSFT GS
python scripts/run_fundamentals_pipeline.py --start-year 2000

# Macro, FX, and factor data
python scripts/run_macro_pipeline.py --start 2000-01-01
python scripts/run_macro_pipeline.py --fx --rates --start 2020-01-01
python scripts/run_macro_pipeline.py --global-factor --countries USA --start 2024-01-31 --end 2024-01-31 --limit 1000

# Institutional ownership
python scripts/run_13f_pipeline.py --tickers AAPL MSFT --start 2020-01-01 --summary-only

# WRDS precomputed financial ratios
python scripts/run_finratio_pipeline.py --tickers AAPL MSFT GS --start 2000-01-01

# Credit data
python scripts/run_credit_pipeline.py --cds --tickers GE IBM JPM --start 2024-01-01 --end 2024-01-31
python scripts/run_credit_pipeline.py --trace --tickers AAPL --start 2024-01-02 --end 2024-01-05 --limit 1000
python scripts/run_credit_pipeline.py --trace --grades investment_grade --start 2024-01-02 --end 2024-01-05 --limit 1000
```

All scripts accept `--profile <name>` to select a WRDS account.

## Output structure

```
lean-data/
├── equity/usa/daily/{ticker}.zip          # OHLCV bars
├── equity/usa/factor_files/{ticker}.csv   # split + dividend adjustments
├── equity/usa/map_files/{ticker}.csv      # ticker history
├── equity/usa/universes/etf/dia/          # daily DIA constituent files
├── alternative/sectors/sector_map.csv     # Morningstar sector codes
├── alternative/fundamentals/
│   ├── piotroski_scores.csv              # point-in-time F-scores (0–9)
│   └── wrds_financial_ratios.csv         # WRDS precomputed ratios
├── alternative/earnings/
│   ├── ibes_consensus.csv
│   └── ibes_surprise.csv
├── alternative/macro/
│   ├── frb_fx_daily.csv
│   └── frb_rates_daily.csv
├── alternative/factors/
│   ├── ff_factors_daily.csv
│   ├── ff_fivefactors_daily.csv
│   └── global_factor.csv
├── alternative/ownership/
│   ├── 13f_holdings.csv
│   └── 13f_summary.csv
├── alternative/credit/
│   ├── markit_cds.csv
│   ├── trace_trades.csv
│   └── trace_enhanced_trades.csv
├── market-hours/market-hours-database.json
└── symbol-properties/symbol-properties-database.csv
```

To use this data in a local LEAN backtest, point `lean.json` at the `lean-data/` directory:

```json
"data-folder": "/path/to/WRDS/lean-data"
```

## Universe

The default universe is a **30-stock Dow Jones-style large-cap basket** plus SPY and SGOV:

AAPL, AMGN, AXP, BA, CAT, CRM, CSCO, CVX, DIS, DOW, GS, HD, HON, IBM, INTC, JNJ, JPM, KO, MCD, MMM, MRK, MSFT, NKE, PG, TRV, UNH, V, VZ, WBA, WMT, SPY, SGOV

Defined in `src/wrds_lean/symbols.py`.

## Data sources

Full catalogue of available WRDS data (tables, row counts, key columns, join patterns) is in [data_sources.md](data_sources.md).

## Project layout

```
src/wrds_lean/
├── connection.py       # WRDS DB connection + multi-profile support
├── symbols.py          # Universe list + PERMNO resolution
├── extract.py          # SQL queries against CRSP tables
├── transform.py        # CRSP → LEAN format conversion
├── publish.py          # Write zips, factor files, map files
├── sid.py              # LEAN SecurityIdentifier generation
├── etf_constituents.py # DIA constituent extraction
├── sectors.py          # GICS → Morningstar sector mapping
├── fundamentals.py     # Piotroski F-score pipeline
├── macro.py            # FRB, Fama-French, global factor exports
├── ownership.py        # 13F holdings and summary exports
├── ratios.py           # WRDS financial ratio exports
└── credit.py           # Markit CDS and TRACE exports

scripts/
├── run_pipeline.py             # Daily equity pipeline
├── run_etf_pipeline.py         # ETF constituent pipeline
├── run_sector_pipeline.py      # Sector classification pipeline
├── run_fundamentals_pipeline.py # Piotroski F-score pipeline
├── run_macro_pipeline.py       # Macro, FX, and factor exports
├── run_13f_pipeline.py         # 13F ownership exports
├── run_finratio_pipeline.py    # WRDS financial ratio exports
├── run_credit_pipeline.py      # Markit CDS and TRACE exports
└── compare_tables.py           # Diagnostic: compare CRSP table variants
```

## Known limitations

- OHLC uses quote-based proxies (`askhi`/`bidlo`) — negligible for large-caps
- SGOV (launched 2020) may be missing from CRSP for earlier dates
- Local backtests will warn about missing `equity/usa/hour/spy.zip` and `alternative/interest-rate/usa/interest-rate.csv` — both are non-critical (LEAN falls back gracefully)
- US equity options are not available through this pipeline; use QuantConnect cloud for options strategies
