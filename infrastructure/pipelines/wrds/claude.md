# WRDS-to-LEAN Data Pipeline

## Purpose

Pull market data from WRDS (CRSP, Compustat), convert to LEAN format, and publish to `lean-data/` so local backtests and research notebooks have complete, up-to-date data for the local equity strategy universe.

## Universe

- **Equity universe (30 stocks)**: AAPL, AMGN, AXP, BA, CAT, CRM, CSCO, CVX, DIS, DOW, GS, HD, HON, IBM, INTC, JNJ, JPM, KO, MCD, MMM, MRK, MSFT, NKE, PG, TRV, UNH, V, VZ, WBA, WMT
- **Benchmarks**: SPY, SGOV (32 total)
- Defined in `src/wrds_lean/symbols.py`

## Project Structure

```
WRDS/
├── venv/                          # Python virtual environment
├── src/wrds_lean/
│   ├── connection.py              # WRDS DB connection (uses ~/.pgpass)
│   ├── symbols.py                 # Universe list + PERMNO resolution
│   ├── extract.py                 # SQL queries: crsp.dsf, dsedist, dsenames
│   ├── transform.py               # CRSP -> LEAN format conversion
│   ├── publish.py                 # Write zips, factor files, map files
│   ├── sid.py                     # LEAN SecurityIdentifier generation
│   ├── etf_constituents.py        # ETF constituent extraction (crsp.holdings)
│   ├── sectors.py                 # Sector classification (Compustat GICS -> Morningstar)
│   ├── fundamentals.py            # Piotroski F-score (comp.funda annual fundamentals)
│   ├── macro.py                   # FRB FX/rates, Fama-French, global factors
│   ├── ownership.py               # TR 13F holdings and summary data
│   ├── ratios.py                  # WRDS precomputed financial ratios
│   └── credit.py                  # Markit CDS and TRACE exports
├── scripts/
│   ├── compare_tables.py          # Compare crsp.dsf vs crsp.crsp_daily_data
│   ├── run_pipeline.py            # Daily equity pipeline CLI
│   ├── run_etf_pipeline.py        # ETF constituent universe CLI
│   ├── run_sector_pipeline.py     # Sector classification CLI
│   ├── run_fundamentals_pipeline.py  # Piotroski F-score pipeline CLI
│   ├── run_macro_pipeline.py      # Macro, FX, and factor data CLI
│   ├── run_13f_pipeline.py        # Institutional ownership CLI
│   ├── run_finratio_pipeline.py   # Financial ratios CLI
│   └── run_credit_pipeline.py     # CDS and TRACE CLI
├── data/raw/                      # Raw CRSP extracts (.gitignored)
└── lean-data/                     # LEAN output (.gitignored)
    ├── equity/usa/daily/          # {ticker}.zip containing {ticker}.csv
    ├── equity/usa/factor_files/   # {ticker}.csv
    ├── equity/usa/map_files/      # {ticker}.csv
    ├── equity/usa/universes/etf/  # ETF constituent universe files
    │   └── dia/{YYYYMMDD}.csv     # DIA daily constituent snapshots
    ├── alternative/sectors/       # Sector classification data
    │   └── sector_map.csv         # Ticker -> Morningstar sector mapping
    ├── alternative/fundamentals/  # Annual fundamental signals
    │   ├── piotroski_scores.csv   # Point-in-time Piotroski F-scores (0-9)
    │   └── wrds_financial_ratios.csv
    ├── alternative/macro/         # FRB FX and rates
    ├── alternative/factors/       # FF and global factors
    ├── alternative/ownership/     # 13F holdings and summaries
    ├── alternative/credit/        # CDS and TRACE exports
    ├── market-hours/              # market-hours-database.json
    └── symbol-properties/         # symbol-properties-database.csv
```

## Quick Start

