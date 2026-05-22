import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def _():
    return


@app.cell(hide_code=True)
def imports():

    import marimo as mo
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots


    return go, make_subplots, mo, np, pd, px


@app.cell(hide_code=True)
def title(mo):
    mo.md("""
    # Piotroski F-Score & Earnings Explorer

    Exploring the F-Score data computed from Compustat (comp.funda) via WRDS.
    The Piotroski F-Score is a 0–9 composite of nine binary signals measuring
    profitability, leverage/liquidity, and operating efficiency.
    """)
    return


@app.cell(hide_code=True)
def load_data(COLS, LEAN_DAILY, SCALE, pd, zipfile):
    # Load all LEAN daily zip files into a single long DataFrame
    frames = []
    for zpath in sorted(LEAN_DAILY.glob("*.zip")):
        ticker = zpath.stem.upper()
        if not ticker.startswith('S'):  # Filter for tickers starting with S
            continue
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


@app.cell(hide_code=True)
def data_preview(df, mo):

    mo.ui.table(df.head(20), label="Raw Data Preview")
    return


@app.cell(hide_code=True)
def score_distribution(df, px):

    fig_dist = px.histogram(
        df, x="F_Score", nbins=10,
        title="F-Score Distribution (All Years)",
        labels={"F_Score": "Piotroski F-Score", "count": "Count"},
        color_discrete_sequence=["steelblue"]
    )
    fig_dist.update_layout(bargap=0.1)
    fig_dist
    return


@app.cell(hide_code=True)
def score_by_year(df, px):

    yearly_dist = df.groupby(["FiscalYear", "F_Score"]).size().reset_index(name="Count")
    fig_heat = px.density_heatmap(
        yearly_dist, x="FiscalYear", y="F_Score", z="Count",
        title="F-Score Distribution by Fiscal Year",
        labels={"FiscalYear": "Fiscal Year", "F_Score": "F-Score"},
        color_continuous_scale="Blues"
    )
    fig_heat
    return


@app.cell(hide_code=True)
def high_scorers_time(df, go, make_subplots):

    high_score_counts = (
        df[df["F_Score"] >= 7]
        .groupby("FiscalYear")["Ticker"]
        .nunique()
        .reset_index(name="HighScorerCount")
    )
    total_counts = df.groupby("FiscalYear")["Ticker"].nunique().reset_index(name="TotalCount")
    merged = high_score_counts.merge(total_counts, on="FiscalYear")
    merged["Pct"] = (merged["HighScorerCount"] / merged["TotalCount"] * 100).round(1)

    fig_high = make_subplots(specs=[[{"secondary_y": True}]])
    fig_high.add_trace(
        go.Bar(x=merged["FiscalYear"], y=merged["HighScorerCount"], name="High Scorers (F>=7)", marker_color="steelblue"),
        secondary_y=False
    )
    fig_high.add_trace(
        go.Scatter(x=merged["FiscalYear"], y=merged["Pct"], name="% of Universe", mode="lines+markers", marker_color="orange"),
        secondary_y=True
    )
    fig_high.update_layout(title="High F-Score Stocks Over Time", xaxis_title="Fiscal Year")
    fig_high.update_yaxes(title_text="Count", secondary_y=False)
    fig_high.update_yaxes(title_text="% of Universe", secondary_y=True)
    fig_high
    return


@app.cell(hide_code=True)
def component_breakdown(df, px):

    components = ["F1_PositiveNI", "F2_PositiveROA", "F3_PositiveCFO", "F4_CFOgtNI",
                  "F5_LeverageDown", "F6_LiquidityUp", "F7_NoNewShares",
                  "F8_GrossMarginUp", "F9_AssetTurnoverUp"]
    comp_means = df.groupby("FiscalYear")[components].mean().reset_index()
    comp_long = comp_means.melt(id_vars="FiscalYear", var_name="Component", value_name="PassRate")

    fig_comp = px.line(
        comp_long, x="FiscalYear", y="PassRate", color="Component",
        title="F-Score Component Pass Rates Over Time",
        labels={"PassRate": "Pass Rate", "FiscalYear": "Fiscal Year"}
    )
    fig_comp.update_layout(yaxis_tickformat=".0%", legend=dict(font=dict(size=10)))
    fig_comp
    return


@app.cell(hide_code=True)
def earnings_header(mo):
    mo.md("""
    ## Earnings & Profitability Metrics

    Exploring the underlying financial data: Net Income, ROA, CFO, and margins.
    """)
    return


