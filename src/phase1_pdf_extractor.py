"""
PREDIX — Phase 1: PDF Text Extraction Pipeline
===============================================
Batch-discovers all PDFs under data/raw/, extracts text page-by-page using
PyMuPDF, preserves page boundaries via sentinel markers, and writes one
plain-text file per PDF to data/processed/text/.

Deliberately excludes table extraction (reserved for Phase 2).
"""

import pymupdf           # PyMuPDF ≥ 1.25 canonical import
import pathlib
import logging
import json
import time
import sys
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR    = pathlib.Path(__file__).resolve().parent.parent      # repo root
RAW_DIR     = BASE_DIR / "data" / "raw"
OUTPUT_DIR  = BASE_DIR / "data" / "processed" / "text"
LOG_DIR     = BASE_DIR / "data" / "processed" / "logs"

# Page boundary sentinel — unique enough not to appear in real report text.
PAGE_BOUNDARY_TEMPLATE = "\n\n<<<PAGE_BREAK page={page_num} total={total_pages}>>>\n\n"

# Text extraction flags passed to page.get_text():
#   "text" mode returns text in reading order, stripping layout artifacts.
EXTRACTION_FLAGS = pymupdf.TEXT_PRESERVE_WHITESPACE

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def setup_logging(log_dir: pathlib.Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file  = log_dir / f"phase1_extraction_{timestamp}.log"

    logger = logging.getLogger("phase1")
    logger.setLevel(logging.DEBUG)

    # File handler — full DEBUG output
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    # Console handler — INFO and above
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info("Log file: %s", log_file)
    return logger


# ---------------------------------------------------------------------------
# PDF discovery
# ---------------------------------------------------------------------------

def discover_pdfs(raw_dir: pathlib.Path) -> list[pathlib.Path]:
    """
    Recursively walks raw_dir and returns all *.pdf paths sorted by
    (subdirectory, filename).  Case-insensitive glob ensures .PDF is caught too.
    """
    pdfs = sorted(
        raw_dir.rglob("*.pdf"),
        key=lambda p: (p.parent.name, p.name)
    )
    # Also catch upper-case extensions on case-sensitive file systems
    pdfs_upper = sorted(
        raw_dir.rglob("*.PDF"),
        key=lambda p: (p.parent.name, p.name)
    )
    seen = set(pdfs)
    for p in pdfs_upper:
        if p not in seen:
            pdfs.append(p)
    return pdfs


# ---------------------------------------------------------------------------
# Output filename derivation
# ---------------------------------------------------------------------------

def derive_output_path(pdf_path: pathlib.Path, raw_dir: pathlib.Path, out_dir: pathlib.Path) -> pathlib.Path:
    """
    Mirrors the subdirectory structure of raw/ inside processed/text/.

    Example:
        raw/monthly/FlashReport_April2026.pdf
        → processed/text/monthly/FlashReport_April2026.txt
    """
    relative   = pdf_path.relative_to(raw_dir)          # e.g. monthly/FlashReport_April2026.pdf
    out_path   = out_dir / relative.with_suffix(".txt")  # swap .pdf → .txt
    out_path.parent.mkdir(parents=True, exist_ok=True)
    return out_path


# ---------------------------------------------------------------------------
# Single-PDF extraction
# ---------------------------------------------------------------------------

def extract_pdf(pdf_path: pathlib.Path, out_path: pathlib.Path, logger: logging.Logger) -> dict:
    """
    Opens one PDF with PyMuPDF, iterates every page, extracts text using
    page.get_text("text"), inserts page-boundary sentinels, and writes the
    full concatenated result to out_path.

    Returns a result dict for the summary log.
    """
    result = {
        "pdf":           str(pdf_path.relative_to(BASE_DIR)),
        "output":        str(out_path.relative_to(BASE_DIR)),
        "status":        None,
        "pages":         0,
        "total_chars":   0,
        "empty_pages":   [],
        "error":         None,
        "duration_sec":  0.0,
    }

    t0 = time.perf_counter()
    try:
        doc = pymupdf.open(str(pdf_path))
    except Exception as exc:
        result["status"] = "FAILED_OPEN"
        result["error"]  = str(exc)
        logger.error("  [FAIL] Cannot open %s - %s", pdf_path.name, exc)
        return result

    total_pages  = len(doc)
    result["pages"] = total_pages
    logger.debug("  Opened %s  (%d pages)", pdf_path.name, total_pages)

    chunks: list[str] = []

    for page_index in range(total_pages):
        page_num = page_index + 1   # 1-based for human readability
        try:
            page = doc[page_index]
            raw_text = page.get_text("text", flags=EXTRACTION_FLAGS)
        except Exception as exc:
            # Log page-level failure but continue processing remaining pages
            logger.warning("    Page %d/%d failed: %s", page_num, total_pages, exc)
            raw_text = f"[PAGE {page_num} EXTRACTION ERROR: {exc}]"

        # Strip trailing whitespace from each page; keep internal structure
        page_text = raw_text.rstrip()

        if not page_text:
            result["empty_pages"].append(page_num)
            logger.debug("    Page %d/%d — empty (likely image-only or blank)", page_num, total_pages)

        # Always insert boundary sentinel so downstream consumers can split
        chunks.append(
            PAGE_BOUNDARY_TEMPLATE.format(page_num=page_num, total_pages=total_pages)
        )
        chunks.append(page_text)

    doc.close()

    full_text = "".join(chunks)
    result["total_chars"] = len(full_text)

    try:
        out_path.write_text(full_text, encoding="utf-8")
    except Exception as exc:
        result["status"] = "FAILED_WRITE"
        result["error"]  = str(exc)
        logger.error("  [FAIL] Cannot write %s - %s", out_path, exc)
        return result

    result["status"] = "OK"
    result["duration_sec"] = round(time.perf_counter() - t0, 2)
    logger.info(
        "  [OK] %s -> %d pages, %d chars, %d empty pages  (%.2fs)",
        pdf_path.name,
        total_pages,
        result["total_chars"],
        len(result["empty_pages"]),
        result["duration_sec"],
    )
    return result


# ---------------------------------------------------------------------------
# Batch runner
# ---------------------------------------------------------------------------

def run_batch(raw_dir: pathlib.Path, out_dir: pathlib.Path, logger: logging.Logger) -> list[dict]:
    pdfs = discover_pdfs(raw_dir)
    if not pdfs:
        logger.warning("No PDFs found under %s", raw_dir)
        return []

    logger.info("Discovered %d PDF(s) under %s", len(pdfs), raw_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for i, pdf_path in enumerate(pdfs, start=1):
        logger.info("[%d/%d] Processing: %s", i, len(pdfs), pdf_path.relative_to(raw_dir))
        out_path = derive_output_path(pdf_path, raw_dir, out_dir)
        res = extract_pdf(pdf_path, out_path, logger)
        results.append(res)
        # Intentionally continues even if res["status"] != "OK"

    return results


# ---------------------------------------------------------------------------
# Summary report
# ---------------------------------------------------------------------------

def write_summary(results: list[dict], log_dir: pathlib.Path, logger: logging.Logger) -> None:
    succeeded   = [r for r in results if r["status"] == "OK"]
    failed      = [r for r in results if r["status"] != "OK"]
    total_pages = sum(r["pages"] for r in succeeded)
    total_chars = sum(r["total_chars"] for r in succeeded)
    all_empty   = []
    for r in succeeded:
        all_empty.extend(r["empty_pages"])

    summary = {
        "run_timestamp":    datetime.now(timezone.utc).isoformat(),
        "pdfs_discovered":  len(results),
        "succeeded":        len(succeeded),
        "failed":           len(failed),
        "total_pages":      total_pages,
        "total_chars":      total_chars,
        "total_empty_pages": len(all_empty),
        "results":          results,
    }

    summary_path = log_dir / "phase1_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    logger.info("=" * 60)
    logger.info("PHASE 1 SUMMARY")
    logger.info("  PDFs discovered : %d", len(results))
    logger.info("  Succeeded       : %d", len(succeeded))
    logger.info("  Failed          : %d", len(failed))
    logger.info("  Total pages     : %d", total_pages)
    logger.info("  Total chars     : %d", total_chars)
    logger.info("  Empty pages     : %d", len(all_empty))
    if failed:
        logger.warning("  Failed PDFs:")
        for r in failed:
            logger.warning("    • %s  [%s] %s", r["pdf"], r["status"], r["error"])
    logger.info("  Summary JSON    : %s", summary_path)
    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger  = setup_logging(LOG_DIR)
    logger.info("PREDIX Phase 1 — PDF Text Extraction Pipeline")
    logger.info("PyMuPDF version : %s", pymupdf.__version__ if hasattr(pymupdf, '__version__') else 'unknown')
    logger.info("Raw dir         : %s", RAW_DIR)
    logger.info("Output dir      : %s", OUTPUT_DIR)

    results = run_batch(RAW_DIR, OUTPUT_DIR, logger)
    write_summary(results, LOG_DIR, logger)
