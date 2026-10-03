"""Regression and failure-mode tests for the public-spectrum audit."""

import csv
from pathlib import Path

import analyze_spectrum as spec
import numpy as np
import pytest


def test_final_spectrum_loader_and_regression_values():
    wave, deviation, error = spec.load_spectrum(spec.DATA_DIR / "trappist1e_decontaminated_spectrum.txt")
    fit = spec.fit_constant(deviation, error)
    assert len(wave) == fit.n_bins == 67
    assert fit.chi2 == pytest.approx(42.85, abs=0.1)
    assert fit.dof == 66
    assert fit.p_value == pytest.approx(0.988, abs=0.005)


def test_all_pipeline_visit_products_are_loaded_and_grouped():
    metrics = spec.collect_pipeline_metrics()
    assert len(metrics) == 24
    assert {metric.pipeline for metric in metrics} == {
        "Canas", "Espinoza", "Grant", "Gressier", "Long", "Stevenson"
    }
    assert {metric.visit for metric in metrics} == set(spec.VISITS)
    summary = spec.summarize_visits(metrics)
    assert all(row["n_pipeline_reductions"] == 6 for row in summary)
    visit_104 = next(row for row in summary if row["visit"] == "104")
    earlier = [row["median_weighted_mean_depth_ppm"] for row in summary if row["visit"] != "104"]
    assert visit_104["median_weighted_mean_depth_ppm"] < min(earlier) - 200


def test_invalid_uncertainties_fail_loudly(tmp_path: Path):
    invalid = tmp_path / "invalid.txt"
    invalid.write_text("1.0 5.0 1.0\n2.0 6.0 0.0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="positive"):
        spec.load_spectrum(invalid)
    with pytest.raises(ValueError, match="positive"):
        spec.fit_constant(np.array([1.0, 2.0]), np.array([1.0, -1.0]))


def test_main_writes_machine_readable_outputs():
    spec.main()
    expected = {
        "summary_statistics.csv", "pipeline_visit_metrics.csv", "visit_summary.csv",
        "analysis_summary.json", "trappist1e_spectral_audit.png",
    }
    assert expected <= {path.name for path in spec.FIG_DIR.iterdir()}
    with (spec.FIG_DIR / "summary_statistics.csv").open(encoding="utf-8") as handle:
        rows = {row["quantity"]: row["value"] for row in csv.DictReader(handle)}
    assert int(rows["n_wavelength_points"]) == 67
    assert float(rows["standardized_residual_rms"]) < 1