```bash
cd ~/Documents/Q-agent/MyProjects/WRDS
source venv/bin/activate

# === Daily Equity Pipeline (CRSP) ===
python scripts/run_pipeline.py --tickers AAPL SPY --validate  # Specific tickers
python scripts/run_pipeline.py --validate                      # Full equity universe (30 stocks)
python scripts/run_pipeline.py --start 1998-01-01 --end 2026-04-18
python scripts/run_pipeline.py --profile new_university --tickers AAPL SPY

# === ETF Constituent Pipeline (CRSP Holdings) ===
python scripts/run_etf_pipeline.py                             # DIA, full date range
python scripts/run_etf_pipeline.py --profile new_university
python scripts/run_etf_pipeline.py --start 2018-01-01 --end 2019-01-01

# === Sector Classification Pipeline (Compustat) ===
python scripts/run_sector_pipeline.py                          # Full equity universe (30 stocks)
python scripts/run_sector_pipeline.py --profile new_university
python scripts/run_sector_pipeline.py --include-dia-history    # + historical DIA members
python scripts/run_sector_pipeline.py --tickers AAPL MSFT GS   # Specific tickers

# === Piotroski F-Score Pipeline (Compustat) ===
python scripts/run_fundamentals_pipeline.py                    # Full equity universe (30 stocks, excludes ETFs)
python scripts/run_fundamentals_pipeline.py --profile new_university
python scripts/run_fundamentals_pipeline.py --tickers AAPL MSFT GS   # Specific tickers
python scripts/run_fundamentals_pipeline.py --start-year 2000  # From 2000 onward

# === IBES Earnings Pipeline ===
python scripts/run_ibes_pipeline.py                            # Full equity universe (30 stocks)
python scripts/run_ibes_pipeline.py --tickers AAPL MSFT GS    # Specific tickers
python scripts/run_ibes_pipeline.py --start-year 2000          # From 2000 onward

# === Macro / FX / Factor Pipelines (default profile works) ===
python scripts/run_macro_pipeline.py --start 2000-01-01        # FX, rates, FF factors
python scripts/run_macro_pipeline.py --fx --rates --start 2020-01-01
python scripts/run_macro_pipeline.py --global-factor --countries USA --start 2024-01-31 --end 2024-01-31 --limit 1000

# === 13F Institutional Ownership Pipeline ===
python scripts/run_13f_pipeline.py --tickers AAPL MSFT --start 2020-01-01 --summary-only

# === WRDS Financial Ratios Pipeline ===
python scripts/run_finratio_pipeline.py --tickers AAPL MSFT GS --start 2000-01-01

# === Credit Data Pipeline ===
python scripts/run_credit_pipeline.py --cds --tickers GE IBM JPM --start 2024-01-01 --end 2024-01-31
python scripts/run_credit_pipeline.py --trace --tickers AAPL --start 2024-01-02 --end 2024-01-05 --limit 1000
python scripts/run_credit_pipeline.py --trace --grades investment_grade --start 2024-01-02 --end 2024-01-05 --limit 1000
```

## LEAN Data Formats

### Daily Bars (`equity/usa/daily/{ticker}.zip`)

Zip containing `{ticker}.csv`, no header:
```
YYYYMMDD 00:00,Open,High,Low,Close,Volume
19980102 00:00,136300,162500,135000,162500,6315000
```
- Prices scaled by 10,000 (integer deci-cents)
- Volume is raw shares

### Factor Files (`equity/usa/factor_files/{ticker}.csv`)

No header:
```
Date,PriceFactor,SplitFactor,ReferencePrice
19980102,0.8613657,0.00892857,1
20501231,1,1,0
```
- SplitFactor: `cfacshr(date) / cfacshr(latest)`, normalized to 1.0 at present
- PriceFactor: cumulative dividend adjustment, 1.0 at present
- ReferencePrice: close price before ex-date
- Sentinel row: `20501231,1,1,0`

### Map Files (`equity/usa/map_files/{ticker}.csv`)

No header:
```
Date,MappedSymbol,PrimaryExchange
19980102,aapl,Q
20501231,aapl,Q
```
- Exchange codes: N=NYSE, Q=NASDAQ, P=Arca, A=AMEX
- Sentinel row at end

## Data Sources

See [data_sources.md](data_sources.md) for the full catalogue of confirmed WRDS access — profiles, table inventory, key column references, CRSP–Compustat join pattern, and not-subscribed datasets.

