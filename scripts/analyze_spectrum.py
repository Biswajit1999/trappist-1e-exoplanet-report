"""Reproduce a scoped, descriptive audit of the public TRAPPIST-1e spectra.

The final 67-bin product is tested against a fitted constant with a diagonal
likelihood. The 24 visit products (four visits reduced by six teams) expose
visit-to-visit and reduction-pipeline sensitivity. Those 24 files are not 24
independent observations: each set of six reuses the same visit.

This does not reproduce the Gaussian-process contamination model or atmospheric
retrieval in Espinoza et al. (2025; arXiv:2509.05414). Failure to reject a
constant is not evidence that no atmosphere is present. The paper's >3-sigma
exclusion of cloudy primary atmospheres with at least 80% H2 comes from the
authors' retrieval, not this audit.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chi2 as chi2_dist

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PIPELINE_DIR = DATA_DIR / "pipeline_visits"
FIG_DIR = ROOT / "figures"
PAPER_SIGNIFICANCE = 3.0
FILE_RE = re.compile(r"JWST_PRISM_([A-Za-z]+)(001|002|003|104)\.txt$")
VISITS = ("001", "002", "003", "104")


@dataclass(frozen=True)
class FlatFit:
    n_bins: int
    weighted_mean_ppm: float
    chi2: float
    dof: int
    reduced_chi2: float
    p_value: float
    standardized_residual_rms: float
    max_abs_standardized_residual: float


@dataclass(frozen=True)
class PipelineVisitMetric:
    pipeline: str
    visit: str
    n_bins: int
    weighted_mean_depth_ppm: float
    mean_standard_error_ppm: float
    chi2: float
    dof: int
    reduced_chi2: float
    p_value: float


def _validate_arrays(wave: np.ndarray, values: np.ndarray, errors: np.ndarray) -> None:
    if not (wave.size == values.size == errors.size) or wave.size < 2:
        raise ValueError("spectrum arrays must have equal length and at least two bins")
    if not np.all(np.isfinite(np.column_stack((wave, values, errors)))):
        raise ValueError("spectrum contains non-finite values")
    if np.any(errors <= 0):
        raise ValueError("all uncertainties must be positive")
    if np.any(np.diff(wave) <= 0):
        raise ValueError("wavelengths must be strictly increasing")


def load_spectrum(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) == 3:
                try:
                    rows.append(tuple(map(float, parts)))
                except ValueError:
                    continue
    if not rows:
        raise ValueError(f"no three-column spectrum rows found in {path}")
    wave, values, errors = (np.asarray(column) for column in zip(*rows, strict=True))
    _validate_arrays(wave, values, errors)
    return wave, values, errors


def load_pipeline_spectrum(
    path: Path,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    data = np.loadtxt(path, comments="#", ndmin=2)
    if data.shape[1] != 5:
        raise ValueError(f"expected five columns in {path}, found {data.shape[1]}")
    wave, lower, upper, depth, error = data.T
    # The published tables use NaN to mark bins excluded by a reduction.
    valid = np.all(np.isfinite(data), axis=1) & (error > 0) & (lower > 0) & (upper > 0)
    wave, lower, upper, depth, error = (column[valid] for column in (wave, lower, upper, depth, error))
    _validate_arrays(wave, depth, error)
    if np.any(lower <= 0) or np.any(upper <= 0):
        raise ValueError("bin half-widths must be positive")
    return wave, lower, upper, depth, error


def fit_constant(values: np.ndarray, errors: np.ndarray) -> FlatFit:
    if values.size != errors.size or values.size < 2:
        raise ValueError("values and errors must have equal length and at least two bins")
    if np.any(~np.isfinite(values)) or np.any(~np.isfinite(errors)) or np.any(errors <= 0):
        raise ValueError("values must be finite and uncertainties finite and positive")
    weights = 1.0 / errors**2
    mean = float(np.sum(values * weights) / np.sum(weights))
    residuals = (values - mean) / errors
    statistic = float(np.sum(residuals**2))
    dof = int(values.size - 1)
    return FlatFit(
        n_bins=int(values.size),
        weighted_mean_ppm=mean,
        chi2=statistic,
        dof=dof,
        reduced_chi2=statistic / dof,
        p_value=float(chi2_dist.sf(statistic, dof)),
        standardized_residual_rms=float(np.sqrt(np.mean(residuals**2))),
        max_abs_standardized_residual=float(np.max(np.abs(residuals))),
    )


def collect_pipeline_metrics(directory: Path = PIPELINE_DIR) -> list[PipelineVisitMetric]:
    metrics = []
    for path in sorted(directory.glob("JWST_PRISM_*.txt")):
        match = FILE_RE.fullmatch(path.name)
        if match is None:
            raise ValueError(f"unexpected pipeline filename: {path.name}")
        pipeline, visit = match.groups()
        _, _, _, depth, error = load_pipeline_spectrum(path)
        fit = fit_constant(depth, error)
        metrics.append(
            PipelineVisitMetric(
                pipeline=pipeline,
                visit=visit,
                n_bins=fit.n_bins,
                weighted_mean_depth_ppm=fit.weighted_mean_ppm,
                mean_standard_error_ppm=float(1.0 / np.sqrt(np.sum(1.0 / error**2))),
                chi2=fit.chi2,
                dof=fit.dof,
                reduced_chi2=fit.reduced_chi2,
                p_value=fit.p_value,
            )
        )
    if len(metrics) != 24:
        raise ValueError(f"expected 24 pipeline/visit spectra, found {len(metrics)}")
    return metrics


def summarize_visits(metrics: list[PipelineVisitMetric]) -> list[dict[str, float | int | str]]:
    summary = []
    for visit in VISITS:
        group = [metric for metric in metrics if metric.visit == visit]
        if len(group) != 6:
            raise ValueError(f"expected six reductions for visit {visit}, found {len(group)}")
        means = np.array([metric.weighted_mean_depth_ppm for metric in group])
        reduced = np.array([metric.reduced_chi2 for metric in group])
        summary.append(
            {
                "visit": visit,
                "n_pipeline_reductions": len(group),
                "median_weighted_mean_depth_ppm": float(np.median(means)),
                "minimum_weighted_mean_depth_ppm": float(np.min(means)),
                "maximum_weighted_mean_depth_ppm": float(np.max(means)),
                "pipeline_range_ppm": float(np.ptp(means)),
                "median_reduced_chi2": float(np.median(reduced)),
            }
        )
    return summary


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _make_figure(
    wave: np.ndarray,
    dev_ppm: np.ndarray,
    err_ppm: np.ndarray,
    final_fit: FlatFit,
    metrics: list[PipelineVisitMetric],
) -> None:
    pipelines = sorted({metric.pipeline for metric in metrics})
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(pipelines)))
    palette = dict(zip(pipelines, colors, strict=True))
    fig, axes = plt.subplots(3, 1, figsize=(10.2, 12), constrained_layout=True)

    ax = axes[0]
    ax.errorbar(wave, dev_ppm, yerr=err_ppm, fmt="o", ms=3.5, lw=0.8, color="#173f5f", capsize=1.5)
    ax.axhline(final_fit.weighted_mean_ppm, color="#b44b2a", ls="--", lw=1.5)
    ax.axhline(0, color="#657786", ls=":", lw=1)
    ax.set(title="A  Final GP-decontaminated combined spectrum", ylabel="Deviation from continuum [ppm]")
    ax.text(
        0.99, 0.95,
        rf"diagonal $\chi^2$/dof = {final_fit.chi2:.2f}/{final_fit.dof}" + "\n" + rf"$p$ = {final_fit.p_value:.3f}",
        transform=ax.transAxes, ha="right", va="top", fontsize=9,
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "edgecolor": "#bdc7cf"},
    )

    ax = axes[1]
    x = np.arange(len(VISITS))
    for pipeline in pipelines:
        ordered = [next(m for m in metrics if m.pipeline == pipeline and m.visit == visit) for visit in VISITS]
        ax.errorbar(
            x, [m.weighted_mean_depth_ppm for m in ordered],
            yerr=[m.mean_standard_error_ppm for m in ordered], marker="o", ms=4,
            lw=1.2, capsize=2, color=palette[pipeline], label=pipeline,
        )
    ax.set_xticks(x, VISITS)
    ax.set(title="B  Visit-level depth persists across six reductions", ylabel="Weighted mean transit depth [ppm]")
    ax.legend(ncol=3, fontsize=8, frameon=False)

    ax = axes[2]
    matrix = np.array([
        [next(m.reduced_chi2 for m in metrics if m.pipeline == pipeline and m.visit == visit) for visit in VISITS]
        for pipeline in pipelines
    ])
    image = ax.imshow(np.log10(matrix), cmap="magma", aspect="auto", vmin=-0.1, vmax=1.6)
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            color = "white" if matrix[row, column] > 2 else "black"
            ax.text(column, row, f"{matrix[row, column]:.2f}", ha="center", va="center", color=color, fontsize=8)
    ax.set_xticks(x, VISITS)
    ax.set_yticks(np.arange(len(pipelines)), pipelines)
    ax.set(title="C  Constant-depth residual structure by reduction", xlabel="Visit", ylabel="Pipeline/team")
    colorbar = fig.colorbar(image, ax=ax, pad=0.02)
    colorbar.set_label(r"$\log_{10}$(reduced $\chi^2$)")
    fig.suptitle("TRAPPIST-1e NIRSpec/PRISM: final product and reduction sensitivity", fontsize=15)
    fig.savefig(FIG_DIR / "trappist1e_spectral_audit.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    wave, dev_ppm, err_ppm = load_spectrum(DATA_DIR / "trappist1e_decontaminated_spectrum.txt")
    final_fit = fit_constant(dev_ppm, err_ppm)
    metrics = collect_pipeline_metrics()
    visit_summary = summarize_visits(metrics)
    summary_rows = [
        {"quantity": "n_wavelength_points", "value": final_fit.n_bins, "unit": "count"},
        {"quantity": "flat_line_deviation", "value": f"{final_fit.weighted_mean_ppm:.2f}", "unit": "ppm"},
        {"quantity": "flat_line_chi2", "value": f"{final_fit.chi2:.2f}", "unit": "dimensionless"},
        {"quantity": "flat_line_dof", "value": final_fit.dof, "unit": "count"},
        {"quantity": "flat_line_reduced_chi2_this_script", "value": f"{final_fit.reduced_chi2:.3f}", "unit": "dimensionless"},
        {"quantity": "flat_line_p_value", "value": f"{final_fit.p_value:.6f}", "unit": "chi2 survival function"},
        {"quantity": "standardized_residual_rms", "value": f"{final_fit.standardized_residual_rms:.3f}", "unit": "sigma"},
        {"quantity": "max_abs_standardized_residual", "value": f"{final_fit.max_abs_standardized_residual:.3f}", "unit": "sigma"},
        {"quantity": "paper_rejection_significance_h2_rich", "value": f"{PAPER_SIGNIFICANCE}+", "unit": "sigma; full published retrieval"},
    ]
    _write_csv(FIG_DIR / "summary_statistics.csv", summary_rows)
    _write_csv(FIG_DIR / "pipeline_visit_metrics.csv", [asdict(metric) for metric in metrics])
    _write_csv(FIG_DIR / "visit_summary.csv", visit_summary)

    visit_104 = next(row for row in visit_summary if row["visit"] == "104")
    earlier = [row for row in visit_summary if row["visit"] != "104"]
    earlier_median = float(np.median([row["median_weighted_mean_depth_ppm"] for row in earlier]))
    payload = {
        "scope": {
            "independent_visits": 4,
            "reductions_per_visit": 6,
            "pipeline_visit_files": 24,
            "warning": "Six reductions of one visit are correlated analyses, not independent observations.",
        },
        "final_decontaminated_flat_fit": asdict(final_fit),
        "visit_summary": visit_summary,
        "visit_104_median_offset_from_earlier_visit_median_ppm": float(visit_104["median_weighted_mean_depth_ppm"] - earlier_median),
        "inference_boundary": "Descriptive diagonal-error audit only; no atmospheric detection, model selection, or retrieval is performed.",
    }
    (FIG_DIR / "analysis_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    _make_figure(wave, dev_ppm, err_ppm, final_fit, metrics)
    print(f"Final spectrum: chi2/dof={final_fit.chi2:.2f}/{final_fit.dof}, p={final_fit.p_value:.6f}")
    offset = payload["visit_104_median_offset_from_earlier_visit_median_ppm"]
    print(f"Visit 104 median offset from median of visits 001-003: {offset:.1f} ppm")
    print(f"Wrote four machine-readable products and {FIG_DIR / 'trappist1e_spectral_audit.png'}")


if __name__ == "__main__":
    main()
