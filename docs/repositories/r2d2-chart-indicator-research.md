# R2D2 Chart Indicator Research

An explainable Pine Script research prototype and a written study of multi-colour candle states. The implementation explores how a trend-state display could combine momentum, trend, volatility, volume and cancellation/continuation logic.

The prototype is an independently written behavioral approximation based on limited visible examples and public descriptions. It is not recovered proprietary source and is not expected to match another indicator's historical output exactly.

## Repository contents

- `smart_candles_reconstruction.pine`: the editable Pine source.
- `report.md`: observed behavior, design hypotheses, reconstruction choices, unknowns and a proposed validation process.
- `check.py`: general repository source-format checks. It is not a Pine compiler.

Source screenshots, private attachment archives, account details and investing records are deliberately omitted. The report distinguishes technical observations from inferred inputs/weights so the missing evidence is not replaced by certainty.

## What the prototype explores

- ATR-normalized price movement and fast/slow trend separation.
- RSI displacement and position within a Bollinger-style envelope.
- Directional volume context and an optional broad-market benchmark.
- Adaptive score thresholds and hysteresis: entering a state can require stronger evidence than remaining in it.
- Separate transition, continuation, cancellation/consolidation and possible trim states.
- Confirmed-bar behavior by default, with the limits described in the source/report.

## Trying the source

Read the report and input settings first. Open the Pine file in TradingView's editor, compile it there and add it to a chart you control. Confirm the Pine version and platform requirements in the file. Compilation and live chart rendering are external steps; they are not performed by the Python check script.

```bash
python3 check.py
```

For a meaningful comparison, record closed-bar outputs across several instruments/timeframes, separate calibration from later evaluation and test whether a displayed state changes after the bar closes. Matching selected screenshots is not a substitute for an untouched evaluation period.

## Limits

The exact reference formula, calibration choices and historical repaint behavior remain unknown. The screenshots used for the original study were not a backtest. This repo makes no assertion of signal accuracy, reproducibility of a third-party product or profitable trading performance.

The study is kept separate from the active trading system. Importing the Pine file does not approve a Lab strategy or change a paper book. Any future strategy built from it still needs explicit rules, execution assumptions, validation and a forward trial.

## Privacy, provenance and updates

This repository is a sanitized source export. No provider credentials, personal contact information, configured IP addresses, private conversations or runtime databases are included. Example hostnames and local environment variables are intentional. Keep newly generated account data and captures outside version control.

A source manifest records exported files. Local adaptations and third-party material retain their own provenance/notices; public visibility does not apply a new blanket license to every file. Related repositories and the manual update process are listed in the [workspace catalogue](https://github.com/r2d2broooo/r2d2-workspace-catalog).

Updates are made only on explicit request. Cloning does not enable an automatic sync, scheduled publication or Git push.
