# WRDS Data Sources

Catalogue of WRDS tables this pipeline can read. Your specific subscription/entitlements depend on the institution that issued your WRDS account — confirm with your institution which schemas you have SELECT access to. The tables listed below cover what the pipeline scripts target; your account may have access to a subset.

See `claude.md` for pipeline commands, LEAN output formats, and known limitations.

## Profiles

The pipeline supports multiple WRDS accounts via named profiles. Configure them in `.wrds_profiles.json` (gitignored — copy from `wrds_profiles.example.json`):

```json
{
  "default_profile": "main",
  "profiles": {
    "main": {
      "username": "your_wrds_username"
    }
  }
}
```

Credentials are read from `~/.pgpass` (Unix) or the `WRDS_PASSWORD` env var.

1. Add a profile to `.wrds_profiles.json`
2. Add a matching line to `~/.pgpass`: `wrds-pgdata.wharton.upenn.edu:9737:wrds:<username>:<password>`
3. Run `chmod 600 ~/.pgpass`

Run any pipeline with `--profile <name>` or set `WRDS_PROFILE=<name>`. If only one profile is configured and it's marked `default_profile`, the flag can be omitted.

---

## Daily Equity — CRSP (both profiles)

- `crsp.dsf` — 107.7M rows, 1926–2024: OHLC proxies, close, volume, adjustment factors
- `crsp_a_stock.msf` — 5.2M rows, monthly (note: `crsp_m_stock` schema is denied; use `crsp_a_stock`)
- `crsp_a_stock.stkdlysecuritydata` — 110.2M rows, newer CRSP v2 data model
- `crsp.dsedist` — dividends (distcd 12xx) and splits (distcd 5xxx)
- `crsp.dsenames` — ticker changes, exchange listings, PERMNO mapping
- `crsp_a_ccm.ccmxpf_lnkhist` — 123k rows, PERMNO ↔ gvkey mapping (CRSP–Compustat link)

## ETF Constituents — CRSP Mutual Fund (both profiles)

- `crsp.holdings` — monthly ETF/fund holdings with tickers, weights, shares
- `crsp.fund_names` — fund metadata, portfolio numbers
- DIA uses crsp_portno 1004198 (2002–2010) and 1021964 (2010–present)

---

## Compustat Fundamentals (both profiles)

### North America

- `comp.funda` — 939k rows, annual fundamentals, 1950–2026
- `comp.fundq` — 2.1M rows, quarterly fundamentals, 1961–2026
- `comp.company` — 57k companies, GICS sector/industry, SIC codes
- `comp.security` — 76k securities, ticker-to-gvkey linkage
- `comp.seg_customer` — 167k rows, customer segment revenue disclosures
- `comp.aco_pnfnda` — 155k rows, pension and post-retirement benefit data
- `comp_na_daily_all.secd` — 159M rows, daily security prices, 1984–2027

Standard filters for `comp.funda` / `comp.fundq`: `indfmt='INDL'`, `datafmt='STD'`, `popsrc='D'`, `consol='C'`

### Key items in `comp.funda` / `comp.fundq`