Pipeline-specific notes for the tables used in each script:
- **Daily equity**: `crsp.dsf`, `crsp.dsedist`, `crsp.dsenames`
- **ETF constituents**: `crsp.holdings`, `crsp.fund_names`
- **Sector classification**: `comp.company` (`gsector`, `gind`), `comp.security`
- **Piotroski F-score**: `comp.funda` with `indfmt='INDL'`, `datafmt='STD'`, `popsrc='D'`, `consol='C'`; point-in-time via `pdate` (falls back to `datadate + 90 days`); ETFs excluded
- **IBES earnings**: `ibes.statsumu_epsus` (monthly consensus, fpi='1' annual/'6' quarterly) + `ibes.actu_epsus` (actuals); Default-account access is confirmed
- **Macro/FX/rates**: `frb.fx_daily`, `frb.rates_daily`; broad CSV exports under `alternative/macro/`
- **Fama-French factors**: `ff.factors_daily`, `ff.fivefactors_daily`; optional global factor slices from `contrib_global_factor.global_factor`
- **13F ownership**: `tr_13f.s34`; publishes manager-level holdings plus ticker-date summary aggregates
- **Financial ratios**: `wrdsapps_finratio.firm_ratio` joined to `wrdsapps_finratio.id`; uses `public_date` for backtest-safe availability
- **Credit**: `markit_cds.cdsYYYY` and TRACE standard/enhanced trade tables; filter by ticker/CUSIP, TRACE grade (`I` investment grade, `H` high yield, `N` not rated), and date before scaling up

## CRSP-to-LEAN Field Mapping

| LEAN Field | CRSP Source | Notes |
|------------|-------------|-------|
| Close | `abs(prc)` | Negative prc = bid/ask midpoint |
| Open | `openprc` | Falls back to Close if null |
| High | `askhi` | Quote-based proxy; clamped >= max(Open,Close) |
| Low | `bidlo` | Quote-based proxy; clamped <= min(Open,Close) |
| Volume | `vol` | Raw shares |
| SplitFactor | `cfacshr` | Normalized: cfacshr(date)/cfacshr(latest) |
| PriceFactor | `dsedist.divamt` | Cumulative (1 - div/price) product, backwards from 1.0 |

### ETF Universe Files (`equity/usa/universes/etf/{etf}/{YYYYMMDD}.csv`)

One file per trading day, no header:
```
Ticker,SID,ReportDate,Weight,SharesHeld,MarketValue
AAPL,AAPL MGOUOCLO92ED,20171231,0.0473,6225229,1053495503
```
- SID generated from map files using LEAN's SecurityIdentifier encoding
- Weight as decimal fraction of total net assets
- Forward-filled from monthly CRSP reports to each trading day

### Piotroski Scores (`alternative/fundamentals/piotroski_scores.csv`)

CSV with header:
```
Ticker,CompanyName,AvailableDate,FiscalYearEnd,FiscalYear,F_Score,
F1_PositiveNI,F2_PositiveROA,F3_PositiveCFO,F4_CFOgtNI,
F5_LeverageDown,F6_LiquidityUp,F7_NoNewShares,
F8_GrossMarginUp,F9_AssetTurnoverUp,
NetIncome,TotalAssets,OperatingCashFlow,LongTermDebt,
CurrentAssets,CurrentLiabilities,SharesOutstanding,GrossProfit,Revenue
```
- **AvailableDate**: point-in-time date (pdate or datadate+90d) — use this for backtesting
- **FiscalYearEnd**: actual fiscal year end (datadate) — do not use directly; causes look-ahead
- All 9 signal columns are 0/1 integers; F_Score is their sum (0–9)
- Raw financial values included for research decomposition

### IBES Consensus (`alternative/earnings/ibes_consensus.csv`)

CSV with header:
```
Ticker,CompanyName,FiscalPeriodEnd,StatDate,Periodicity,NumAnalysts,NumUp,NumDown,MeanEPS,MedianEPS,StdEPS,HighestEPS,LowestEPS
AAPL,APPLE INC,2026-09-30,2026-02-19,ANN,35,35,2,8.50,8.50,0.15,8.83,8.15
```
- **StatDate**: point-in-time date (when IBES published the snapshot) — use this for backtesting
- **Periodicity**: ANN (fpi='1') or QTR (fpi='6')
- Coverage: 1980–present for most equity universe tickers

### IBES Surprise (`alternative/earnings/ibes_surprise.csv`)

