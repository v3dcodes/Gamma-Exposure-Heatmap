"""Gamma exposure as a strike x expiry grid.

Each cell is net dealer gamma exposure for that (strike, expiry) bucket:
    sum over calls (gamma*OI*100*spot^2*0.01) - sum over puts (...)
which makes it easy to see where positioning is concentrated and how it shifts
across the term structure.
"""
import numpy as np
import pandas as pd

CONTRACT = 100
SCALE = 0.01


def gamma_grid(df, spot):
    df = df.copy()
    notional = df.gamma * df.oi * CONTRACT * (spot ** 2) * SCALE
    df["gex"] = np.where(df.type == "C", notional, -notional)
    grid = df.pivot_table(index="strike", columns="dte", values="gex",
                          aggfunc="sum", fill_value=0.0).sort_index()
    return grid


def payload(df, spot):
    grid = gamma_grid(df, spot)
    return {
        "spot": spot,
        "strikes": [float(s) for s in grid.index],
        "expiries": [f"+{c}d" for c in grid.columns],
        "z": [[float(v) for v in row] for row in grid.values],
        "vmax": float(np.abs(grid.values).max() or 1.0),
    }