| Category | Annual | Quarterly | Description |
|----------|--------|-----------|-------------|
| Revenue | `sale` | `saleq` | Net sales |
| Revenue | `revt` | `revtq` | Total revenue (incl. non-operating) |
| Gross profit | `gp` | — | Revenue − COGS |
| COGS | `cogs` | `cogsq` | Cost of goods sold |
| EBIT/EBITDA | `ebit`, `ebitda` | — | Operating income variants |
| Operating income | `oibdp` | `oibdpq` | Op. income before D&A |
| Net income | `ni` | `niq` | Net income |
| Income (adj.) | `ib` | `ibq` | Income before extraordinary items |
| Pretax income | `pi` | `piq` | Pre-tax income |
| SG&A | `xsga` | `xsgaq` | Selling, general & administrative |
| R&D | `xrd` | `xrdq` | Research & development |
| Interest expense | `xint` | `xintq` | Interest paid |
| Tax | `txt` | `txtq` | Income tax expense |
| Total assets | `at` | `atq` | Total assets |
| Current assets | `act` | `actq` | Current assets |
| Cash | `che` | `cheq` | Cash & short-term investments |
| Receivables | `rect` | `rectq` | Accounts receivable |
| Inventory | `invt` | `invtq` | Inventories |
| PP&E (net) | `ppent` | `ppentq` | Property, plant & equipment net |
| Goodwill | `gdwl` | `gdwlq` | Goodwill |
| Intangibles | `intan` | `intanq` | Total intangibles |
| Long-term debt | `dltt` | `dlttq` | LT debt (total) |
| Current debt | `dlc` | `dlcq` | Debt in current liabilities |
| LT debt due 1–5yr | `dd1`–`dd5` | — | Scheduled LT debt maturities |
| Total liabilities | `lt` | `ltq` | Total liabilities |
| Common equity | `ceq` | `ceqq` | Common/ordinary equity |
| Stockholders' equity | `seq` | `seqq` | Total stockholders' equity |
| Retained earnings | `re` | `req` | Retained earnings |
| Shares outstanding | `csho` | `cshoq` | Common shares outstanding |
| Operating cash flow | `oancf` | — | Cash from operations |
| Capex | `capx` | `capxq` | Capital expenditures |
| D&A | `dp` | `dpq` | Depreciation & amortization |
| EPS (diluted) | `epspx` | `epspxq` | Earnings per share (excl. extraordinary) |
| Dividends | `dvt` | — | Total dividends paid |
| Market cap | `mkvalt` | `mkvaltq` | Market value of equity |
| Price (fiscal yr-end) | `prcc_f` | `prccq` | Share price at fiscal year-end |

Plus 800+ additional items: pension obligations, derivatives, segment revenue, foreign operations, lease commitments, off-balance-sheet items, XBRL-tagged line items, and industry-specific disclosures.

### CRSP–Compustat join (CCM link)

```python
query = """
SELECT
    f.gvkey, f.datadate, f.tic, f.conm,
    f.sale, f.ni, f.at, f.dltt, f.ceq,
    f.oancf, f.capx, f.ebitda,
    l.lpermno AS permno
FROM comp.funda f
JOIN crsp_a_ccm.ccmxpf_lnkhist l
    ON f.gvkey = l.gvkey
    AND l.linktype IN ('LU','LC')
    AND l.linkprim IN ('P','C')
    AND l.linkdt <= f.datadate
    AND (l.linkenddt IS NULL OR l.linkenddt >= f.datadate)
WHERE f.indfmt='INDL' AND f.datafmt='STD'
  AND f.popsrc='D' AND f.consol='C'
  AND f.fyear >= 2000
ORDER BY f.gvkey, f.datadate
"""
# permno links to crsp.dsf for daily prices → compute P/E, P/B, EV/EBITDA at any date
```

**Point-in-time warning**: `datadate` is the fiscal year-end, not when the data was public. Use `pdate` (preliminary release) or `datadate + 90 days` for backtest-safe signals. The Piotroski pipeline already handles this.

### Global / International

- `comp_global_daily.g_funda` — 1.1M rows, international annual fundamentals, 1987–2026
- `comp_global_daily.g_fundq` — 4M rows, international quarterly fundamentals
- `comp_global_daily.g_secd` — 307M rows, international daily security prices, 1913–2028

### Banks

- `comp_bank_daily.bank_funda` — 73k rows, bank-specific line items (regulatory capital, loan categories), 1955–2025

### Executive Compensation

- `comp_execucomp.anncomp` — 374k rows: CEO/CFO/named-exec annual pay, options granted, pension values
- Also: `directorcomp`, `outstandingawards`, `planbasedawards`, `pension`, `ex_black`

**Not subscribed:** `comp_pit` (point-in-time snapshots), `wrds_xbrl_fundamental`, `calcbench_*`

---

## Analyst Estimates & Earnings Surprise — IBES (both profiles)

Full access: 194 tables.

**GAAP EPS (as-reported):**
- `ibes.det_epsus` — 35.4M rows, 1980–2026: individual analyst estimates (analyst, firm, fiscal period, revision date)
- `ibes.act_epsus` — 1.3M rows: GAAP EPS actuals
- `ibes.statsum_epsus` — 14.9M rows, 1976–2026: consensus summary — mean, median, stdev, analyst count, upgrades/downgrades, actual + announcement timestamp

