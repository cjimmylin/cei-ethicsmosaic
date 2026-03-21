"""
merge_all_recovery.py — Phase 5 of council-of-experts recovery
Consolidate all recovery results (wayback + websearch + playwright + webfetch)
with original Wave 1+2 successes into a final picture.

Run as: python merge_all_recovery.py
Output:
  logs/20260321-recovery-report.md
  logs/20260321-still-missing.md
  logs/20260321-download-results-post-recovery.json
"""
from __future__ import annotations

import functools
import glob
import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

print = functools.partial(print, flush=True)

BASE_DIR = Path(__file__).resolve().parent.parent          # EthicsMosaic/NAICS/
DOCUMENTS_DIR = BASE_DIR / "DOCUMENTS"
LOGS_DIR = BASE_DIR / "logs"

ORIGINAL_RESULTS = LOGS_DIR / "20260321-download-results-final.json"
RECOVERY_INPUT = LOGS_DIR / "20260321-recovery-input.json"
MANIFEST = LOGS_DIR / "20260321-download-manifest.json"


def find_result_files(pattern: str) -> list[Path]:
    """Find all result JSON files matching a glob pattern."""
    return sorted(LOGS_DIR.glob(pattern))


def load_all_recovery_results() -> dict[int, dict]:
    """Load and merge all recovery phase results. Later phases override earlier."""
    merged: dict[int, dict] = {}

    # Phase 1: Wayback results
    for f in find_result_files("20260321-wayback-results-*.json"):
        data = json.load(open(f))
        for r in data.get("results", []):
            idx = r["index"]
            if r["status"] == "success":
                merged[idx] = r
            elif idx not in merged:
                merged[idx] = r

    # Phase 2: WebSearch results
    for f in find_result_files("20260321-websearch-results-*.json"):
        data = json.load(open(f))
        for r in data.get("results", []):
            idx = r["index"]
            if r["status"] == "success":
                merged[idx] = r
            elif idx not in merged:
                merged[idx] = r

    # Phase 3: Playwright results
    for f in find_result_files("20260321-playwright-results-*.json"):
        data = json.load(open(f))
        for r in data.get("results", []):
            idx = r["index"]
            if r["status"] == "success":
                merged[idx] = r
            elif idx not in merged:
                merged[idx] = r

    # Phase 4: WebFetch results
    for f in find_result_files("20260321-webfetch-results-*.json"):
        data = json.load(open(f))
        for r in data.get("results", []):
            idx = r["index"]
            if r["status"] == "success":
                merged[idx] = r
            elif idx not in merged:
                merged[idx] = r

    return merged


def verify_on_disk(stem: str) -> tuple[bool, str, int]:
    """Check if a file actually exists in DOCUMENTS/."""
    for ext in (".pdf", ".html"):
        p = DOCUMENTS_DIR / f"{stem}{ext}"
        if p.exists() and p.stat().st_size >= 500:
            return True, ext[1:], p.stat().st_size
    return False, "", 0


