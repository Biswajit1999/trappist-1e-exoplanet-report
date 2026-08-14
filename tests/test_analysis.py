"""Executable checks on the spectrum loader and chi-squared p-value
formula, and a regression guard that the pipeline still reproduces the
documented headline numbers when run on the real downloaded data."""

import csv

import numpy as np
from scipy.stats import chi2 as chi2_dist
import analyze_spectrum as spec


def test_load_spectrum_returns_matching_length_arrays():
    wave, dev_ppm, err_ppm = spec.load_spectrum(spec.DATA_DIR / "trappist1e_decontaminated_spectrum.txt")
    assert len(wave) == len(dev_ppm) == len(err_ppm) == 67
    assert np.all(err_ppm > 0)


def test_chi2_p_value_matches_known_case():
    # A perfectly flat, noiseless-relative-to-error dataset around its own
    # weighted mean should have chi2 = 0 and p-value = 1.
    values = np.full(10, 5.0)
    errors = np.full(10, 1.0)
    weights = 1.0 / errors**2
    flat = np.sum(values * weights) / np.sum(weights)
    chi2 = np.sum(((values - flat) / errors) ** 2)
    assert np.isclose(chi2, 0.0, atol=1e-10)
    assert np.isclose(chi2_dist.sf(chi2, len(values) - 1), 1.0)


def test_pipeline_reproduces_documented_headline_numbers():
    spec.FIG_DIR.mkdir(exist_ok=True)
    spec.main()
    rows = {}
    with (spec.FIG_DIR / "summary_statistics.csv").open() as f:
        for row in csv.DictReader(f):
            rows[row["quantity"]] = row["value"]
    assert int(rows["n_wavelength_points"]) == 67
    assert abs(float(rows["flat_line_chi2"]) - 42.85) < 0.1
    assert int(rows["flat_line_dof"]) == 66
    assert abs(float(rows["flat_line_p_value"]) - 0.988) < 0.005
