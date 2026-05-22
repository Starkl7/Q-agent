# Treasury.gov Rates Pipeline

This document describes the Treasury.gov rates pipeline added to the Q-agent repository.

## Purpose

The pipeline downloads Treasury rate data from the U.S. Treasury FiscalData API and converts the data into research-friendly CSV files.

This pipeline is designed for:

- Yield curve research
- Macro trading strategies
- Regime detection
- Fixed income analytics
- Feature engineering for machine learning
- QuantConnect research notebooks
- Cross-asset studies involving rates and equities

## Pipeline Location

```text
infrastructure/pipelines/treasury_gov_rates/
```

## Main Script

```text
download_treasury_rates.py
```

## Output Files

The script writes two CSV files:

```text
raw Treasury dataset
curve matrix dataset
```

The curve matrix pivots the Treasury security descriptions into columns.

## Example Usage

```bash
python infrastructure/pipelines/treasury_gov_rates/download_treasury_rates.py
```

Custom output directory:

```bash
python infrastructure/pipelines/treasury_gov_rates/download_treasury_rates.py \
    --output-dir data/treasury_rates
```

## Example Research Projects

### Equity Returns vs Yield Curve

Combine:

- WRDS equity returns
- Treasury curve steepness
- Treasury regime classifications

Potential factors:

- 10Y minus 2Y spread
- Curve inversion duration
- Rolling rate volatility
- Front-end vs long-end momentum

### Options Volatility vs Rates

Combine:

- Treasury yields
- VIX term structure
- Option implied volatility

### ETF Rotation

Use Treasury curve information to classify macro environments:

- Steepening
- Flattening
- Inversion
- Re-steepening

Then test ETF sector rotation strategies.

## Future Enhancements

Potential future upgrades:

- Daily Treasury par yield curve endpoint
- SOFR ingestion
- Fed Funds ingestion
- FRED integration
- QuantConnect custom data wrappers
- ObjectStore export helpers
- Automated scheduling jobs
- Notebook templates
- Database persistence layer
- Yield curve interpolation
- Nelson-Siegel fitting
- PCA factor extraction

## Notes

This pipeline intentionally uses minimal dependencies:

- pandas
- requests

The goal is to keep the example easy for masters students to understand and extend.