def main():
    # Load original results
    with open(ORIGINAL_RESULTS) as f:
        original = json.load(f)

    # Load manifest for metadata
    with open(MANIFEST) as f:
        manifest = json.load(f)
    manifest_by_idx = {e["index"]: e for e in manifest["entries"]}

    # Load recovery input (failure list)
    with open(RECOVERY_INPUT) as f:
        recovery = json.load(f)
    failure_indices = {f["index"] for f in recovery["failures"]}

    # Load all recovery results
    recovery_results = load_all_recovery_results()

    # Build final combined results
    final_results = []
    total_success = 0
    total_failed = 0
    recovery_success = 0
    recovery_failed = 0
    format_counts: Counter[str] = Counter()
    strategy_counts: Counter[str] = Counter()
    still_missing: list[dict] = []

    for entry in original["results"]:
        idx = entry["index"]

        if entry["status"] == "success":
            # Original success — keep as-is but verify on disk
            on_disk, fmt, sz = verify_on_disk(entry["filename_stem"])
            if on_disk:
                total_success += 1
                format_counts[fmt] += 1
                final_results.append(entry)
            else:
                # File missing from disk — mark as failed
                entry["status"] = "failed"
                entry["error"] = "file_missing_from_disk"
                total_failed += 1
                final_results.append(entry)
            continue

        # This was a failure — check recovery results
        # Use manifest stem (full, not truncated) for disk verification
        m_entry = manifest_by_idx.get(idx, {})
        full_stem = m_entry.get("filename_stem", entry["filename_stem"])

        if idx in recovery_results:
            rec = recovery_results[idx]
            if rec["status"] == "success":
                # Verify file actually on disk — try recovery stem, then manifest stem
                rec_stem = rec.get("filename_stem", full_stem)
                on_disk, fmt, sz = verify_on_disk(rec_stem)
                if not on_disk:
                    on_disk, fmt, sz = verify_on_disk(full_stem)
                if not on_disk:
                    on_disk, fmt, sz = verify_on_disk(entry["filename_stem"])
                if on_disk:
                    total_success += 1
                    recovery_success += 1
                    format_counts[fmt] += 1
                    strategy = rec.get("strategy", "unknown")
                    strategy_counts[strategy] += 1
                    final_results.append({
                        **entry,
                        "status": "success",
                        "format": fmt,
                        "local_file": f"{full_stem}.{fmt}",
                        "bytes": sz,
                        "error": None,
                        "recovery_strategy": strategy,
                    })
                    continue

        # Still failed
        total_failed += 1
        recovery_failed += 1
        rec = recovery_results.get(idx, {})
        final_results.append({
            **entry,
            "recovery_attempted": True,
            "recovery_error": rec.get("recovery_error", "no_recovery_result"),
        })
        m = manifest_by_idx.get(idx, {})
        still_missing.append({
            "index": idx,
            "organization": entry.get("organization", ""),
            "document_title": m.get("document_title", ""),
            "url": entry.get("url", ""),
            "original_error": entry.get("error", ""),
            "recovery_error": rec.get("recovery_error", "no_recovery_result"),
        })

    # Also check DOCUMENTS/ for files that might have been downloaded
    # by WebSearch agents outside the JSON tracking
    for fail in recovery["failures"]:
        idx = fail["index"]
        stem = fail["filename_stem"]
        # If still in failed list, check disk one more time
        if any(r["index"] == idx and r.get("status") == "failed"
               for r in final_results):
            on_disk, fmt, sz = verify_on_disk(stem)
            if on_disk:
                # Update the result
                for r in final_results:
                    if r["index"] == idx:
                        r["status"] = "success"
                        r["format"] = fmt
                        r["local_file"] = f"{stem}.{fmt}"
                        r["bytes"] = sz
                        r["error"] = None
                        r["recovery_strategy"] = "disk_discovery"
                        total_success += 1
                        total_failed -= 1
                        recovery_success += 1
                        recovery_failed -= 1
                        strategy_counts["disk_discovery"] += 1
                        # Remove from still_missing
                        still_missing = [m for m in still_missing if m["index"] != idx]
                        break

    total = len(final_results)

    # Count files on disk
    pdf_on_disk = len(list(DOCUMENTS_DIR.glob("*.pdf")))
    html_on_disk = len(list(DOCUMENTS_DIR.glob("*.html")))

    # ---------------------------------------------------------------------------
    # Write post-recovery results JSON
    # ---------------------------------------------------------------------------
    post_recovery_path = LOGS_DIR / "20260321-download-results-post-recovery.json"
    with open(post_recovery_path, "w") as f:
        json.dump({
            "generated": "2026-03-21",
            "description": "Post council-of-experts recovery — combined Wave 1+2 + recovery",
            "total": total,
            "success": total_success,
            "failed": total_failed,
            "success_rate_pct": round(100 * total_success / total, 1) if total else 0,
            "recovery_success": recovery_success,
            "recovery_failed": recovery_failed,
            "format_counts": dict(format_counts),
            "strategy_counts": dict(strategy_counts),
            "files_on_disk": {"pdf": pdf_on_disk, "html": html_on_disk},
            "results": final_results,
        }, f, indent=2)
    print(f"Wrote: {post_recovery_path}")

    # ---------------------------------------------------------------------------
    # Write still-missing report
    # ---------------------------------------------------------------------------
    missing_path = LOGS_DIR / "20260321-still-missing.md"
    with open(missing_path, "w") as f:
        f.write("# Still-Missing Ethics Codes — Post Recovery\n\n")
        f.write(f"**Date:** 2026-03-21\n")
        f.write(f"**Total missing:** {len(still_missing)} / {total}\n\n")
        f.write("| # | Organization | Document | Original Error | Recovery Error |\n")
        f.write("|---|-------------|----------|----------------|----------------|\n")
        for m in still_missing:
            org = m["organization"][:50]
            doc = m["document_title"][:40]
            oerr = (m["original_error"] or "")[:25]
            rerr = (m["recovery_error"] or "")[:25]
            f.write(f"| {m['index']} | {org} | {doc} | {oerr} | {rerr} |\n")
    print(f"Wrote: {missing_path}")

    # ---------------------------------------------------------------------------
    # Write recovery report
    # ---------------------------------------------------------------------------
    report_path = LOGS_DIR / "20260321-recovery-report.md"
    with open(report_path, "w") as f:
        f.write("# Council-of-Experts Recovery Report\n\n")
        f.write(f"**Date:** 2026-03-21\n")
        f.write(f"**Original:** {original['success']}/{original['total']} "
                f"({original['success_rate_pct']}%)\n")
        f.write(f"**Post-recovery:** {total_success}/{total} "
                f"({round(100 * total_success / total, 1) if total else 0}%)\n")
        f.write(f"**Recovered:** {recovery_success} / {len(recovery['failures'])} failures\n")
        f.write(f"**Still missing:** {recovery_failed}\n\n")

        f.write("## Recovery by Strategy\n\n")
        f.write("| Strategy | Count |\n")
        f.write("|----------|-------|\n")
        for strat, count in strategy_counts.most_common():
            f.write(f"| {strat} | {count} |\n")
        f.write(f"| **Total recovered** | **{recovery_success}** |\n\n")

        f.write("## Files on Disk\n\n")
        f.write(f"- PDFs: {pdf_on_disk}\n")
        f.write(f"- HTML: {html_on_disk}\n")
        f.write(f"- Total: {pdf_on_disk + html_on_disk}\n\n")

        f.write("## Error Buckets (Still Missing)\n\n")
        err_buckets: Counter[str] = Counter()
        for m in still_missing:
            err_buckets[m["original_error"][:30]] += 1
        f.write("| Error Type | Count |\n")
        f.write("|-----------|-------|\n")
        for err, count in err_buckets.most_common():
            f.write(f"| {err} | {count} |\n")

    print(f"Wrote: {report_path}")

    # Summary
    print(f"\n{'='*60}")
    print(f"RECOVERY SUMMARY")
    print(f"{'='*60}")
    print(f"Original: {original['success']}/{original['total']} ({original['success_rate_pct']}%)")
    print(f"Recovered: {recovery_success}/{len(recovery['failures'])} failures")
    print(f"Post-recovery: {total_success}/{total} ({round(100*total_success/total,1)}%)")
    print(f"Still missing: {recovery_failed}")
    print(f"Files on disk: {pdf_on_disk} PDF + {html_on_disk} HTML = {pdf_on_disk+html_on_disk}")
    print(f"\nStrategies: {dict(strategy_counts)}")


if __name__ == "__main__":
    main()
