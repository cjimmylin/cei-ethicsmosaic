"""
retry_download_codes.py — Wave 2 mop-up
Retry failed downloads from the merged results.
Mode 'timeout' = retry timeout/5xx/connection failures with longer timeout.
Mode 'all-retryable' = retry all non-permanent failures.

Usage: python retry_download_codes.py [timeout|all-retryable]
Output: logs/20260321-download-retry-results-{PID}.json
"""
from __future__ import annotations

import functools
import json
import os
import sys
import time
from pathlib import Path

# Reuse download logic from batch script
sys.path.insert(0, str(Path(__file__).resolve().parent))
from batch_download_codes import (
    process_entry, DOCUMENTS_DIR, RECYCLE_BIN, LOGS_DIR, MIN_FILE_SIZE,
)

print = functools.partial(print, flush=True)

MERGED_JSON = LOGS_DIR / "20260321-download-results-merged.json"
MANIFEST_JSON = LOGS_DIR / "20260321-download-manifest.json"


def is_retryable_timeout(error: str) -> bool:
    """Timeout, 5xx, connection reset, too_small — worth retrying with longer timeout."""
    indicators = ["timeout", "http_5", "timed out", "curl_error_56",
                  "too_small", "reset", "empty_response"]
    return any(x in error for x in indicators)


def is_retryable_blocked(error: str) -> bool:
    """HTTP 403 at runtime (not preclassified) — worth trying again."""
    return "blocked_http_403" in error or "blocked_http_429" in error


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all-retryable"

    with open(MERGED_JSON, "r", encoding="utf-8") as f:
        merged = json.load(f)

    with open(MANIFEST_JSON, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Build index→manifest entry lookup
    entry_by_index = {e["index"]: e for e in manifest["entries"]}

    # Find retryable failures
    failures = [r for r in merged["results"] if r["status"] == "failed"]
    retry_list = []
    for r in failures:
        err = r.get("error", "")
        if mode == "timeout":
            if is_retryable_timeout(err):
                retry_list.append(r)
        elif mode == "all-retryable":
            if is_retryable_timeout(err) or is_retryable_blocked(err):
                retry_list.append(r)

    print(f"Mode: {mode}")
    print(f"Total failures: {len(failures)}")
    print(f"Retrying: {len(retry_list)}")

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    RECYCLE_BIN.mkdir(parents=True, exist_ok=True)

    results = []
    success_count = 0
    for i, fail in enumerate(retry_list, 1):
        idx = fail["index"]
        entry = entry_by_index.get(idx)
        if not entry:
            print(f"  [{i:3d}/{len(retry_list)}] #{idx} — missing from manifest, skip")
            continue

        # For blocked entries, reclassify as html_page for retry
        if entry["category"] == "blocked":
            entry = dict(entry)
            entry["category"] = "html_page"

        print(f"  [{i:3d}/{len(retry_list)}] #{idx} ({entry['category']}) "
              f"{entry['organization'][:35]} — {fail['error'][:30]}")

        result = process_entry(entry)
        status_label = "OK" if result["status"] == "success" else f"FAIL:{result['error']}"
        fmt = result.get("format") or "-"
        print(f"           → {status_label} [{fmt}]")
        results.append(result)

        if result["status"] == "success":
            success_count += 1

        time.sleep(2.0)  # Longer delay for retry

    # Write results
    pid = os.getpid()
    out_path = LOGS_DIR / f"20260321-download-retry-results-{pid}.json"
    tmp_path = LOGS_DIR / f".tmp.{pid}.json"
    output = {
        "mode": mode,
        "total_retried": len(retry_list),
        "success": success_count,
        "failed": len(retry_list) - success_count,
        "results": results,
    }
    tmp_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), "utf-8")
    os.replace(str(tmp_path), str(out_path))

    print(f"\n{'='*60}")
    print(f"Retry complete: {success_count}/{len(retry_list)} additional successes")
    print(f"Output: {out_path}")


if __name__ == "__main__":
    main()
