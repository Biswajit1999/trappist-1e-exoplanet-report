"""Conditional diagnostics for binned transmission spectra.

No observational data are loaded or modified. Covariance is an explicit assumption.
"""
import numpy as np


def ar1_covariance(sigma, rho):
    """Construct D R D, R_ij=rho**abs(i-j), for ordered spectral bins."""
    sigma = np.asarray(sigma, dtype=float)
    if sigma.ndim != 1 or sigma.size < 2 or not np.all(np.isfinite(sigma)):
        raise ValueError("sigma must be a finite vector of at least two bins")
    if np.any(sigma <= 0) or not np.isfinite(rho) or abs(rho) >= 1:
        raise ValueError("positive errors and |rho| < 1 required")
    index = np.arange(sigma.size)
    return np.outer(sigma, sigma) * rho ** np.abs(index[:, None] - index[None, :])


def gls_flatness(depth, covariance):
    """Fit a constant depth with full covariance; return estimate, error and chi2."""
    y = np.asarray(depth, dtype=float)
    c = np.asarray(covariance, dtype=float)
    if y.ndim != 1 or y.size < 2 or not np.all(np.isfinite(y)):
        raise ValueError("depth must be a finite vector")
    if c.shape != (y.size, y.size) or not np.all(np.isfinite(c)):
        raise ValueError("invalid covariance shape or values")
    if not np.allclose(c, c.T, atol=1e-12, rtol=1e-12):
        raise ValueError("covariance must be symmetric")
    l = np.linalg.cholesky(c)
    one = np.ones_like(y)
    wy = np.linalg.solve(l, y)
    wone = np.linalg.solve(l, one)
    denom = float(wone @ wone)
    mean = float((wone @ wy) / denom)
    residual = wy - mean * wone
    return mean, denom ** -0.5, float(residual @ residual)


def leave_one_bin_out(depth, sigma):
    """Return full weighted constant and exact deletion influence for each bin."""
    y = np.asarray(depth, dtype=float)
    s = np.asarray(sigma, dtype=float)
    if y.ndim != 1 or s.shape != y.shape or y.size < 3:
        raise ValueError("at least three matched bins required")
    if not np.all(np.isfinite(y)) or not np.all(np.isfinite(s)) or np.any(s <= 0):
        raise ValueError("finite depths and positive errors required")
    w = 1 / s**2
    total_w = w.sum()
    total_y = np.dot(w, y)
    full = float(total_y / total_w)
    deleted = (total_y - w * y) / (total_w - w)
    return full, deleted - full
