import marimo

__generated_with = "0.23.5"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    mo.md("""
    # Analyse de Corrélation Crypto × Polymarket

    Comparaison des **probabilités des marchés prédictifs Polymarket** pour les événements crypto
    avec les prix au comptant de **Coinbase** et **Kraken**.

    Sources de données :
    - **Coinbase** : BTC/USD, ETH/USD — barres journalières depuis 2013
    - **Kraken** : BTC/USD, ETH/USD, SOL/USD — barres journalières (~2 ans)
    - **Polymarket** : 505 marchés liés aux cryptos (probabilité du jeton YES 0–1, horaire → rééchantillonné quotidiennement)
    """)
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    import pathlib, zipfile
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import re

    INFRA_ROOT = pathlib.Path(__file__).resolve().parents[1]
    CRYPTO_ROOT = INFRA_ROOT / "pipelines" / "crypto" / "lean-data" / "crypto"
    POLY_ROOT = INFRA_ROOT / "pipelines" / "polymarket" / "lean-data" / "alternative" / "polymarket"
    YFINANCE_DAILY = INFRA_ROOT / "pipelines" / "yfinance" / "lean-data" / "equity" / "usa" / "daily"

    def read_lean_zip(path: pathlib.Path) -> pd.DataFrame:
        """Lit un zip LEAN quotidien : YYYYMMDD 00:00,O,H,L,C,V sans en-tête."""
        with zipfile.ZipFile(path) as z:
            df = pd.read_csv(
                z.open(z.namelist()[0]),
                header=None,
                names=["datetime", "open", "high", "low", "close", "volume"],
                parse_dates=["datetime"],
            )
        df["date"] = pd.to_datetime(df["datetime"].dt.date)
        return df.set_index("date")

    mo.md("✅ Imports et fonctions utilitaires chargés.")
    return CRYPTO_ROOT, POLY_ROOT, YFINANCE_DAILY, mdates, pathlib, pd, plt, re, read_lean_zip


@app.cell(hide_code=True)
def _(CRYPTO_ROOT, POLY_ROOT, YFINANCE_DAILY, mo):
    _expected_crypto = [
        CRYPTO_ROOT / "coinbasepro" / "daily" / "btcusd.zip",
        CRYPTO_ROOT / "coinbasepro" / "daily" / "ethusd.zip",
        CRYPTO_ROOT / "kraken" / "daily" / "btcusd.zip",
        CRYPTO_ROOT / "kraken" / "daily" / "ethusd.zip",
        CRYPTO_ROOT / "kraken" / "daily" / "solusd.zip",
    ]
    _expected_poly = [
        POLY_ROOT / "markets.csv",
        POLY_ROOT / "prices",
    ]
    _optional_equity = YFINANCE_DAILY / "coin.zip"
    _missing = [p for p in _expected_crypto + _expected_poly if not p.exists()]
    _optional_status = "present" if _optional_equity.exists() else "not present"
    _kind = "warn" if _missing else "info"
    _missing_lines = "\n".join(f"- `{p}`" for p in _missing) or "- None"

    mo.callout(
        mo.md(f"""
        **Data availability check**

        This notebook expects local pipeline outputs that are intentionally not committed to GitHub.
        If you just cloned the repository, the notebook still opens, but charts and tables that depend
        on local market data may be empty until you generate or copy the data.

        Missing required local inputs:
        {_missing_lines}

        Optional COIN equity file: `{_optional_equity}` ({_optional_status}).
        """),
        kind=_kind,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 1. OHLCV Crypto
    """)
    return


@app.cell(hide_code=True)
def _(CRYPTO_ROOT, mo, pd, read_lean_zip):
    # Load all available daily zips
    _price_files = {
        ("coinbase", "BTC"): CRYPTO_ROOT / "coinbasepro/daily/btcusd.zip",
        ("coinbase", "ETH"): CRYPTO_ROOT / "coinbasepro/daily/ethusd.zip",
        ("kraken",   "BTC"): CRYPTO_ROOT / "kraken/daily/btcusd.zip",
        ("kraken",   "ETH"): CRYPTO_ROOT / "kraken/daily/ethusd.zip",
        ("kraken",   "SOL"): CRYPTO_ROOT / "kraken/daily/solusd.zip",
    }

    _frames = {}
    for (exchange, asset), path in _price_files.items():
        if path.exists():
            _frames[(exchange, asset)] = read_lean_zip(path)["close"].rename(f"{exchange}_{asset}")

    # Merged close-price table (each column = exchange_asset)
    _price_columns = ["coinbase_BTC", "coinbase_ETH", "kraken_BTC", "kraken_ETH", "kraken_SOL"]
    prices = (
        pd.concat(_frames.values(), axis=1).sort_index()
        if _frames
        else pd.DataFrame({col: pd.Series(dtype=float) for col in _price_columns})
    )

    # Summary
    _summary = pd.DataFrame([
        {
            "Exchange": ex,
            "Asset": asset,
            "Start": _frames[(ex, asset)].index.min().date(),
            "End":   _frames[(ex, asset)].index.max().date(),
            "Bars":  len(_frames[(ex, asset)]),
        }
        for (ex, asset) in _frames
    ])
    mo.ui.table(_summary, show_column_summaries=False)
    return (prices,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 2. Marchés Polymarket Crypto
    """)
    return


