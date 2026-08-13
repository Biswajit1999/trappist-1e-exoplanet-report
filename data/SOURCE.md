# Data source

`trappist1e_decontaminated_spectrum.txt` is the final, stellar-
contamination-corrected transmission spectrum of TRAPPIST-1e from
Espinoza et al. (2025), "JWST-TST DREAMS: NIRSpec/PRISM Transmission
Spectroscopy of the Habitable Zone Planet TRAPPIST-1e," *The
Astrophysical Journal Letters*, 990(2), L52 (arXiv:2509.05414).

Downloaded 2026-08-12 from the paper's data release, Zenodo record
16125662, file `espinoza+2025/figure3/tspectra_decontaminated_corrected_flat_JWST-CLR-R10000.txt`
within `TRAPPIST-1e-GTO-2025-main.zip` (the frozen snapshot of
<https://github.com/nespinoza/TRAPPIST-1e-GTO-2025>).

Three columns, no header in the original file: wavelength (microns),
deviation from a flat continuum (ppm), and its uncertainty (ppm). 67
wavelength points spanning four NIRSpec/PRISM transit visits combined
and corrected for unocculted starspot/faculae contamination.

The "R10000" in the filename is the pipeline's internal wavelength
resampling grid, not the spectrum's actual spectral resolving power.
NIRSpec/PRISM's real resolving power is low and wavelength-dependent,
about R~30-300 across 0.6-5.3 microns (nominally R~100), per STScI's
JWST NIRSpec documentation and consistent with the values quoted in
Espinoza et al. (2025) itself.

The same release also contains the four individual visit spectra as
reduced independently by six different pipelines (Canas, Espinoza,
Grant, Gressier, Long, Stevenson), plus two archival HST/WFC3 spectra
used for a cross-instrument comparison in the paper — not included here
to keep this repository small.

An earlier version of this repository analyzed TRAPPIST-1b instead,
because no TRAPPIST-1e-specific spectrum had been published at the
time it was written. That is no longer the case; this version uses the
planet's own data directly.