CSV with header:
```
Ticker,CompanyName,FiscalPeriodEnd,Periodicity,AnnouncementDate,ActualEPS,ConsensusEPS,ConsensusMedianEPS,ConsensusStd,NumAnalysts,SUE,ConsensusDate
AAPL,APPLE INC,2025-09-30,ANN,2025-10-30,1.64,1.60,1.60,0.02,44,1.29,2025-10-16
```
- **AnnouncementDate**: when earnings were reported — use as event date for PEAD strategies
- **SUE**: standardized unexpected earnings = (ActualEPS - ConsensusEPS) / ConsensusStd
- **ConsensusDate**: date of the matched pre-announcement consensus snapshot

### Sector Map (`alternative/sectors/sector_map.csv`)

CSV with header:
```
Ticker,CompanyName,GICSSector,GICSIndustryGroup,GICSSubIndustry,SIC,MorningstarSectorCode,MorningstarSectorName
AAPL,APPLE INC,45,452020,45202030,3663,311,Technology
```

## Validation

Run with `--validate` to compare generated data against existing LEAN reference at `MyProjects/data/equity/usa/`:
- Close prices checked within 1 deci-cent tolerance
- Factor file row counts compared
- Reference data covers 1998-2021

## Known Limitations

- **SGOV** (launched 2020) may not exist in CRSP — will be skipped with a warning
- **OHLC quality**: askhi/bidlo are quote-based, not trade-based; negligible for large-caps
- **Factor files**: CRSP cfacpr combines splits + stock dividends differently than LEAN separates PriceFactor/SplitFactor — validated iteratively against reference
- **ETF universe coverage**: 26 historical DIA members (e.g. AMZN, NVDA, XOM, GE) need equity data pulled separately before they appear in universe files. Run `run_pipeline.py --tickers AMZN NVDA XOM ...` first.
- **ETF universe end date**: Forward-fill stops at CRSP daily data end (currently 2024-12-31), even though CRSP holdings go to 2025-11-30
- **Sector data**: ETFs (SPY, SGOV, DIA, BIL) have no Compustat GICS classification. Some historical tickers (GM, KFT, UTX) are missing from current Compustat.
- **IBES ticker mapping**: IBES uses proprietary internal tickers that differ from exchange tickers (NKE→NIKE, TRV→STPL, UNH→UNIH, VZ→BEL, WBA→WAG). `resolve_ibes_tickers()` in `ibes.py` handles this automatically via `ibes.id.oftic`. All 30 equity universe tickers have coverage.
- **Additional-entitlement access gaps**: RavenPack, institutional ownership (13F/tr_ownership), TR Datastream equities, US options (cboe_eod, optionm_all), and short interest are permission denied. Default-account access to `tr_13f.s34` is confirmed. TAQ tick data schemas are visible but SELECT access is not yet confirmed.
- **TAQ table size**: Each daily `ctm` table covers the full market; filter by `sym_root` early and never `SELECT *` on an unfiltered day table.
- **TAQ pre-2003**: Millisecond TAQ begins 2003; for 1983–1992 use the `issm` schema (coarser, quote-based).
- **Piotroski — financials/utilities**: F5 (leverage) and F6 (current ratio) are less meaningful for banks and utilities; interpret with care for GS, JPM, TRV, UNH.
- **Piotroski — F4 (CFO > NI)**: `oancf` can be null for some tickers before ~1988; those rows score 0 on F4.
- **Piotroski — first year dropped**: YoY signals require a prior year, so each ticker loses its earliest fiscal year observation.
- **Local backtest — missing SPY hourly**: LEAN looks for `equity/usa/hour/spy.zip` to power time-based scheduling. The pipeline only generates daily bars; LEAN falls back gracefully and the scheduler still works.
- **Local backtest — missing interest-rate file**: LEAN fetches `alternative/interest-rate/usa/interest-rate.csv` for Sharpe ratio computation. When absent it defaults to 0% risk-free rate — no impact on trading logic. Copy from `MyProjects/data/alternative/` to fix.

## Connecting to Local Backtests

After running the pipeline, update `MyProjects/lean.json` line 2:
```json
"data-folder": "~/Documents/Q-agent/MyProjects/WRDS/lean-data"
```
