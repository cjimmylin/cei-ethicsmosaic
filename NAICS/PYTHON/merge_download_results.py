"""
merge_download_results.py — Phase 2
Consolidate PID-scoped download result files into a single merged report.

Output: logs/20260321-download-results-merged.json
        logs/20260321-download-report.md
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
DOCUMENTS_DIR = BASE_DIR / "DOCUMENTS"


def main():
    # Find all PID-scoped result files
    result_files = sorted(LOGS_DIR.glob("20260321-download-results-*.json"))
    # Exclude the merged file itself
    result_files = [f for f in result_files if "merged" not in f.name]

    if not result_files:
        print("No result files found!")
        sys.exit(1)

    print(f"Found {len(result_files)} result files:")
    for f in result_files:
        print(f"  {f.name}")

    # Merge all results
    all_results: list[dict] = []
    for f in result_files:
        with open(f, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        results = data.get("results", [])
        print(f"  {f.name}: {len(results)} entries, "
              f"{data.get('success', 0)} success, {data.get('failed', 0)} failed")
        all_results.extend(results)

    # Deduplicate by index (in case of retries)
    seen_indices: dict[int, dict] = {}
    for r in all_results:
        idx = r["index"]
        # Prefer success over failure
        if idx in seen_indices:
            if r["status"] == "success" and seen_indices[idx]["status"] != "success":
                seen_indices[idx] = r
        else:
            seen_indices[idx] = r

    deduped = sorted(seen_indices.values(), key=lambda x: x["index"])

    # Compute stats
    total = len(deduped)
    success = sum(1 for r in deduped if r["status"] == "success")
    failed = total - success

    format_counts = {"pdf": 0, "html": 0}
    error_buckets: dict[str, int] = {}
    for r in deduped:
        if r["status"] == "success":
            fmt = r.get("format", "")
            if fmt in format_counts:
                format_counts[fmt] += 1
        else:
            err = r.get("error", "unknown")
            if "blocked" in err:
                bucket = "blocked"
            elif "404" in err or "dead_link" in err:
                bucket = "dead_link"
            elif "timeout" in err:
                bucket = "timeout"
            elif "http_" in err:
                bucket = "http_error"
            elif "url_error" in err or "connection" in err.lower():
                bucket = "connection_error"
            elif "error_page" in err:
                bucket = "error_page"
            else:
                bucket = "other"
            error_buckets[bucket] = error_buckets.get(bucket, 0) + 1

    # Count actual files on disk
    pdf_on_disk = len(list(DOCUMENTS_DIR.glob("*.pdf")))
    html_on_disk = len(list(DOCUMENTS_DIR.glob("*.html")))

    print(f"\n{'='*60}")
    print(f"Total entries:     {total}")
    print(f"Success:           {success} ({100*success/max(total,1):.1f}%)")
    print(f"Failed:            {failed}")
    print(f"Format: PDF={format_counts['pdf']}, HTML={format_counts['html']}")
    print(f"Files on disk: PDF={pdf_on_disk}, HTML={html_on_disk}")
    if error_buckets:
        print(f"Error breakdown:   {error_buckets}")

    # Write merged JSON
    merged = {
        "generated": "2026-03-21",
        "source_files": [f.name for f in result_files],
        "total": total,
        "success": success,
        "failed": failed,
        "success_rate_pct": round(100 * success / max(total, 1), 1),
        "format_counts": format_counts,
        "error_buckets": error_buckets,
        "files_on_disk": {"pdf": pdf_on_disk, "html": html_on_disk},
        "results": deduped,
    }
    merged_path = LOGS_DIR / "20260321-download-results-merged.json"
    with open(merged_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    print(f"\nMerged JSON: {merged_path}")

    # Write markdown report
    report_lines = [
        "# EthicsMosaic Download Report — 2026-03-21\n",
        f"## Summary\n",
        f"- **Total URLs:** {total}",
        f"- **Successful:** {success} ({100*success/max(total,1):.1f}%)",
        f"- **Failed:** {failed}",
        f"- **PDF downloads:** {format_counts['pdf']}",
        f"- **HTML downloads:** {format_counts['html']}",
        f"- **Files on disk:** {pdf_on_disk} PDF + {html_on_disk} HTML\n",
    ]

    if error_buckets:
        report_lines.append("## Error Breakdown\n")
        report_lines.append("| Error Type | Count |")
        report_lines.append("|-----------|-------|")
        for bucket, count in sorted(error_buckets.items(), key=lambda x: -x[1]):
            report_lines.append(f"| {bucket} | {count} |")
        report_lines.append("")

    # List failures for manual follow-up
    failures = [r for r in deduped if r["status"] == "failed"]
    if failures:
        report_lines.append("## Failed Downloads (Manual Follow-up Needed)\n")
        report_lines.append("| # | Organization | Error | URL |")
        report_lines.append("|---|-------------|-------|-----|")
        for r in failures:
            org = r.get("organization", "?")[:40]
            err = r.get("error", "?")[:30]
            url = r.get("url", "")[:60]
            report_lines.append(f"| {r['index']} | {org} | {err} | {url} |")

    report_path = LOGS_DIR / "20260321-download-report.md"
    report_path.write_text("\n".join(report_lines), "utf-8")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