@app.cell(hide_code=True)
def roa_by_score(df, np, pd, px):

    df_metrics = df.copy()
    df_metrics["ROA"] = df_metrics["NetIncome"] / df_metrics["TotalAssets"]
    df_metrics["CFO_to_Assets"] = df_metrics["OperatingCashFlow"] / df_metrics["TotalAssets"]
    df_metrics["GrossMargin"] = df_metrics["GrossProfit"] / df_metrics["Revenue"]
    df_metrics["ScoreBucket"] = pd.cut(df_metrics["F_Score"], bins=[-1, 3, 5, 7, 9], labels=["0-3", "4-5", "6-7", "8-9"])

    # Replace inf and filter to reasonable range for plotting
    for col in ["ROA", "CFO_to_Assets", "GrossMargin"]:
        df_metrics[col] = df_metrics[col].replace([np.inf, -np.inf], np.nan)

    roa_plot = df_metrics.dropna(subset=["ScoreBucket", "ROA"]).copy()
    roa_plot = roa_plot[(roa_plot["ROA"] >= -1) & (roa_plot["ROA"] <= 1)]

    fig_roa = px.violin(
        roa_plot,
        x="ScoreBucket", y="ROA", color="ScoreBucket",
        box=True, points=False,
        title="ROA by F-Score Bucket",
        labels={"ScoreBucket": "F-Score Bucket", "ROA": "Return on Assets"},
    )
    fig_roa.update_layout(showlegend=False)
    fig_roa
    return (df_metrics,)


@app.cell(hide_code=True)
def cfo_by_score(df_metrics, px):

    cfo_plot = df_metrics.dropna(subset=["ScoreBucket", "CFO_to_Assets"]).copy()
    cfo_plot = cfo_plot[(cfo_plot["CFO_to_Assets"] >= -1) & (cfo_plot["CFO_to_Assets"] <= 1)]

    fig_cfo = px.violin(
        cfo_plot,
        x="ScoreBucket", y="CFO_to_Assets", color="ScoreBucket",
        box=True, points=False,
        title="Cash Flow from Operations / Total Assets by F-Score Bucket",
        labels={"ScoreBucket": "F-Score Bucket", "CFO_to_Assets": "CFO / Assets"},
    )
    fig_cfo.update_layout(showlegend=False)
    fig_cfo
    return


@app.cell(hide_code=True)
def margin_by_score(df_metrics, px):

    margin_plot = df_metrics.dropna(subset=["ScoreBucket", "GrossMargin"]).copy()
    margin_plot = margin_plot[(margin_plot["GrossMargin"] >= -1) & (margin_plot["GrossMargin"] <= 1)]

    fig_margin = px.violin(
        margin_plot,
        x="ScoreBucket", y="GrossMargin", color="ScoreBucket",
        box=True, points=False,
        title="Gross Margin by F-Score Bucket",
        labels={"ScoreBucket": "F-Score Bucket", "GrossMargin": "Gross Margin"},
    )
    fig_margin.update_layout(showlegend=False)
    fig_margin
    return


@app.cell(hide_code=True)
def filters(df, mo):

    score_slider = mo.ui.slider(0, 9, value=7, label="Minimum F-Score")
    year_slider = mo.ui.range_slider(
        int(df["FiscalYear"].min()), int(df["FiscalYear"].max()),
        value=[2015, int(df["FiscalYear"].max())],
        label="Fiscal Year Range"
    )
    mo.hstack([score_slider, year_slider])
    return score_slider, year_slider


@app.cell(hide_code=True)
def filtered_summary(df, mo, score_slider, year_slider):

    filtered = df[
        (df["F_Score"] >= score_slider.value) &
        (df["FiscalYear"] >= year_slider.value[0]) &
        (df["FiscalYear"] <= year_slider.value[1])
    ].sort_values(["FiscalYear", "F_Score"], ascending=[False, False])

    mo.md(f"**{len(filtered):,} rows matching F-Score >= {score_slider.value}, years {year_slider.value[0]}–{year_slider.value[1]}** ({filtered['Ticker'].nunique()} unique tickers)")
    return (filtered,)


@app.cell(hide_code=True)
def filtered_table(filtered, mo):

    mo.ui.table(filtered[["Ticker", "CompanyName", "FiscalYear", "F_Score", "NetIncome", "Revenue", "TotalAssets"]].head(100), label="Filtered Stocks")
    return


if __name__ == "__main__":
    app.run()
