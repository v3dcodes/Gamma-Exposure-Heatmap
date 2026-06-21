"""Black-Scholes pricing and Greeks (vectorized, NumPy-only).

All functions accept scalars or NumPy arrays. Time `t` is in years,
rates `r`/`q` are continuously compounded, `sigma` is annualized vol.
"""
import math
import numpy as np

_erf = np.vectorize(math.erf)


def norm_pdf(x):
    x = np.asarray(x, dtype=float)
    return np.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def norm_cdf(x):
    x = np.asarray(x, dtype=float)
    return 0.5 * (1.0 + _erf(x / math.sqrt(2.0)))


def d1d2(s, k, t, r, sigma, q=0.0):
    s, k, t, sigma = map(lambda v: np.asarray(v, dtype=float), (s, k, t, sigma))
    t = np.maximum(t, 1e-9)
    sigma = np.maximum(sigma, 1e-9)
    vol_t = sigma * np.sqrt(t)
    d1 = (np.log(s / k) + (r - q + 0.5 * sigma * sigma) * t) / vol_t
    d2 = d1 - vol_t
    return d1, d2


def price(s, k, t, r, sigma, kind="C", q=0.0):
    d1, d2 = d1d2(s, k, t, r, sigma, q)
    disc_r, disc_q = np.exp(-r * t), np.exp(-q * t)
    if kind.upper().startswith("C"):
        return s * disc_q * norm_cdf(d1) - k * disc_r * norm_cdf(d2)
    return k * disc_r * norm_cdf(-d2) - s * disc_q * norm_cdf(-d1)


def delta(s, k, t, r, sigma, kind="C", q=0.0):
    d1, _ = d1d2(s, k, t, r, sigma, q)
    disc_q = np.exp(-q * t)
    if kind.upper().startswith("C"):
        return disc_q * norm_cdf(d1)
    return disc_q * (norm_cdf(d1) - 1.0)


def gamma(s, k, t, r, sigma, q=0.0):
    d1, _ = d1d2(s, k, t, r, sigma, q)
    t = np.maximum(np.asarray(t, float), 1e-9)
    sigma = np.maximum(np.asarray(sigma, float), 1e-9)
    return np.exp(-q * t) * norm_pdf(d1) / (s * sigma * np.sqrt(t))


def charm(s, k, t, r, sigma, kind="C", q=0.0):
    """Charm = d(Delta)/d(time), returned per calendar day (delta drift per day)."""
    d1, d2 = d1d2(s, k, t, r, sigma, q)
    t = np.maximum(np.asarray(t, float), 1e-9)
    sigma = np.maximum(np.asarray(sigma, float), 1e-9)
    common = np.exp(-q * t) * norm_pdf(d1) * (2.0 * (r - q) * t - d2 * sigma * np.sqrt(t)) \
        / (2.0 * t * sigma * np.sqrt(t))
    if kind.upper().startswith("C"):
        per_year = q * np.exp(-q * t) * norm_cdf(d1) - common
    else:
        per_year = -q * np.exp(-q * t) * norm_cdf(-d1) - common
    return per_year / 365.0
