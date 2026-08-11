# Data source

All three CSVs are downloaded, unmodified except for filename, from Zenodo
record **10.5281/zenodo.13385020** ("Products of Combined analysis of the
12.8 and 15 micron JWST/MIRI eclipse observations of TRAPPIST-1 b",
Ducrot et al.):

- `trappist1b_miri_12um8_phasecurve.csv` ← `Fig1a_binned_data.csv`
  (orbital-phase-folded, binned relative flux at 12.8 micron)
- `trappist1b_miri_15um_phasecurve.csv` ← `Fig1b_binned_data.csv`
  (same, at 15 micron)
- `trappist1b_eclipse_depths.csv` ← `Fig2_observations.csv`
  (measured secondary-eclipse depths and uncertainties at both wavelengths)

Retrieved: 2026-08-11, via `https://zenodo.org/api/records/13385020`.

Note: this data is for **TRAPPIST-1 b**, not TRAPPIST-1 e. It is included
here as real system context, because TRAPPIST-1 e has no public JWST (or
other) atmospheric spectrum as of this report -- see `index.html` for the
explanation of why this substitution is made explicit rather than hidden.
