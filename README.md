# TRAPPIST-1 e — Exoplanet System Report

One of the most Earth-like planets known, in the habitable zone of an
ultracool dwarf 12.4 parsecs away — and honestly reported: TRAPPIST-1 e has
no published atmospheric spectrum of its own yet. This repo uses real JWST
MIRI eclipse data for its siblings b and c to derive their dayside
temperatures with real physics, setting the real observational context for
e rather than fabricating a spectrum that doesn't exist.

**[Open the full report](index.html)** (open locally in a browser, or serve
with `python -m http.server` from this directory).

## What's real here

- **System parameters** — TRAPPIST-1 e and b, queried live from the NASA
  Exoplanet Archive TAP service (`pscomppars` table).
- **JWST MIRI eclipse photometry** — real reduced secondary-eclipse depths
  and phase-curve data for TRAPPIST-1 b at 12.8 and 15 microns, from Ducrot
  et al., released publicly on Zenodo
  ([10.5281/zenodo.13385020](https://doi.org/10.5281/zenodo.13385020)).
- **Analysis** — `scripts/analyze_spectrum.py` inverts each real eclipse
  depth into a dayside brightness temperature via the Planck function
  (root-finding, not a lookup table), and compares it to the two
  theoretical bare-rock heat-redistribution limits. Run it yourself:

  ```bash
  pip install -r requirements.txt
  python scripts/analyze_spectrum.py
  ```

## Repository structure

```text
index.html              the report webpage
data/                    real JWST MIRI eclipse/phase-curve CSVs (Zenodo)
scripts/analyze_spectrum.py   real Planck-inversion analysis
figures/                 generated plot + summary_statistics.csv
```

## Key finding this repo shows directly

Real derived dayside brightness temperatures for TRAPPIST-1 b: 493 ± 37 K
(12.6 um) and 579 ± 32 K (14.8 um), both at or above the 508 K "zero
redistribution, bare rock" limit and well above the 398 K "full
redistribution" limit — directly reproducing, from real data and real
physics, the published conclusion that TRAPPIST-1 b has no thick,
heat-redistributing atmosphere.

## Why this matters for planet e

TRAPPIST-1 b and c orbit much closer to their star than e, so a bare-rock
result for them does not automatically extend to e. But it establishes a
real, load-bearing fact: this host star's activity and the inner planets'
atmospheric histories make "has TRAPPIST-1 e kept an atmosphere at all" a
genuinely open, first-order question — which is exactly why it remains a
top-priority JWST target rather than a settled case.

## References

1. Gillon, M. et al., 2017. Seven temperate terrestrial planets around the
   nearby ultracool dwarf star TRAPPIST-1. *Nature*, 542, pp.456-460.
2. Ducrot, E. et al. Combined analysis of the 12.8 and 15 micron JWST/MIRI
   eclipse observations of TRAPPIST-1 b. Zenodo record
   [10.5281/zenodo.13385020](https://doi.org/10.5281/zenodo.13385020).
3. Greene, T.P. et al., 2023. Thermal emission from the Earth-sized
   exoplanet TRAPPIST-1 b. *Nature*, 618, pp.39-42.
4. Agol, E. et al., 2021. Refining the Transit-timing and Photometric
   Analysis of TRAPPIST-1. *The Planetary Science Journal*, 2, 1.
5. NASA Exoplanet Archive, <https://exoplanetarchive.ipac.caltech.edu/>.

## Author

Biswajit Jana — [Portfolio](https://biswajit1999.github.io/Biswajit_Jana.github.io/) · [GitHub](https://github.com/Biswajit1999) · [LinkedIn](https://www.linkedin.com/in/biswajit-jana-27011a151/) · [ORCID](https://orcid.org/0009-0002-2411-1891)