**Street EPS (non-GAAP — what markets react to):**
- `ibes.det_xepsus` — 165.1M rows, 1989–2026: individual analyst Street EPS estimates
- `ibes.act_xepsus` — 14.2M rows, 1984–2026: Street EPS actuals

**Earnings surprise (pre-computed):**
- `ibes.surpsumu` — 4.6M rows, 1992–2026: `surpmean` (actual − consensus), `suescore` (SUE), `surpstdev`
- `ibes.surpsum` — 13.4M rows: same at detail level

International coverage: `det_epsint`, `act_epsint`, `statsum_epsint`. Also revenue/other-metric estimates.

**Key use cases:** PEAD via `surpsumu.suescore`, analyst revision momentum via `det_xepsus`, estimate dispersion via `statsum_epsus.stdev`. No pipeline built yet.

**Not subscribed:** `ibes.det_guidance`, earnings call transcripts (`ciq_transcripts`), SEC filings (`wrdssec`)

---

## Options — OptionMetrics Europe (requires OptionMetrics Europe entitlement)

Full access: all 148 tables, 2002–2023.

- **Exchanges**: 30 European venues — EUREX, Euronext (Amsterdam/Paris/Brussels/Lisbon), London, OMX Nordic, XETRA, Borsa Italiana, MEFF, Swiss, Oslo, and more
- `option_price_{year}` (2002–2023): bid/ask, implied vol, delta, gamma, vega, theta, open interest — 1.64B rows total via `option_price_view`
- `std_option_price_{year}` (2002–2023): interpolated to standard delta/tenor grid — preferred for vol surface research; 63.5M rows total
- `tick_option_price_{year}` (2006–2023): intraday timestamps; 1.58B rows total
- `tick_std_option_price_{year}` (2006–2023): tick-level on standard grid; 63.4M rows
- `volatility_surface_{year}` (2002–2023): 1.33B rows; tick variant 2006–2023
- Reference: `security` (96k), `security_price` (132M rows), `ticker` (150k), `zero_curve` (627k), `forward_price` (45M rows), `futures_price` (93M rows), `historical_volatility` (57M rows), `index_dividend` (3.8M rows)

No pipeline built yet.

## Options — US (sample only)

- `optionm_all` (OptionMetrics US): permission denied
- `cboe_eod`: permission denied
- Samples available for schema exploration only: `cboe_sample` (~75k rows), `optionmsamp_us` (2014), `omtrial` (2013–2014)

---

## TAQ Millisecond Tick Data (requires TAQ entitlement)

- **Schema per year**: `taqm_2003` through `taqm_2026`; one table per trading day, e.g. `taqm_2024.ctm_20240102`
- **Table types per day**:
  - `ctm` — Consolidated Trades: exchange, size, price, nanosecond timestamp
  - `complete_nbbo` — Full NBBO: best bid/ask + sizes across all exchanges
  - `cqm` — Consolidated Quotes
  - `luld_ctm` / `luld_cqm` — Limit Up/Limit Down filtered trades/quotes
  - `mastm` — Symbol master (reference)
- **By-security partition**: `taqmsec` (36,778 tables) — same data partitioned by ticker
- **Pre-2003**: `issm` schema — NASDAQ + NYSE/AMEX quotes and trades (1983–1992)
- Filter by `sym_root = 'AAPL'` early; never `SELECT *` on an unfiltered day table

---

## Fama-French Factors (both profiles)

- `ff.factors_daily` — 26k rows, 1926–2026: `mktrf`, `smb`, `hml`, `umd` (momentum), `rf`
- `contrib.factors_daily` — 117k rows, 1989–2018: same factor family by country (international)

---

## Foreign Exchange (both profiles — confirmed via `scripts/probe_fx_access.py`)

No pipeline built yet.

### Federal Reserve H.10 — `frb` schema (preferred for FX)

