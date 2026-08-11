"""Analyze real JWST MIRI eclipse data for TRAPPIST-1 b, as system context for
interpreting TRAPPIST-1 e (which has no public atmospheric spectrum yet).

Data source: Zenodo record 10.5281/zenodo.13385020, "Products of Combined
analysis of the 12.8 and 15 micron JWST/MIRI eclipse observations of
TRAPPIST-1 b" (Ducrot et al.). Retrieved directly from Zenodo; reproduced
unmodified in data/.

This script performs the same real physics used to conclude TRAPPIST-1 b
has no thick atmosphere: it inverts each measured secondary-eclipse depth
into a dayside brightness temperature (via the Planck function, using the
real measured Rp/Rs and host Teff), then compares that temperature to the
two theoretical limits for a bare rock -- full heat redistribution (an
atmosphere efficiently spreads absorbed starlight around the planet) and
zero redistribution (all absorbed energy re-radiates from the dayside
only, i.e. no atmosphere to move heat around).
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FIG_DIR = Path(__file__).resolve().parents[1] / "figures"

H = 6.62607015e-34   # J s
C = 2.99792458e8     # m/s
KB = 1.380649e-23    # J/K

# Real TRAPPIST-1 b system parameters (NASA Exoplanet Archive, pscomppars)
RP_REARTH = 1.116
RS_RSUN = 0.1192
TEFF_STAR_K = 2566.0
A_AU = 0.01154
REARTH_M = 6.371e6
RSUN_M = 6.957e8
AU_M = 1.495978707e11


def planck(wavelength_m: np.ndarray, temperature_k: float) -> np.ndarray:
    return (2 * H * C**2 / wavelength_m**5) / (
        np.expm1(H * C / (wavelength_m * KB * temperature_k))
    )


def brightness_temperature(eclipse_depth: float, wavelength_um: float) -> float:
    wavelength_m = wavelength_um * 1e-6
    rp_over_rs = (RP_REARTH * REARTH_M) / (RS_RSUN * RSUN_M)

    def residual(t_planet: float) -> float:
        predicted_depth = rp_over_rs**2 * planck(wavelength_m, t_planet) / planck(
            wavelength_m, TEFF_STAR_K
        )
        return predicted_depth - eclipse_depth

    return brentq(residual, 50, 3000)


def load_observations(path: Path):
    rows = []
    with path.open() as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "wavelength": float(row["Wavelength"]),
                    "depth_ppm": float(row["eclipse_depth"]),
                    "depth_err_ppm": float(row["err_eclipse_depth"]),
                }
            )
    return rows


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    observations = load_observations(DATA_DIR / "trappist1b_eclipse_depths.csv")

    a_m = A_AU * AU_M
    rs_m = RS_RSUN * RSUN_M
    t_zero_redistribution = TEFF_STAR_K * np.sqrt(rs_m / a_m) * (2.0 / 3.0) ** 0.25
    t_full_redistribution = TEFF_STAR_K * np.sqrt(rs_m / (2 * a_m))

    results = []
    for obs in observations:
        depth = obs["depth_ppm"] * 1e-6
        depth_hi = (obs["depth_ppm"] + obs["depth_err_ppm"]) * 1e-6
        depth_lo = max((obs["depth_ppm"] - obs["depth_err_ppm"]) * 1e-6, 1e-8)
        t_best = brightness_temperature(depth, obs["wavelength"])
        t_hi = brightness_temperature(depth_hi, obs["wavelength"])
        t_lo = brightness_temperature(depth_lo, obs["wavelength"])
        results.append({**obs, "t_day_k": t_best, "t_day_err_k": (t_hi - t_lo) / 2})

    summary_path = FIG_DIR / "summary_statistics.csv"
    with summary_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "value", "unit"])
        writer.writerow(["t_zero_redistribution_bare_rock", f"{t_zero_redistribution:.1f}", "K"])
        writer.writerow(["t_full_redistribution_bare_rock", f"{t_full_redistribution:.1f}", "K"])
        for r in results:
            writer.writerow(
                [f"t_day_at_{r['wavelength']}um", f"{r['t_day_k']:.1f} +/- {r['t_day_err_k']:.1f}", "K"]
            )

    fig, ax = plt.subplots(figsize=(8, 5.5))
    waves = [r["wavelength"] for r in results]
    temps = [r["t_day_k"] for r in results]
    errs = [r["t_day_err_k"] for r in results]
    ax.errorbar(waves, temps, yerr=errs, fmt="o", ms=8, color="#8a3c3c", label="TRAPPIST-1 b dayside T (this analysis)")
    ax.axhline(t_zero_redistribution, color="#c0562a", ls="--", lw=1.3, label=f"bare rock, no redistribution ({t_zero_redistribution:.0f} K)")
    ax.axhline(t_full_redistribution, color="#2c5f8a", ls="--", lw=1.3, label=f"bare rock, full redistribution ({t_full_redistribution:.0f} K)")
    ax.set_xlabel("Wavelength [micron]")
    ax.set_ylabel("Dayside brightness temperature [K]")
    ax.set_title("TRAPPIST-1 b dayside temperature from real JWST MIRI eclipse depths\n(system context for interpreting TRAPPIST-1 e)")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "trappist1b_dayside_temperature.png", dpi=200)

    print(f"Wrote {summary_path}")
    print(f"Wrote {FIG_DIR / 'trappist1b_dayside_temperature.png'}")
    print(f"Bare-rock limits: zero redistribution={t_zero_redistribution:.1f} K, full redistribution={t_full_redistribution:.1f} K")
    for r in results:
        print(f"  {r['wavelength']} um: T_day = {r['t_day_k']:.1f} +/- {r['t_day_err_k']:.1f} K")


if __name__ == "__main__":
    main()