@app.cell(hide_code=True)
def _(POLY_ROOT, mo, pd, re):
    markets_path = POLY_ROOT / "markets.csv"
    _market_columns = ["Slug", "Question", "Volume", "YesTokenId", "Theme"]
    markets = pd.read_csv(markets_path) if markets_path.exists() else pd.DataFrame(columns=_market_columns)

    if not markets.empty:
        _theme_patterns = {
            "ETH_merge":   r"merge|EIP.3675|proof.of.stake|shanghai",
            "BTC_price":   r"bitcoin.{0,20}(\$|hit|reach|dip|drop|\d{2,3}k)",
            "ETH_price":   r"ethereum.{0,20}(\$|hit|reach|dip|drop|\d{1,3}k)",
            "SOL_price":   r"solana.{0,20}(\$|hit|reach|dip|drop|\d+)",
            "regulation":  r"SEC|ETF|ban|legal|approved|classify|unban",
            "BTC_general": r"bitcoin|BTC",
            "ETH_general": r"ethereum|ETH",
            "SOL_general": r"solana|SOL",
        }
        def _theme(q):
            if not isinstance(q, str):
                return "other"
            for theme, pat in _theme_patterns.items():
                if re.search(pat, q, re.I):
                    return theme
            return "other_crypto"

        markets["Theme"] = markets["Question"].apply(_theme)
        markets["Volume"] = pd.to_numeric(markets["Volume"], errors="coerce")

        _overview = (
            markets.groupby("Theme")
            .agg(Count=("Slug","count"), TotalVolume=("Volume","sum"), HasToken=("YesTokenId", lambda x: x.notna().sum()))
            .sort_values("TotalVolume", ascending=False)
            .reset_index()
        )
        _overview["TotalVolume"] = _overview["TotalVolume"].map("${:,.0f}".format)
        _ = mo.ui.table(_overview, show_column_summaries=False)
    else:
        _ = mo.callout(mo.md("⚠️ `markets.csv` not found."), kind="warn")
    return (markets,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 3. Historiques de Prix Polymarket Disponibles
    """)
    return


@app.cell(hide_code=True)
def _(POLY_ROOT, markets, mo):
    prices_dir = POLY_ROOT / "prices"

    price_files_on_disk = {p.stem: p for p in prices_dir.glob("*.csv")} if prices_dir.exists() else {}
    _markets_with_prices = markets[markets["Slug"].isin(price_files_on_disk)].copy()
    _n_total = len(markets[markets["YesTokenId"].notna()])
    _n_loaded = len(price_files_on_disk)

    mo.md(f"""
    **{_n_loaded}** fichiers de prix sur disque sur **{_n_total}** marchés avec un jeton YES
    *(le pipeline de prix est peut-être encore en cours — rechargez pour en voir plus)*
    """)
    return price_files_on_disk, prices_dir


@app.cell(hide_code=True)
def _(pd, prices_dir):
    def load_poly_prices(slug: str) -> pd.Series:
        """Load a Polymarket YES-probability CSV and resample to daily (last value)."""
        path = prices_dir / f"{slug}.csv"
        if not path.exists():
            return pd.Series(dtype=float, name=slug)
        df = pd.read_csv(path, index_col="datetime", parse_dates=True)
        df.index = pd.to_datetime(df.index, utc=True).normalize()
        daily = df["price"].resample("D").last().dropna()
        daily.index = daily.index.tz_localize(None).rename("date")
        return daily.rename(slug)

    return (load_poly_prices,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 4. Analyse de la Fusion Ethereum

    La Fusion Ethereum (EIP-3675) a eu lieu le **15 septembre 2022**, faisant la transition
    de la Preuve de Travail à la Preuve d'Enjeu. Polymarket a lancé plusieurs marchés sur la
    probabilité que la fusion ait lieu avant des dates précises. Nous examinons si les variations
    de probabilité ont précédé les mouvements du cours ETH au comptant.
    """)
    return


