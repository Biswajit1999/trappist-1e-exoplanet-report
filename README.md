# TRAPPIST-1 e — Exoplanet Atmosphere Report

One of the most Earth-like planets known by size and insolation, and
one of JWST's highest-priority habitable-zone targets. This repo tests
its own decontaminated JWST NIRSpec/PRISM transmission spectrum for
flatness and reports the result next to the atmosphere constraints
Espinoza et al. (2025) actually publish.

**[Open the full report](index.html)** (open locally in a browser, or serve
with `python -m http.server` from this directory).

## Data sources

- **System parameters** — from the NASA Exoplanet Archive TAP
  service (`pscomppars`).
- **Transmission spectrum** — the decontaminated, stellar-contamination-
  corrected combination of four NIRSpec/PRISM transits from Espinoza et
  al. (2025), *JWST-TST DREAMS: NIRSpec/PRISM Transmission Spectroscopy
  of the Habitable Zone Planet TRAPPIST-1e*, ApJL 990, L52
  (arXiv:2509.05414). See [data/SOURCE.md](data/SOURCE.md) for the
  exact file and Zenodo record.
- **Analysis** — `scripts/analyze_spectrum.py` fits an inverse-
  variance-weighted flat line to the spectrum and reports the reduced
  chi-squared next to the paper's own atmosphere-rejection
  significance. Run it yourself:

  ```bash
  pip install -r requirements.txt
  python scripts/analyze_spectrum.py
  ```

## Repository structure

```text
index.html              the report webpage
data/                    decontaminated NIRSpec/PRISM spectrum (Espinoza et al. 2025)
scripts/analyze_spectrum.py   flat-line analysis, this script vs. the paper
figures/                 generated plot + summary_statistics.csv
```

## What the numbers show

A chi-squared of 42.85 over 66 degrees of freedom (reduced χ² = 0.65,
p = 0.988) across 67 wavelength points is consistent with a flat,
featureless spectrum, matching the paper's own description. Flatness
alone doesn't rule out an atmosphere — a high-altitude cloud deck or a
compact, high-mean-molecular-weight atmosphere can look flat too.
Espinoza et al. (2025) push further with their own retrieval framework
and report ruling out cloud-free, hydrogen-dominated atmospheres (at
least 80% H2 by volume) at better than 3σ, while denser secondary
atmospheres remain possible — addressed further in the companion paper
by Glidden et al. (2025).

## Limitations

This repo's chi-squared treats each wavelength point's quoted error as
independent (a diagonal-covariance likelihood). The paper's stellar-
contamination correction was derived with a Gaussian-process
marginalization over correlated systematics, which a diagonal
chi-squared on the output spectrum doesn't reproduce — so this is a
first-pass flatness check, not the retrieval the paper runs to reach
its own quantitative atmosphere limits, and shouldn't be read as
reproducing that result. Separately: NIRSpec/PRISM's actual resolving
power is R~30-300 (wavelength-dependent, nominally R~100) — the
"R10000" appearing in the source data filename labels the pipeline's
internal wavelength resampling grid, not the spectrum's real spectral
resolution. An earlier version of this repository analyzed TRAPPIST-1b
instead of e, because no TRAPPIST-1e-specific spectrum had been
published when it was written; that's no longer the case, and this
version uses the planet's own data.

## References

1. Gillon, M. et al., 2017. Seven temperate terrestrial planets around
   the nearby ultracool dwarf star TRAPPIST-1. *Nature*, 542,
   pp.456-460.
2. Espinoza, N. et al., 2025. JWST-TST DREAMS: NIRSpec/PRISM
   Transmission Spectroscopy of the Habitable Zone Planet TRAPPIST-1 e.
   *The Astrophysical Journal Letters*, 990(2), L52 (arXiv:2509.05414).
3. Glidden, A. et al., 2025. JWST-TST DREAMS: Secondary Atmosphere
   Constraints for the Habitable Zone Planet TRAPPIST-1 e. *The
   Astrophysical Journal Letters*, 990(2), L53.
4. Agol, E. et al., 2021. Refining the Transit-timing and Photometric
   Analysis of TRAPPIST-1: Masses, Radii, Densities, Dynamics, and
   Ephemerides. *The Planetary Science Journal*, 2, 1.
5. NASA Exoplanet Archive, <https://exoplanetarchive.ipac.caltech.edu/>.

## Author

Biswajit Jana — [Portfolio](https://biswajit1999.github.io/Biswajit_Jana.github.io/) · [GitHub](https://github.com/Biswajit1999) · [LinkedIn](https://www.linkedin.com/in/biswajit-jana-27011a151/) · [ORCID](https://orcid.org/0009-0002-2411-1891)
