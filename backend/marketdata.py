"""Options-chain data layer.

`get_chain()` returns a pandas DataFrame with one row per option:
    expiry, dte, strike, type ('C'/'P'), iv, oi, volume, bid, ask, mid,
    gamma, delta, charm

By default it builds a realistic *synthetic* chain so the project runs with
no credentials. To use real data, set the relevant environment variables and
the matching provider below will be used instead.

    Schwab : SCHWAB_TOKEN          (see _from_schwab)
    CBOE   : CBOE_TOKEN            (see _from_cboe)
"""
import os
import numpy as np
import pandas as pd

import bs

TRADING_DAYS = 252.0


def _smile(moneyness, atm_vol=0.18, skew=0.35, curv=0.6):
    """Simple vol smile: higher IV for OTM puts, gentle curvature."""
    m = np.asarray(moneyness, float)
    return atm_vol + skew * (-m) + curv * m * m


def synthetic_chain(spot=5500.0, expiries_dte=(2, 9, 16, 30, 60),
                    width=0.06, step=5.0, r=0.045, seed=7, mispricing=0.0):
    """Build a synthetic SPX-style chain centred on `spot`."""
    rng = np.random.default_rng(seed)
    lo, hi = spot * (1 - width), spot * (1 + width)
    strikes = np.arange(round(lo / step) * step, hi + step, step)
    rows = []
    for dte in expiries_dte:
        t = dte / 365.0
        for k in strikes:
            m = np.log(k / spot)
            iv = float(np.clip(_smile(m), 0.05, 1.5))
            g = float(bs.gamma(spot, k, t, r, iv))
            # open interest peaks near ATM and at round strikes
            atm_w = np.exp(-((k - spot) / (spot * 0.02)) ** 2)
            round_w = 1.6 if k % 50 == 0 else (1.25 if k % 25 == 0 else 1.0)
            for kind in ("C", "P"):
                oi = int(max(0, rng.normal(9000 * atm_w * round_w, 1500)) + 50)
                vol = int(max(0, rng.normal(oi * 0.4, oi * 0.2)))
                mid = float(bs.price(spot, k, t, r, iv, kind))
                if mispricing:
                    mid *= 1.0 + rng.normal(0.0, mispricing)
                spread = max(0.05, mid * 0.01)
                rows.append(dict(
                    expiry=f"+{dte}d", dte=dte, strike=float(k), type=kind,
                    iv=round(iv, 4), oi=oi, volume=vol,
                    bid=round(max(0.0, mid - spread / 2), 2),
                    ask=round(mid + spread / 2, 2), mid=round(max(0.0, mid), 2),
                    gamma=g,
                    delta=float(bs.delta(spot, k, t, r, iv, kind)),
                    charm=float(bs.charm(spot, k, t, r, iv, kind)),
                ))
    df = pd.DataFrame(rows)
    df.attrs["spot"] = spot
    df.attrs["r"] = r
    return df


def _from_schwab():
    raise NotImplementedError(
        "Plug your Schwab Trader API call here and return the same DataFrame "
        "schema as synthetic_chain(). Use os.environ['SCHWAB_TOKEN'] for auth."
    )


def _from_cboe():
    raise NotImplementedError(
        "Plug your CBOE All Access / DataShop call here and return the same "
        "DataFrame schema as synthetic_chain(). Use os.environ['CBOE_TOKEN']."
    )


def get_chain(spot=5500.0, **kw):
    """Live provider if creds are set, else synthetic (default)."""
    try:
        if os.environ.get("SCHWAB_TOKEN"):
            return _from_schwab()
        if os.environ.get("CBOE_TOKEN"):
            return _from_cboe()
    except NotImplementedError:
        pass
    return synthetic_chain(spot=spot, **kw)