@app.cell(hide_code=True)
def _(load_poly_prices, markets, mo, pd, price_files_on_disk):
    MERGE_DATE = pd.Timestamp("2022-09-15")
    _merge_markets = markets[markets["Theme"] == "ETH_merge"].copy()
    _merge_on_disk  = _merge_markets[_merge_markets["Slug"].isin(price_files_on_disk)]

    # Vérifie la variation réelle des prix (le CLOB retourne des prix plats post-résolution pour les vieux marchés)
    _live_merge = []
    for _, row in _merge_on_disk.iterrows():
        s = load_poly_prices(row["Slug"])
        if s.std() > 0.01:
            _live_merge.append(row["Slug"])

    if _live_merge:
        _ = mo.md("**Séries de prix de la Fusion ETH disponibles.**")
    else:
        _ = mo.callout(mo.md("""
    **Données historiques de la Fusion ETH indisponibles via l'API CLOB.**

    L'endpoint d'historique de prix Polymarket CLOB ne conserve des données qu'à partir de fin 2022,
    et tous les marchés de la Fusion ont été résolus en 2022. L'API retourne un prix plat post-résolution
    (0,5) pour ces anciens marchés — aucune série de probabilités pré-événement n'est accessible.

    L'analyse ci-dessous se concentre sur les **marchés actifs à objectif de prix 2025–2026**
    pour lesquels de riches historiques de probabilités sont disponibles.
    """), kind="info")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 5. Marchés Objectifs de Prix Crypto vs Prix au Comptant

    Ce sont des marchés de type « X atteindra-t-il $Y avant la date Z ? » — la probabilité YES reflète
    la vision collective du marché sur l'atteinte ou non de l'objectif.
    Plus le prix BTC au comptant est élevé → plus P(BTC atteint 150 k$) est élevée.
    """)
    return


@app.cell(hide_code=True)
def _(load_poly_prices, mdates, plt, price_files_on_disk, prices):
    TARGET_MARKETS = {
        "BTC": ["will-bitcoin-hit-150k-by-june-30-2026", "will-bitcoin-hit-150k-by-december-31-2026",
                "will-bitcoin-reach-100000-by-december-31-2026-571-361-361"],
        "ETH": ["will-ethereum-reach-3500-by-december-31-2026", "will-ethereum-reach-4000-by-december-31-2026"],
        "SOL": ["will-solana-reach-160-by-december-31-2026", "will-solana-reach-180-by-december-31-2026"],
    }
    SPOT_COL = {"BTC": "kraken_BTC", "ETH": "kraken_ETH", "SOL": "kraken_SOL"}

    fig, axes = plt.subplots(3, 1, figsize=(13, 13))

    for _ax, (_tkr, _slugs) in zip(axes, TARGET_MARKETS.items()):
        _spot = prices[SPOT_COL[_tkr]].dropna()
        _ax2 = _ax.twinx()
        _ax2.plot(_spot.index, _spot.values, color="#f59e0b", lw=1.5, alpha=0.7, label=f"{_tkr}/USD")
        _ax2.set_ylabel(f"{_tkr}/USD (Kraken)", color="#f59e0b")
        _ax2.tick_params(axis="y", colors="#f59e0b")

        for _slug, _color in zip(_slugs, ["#3b82f6", "#10b981", "#8b5cf6"]):
            if _slug not in price_files_on_disk:
                continue
            _prob = load_poly_prices(_slug)
            if _prob.empty:
                continue
            _label = _slug.replace("will-", "").replace("-by-", " by ").replace("-", " ").title()[:55]
            _ax.plot(_prob.index, _prob.values, color=_color, lw=1.5, label=_label)

        _ax.set_ylabel("YES probability")
        _ax.set_ylim(-0.05, 1.1)
        _ax.set_title(f"{_tkr}: Polymarket Probability vs Spot", fontsize=10, fontweight="bold")
        _ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        _ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(_ax.xaxis.get_majorticklabels(), rotation=30, ha="right")
        _l1, _lb1 = _ax.get_legend_handles_labels()
        _l2, _lb2 = _ax2.get_legend_handles_labels()
        _ax.legend(_l1+_l2, _lb1+_lb2, fontsize=7.5, loc="upper left", ncol=2)

    fig.suptitle("Polymarket YES Probability vs Spot Price (2025–2026)", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.gca()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 6. Corrélation : La Probabilité Précède-t-elle ou Suit-elle le Prix ?

    Pour chaque marché à objectif de prix, nous calculons :
    - **Corrélation de niveau** : r de Pearson entre la probabilité YES quotidienne et le prix au comptant
    - **Avance d'un jour** : la variation de probabilité d'aujourd'hui prédit-elle le rendement de demain ?
    - **Retard d'un jour** : le rendement d'aujourd'hui prédit-il la variation de probabilité de demain ?
    """)
    return


