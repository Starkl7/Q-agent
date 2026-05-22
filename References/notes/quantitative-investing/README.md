# Quantitative Investing Notes

Working notes for `Quantitative Investing`.

## Files

- `book_toc.md`: top-level table of contents from the full-book PDF
- `advanced_sections.md`: sections that look most technical or reusable
- `multi_signal_markowitz_strategy.md`: explanation of the attached multi-signal equity strategy framework

## Source

- `../../books/Quantitative_Investing/978-3-030-47202-3.pdf`

---

## Signal Coverage by Data Source

Coverage assessment for the 11 signals in `multi_signal_markowitz_strategy.md` across local WRDS, free public sources, and the QC cloud platform. WRDS access verified by direct probe of `information_schema` and `SELECT` tests under both `ncsu` and `additional` profiles (2026-05-06).

### Signal-by-signal matrix

| # | Signal | WRDS (ncsu) | WRDS (skema adds) | Free public sources | QC Cloud |
|---|--------|-------------|-------------------|---------------------|----------|
| 1 | CTA Momentum | YES — `crsp.dsf` (daily) or `contrib.global_factor` (monthly, pre-computed `ret_6_1`, `ret_9_1`, `ret_12_1`, ...) | — | — | YES |
| 2 | Regime Probability | PARTIAL — `frb.rates_daily` provides yield-curve slopes (`t10y2y`, `t10y3m`), HY credit OAS (`bamlh0a0hym2`), breakeven inflation (`t5yie`, `t10yie`), policy rates (`effr`, `sofr`); plus `ff.factors_daily` for equity regime. No OECD CLI / PMI directly. | — | YES — OECD CLI (oecd.org), FRED PMI series, VIX (CBOE) | YES — Nasdaq Data Link (paid add-on) |
| 3 | Crowding | NO — 13F, short interest, prime broker all denied | NO — same denials persist under skema | PARTIAL — SEC EDGAR 13F (free, ~45-day delay), FINRA short interest (free, semi-monthly); use `contrib.global_factor` issuance/turnover columns as soft proxies | PARTIAL — Quiver Quant (paid), delayed 13F |
| 4 | EPS Growth vs Consensus | NO | YES — `comp.funda` + `ibes.statsum_epsus` + `ibes.det_xepsus` | — | PARTIAL — Morningstar consensus EPS only; no individual analyst estimates |
| 5 | Extreme Rates Momentum | YES — `frb.rates_daily.dgs10` (10Y) plus full curve `dgs1mo, dgs3mo, dgs6mo, dgs1, dgs2, dgs3, dgs5, dgs7, dgs20, dgs30`, real yields `dfii5..dfii30`, swaps `dswp1..dswp30`, 1954-01-04 to 2025-02-13. Note: `crsp_a_treasuries.tfz_*` schema is denied under both profiles. | — | YES — FRED `DGS10` (daily, 1962–present, free) | YES — `USTreasuryYieldCurveRate` built in |
| 6 | Risk Targeting | YES — `crsp.dsf` (daily vol) or `contrib.global_factor` (`rvol_21d`, `rvol_252d`, `ivol_capm_*`) | — | — | YES |
| 7 | Up/Down Volatility | YES — `crsp.dsf` (build directly from daily returns); soft proxies in `contrib.global_factor` (`betadown_252d`, `iskew_capm_21d`, `coskew_21d`, `rmax5_rvol_21d`) | — | — | YES |
| 8 | Options Volumes | NO — `optionm_all`, `cboe_eod`, `cboe`, `wrdsapps_optsigd` all denied or unsubscribed under both profiles (verified) | NO — `optionm_europe` accessible but doesn't cover the 30-stock US equity universe | PARTIAL — CBOE total/equity/index put-call ratio (free daily CSV, 2006–present) and VIX as **market-level** proxies; no per-stock option signal possible from free sources | YES — full US options chains 2012–present (only path to true single-stock Signal 8) |
| 9 | Adjusted Forward P/E | NO trailing-only via `comp.funda` and `contrib.global_factor` (`be_me`, `ni_me`, `qmj`, `z_score`) — no forward EPS | YES — `ibes.statsum_epsus` provides forward EPS consensus | — | PARTIAL — Morningstar `ForwardPERatio` less granular than IBES |
| 10 | Sector PMI New Orders | NO — not in WRDS | — | YES — ISM publishes free monthly headline + sector PMI; FRED `NAPM*` series | YES — Nasdaq Data Link (paid add-on) |
| 11 | Earnings Revisions | NO | YES — `ibes.det_epsus` / `ibes.det_xepsus` (individual analyst-level) | — | PARTIAL — no individual analyst revisions; proxy from Morningstar consensus EPS changes |

### Summary

| Source | Signals available |
|--------|------------------|
| WRDS ncsu alone | 5/11 — signals 1, 5, 6, 7 + partial 2 (`frb.rates_daily` covers Treasuries, credit, partial regime) |
| WRDS ncsu + skema | 8/11 — adds 4, 9, 11 (IBES) |
| WRDS ncsu + free public (ISM PMI, OECD CLI, EDGAR, FINRA, CBOE PCR) | 7/11 — adds 10 and partial 3 (crowding) |
| WRDS skema + free public | ~10/11 — only Signal 8 (per-stock options) missing |
| QC cloud alone | ~9/11 — everything except IBES-quality analyst estimates (4, 9, 11) |
| WRDS skema + QC cloud | 11/11 — complementary: WRDS for analyst estimates + rates + factors, QC for per-stock options |

### WRDS bonus: `contrib.global_factor` (both profiles)

