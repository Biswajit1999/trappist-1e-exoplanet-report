"""Analyze the decontaminated JWST NIRSpec/PRISM transmission spectrum
of TRAPPIST-1e, testing how consistent it is with a flat, featureless
line -- the same first-pass test used elsewhere in this portfolio for
other rocky planets (see the LHS 475b report).

Data source: Espinoza et al. (2025), JWST-TST DREAMS: NIRSpec/PRISM
Transmission Spectroscopy of the Habitable Zone Planet TRAPPIST-1e,
ApJL 990, L52 (arXiv:2509.05414), Zenodo record 16125662. See
data/SOURCE.md for the exact file used.

This script's own flat-line chi-squared is a simpler test than the
paper's own atmospheric retrieval, which combines this spectrum with
instrument systematics modeling and forward-model grids to place
quantitative limits on specific atmosphere types. The paper reports
ruling out cloud-free, hydrogen-dominated atmospheres (>=80% H2 by
volume) at better than 3-sigma; this script's own statistic is reported
next to that, not as a substitute for it.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import scienceplots  # noqa: F401 (registers 'science' style)
import numpy as np

plt.style.use(["science", "no-latex"])

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FIG_DIR = Path(__file__).resolve().parents[1] / "figures"

PAPER_SIGNIFICANCE = 3.0  # paper's own stated rejection of a cloud-free, H2-dominated (>=80%) atmosphere


def load_spectrum(path: Path):
    wave, dev_ppm, err_ppm = [], [], []
    with path.open() as handle:
        for line in handle:
            parts = line.split()
            if len(parts) != 3:
                continue
            w, d, e = map(float, parts)
            wave.append(w)
            dev_ppm.append(d)
            err_ppm.append(e)
    return np.array(wave), np.array(dev_ppm), np.array(err_ppm)


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    wave, dev_ppm, err_ppm = load_spectrum(DATA_DIR / "trappist1e_decontaminated_spectrum.txt")

    # Flat-line (featureless) fit: inverse-variance-weighted mean deviation.
    weights = 1.0 / err_ppm**2
    flat_dev = np.sum(dev_ppm * weights) / np.sum(weights)
    flat_chi2 = np.sum(((dev_ppm - flat_dev) / err_ppm) ** 2)
    dof = len(wave) - 1
    reduced_chi2 = flat_chi2 / dof

    summary_path = FIG_DIR / "summary_statistics.csv"
    with summary_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "value", "unit"])
        writer.writerow(["n_wavelength_points", len(wave), "count"])
        writer.writerow(["flat_line_deviation", f"{flat_dev:.2f}", "ppm"])
        writer.writerow(["flat_line_reduced_chi2_this_script", f"{reduced_chi2:.2f}", "dimensionless"])
        writer.writerow(["paper_rejection_significance_h2_rich", f"{PAPER_SIGNIFICANCE}+", "sigma (Espinoza et al. 2025, full retrieval)"])

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.errorbar(wave, dev_ppm, yerr=err_ppm, fmt="o", ms=4, color="#1f4e79", capsize=2, label="Decontaminated NIRSpec/PRISM spectrum")
    ax.axhline(flat_dev, color="#a8431f", ls="--", lw=1.5, label=f"Flat-line fit (χ²/dof = {reduced_chi2:.2f})")
    ax.axhline(0, color="#999", ls=":", lw=1)
    ax.set_xlabel("Wavelength [μm]")
    ax.set_ylabel("Deviation from flat continuum [ppm]")
    ax.set_title("TRAPPIST-1e: decontaminated transmission spectrum\n(Espinoza et al. 2025)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "trappist1e_transmission_spectrum.png", dpi=200)

    print(f"Wrote {summary_path}")
    print(f"Wrote {FIG_DIR / 'trappist1e_transmission_spectrum.png'}")
    print(f"n={len(wave)}, flat-line deviation = {flat_dev:.2f} ppm, reduced chi2 = {reduced_chi2:.2f}")
    print(f"Paper's own rejection of a cloud-free, H2-dominated (>=80%) atmosphere: {PAPER_SIGNIFICANCE}+ sigma")


if __name__ == "__main__":
    main()