@app.cell(hide_code=True)
def _(load_poly_prices, mo, pd, price_files_on_disk, prices):
    ALL_TARGETS = [
        ("BTC", "will-bitcoin-hit-150k-by-june-30-2026"),
        ("BTC", "will-bitcoin-hit-150k-by-december-31-2026"),
        ("BTC", "will-bitcoin-reach-100000-by-december-31-2026-571-361-361"),
        ("ETH", "will-ethereum-reach-3500-by-december-31-2026"),
        ("ETH", "will-ethereum-reach-4000-by-december-31-2026"),
        ("SOL", "will-solana-reach-160-by-december-31-2026"),
        ("SOL", "will-solana-reach-180-by-december-31-2026"),
    ]
    _SPOT = {"BTC": "kraken_BTC", "ETH": "kraken_ETH", "SOL": "kraken_SOL"}

    _rows = []
    for _tkr, _slug in ALL_TARGETS:
        if _slug not in price_files_on_disk:
            continue
        _prob = load_poly_prices(_slug)
        if _prob.empty or _prob.std() < 0.01:
            continue
        _spot = prices[_SPOT[_tkr]].dropna()
        _dj = pd.concat([_prob.rename("prob"), _spot.rename("spot")], axis=1, sort=False).dropna()
        if len(_dj) < 20:
            continue

        _dj["prob_chg"] = _dj["prob"].diff()
        _dj["ret"]      = _dj["spot"].pct_change()

        _r_level = _dj[["prob","spot"]].corr().iloc[0,1]
        _r_lead  = _dj["prob_chg"].corr(_dj["ret"].shift(-1))
        _r_lag   = _dj["ret"].corr(_dj["prob_chg"].shift(-1))
        _label   = _slug.replace("will-","").replace("-by-"," by ").replace("-"," ").title()[:60]

        _rows.append({
            "Asset": _tkr,
            "Market": _label,
            "N": len(_dj),
            "r(prob~spot)": round(_r_level, 3),
            "r(Δprob→nextRet)": round(_r_lead, 3),
            "r(ret→nextΔprob)": round(_r_lag, 3),
        })

    _corr_columns = ["Asset", "Market", "N", "r(prob~spot)", "r(Δprob→nextRet)", "r(ret→nextΔprob)"]
    corr_table = pd.DataFrame(_rows, columns=_corr_columns)
    mo.ui.table(corr_table, show_column_summaries=False)
    return (corr_table,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 7. Comparaison des Prix Entre Exchanges (Coinbase vs Kraken)
    """)
    return


@app.cell(hide_code=True)
def _(mdates, pd, plt, prices):
    # Compare BTC and ETH across exchanges (both have data)
    _xex_pairs = [("BTC", "coinbase_BTC", "kraken_BTC"), ("ETH", "coinbase_ETH", "kraken_ETH")]
    _fig, _axes = plt.subplots(2, 2, figsize=(14, 8))

    for _i, (_name, _col_cb, _col_kr) in enumerate(_xex_pairs):
        _cb = prices[_col_cb].dropna()
        _kr = prices[_col_kr].dropna()
        _aligned = pd.concat([_cb.rename("CB"), _kr.rename("KR")], axis=1).dropna()

        # Price overlay
        _ax = _axes[_i, 0]
        if _aligned.empty:
            _ax.text(0.5, 0.5, "No local price data", ha="center", va="center", transform=_ax.transAxes)
            _axes[_i, 1].text(0.5, 0.5, "No local price data", ha="center", va="center", transform=_axes[_i, 1].transAxes)
            continue
        _ax.plot(_aligned.index, _aligned["CB"], lw=1, label="Coinbase", color="#3b82f6", alpha=0.8)
        _ax.plot(_aligned.index, _aligned["KR"], lw=1, label="Kraken", color="#f59e0b", alpha=0.8, ls="--")
        _ax.set_title(f"{_name}/USD — Close Price", fontweight="bold")
        _ax.legend(fontsize=8)
        _ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        _ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:,.0f}"))

        # Spread
        _ax2 = _axes[_i, 1]
        _spread_pct = ((_aligned["CB"] - _aligned["KR"]) / _aligned["KR"] * 100)
        _corr = _aligned["CB"].corr(_aligned["KR"])
        _ax2.plot(_aligned.index[-400:], _spread_pct[-400:], lw=0.8, color="#6366f1")
        _ax2.axhline(0, color="gray", ls="--", lw=0.8)
        _ax2.fill_between(_aligned.index[-400:], _spread_pct[-400:], 0,
                          where=_spread_pct[-400:]>0, alpha=0.2, color="#10b981", label="CB premium")
        _ax2.fill_between(_aligned.index[-400:], _spread_pct[-400:], 0,
                          where=_spread_pct[-400:]<0, alpha=0.2, color="#ef4444", label="KR premium")
        _ax2.set_title(f"{_name}: (Coinbase − Kraken) / Kraken %  |  r={_corr:.6f}", fontweight="bold")
        _ax2.set_ylabel("Spread (%)")
        _ax2.legend(fontsize=8)
        _ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    _fig.suptitle("Coinbase vs Kraken: Price Comparison (last 400 days for spread)", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.gca()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 8. Action Coinbase (COIN) vs Prix Crypto

    Comparaison du cours de l'action Coinbase (COIN) avec les prix au comptant BTC et ETH
    pour évaluer à quel point le titre suit les cycles crypto.
    """)
    return