The Jensen, Kelly & Pedersen panel (444 columns × 91 countries × 1925–2025, monthly) ships pre-computed firm characteristics that materially shorten signal construction:

- **Multi-horizon momentum** (Signal 1): `ret_6_1`, `ret_9_1`, `ret_12_1`, `ret_18_1`, `ret_24_1`, `ret_36_1`, `ret_48_1`, `ret_60_1` plus skip-zero variants
- **Realized & idiosyncratic vol** (Signal 6): `rvol_21d`, `rvol_252d`, `ivol_capm_21d`, `ivol_capm_252d`, `ivol_capm_60m`, `ivol_ff3_21d`, `ivol_hxz4_21d`, `rvolhl_21d`
- **Asymmetric-risk proxies for up/down vol** (Signal 7): `betadown_252d`, `coskew_21d`, `iskew_capm_21d`, `iskew_ff3_21d`, `iskew_hxz4_21d`, `rmax5_rvol_21d`
- **Value + quality decomposition for Signal 9**: `be_me`, `ni_me`, `fcf_me`, `sale_me`, `qmj`, `qmj_prof`, `qmj_safety`, `gp_at`, `cop_at`, `z_score`, `debt_at`, `netdebt_me`
- **Crowding-adjacent proxies for Signal 3**: `chcsho_12m`, `eqnetis_at`, `eqnpo_12m`, `dolvol_var_126d`, `turnover_126d`, `ami_126d`

Trade-offs: monthly (not daily — still need `crsp.dsf` for daily vol-targeting and execution), trailing fundamentals only (no forward EPS), and the panel uses lagged availability dates so PIT semantics need verification before relying on the `date` column for backtests.

### WRDS bonus: `frb.rates_daily` (both profiles)

Federal Reserve Board H.15 daily rates feed — 83 columns, 25,924 rows, 1954-01-04 to 2025-02-13. Replaces the FRED scraping path entirely for rates-based signals:

- **Treasury yield curve** (Signal 5 direct): `dgs1mo, dgs3mo, dgs6mo, dgs1, dgs2, dgs3, dgs5, dgs7, dgs10, dgs20, dgs30`
- **Real (TIPS) yields**: `dfii5, dfii7, dfii10, dfii20, dfii30`
- **Yield curve slopes** (Signal 2 regime input): `t10y2y` (10Y–2Y), `t10y3m` (10Y–3M, NY Fed recession proxy)
- **Breakeven inflation**: `t5yie`, `t10yie`
- **Credit spreads** (Signal 2 risk-on/risk-off): `bamlh0a0hym2` (HY OAS), `bamlc0a0cmey` (IG corporate), `bamlh0a3hycey` (HY CCC)
- **Policy rates / risk-free**: `effr`, `dff`, `obfr`, `sofr`, `iorb`, `dfedtaru`, `dfedtarl`, `dprime`
- **Swap curve**: `dswp1, dswp2, dswp3, dswp4, dswp5, dswp7, dswp10, dswp30`

Caveats: feed updates on irregular cadence (currently lags ~3 months behind real time); some columns are NaN on the latest available date. For a live algo, fall back to FRED API or QC's built-in `USTreasuryYieldCurveRate` to fill the gap.

### Verified WRDS denials (2026-05-06 probe)

For Signal 8 specifically, every plausible WRDS path was tested under both profiles:

- `optionm_all` (US OptionMetrics, full) — permission denied
- `cboe_eod` (CBOE end-of-day) — permission denied
- `cboe` (metadata-visible alias of `cboe_eod`) — denied at SELECT time
- `wrdsapps_optsigd` / `wrdsapps_optsigs` (OptionMetrics-derived signal app) — schema not subscribed
- `optionm_europe` — accessible under skema but covers 30 European venues only; no coverage of the 30-stock US equity universe
- Sample-only schemas: `cboe_sample`, `optionmsamp_us`, `omtrial` (schema exploration only)

Conclusion: **no WRDS path exists for US single-stock option volumes/IV under current entitlements.** Signal 8 must come from QC Cloud (paid options chains) or be approximated at the market level via the free CBOE PCR.

CRSP Treasuries also denied: `crsp_a_treasuries.tfz_dly_ts2`, `crsp_a_treasuries.tfz_dly_rf`, etc. all return permission-denied under both profiles. The accessible rates path is `frb.rates_daily` instead — see bonus section above.

### QC platform data catalogue

Core data included with all accounts:

| Category | Coverage |
|----------|----------|
| US Equities | Daily 1998–present, minute 2009–present; OHLCV, splits, dividends |
| US Equity Options | Minute + tick 2012–present; full chains, open interest, volume |
| US Futures + Future Options | Full history, 100+ contracts |
| Forex | Major/minor pairs, tick |
| Crypto | Coinbase, Binance, and others |
| Morningstar Fundamentals | 1998–present — P/E, EPS, revenue, balance sheet via `AddEquity` |

Alternative data marketplace (most are paid add-ons):

| Dataset | Relevant signals |
|---------|-----------------|
| US Treasury yield curve | Signal 5 — 10Y yield momentum |
| Nasdaq Data Link | Signals 2, 10 — OECD CLI, PMI, macro indicators |
| Quiver Quant | Signal 3 — short interest, Congress trades, insider activity |
| Brain ML / NLP | Signals 4, 11 — earnings revision proxies, sentiment |
| Tiingo News | Sentiment signal |
| SEC filings / EDGAR | Fundamental quality signals |
| CBOE volatility products | VIX term structure, vol regime |