- `frb.fx_daily` — 14,115 rows, 1971-01-04 → 2025-02-07: ~24 USD pairs + Fed trade-weighted dollar indices
  - Bilateral pairs (both directions): AUD, CAD, CHF, CNY, DKK, EUR, GBP, HKD, INR, JPY, KRW, MXN, MYR, NOK, NZD, SEK, SGD, THB, TWD, ZAR, plus legacy pre-euro currencies (DEM, FRF, ITL, ESP, NLG, BEF, FIM, IEP, GRD, ATS, PTE, ECU)
  - Naming: `dexXXus` = X per USD, `dexusXX` = USD per X (e.g. `dexjpus`, `dexusuk`)
  - Trade-weighted dollar: `dtwexb`, `dtwexbgs` (broad, goods+services), `dtwexm` (major currencies), `dtwexafegs` (advanced foreign econ.), `dtwexemegs` (emerging mkts)
- `frb.fx_monthly` — 649 rows, 1971–2025: monthly versions (`exXXus` / `exusXX`, `twex*mth` indices)

`frb.rates_daily` and `frb.rates_monthly` are also accessible but contain interest rates (Treasury yields, CDs, commercial paper), not FX.

### Compustat currency translation — `comp` schema

- `comp.wrds_g_exrate` — **2.21M rows, 1982-02-01 → 2026-05-06: best general-purpose FX table**
  - Columns: `curd`, `datadate`, `exrattpd`, `exratd_fromgbp`, `exratd_togbp`, `exratd_fromusd`, `exratd_tousd`
  - Pre-computed USD and GBP cross-rates for every currency — no triangulation needed
- `comp.exrt_dly` / `comp_global_daily.g_exrt_dly` — raw Compustat daily FX (GBP-anchored: `fromcurd`, `tocurd`, `exratd`, `datadate`)
- `comp.exrt_mth` / `comp.g_exrt_mth` — 75k rows, 1982–2026 monthly: includes 18 forward tenors (`exrat1m` … `exrat18m`)
- `comp.currency` / `comp.g_currency` — 222 rows: ISO currency reference (`isocurcd`, `isocurnm`, `isocurbd` start, `isocurdd` end)
- `comp.r_exrt_typ` — exchange rate type codes (`AR` = As Reported)

**Rule of thumb:**
- Tradable FX research → `frb.fx_daily` (transparent USD pairs, deep history, includes trade-weighted indices)
- Translating any foreign-currency Compustat field to USD/GBP at a `datadate` → `comp.wrds_g_exrate`

---

## Global Factor Data — `contrib.global_factor` (both profiles)

**444 columns × 91 countries × 1925–2025** — Jensen, Kelly & Pedersen pre-computed firm-characteristic panel ("Is There a Replication Crisis in Finance?")

- Pre-computed: momentum (1–60m lookbacks), seasonality, balance sheet growth rates, accounting variables, size, volume, turnover, dividends, share issuance, and ~350 more
- Covers USA, GBR, JPN, DEU, FRA, AUS, CAN, CHN, KOR, IND, BRA and 80 more countries
- Linked to CRSP (`permno`) and Compustat (`gvkey`); includes FX-adjusted returns
- **Key use**: study any published return factor without computing it from raw CRSP/Compustat

---

## Contributed Research Datasets — `contrib` (both profiles)

- `contrib.char_returns` — 2.6M rows, 1964–2021: Characteristic-Based Benchmark Returns (CBBR) — expected return per stock given characteristics using 5 or 14 benchmarks; for alpha attribution, not signal construction
- Other notable tables: `corp_culture` (10-K culture scores), `ceo_turnover` (forced/voluntary), `classified_boards` (staggered boards), `common_own_firm` (institutional common ownership), `green_returns` (environmental exposure sorts), `kpss_patents` (patents linked to Compustat), `marginal_tax` (firm-level tax rates), `dealscan_link_comp` (loan data linked to gvkeys)

---

## Not Subscribed

| Dataset | Schema | Notes |
|---------|--------|-------|
| Institutional ownership | `tr_ownership` | Often requires a separate entitlement; check your account |
| News sentiment | `ravenpack_dj`, `ravenpack_full`, `ravenpack_web` | Requires RavenPack entitlement |
| US options (full) | `optionm_all`, `cboe_eod` | Permission denied |
| TR Datastream equities | `tr_ds_equities` | Permission denied |
| Short interest | — | Permission denied |
| Point-in-time Compustat | `comp_pit` | Not subscribed |
