import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Signal Research — 30-Stock Equity Universe (WRDS/CRSP)

    Exploratory signal research using local CRSP daily data.
    Data lives in `MyProjects/WRDS/data/raw/`.
    """)
    return


@app.cell
def _():
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import zipfile, pathlib

    # Dark theme with polished styling
    plt.style.use('dark_background')
    mpl.rcParams.update({
        'figure.facecolor': '#0d1117',
        'axes.facecolor': '#161b22',
        'axes.edgecolor': '#30363d',
        'axes.labelcolor': '#c9d1d9',
        'axes.grid': True,
        'grid.color': '#21262d',
        'grid.alpha': 0.6,
        'text.color': '#c9d1d9',
        'xtick.color': '#8b949e',
        'ytick.color': '#8b949e',
        'font.family': 'sans-serif',
        'font.size': 11,
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'figure.dpi': 150,
        'savefig.facecolor': '#0d1117',
        'savefig.edgecolor': '#0d1117',
    })

    LEAN_DAILY = pathlib.Path("../WRDS/lean-data/equity/usa/daily")
    COLS = ["datetime", "open", "high", "low", "close", "volume"]
    SCALE = 10_000
    return COLS, LEAN_DAILY, SCALE, mpl, np, pd, plt, zipfile


@app.cell
def _(COLS, LEAN_DAILY, SCALE, pd, zipfile):
    # Load all LEAN daily zip files into a single long DataFrame
    frames = []
    for zpath in sorted(LEAN_DAILY.glob("*.zip")):
        ticker = zpath.stem.upper()
        with zipfile.ZipFile(zpath) as z:
            csv_name = z.namelist()[0]
            df_t = pd.read_csv(z.open(csv_name), header=None, names=COLS,
                               parse_dates=["datetime"])
        df_t["ticker"] = ticker
        df_t["close_adj"] = df_t["close"] / SCALE
        frames.append(df_t[["datetime", "ticker", "close_adj"]])

    df = pd.concat(frames, ignore_index=True)
    df["date"] = df["datetime"].dt.normalize()
    print(f"Loaded {df['ticker'].nunique()} tickers  |  {df['date'].min().date()} → {df['date'].max().date()}  |  {len(df):,} rows")
    df.head()
    return (df,)


@app.cell
def _(df):
    # Pivot to wide: rows=date, cols=ticker
    close = df.pivot(index="date", columns="ticker", values="close_adj")

    # Drop tickers with >20% missing trading days
    thresh = int(len(close) * 0.8)
    close = close.dropna(axis=1, thresh=thresh)
    print(f"Universe after cleaning: {close.shape[1]} tickers × {close.shape[0]} days")
    close.tail()
    return (close,)


@app.cell
def _(close, np):
    # Daily log returns
    returns = np.log(close / close.shift(1))
    returns.tail()
    return


@app.cell
def _(mo):
    mo.md("""
    ## Momentum Signal (12-1 month)
    """)
    return


@app.cell
def _(close):
    # 12-month return skipping the most recent month (standard momentum)
    mom = close.pct_change(252).shift(21)  # 252 trading days back, skip 21
    mom_rank = mom.rank(axis=1, pct=True)  # cross-sectional percentile rank

    print("Momentum signal (most recent date):")
    latest = mom_rank.iloc[-1].sort_values(ascending=False)
    print(latest.to_string())
    return (latest,)


@app.cell
def _(latest, mpl, plt):
    fig, ax = plt.subplots(figsize=(14, 5))

    # Color bars by rank: red (weak) → green (strong)
    cmap = mpl.colormaps['RdYlGn']
    norm = mpl.colors.Normalize(vmin=0, vmax=1)
    colors = [cmap(norm(v)) for v in latest.values]

    bars = ax.bar(range(len(latest)), latest.values, color=colors,
                  edgecolor='#30363d', linewidth=0.5, width=0.8)

    ax.axhline(0.5, color='#f85149', linestyle='--', linewidth=1.2,
               alpha=0.7, label='Median')

    ax.set_xticks(range(len(latest)))
    ax.set_xticklabels(latest.index, rotation=45, ha='right', fontsize=9)
    ax.set_title("Cross-Sectional Momentum Rank  (12-1 month)")
    ax.set_ylabel("Percentile Rank")
    ax.set_ylim(0, 1.05)
    ax.legend(loc='upper right', framealpha=0.3)

    # Add a subtle colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, pad=0.02, aspect=30, shrink=0.8)
    cbar.set_label('Signal Strength', fontsize=9)
    cbar.ax.tick_params(labelsize=8)

    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(mo):
    mo.md("""
    ## Next Steps

    - Add more signals: value (P/B), quality (ROE), low-vol
    - Build a simple long/short portfolio and compute IC
    - Export signal scores to ObjectStore for use in QC backtests
    """)
    return


app._unparsable_cell(
    r"""
    # 2-Year Returns Analysis
    end_date = close.index[-1]
    start_date = end_date - pd.Timedelta(days=365*2)

    # Filter data to 2-year window
    close_2yr = close[close.index >= start_date]

    # Calculate 2-year returns (percentage)
    returns_2yr = ((close_2yr.iloc[-1] / close_2yr.iloc[0]) - 1) * 100

    # Sort by return
    returns_2yr_sorted = returns_2yr.sort_values(ascending=False)

    # Display summary
    mo.md(f"**2-Year Returns** (from {start_date.date()} to {end_date.date()})")
    """,
    column=None, disabled=False, hide_code=True, name="2yr_returns_calc"
)


app._unparsable_cell(
    r"""
    # Visualize 2-Year Returns
    fig_2yr, ax_2yr = plt.subplots(figsize=(12, 8))

    # Color code: green for positive, red for negative
    colors_2yr = ['green' if x > 0 else 'red' for x in returns_2yr_sorted.values]

    ax_2yr.barh(range(len(returns_2yr_sorted)), returns_2yr_sorted.values, color=colors_2yr, alpha=0.7)
    ax_2yr.set_yticks(range(len(returns_2yr_sorted)))
    ax_2yr.set_yticklabels(returns_2yr_sorted.index, fontsize=9)
    ax_2yr.set_xlabel('Return (%)', fontsize=11)
    ax_2yr.set_title(f'30-Stock Equity Universe: 2-Year Returns ({start_date.date()} to {end_date.date()})', fontsize=12, fontweight='bold')
    ax_2yr.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    ax_2yr.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.show()
    """,
    column=None, disabled=False, hide_code=True, name="2yr_returns_viz"
)


app._unparsable_cell(
    """
    # 2-Year Returns Summary Statistics
    summary_stats = mo.md(f\"\"\"
    ### Portfolio Statistics (2-Year Period)
    - **Mean Return**: {returns_2yr.mean():.2f}%
    - **Median Return**: {returns_2yr.median():.2f}%
    - **Std Dev**: {returns_2yr.std():.2f}%
    - **Best Performer**: {returns_2yr_sorted.index[0]} ({returns_2yr_sorted.values[0]:.2f}%)
    - **Worst Performer**: {returns_2yr_sorted.index[-1]} ({returns_2yr_sorted.values[-1]:.2f}%)
    - **Positive Returns**: {(returns_2yr > 0).sum()} stocks
    - **Negative Returns**: {(returns_2yr < 0).sum()} stocks

    ### Top 5 Performers
    {returns_2yr_sorted.head(5).to_string()}

    ### Bottom 5 Performers
    {returns_2yr_sorted.tail(5).to_string()}
    \"\"\")
    summary_stats
    """,
    column=None, disabled=False, hide_code=True, name="2yr_summary_stats"
)


app._unparsable_cell(
    r"""
    # Better 2-Year Returns Visualization
    fig_better, (ax_top, ax_bottom) = plt.subplots(1, 2, figsize=(16, 6))

    # Top 10 performers
    top_10 = returns_2yr_sorted.head(10)
    colors_top = ['darkgreen' if x > 0 else 'darkred' for x in top_10.values]
    ax_top.barh(range(len(top_10)), top_10.values, color=colors_top, alpha=0.8)
    ax_top.set_yticks(range(len(top_10)))
    ax_top.set_yticklabels(top_10.index, fontsize=10)
    ax_top.set_xlabel('Return (%)', fontsize=11)
    ax_top.set_title('Top 10 Performers', fontsize=12, fontweight='bold')
    ax_top.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    ax_top.grid(axis='x', alpha=0.3)

    # Bottom 10 performers
    bottom_10 = returns_2yr_sorted.tail(10)
    colors_bottom = ['darkred' if x < 0 else 'darkgreen' for x in bottom_10.values]
    ax_bottom.barh(range(len(bottom_10)), bottom_10.values, color=colors_bottom, alpha=0.8)
    ax_bottom.set_yticks(range(len(bottom_10)))
    ax_bottom.set_yticklabels(bottom_10.index, fontsize=10)
    ax_bottom.set_xlabel('Return (%)', fontsize=11)
    ax_bottom.set_title('Bottom 10 Performers', fontsize=12, fontweight='bold')
    ax_bottom.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    ax_bottom.grid(axis='x', alpha=0.3)

    plt.suptitle(f'30-Stock Equity Universe: 2-Year Returns ({start_date.date()} to {end_date.date()})', 
                 fontsize=13, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.show()
    """,
    column=None, disabled=False, hide_code=True, name="2yr_returns_improved"
)


@app.cell(hide_code=True)
def _(mo):

    # Load WRDS Global Factors (contrib.global_factor sample)
    import pandas as pd

    gf_df = pd.read_csv('/tmp/global_factors_sample.csv')
    gf_df['datadate'] = pd.to_datetime(gf_df['datadate'])

    mo.md(f"**✓ Loaded {len(gf_df):,} rows of global factor data**")
    return gf_df, pd


@app.cell(hide_code=True)
def _(gf_df):
    gf_df.head(12)
    return


@app.cell(hide_code=True)
def _(gf_df, mo):
    mo.md(f"""
    ## Global Factor Dataset (`contrib.global_factor`)
    - **Total rows**: {len(gf_df):,}
    - **Date range**: {gf_df['datadate'].min().date()} to {gf_df['datadate'].max().date()}
    - **Unique tickers**: {gf_df['permno'].nunique()}

    ### Sample Factors (444 available in full WRDS dataset)
    - **Momentum**: `mom1m`, `mom6m`, `mom12m` — price momentum
    - **Risk/Liquidity**: `si` (size), `dolvol` (dollar volume), `beta` (market beta)
    - **Quality**: `roe` (return on equity), `gpa` (gross profit margin), `acc` (accruals quality)

    Full dataset spans 91 countries with 444 firm characteristics.
    """)
    return


@app.cell(hide_code=True)
def _(gf_df):
    gf_df.describe().round(3)
    return


@app.cell(hide_code=True)
def _(gf_df, plt):

    # Correlation heatmap
    import seaborn as sns
    corr_cols = ['mom1m', 'mom6m', 'mom12m', 'si', 'dolvol', 'beta', 'roe', 'gpa', 'acc']
    corr_mat = gf_df[corr_cols].corr()

    fig_corr, ax_corr = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_mat, annot=True, fmt='.2f', cmap='coolwarm', center=0, 
                square=True, ax=ax_corr, cbar_kws={'label': 'Correlation'})
    ax_corr.set_title('Factor Correlations (Global Factor Dataset)')
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(gf_df, plt):

    # Distribution and scatter plots
    fig_dist, axes_dist = plt.subplots(2, 2, figsize=(12, 8))

    axes_dist[0,0].hist(gf_df['mom1m'].dropna(), bins=30, alpha=0.7, color='steelblue', edgecolor='black')
    axes_dist[0,0].set_title('1-Month Momentum')
    axes_dist[0,0].set_xlabel('Value')

    axes_dist[0,1].hist(gf_df['mom6m'].dropna(), bins=30, alpha=0.7, color='green', edgecolor='black')
    axes_dist[0,1].set_title('6-Month Momentum')
    axes_dist[0,1].set_xlabel('Value')

    axes_dist[1,0].hist(gf_df['mom12m'].dropna(), bins=30, alpha=0.7, color='coral', edgecolor='black')
    axes_dist[1,0].set_title('12-Month Momentum')
    axes_dist[1,0].set_xlabel('Value')

    axes_dist[1,1].scatter(gf_df['beta'].dropna(), gf_df['roe'].dropna(), alpha=0.4, s=30)
    axes_dist[1,1].set_xlabel('Beta')
    axes_dist[1,1].set_ylabel('ROE')
    axes_dist[1,1].set_title('Beta vs. Profitability')

    plt.tight_layout()
    plt.show()
    return


if __name__ == "__main__":
    app.run()
