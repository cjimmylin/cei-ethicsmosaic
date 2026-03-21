#!/usr/bin/env python3
"""
download_documents.py
Downloads all ethics codes from the ISIC registry as PDF or HTML.

Strategy per record:
  1. Direct PDF URL → curl download → save as {id}.pdf
  2. HTML page URL → fetch page → scan for PDF link → download PDF if found
  3. No PDF found on page → save raw HTML as {id}.html
  4. HTTP 401/403 or login wall detected → mark "restricted", skip
  5. Timeout or connection error → mark "failed"

Usage (run from EthicsMosaic/ISIC/):
  python PYTHON/download_documents.py 1 60       # records 1-60
  python PYTHON/download_documents.py 1 473      # all records
  python PYTHON/download_documents.py --dry-run  # preview only
  python PYTHON/download_documents.py --retry-failed  # retry failed/timeout

Output:
  DOCUMENTS/{id}.pdf  or  DOCUMENTS/{id}.html
  DOCUMENTS/download-log.json  (one entry per record)
"""
from __future__ import annotations

import functools
import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Force flush for parallel monitoring
print = functools.partial(print, flush=True)

# ── Paths ────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent.parent          # EthicsMosaic/ISIC/
REGISTRY = BASE / "data" / "ethics-codes-registry.json"
DOCS_DIR = BASE / "DOCUMENTS"
LOG_FILE  = DOCS_DIR / "download-log.json"

DOCS_DIR.mkdir(exist_ok=True)

# ── HTTP settings ─────────────────────────────────────────────────────────────
CONNECT_TIMEOUT = 30    # seconds
READ_TIMEOUT    = 60
DELAY_BASE      = 1.5   # seconds between requests
DELAY_JITTER    = 0.5   # ± random jitter
MAX_RETRIES     = 2

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]

# Patterns that indicate a login wall / member-only page
LOGIN_MARKERS = [
    "sign in", "log in", "login required", "members only", "member login",
    "please login", "access denied", "subscription required", "create an account",
    "register to access", "restricted access",
]

# ── Log helpers ───────────────────────────────────────────────────────────────

