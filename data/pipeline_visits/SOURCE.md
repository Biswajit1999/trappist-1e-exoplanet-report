# Six-pipeline, four-visit spectra

These 24 text files are copied without numerical modification from
`espinoza+2025/appendix-figure1/spectra/` in the frozen Zenodo v1 archive
[10.5281/zenodo.16125662](https://doi.org/10.5281/zenodo.16125662), file
`TRAPPIST-1e-GTO-2025-main (2).zip` (Zenodo MD5
`940629687ff8a25fa10046491340d60f`). They were retrieved on 3 October 2026.

The filename encodes one of six reduction teams/pipelines—Cañas, Espinoza,
Grant, Gressier, Long, or Stevenson—and one of four visits (`001`, `002`,
`003`, `104`). Each table contains wavelength, lower and upper half-bin width,
transit depth, and reported uncertainty. Commented or numeric `nan` rows remain
as published and must be excluded explicitly by analysis code.

These are not 24 independent observations: the six pipelines reprocess the
same four visits. They are included to separate visit-to-visit stellar/
instrument variability from reduction-pipeline sensitivity before assessing
the final GP-decontaminated combined spectrum.

For a deterministic set digest, files are sorted by name and SHA-256 is fed
each UTF-8 filename, a null byte, and its LF-normalized contents. The resulting
digest is `4d268a522a7ef44f946754f658d68a99ce515c30281ebc5b59d7bbbb01116fdc`.