@app.cell
def _(YFINANCE_DAILY, mdates, pd, plt, prices):
    import zipfile as _zf

    _coin_path = YFINANCE_DAILY / "coin.zip"
    if _coin_path.exists():
        with _zf.ZipFile(_coin_path) as _z:
            _coin_df = pd.read_csv(
                _z.open(_z.namelist()[0]),
                header=None,
                names=["datetime","open","high","low","close","volume"],
                parse_dates=["datetime"],
            )
        _coin_df["date"] = pd.to_datetime(_coin_df["datetime"].dt.date)
        coin = _coin_df.set_index("date")["close"] / 10000  # LEAN stores cents
    else:
        coin = pd.Series(dtype=float, name="COIN")

    _btc = prices["coinbase_BTC"].dropna()
    _eth = prices["coinbase_ETH"].dropna()

    _fig_coin, _axes_coin = plt.subplots(3, 1, figsize=(13, 11), sharex=True)

    # --- BTC vs COIN ---
    _ax_btc = _axes_coin[0]
    _ax_coin1 = _ax_btc.twinx()
    _ax_btc.plot(_btc.index, _btc.values, color="#f59e0b", lw=1.5, label="BTC/USD (Coinbase)")
    _ax_coin1.plot(coin.index, coin.values, color="#3b82f6", lw=1.5, alpha=0.8, label="COIN")
    _ax_btc.set_ylabel("BTC/USD", color="#f59e0b")
    _ax_coin1.set_ylabel("COIN ($)", color="#3b82f6")
    _ax_btc.tick_params(axis="y", colors="#f59e0b")
    _ax_coin1.tick_params(axis="y", colors="#3b82f6")
    _l1, _lb1 = _ax_btc.get_legend_handles_labels()
    _l2, _lb2 = _ax_coin1.get_legend_handles_labels()
    _ax_btc.legend(_l1+_l2, _lb1+_lb2, fontsize=8, loc="upper left")
    _ax_btc.set_title("BTC/USD vs COIN", fontweight="bold")
    _ax_btc.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:,.0f}"))
    _ax_coin1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:,.0f}"))

    # --- ETH vs COIN ---
    _ax_eth = _axes_coin[1]
    _ax_coin2 = _ax_eth.twinx()
    _ax_eth.plot(_eth.index, _eth.values, color="#10b981", lw=1.5, label="ETH/USD (Coinbase)")
    _ax_coin2.plot(coin.index, coin.values, color="#3b82f6", lw=1.5, alpha=0.8, label="COIN")
    _ax_eth.set_ylabel("ETH/USD", color="#10b981")
    _ax_coin2.set_ylabel("COIN ($)", color="#3b82f6")
    _ax_eth.tick_params(axis="y", colors="#10b981")
    _ax_coin2.tick_params(axis="y", colors="#3b82f6")
    _l3, _lb3 = _ax_eth.get_legend_handles_labels()
    _l4, _lb4 = _ax_coin2.get_legend_handles_labels()
    _ax_eth.legend(_l3+_l4, _lb3+_lb4, fontsize=8, loc="upper left")
    _ax_eth.set_title("ETH/USD vs COIN", fontweight="bold")
    _ax_eth.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:,.0f}"))
    _ax_coin2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:,.0f}"))

    # --- Rolling 60-day correlation COIN vs BTC ---
    _ax_corr = _axes_coin[2]
    _aligned_cb = pd.concat([coin.rename("COIN"), _btc.rename("BTC"), _eth.rename("ETH")], axis=1, sort=True).dropna()
    _roll_btc = _aligned_cb["COIN"].rolling(60).corr(_aligned_cb["BTC"])
    _roll_eth = _aligned_cb["COIN"].rolling(60).corr(_aligned_cb["ETH"])
    _ax_corr.plot(_roll_btc.index, _roll_btc.values, color="#f59e0b", lw=1.5, label="r(COIN, BTC) 60j")
    _ax_corr.plot(_roll_eth.index, _roll_eth.values, color="#10b981", lw=1.5, label="r(COIN, ETH) 60j")
    _ax_corr.axhline(0, color="gray", ls="--", lw=0.8)
    _ax_corr.set_ylabel("Corrélation glissante (60j)")
    _ax_corr.set_ylim(-1, 1)
    _ax_corr.set_title("Corrélation glissante COIN vs BTC & ETH (60 jours)", fontweight="bold")
    _ax_corr.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    _ax_corr.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    plt.setp(_ax_corr.xaxis.get_majorticklabels(), rotation=30, ha="right")
    _ax_corr.legend(fontsize=8)

    _fig_coin.suptitle("Action Coinbase (COIN) vs Prix Crypto au Comptant", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.gca()
    return


@app.cell(hide_code=True)
def _(corr_table, mo):
    _btc_r = corr_table[corr_table["Asset"]=="BTC"]["r(prob~spot)"].mean()
    _eth_r = corr_table[corr_table["Asset"]=="ETH"]["r(prob~spot)"].mean()
    _sol_r = corr_table[corr_table["Asset"]=="SOL"]["r(prob~spot)"].mean()

    _lead_r = corr_table["r(Δprob→nextRet)"].mean()
    _lag_r  = corr_table["r(ret→nextΔprob)"].mean()

    mo.md(f"""
    ## 8. Conclusions Clés

    ### Corrélation de Niveau de Prix (Polymarket vs Comptant)
    | Actif | r(prob ~ comptant) |
    |-------|-------------------|
    | BTC   | {_btc_r:.3f} |
    | ETH   | {_eth_r:.3f} |
    | SOL   | {_sol_r:.3f} |

    Toutes extrêmement élevées (0,92–0,97) — les probabilités suivent de près le prix au comptant,
    comme prévu pour les marchés à objectif de prix.

    ### Avance-Retard : Qui bouge en premier ?

    | Direction | r moyen |
    |-----------|---------|
    | Δprob aujourd'hui → rendement demain (PM précède le prix) | {_lead_r:.3f} |
    | rendement aujourd'hui → Δprob demain (le prix précède PM)  | {_lag_r:.3f} |

    **Le prix au comptant précède Polymarket, et non l'inverse.**
    Un rendement exchange de +1 % aujourd'hui prédit un mouvement de probabilité Polymarket de +{_lag_r:.2f} std demain
    (moyenne sur les marchés). Les variations de probabilité Polymarket ont un pouvoir prédictif
    quasi nul sur les rendements exchange du lendemain.

    ### Inter-Exchanges (Coinbase vs Kraken)
    La corrélation est extrêmement élevée (>0,999999). Tout écart à court terme est du bruit
    et ne peut être arbitragé compte tenu des coûts de transaction.

    ### Implications
    - Les marchés d'événements crypto Polymarket sont **réactifs**, pas des indicateurs avancés.
    - Les probabilités des objectifs de prix sont essentiellement une transformation monotone du prix au comptant.
    - Pour des signaux alpha, il faudrait des marchés où les traders Polymarket ont un
      avantage informationnel — marchés réglementaires ou événementiels, pas de simples paris sur le niveau de prix.
    """)
    return


if __name__ == "__main__":
    app.run()
