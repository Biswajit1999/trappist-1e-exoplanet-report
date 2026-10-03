"""Validate the identity and parseability of the committed public data."""

from __future__ import annotations

import hashlib
from pathlib import Path

from analyze_spectrum import DATA_DIR, collect_pipeline_metrics, load_spectrum

FINAL_SHA256 = "d07c0aa4916a714f5cdb6205d653b3bf57159e2cde9e18c1c616c43786ea8835"
PIPELINE_SET_SHA256 = "4d268a522a7ef44f946754f658d68a99ce515c30281ebc5b59d7bbbb01116fdc"


def canonical_bytes(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return text.encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(canonical_bytes(path)).hexdigest()


def pipeline_set_sha256() -> str:
    digest = hashlib.sha256()
    paths = sorted((DATA_DIR / "pipeline_visits").glob("JWST_PRISM_*.txt"))
    for path in paths:
        digest.update(path.name.encode("utf-8") + b"\0")
        digest.update(canonical_bytes(path))
    return digest.hexdigest()


def main() -> None:
    final_path = DATA_DIR / "trappist1e_decontaminated_spectrum.txt"
    actual_final = sha256(final_path)
    actual_set = pipeline_set_sha256()
    if actual_final != FINAL_SHA256:
        raise SystemExit(f"final-spectrum SHA-256 mismatch: {actual_final}")
    if actual_set != PIPELINE_SET_SHA256:
        raise SystemExit(f"pipeline-set SHA-256 mismatch: {actual_set}")
    load_spectrum(final_path)
    metrics = collect_pipeline_metrics()
    print(f"Validated final spectrum and {len(metrics)} pipeline/visit products")


if __name__ == "__main__":
    main()