def load_log() -> dict:
    if LOG_FILE.exists():
        try:
            return json.loads(LOG_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_log(log: dict) -> None:
    # Atomic write via temp file
    tmp = LOG_FILE.with_suffix(f".tmp.{os.getpid()}.json")
    tmp.write_text(json.dumps(log, indent=2, ensure_ascii=False))
    os.replace(tmp, LOG_FILE)


def log_entry(record_id: str, status: str, fmt: str, filename: str,
              size: int, url: str, notes: str = "") -> dict:
    return {
        "status": status,
        "format": fmt,
        "filename": filename,
        "file_size_bytes": size,
        "source_url": url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
    }

# ── Download helpers ──────────────────────────────────────────────────────────

def pick_ua() -> str:
    return random.choice(USER_AGENTS)


def curl_download(url: str, dest: Path, retries: int = MAX_RETRIES) -> bool:
    """Download url to dest using curl. Returns True on success."""
    for attempt in range(retries + 1):
        cmd = [
            "curl", "-L", "--silent", "--show-error",
            "--connect-timeout", str(CONNECT_TIMEOUT),
            "--max-time", str(READ_TIMEOUT),
            "-A", pick_ua(),
            "-o", str(dest),
            url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and dest.exists() and dest.stat().st_size > 500:
            # Verify it's not an HTML error page disguised as PDF
            if str(dest).endswith(".pdf"):
                header = dest.read_bytes()[:5]
                if header != b"%PDF-":
                    dest.unlink()
                    return False
            return True
        if dest.exists():
            dest.unlink()
        if attempt < retries:
            time.sleep(2)
    return False


def fetch_html(url: str) -> Optional[str]:
    """Fetch HTML content of a page using curl, return text or None."""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tf:
        tmp = Path(tf.name)
    try:
        cmd = [
            "curl", "-L", "--silent", "--show-error",
            "--connect-timeout", str(CONNECT_TIMEOUT),
            "--max-time", str(READ_TIMEOUT),
            "-A", pick_ua(),
            "-o", str(tmp),
            url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not tmp.exists():
            return None
        content = tmp.read_text(errors="replace")
        return content if len(content) > 200 else None
    finally:
        if tmp.exists():
            tmp.unlink()


def is_login_wall(html: str) -> bool:
    lower = html.lower()
    return any(marker in lower for marker in LOGIN_MARKERS)


def extract_pdf_links(html: str, base_url: str) -> list[str]:
    """Extract candidate PDF URLs from HTML content."""
    candidates = []
    # Match href="...pdf" or href="...pdf?..."
    pattern = re.compile(
        r'href=["\']([^"\']*\.pdf[^"\']*)["\']',
        re.IGNORECASE
    )
    for m in pattern.finditer(html):
        href = m.group(1).strip()
        if not href:
            continue
        # Resolve relative URLs
        full = urllib.parse.urljoin(base_url, href)
        if full.startswith("http"):
            candidates.append(full)
    # Also look for data-href and src attributes pointing to PDFs
    for attr_pattern in [r'data-href=["\']([^"\']*\.pdf[^"\']*)["\']',
                         r'src=["\']([^"\']*\.pdf[^"\']*)["\']']:
        for m in re.finditer(attr_pattern, html, re.IGNORECASE):
            href = m.group(1).strip()
            full = urllib.parse.urljoin(base_url, href)
            if full.startswith("http"):
                candidates.append(full)
    # Deduplicate preserving order
    seen = set()
    result = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            result.append(c)
    return result

# ── Main download logic ───────────────────────────────────────────────────────

def download_record(record: dict, dry_run: bool, log: dict) -> dict:
    """Process one registry record. Returns updated log entry dict."""
    rid   = record["id"]
    url   = record.get("url", "").strip()
    title = record.get("document_title", "")

    if not url:
        return log_entry(rid, "skipped", "none", "", 0, url, "no URL")

    # Already done?
    if rid in log and log[rid]["status"] in ("success", "restricted"):
        existing_file = DOCS_DIR / log[rid]["filename"] if log[rid]["filename"] else None
        if existing_file and existing_file.exists() and existing_file.stat().st_size > 0:
            print(f"  [SKIP] {rid} — already downloaded")
            return log[rid]

    print(f"  [{rid}] {title[:60]}")

    if dry_run:
        fmt = "pdf" if url.lower().endswith(".pdf") else "html"
        return log_entry(rid, "dry_run", fmt, f"{rid}.{fmt}", 0, url)

    # ── Case 1: Direct PDF URL ────────────────────────────────────────────────
    if url.lower().split("?")[0].endswith(".pdf"):
        dest = DOCS_DIR / f"{rid}.pdf"
        ok = curl_download(url, dest)
        if ok:
            size = dest.stat().st_size
            print(f"    → PDF ({size:,} bytes)")
            return log_entry(rid, "success", "pdf", dest.name, size, url)
        else:
            print(f"    → PDF download failed")
            return log_entry(rid, "failed", "none", "", 0, url, "PDF download failed")

    # ── Case 2: HTML page — fetch and look for PDF ───────────────────────────
    html = fetch_html(url)
    if html is None:
        print(f"    → fetch failed (connection/timeout)")
        return log_entry(rid, "timeout", "none", "", 0, url, "fetch timeout/error")

    # Check for login wall
    if is_login_wall(html):
        print(f"    → login wall detected")
        return log_entry(rid, "restricted", "none", "", 0, url, "login/member-only wall")

    # Look for embedded PDF links
    pdf_links = extract_pdf_links(html, url)
    for pdf_url in pdf_links[:3]:  # Try at most 3 candidates
        dest = DOCS_DIR / f"{rid}.pdf"
        ok = curl_download(pdf_url, dest)
        if ok:
            size = dest.stat().st_size
            print(f"    → PDF via link ({size:,} bytes) — {pdf_url[:80]}")
            return log_entry(rid, "success", "pdf", dest.name, size, pdf_url,
                             f"PDF link extracted from page: {url}")

    # ── Case 3: HTML fallback — save raw HTML ────────────────────────────────
    dest = DOCS_DIR / f"{rid}.html"
    dest.write_text(html, encoding="utf-8")
    size = dest.stat().st_size
    if size < 1000:
        dest.unlink()
        print(f"    → HTML too small ({size} bytes), marking failed")
        return log_entry(rid, "failed", "none", "", 0, url, f"HTML too small: {size}B")
    print(f"    → HTML saved ({size:,} bytes)")
    return log_entry(rid, "success", "html", dest.name, size, url)


def sleep_between() -> None:
    delay = DELAY_BASE + random.uniform(-DELAY_JITTER, DELAY_JITTER)
    time.sleep(max(0.5, delay))

# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    retry_failed = "--retry-failed" in args
    args = [a for a in args if not a.startswith("--")]

    # Load registry
    data = json.loads(REGISTRY.read_text())
    records = data["records"]
    total = len(records)
    print(f"Registry: {total} records")

    # Determine slice
    if retry_failed:
        log = load_log()
        retry_ids = {rid for rid, entry in log.items()
                     if entry["status"] in ("failed", "timeout")}
        subset = [r for r in records if r["id"] in retry_ids]
        print(f"Retrying {len(subset)} failed/timeout records...")
    elif len(args) >= 2:
        start = int(args[0]) - 1   # convert to 0-indexed
        end   = int(args[1])       # exclusive
        subset = records[start:end]
        print(f"Processing records {start+1}–{end} ({len(subset)} records)")
    else:
        subset = records
        print(f"Processing all {len(subset)} records")

    log = load_log()
    counts = {"success_pdf": 0, "success_html": 0, "restricted": 0,
              "failed": 0, "timeout": 0, "skipped": 0, "dry_run": 0}

    for i, record in enumerate(subset, 1):
        rid = record["id"]
        print(f"\n[{i}/{len(subset)}]", end=" ")
        entry = download_record(record, dry_run, log)
        log[rid] = entry
        # Count
        s = entry["status"]
        fmt = entry.get("format", "none")
        if s == "success" and fmt == "pdf":
            counts["success_pdf"] += 1
        elif s == "success" and fmt == "html":
            counts["success_html"] += 1
        elif s in counts:
            counts[s] += 1
        # Save log after each record (safe for parallel use via PID temp)
        save_log(log)
        if i < len(subset):
            sleep_between()

    # Summary
    print(f"\n{'='*60}")
    print(f"DONE — {len(subset)} records processed")
    print(f"  PDF success  : {counts['success_pdf']}")
    print(f"  HTML success : {counts['success_html']}")
    print(f"  Restricted   : {counts['restricted']}")
    print(f"  Failed       : {counts['failed']}")
    print(f"  Timeout      : {counts['timeout']}")
    print(f"  Skipped      : {counts['skipped']}")
    if dry_run:
        print(f"  Dry run      : {counts['dry_run']}")


if __name__ == "__main__":
    main()
