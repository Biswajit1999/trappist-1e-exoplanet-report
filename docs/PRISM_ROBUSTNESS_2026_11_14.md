# PRISM binned-spectrum robustness (14 November 2026)

Two independent, conditional numerical diagnostics accompany the existing TRAPPIST-1 e report without changing its published measurements:

1. **AR(1) covariance flatness:** use a hypothesised wavelength-bin correlation coefficient and the supplied per-bin errors to fit a common depth by Cholesky-whitened GLS. This tests sensitivity of the formal constant-depth uncertainty and chi-square to an assumed covariance, **not** a measured JWST covariance. The AR(1) model assumes ordered, equally spaced *bin indices*, not physical wavelength separation.
2. **Exact leave-one-bin-out influence:** recompute the inverse-variance weighted constant after deleting each bin. This tests leverage and is **not** an independent-visit jackknife or a detection-significance calculation.

The functions are import-only and do not alter archived spectra, figures, provenance or the browser. Run `python -m unittest discover -s tests -p 'test_prism_robustness.py'` from the repository root. No numerical observational result is claimed until these functions are explicitly applied to verified release tables with their error definitions. A covariance inferred from multiple pipelines on the same four visits would not be independent.

Scientific implementation and tests were prepared with AI assistance for review; the repository owner remains the requested Git commit author. No new observations, retrieved atmosphere, or molecule detection are asserted.
