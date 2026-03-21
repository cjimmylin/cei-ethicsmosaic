"""
batch_download_codes.py — Phase 1
Download ethics codes for a range of manifest entries.
Run as 8 parallel agents: python batch_download_codes.py START END

START/END are 1-indexed over the manifest list.
Output: logs/20260321-download-results-{PID}.json
"""
from __future__ import annotations

import functools
import html.parser
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional, Tuple

print = functools.partial(print, flush=True)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent          # EthicsMosaic/NAICS/
DOCUMENTS_DIR = BASE_DIR / "DOCUMENTS"
RECYCLE_BIN = BASE_DIR / "RECYCLE-BIN"
LOGS_DIR = BASE_DIR / "logs"

MANIFEST_JSON = LOGS_DIR / "20260321-download-manifest.json"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

# Minimum file size to consider valid (bytes)
MIN_FILE_SIZE = 500

# Delay between requests (seconds) to be polite
REQUEST_DELAY = 1.5


# ---------------------------------------------------------------------------
# HTML parser for PDF link detection
# ---------------------------------------------------------------------------

class PDFLinkExtractor(html.parser.HTMLParser):
    """Extract PDF hrefs from an HTML page."""

    def __init__(self):
        super().__init__()
        self.pdf_links: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrs_dict = dict(attrs)
        href = attrs_dict.get("href", "")
        if not href:
            return
        href_lower = href.lower()
        if href_lower.endswith(".pdf") or ("/download" in href_lower and "pdf" in href_lower):
            self.pdf_links.append(href)


def scrape_for_embedded_pdf(html_content: str, base_url: str) -> Optional[str]:
    """Parse HTML and return first embedded PDF link as absolute URL."""
    parser = PDFLinkExtractor()
    try:
        parser.feed(html_content)
    except Exception:
        pass
    if not parser.pdf_links:
        return None
    href = parser.pdf_links[0]
    return urllib.parse.urljoin(base_url, href)


# ---------------------------------------------------------------------------
# Download strategies
# ---------------------------------------------------------------------------

def download_pdf(url: str, dest_path: Path, timeout: int = 30) -> Tuple[bool, str]:
    """
    Download PDF via curl. Validates %PDF- magic bytes.
    Returns (success, error_msg).
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            ["curl", "-L", "-A", UA, "--max-time", str(timeout), "--silent",
             "--fail", "-o", str(dest_path), url],
            capture_output=True, timeout=timeout + 30
        )
        if result.returncode != 0:
            return False, f"curl_error_{result.returncode}"
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)[:80]

    # Validate PDF
    if not dest_path.exists() or dest_path.stat().st_size < MIN_FILE_SIZE:
        if dest_path.exists():
            recycle = RECYCLE_BIN / dest_path.name
            try:
                dest_path.rename(recycle)
            except Exception:
                pass
        return False, "too_small"

    with open(dest_path, "rb") as f:
        header = f.read(5)
    if header[:4] != b"%PDF":
        recycle = RECYCLE_BIN / dest_path.name
        try:
            dest_path.rename(recycle)
        except Exception:
            pass
        return False, "not_a_pdf"

    return True, ""


def download_html(url: str, dest_path: Path, timeout: int = 30) -> Tuple[bool, str, str]:
    """
    Download HTML page via urllib.
    Returns (success, error_msg, html_content).
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com/",
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            try:
                content = raw.decode("utf-8")
            except UnicodeDecodeError:
                content = raw.decode("latin-1", errors="replace")
    except urllib.error.HTTPError as e:
        return False, f"http_{e.code}", ""
    except urllib.error.URLError as e:
        return False, f"url_error_{str(e.reason)[:40]}", ""
    except Exception as e:
        return False, str(e)[:60], ""

    if not content.strip():
        return False, "empty_response", ""

    # Check for common error pages in 200 responses
    content_lower = content[:2000].lower()
    error_markers = ["403 forbidden", "access denied", "page not found",
                     "404 not found", "error 404", "error 403"]
    is_error_page = any(marker in content_lower for marker in error_markers)
    if is_error_page and len(content) < 3000:
        # Small error pages are useless — don't save
        return False, "error_page_in_200", ""

    if len(content) < MIN_FILE_SIZE:
        return False, "too_small", ""

    dest_path.write_text(content, "utf-8")
    return True, "", content


# ---------------------------------------------------------------------------
# Main download dispatcher
# ---------------------------------------------------------------------------

def process_entry(entry: dict) -> dict:
    """Download one ethics code document. Returns result dict."""
    url = entry["url"]
    stem = entry["filename_stem"]
    category = entry["category"]

    result = {
        "index": entry["index"],
        "url": url,
        "organization": entry["organization"],
        "filename_stem": stem,
        "status": "failed",
        "format": None,
        "local_file": None,
        "bytes": 0,
        "error": None,
        "category": category,
    }

    if category == "blocked":
        result["error"] = "blocked_preclassified"
        return result

    if category == "direct_pdf":
        dest = DOCUMENTS_DIR / f"{stem}.pdf"
        # Skip if already downloaded
        if dest.exists() and dest.stat().st_size >= MIN_FILE_SIZE:
            result.update({
                "status": "success",
                "format": "pdf",
                "local_file": dest.name,
                "bytes": dest.stat().st_size,
                "error": "already_exists",
            })
            return result

        success, err = download_pdf(url, dest)
        if success:
            result.update({
                "status": "success",
                "format": "pdf",
                "local_file": dest.name,
                "bytes": dest.stat().st_size,
            })
        else:
            # Fallback: try as HTML page (some .pdf URLs redirect to gateways)
            html_dest = DOCUMENTS_DIR / f"{stem}.html"
            html_ok, html_err, html_content = download_html(url, html_dest)
            if html_ok:
                # Check for embedded PDF link
                pdf_link = scrape_for_embedded_pdf(html_content, url)
                if pdf_link:
                    pdf_dest = DOCUMENTS_DIR / f"{stem}.pdf"
                    pdf_ok, pdf_err = download_pdf(pdf_link, pdf_dest)
                    if pdf_ok:
                        # Move HTML to recycle
                        recycle = RECYCLE_BIN / html_dest.name
                        try:
                            html_dest.rename(recycle)
                        except Exception:
                            pass
                        result.update({
                            "status": "success",
                            "format": "pdf",
                            "local_file": pdf_dest.name,
                            "bytes": pdf_dest.stat().st_size,
                        })
                        return result
                result.update({
                    "status": "success",
                    "format": "html",
                    "local_file": html_dest.name,
                    "bytes": html_dest.stat().st_size,
                })
            else:
                result["error"] = f"pdf_failed:{err} html_fallback:{html_err}"

    elif category == "html_page":
        html_dest = DOCUMENTS_DIR / f"{stem}.html"
        # Skip if already downloaded
        if html_dest.exists() and html_dest.stat().st_size >= MIN_FILE_SIZE:
            result.update({
                "status": "success",
                "format": "html",
                "local_file": html_dest.name,
                "bytes": html_dest.stat().st_size,
                "error": "already_exists",
            })
            return result
        # Also check if PDF already exists
        pdf_check = DOCUMENTS_DIR / f"{stem}.pdf"
        if pdf_check.exists() and pdf_check.stat().st_size >= MIN_FILE_SIZE:
            result.update({
                "status": "success",
                "format": "pdf",
                "local_file": pdf_check.name,
                "bytes": pdf_check.stat().st_size,
                "error": "already_exists",
            })
            return result

        success, err, html_content = download_html(url, html_dest)
        if success:
            # Try to find embedded PDF link
            pdf_link = scrape_for_embedded_pdf(html_content, url)
            if pdf_link:
                pdf_dest = DOCUMENTS_DIR / f"{stem}.pdf"
                pdf_ok, pdf_err = download_pdf(pdf_link, pdf_dest)
                if pdf_ok:
                    # Move HTML to recycle
                    recycle = RECYCLE_BIN / html_dest.name
                    try:
                        html_dest.rename(recycle)
                    except Exception:
                        pass
                    result.update({
                        "status": "success",
                        "format": "pdf",
                        "local_file": pdf_dest.name,
                        "bytes": pdf_dest.stat().st_size,
                    })
                    return result
            # Keep HTML
            result.update({
                "status": "success",
                "format": "html",
                "local_file": html_dest.name,
                "bytes": html_dest.stat().st_size,
            })
        else:
            if err.startswith("http_403") or err.startswith("http_429"):
                result["error"] = f"blocked_{err}"
            elif err.startswith("http_404"):
                result["error"] = "dead_link_404"
            else:
                result["error"] = err

    else:
        result["error"] = f"unknown_category:{category}"

    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print("Usage: python batch_download_codes.py START END")
        sys.exit(1)

    start = int(sys.argv[1])
    end = int(sys.argv[2])

    if not MANIFEST_JSON.exists():
        print(f"ERROR: {MANIFEST_JSON} not found. Run prepare_download_manifest.py first.")
        sys.exit(1)

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    RECYCLE_BIN.mkdir(parents=True, exist_ok=True)

    with open(MANIFEST_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = data["entries"]
    batch = entries[start - 1:end]  # 1-indexed → 0-indexed

    print(f"Agent range [{start}–{end}]: processing {len(batch)} entries")
    print(f"Categories: {sum(1 for e in batch if e['category'] == 'direct_pdf')} PDF, "
          f"{sum(1 for e in batch if e['category'] == 'html_page')} HTML, "
          f"{sum(1 for e in batch if e['category'] == 'blocked')} blocked")

    results = []
    format_counts = {"pdf": 0, "html": 0}
    error_counts: dict[str, int] = {}

    for i, entry in enumerate(batch, 1):
        print(f"  [{i:3d}/{len(batch)}] #{entry['index']} ({entry['category']}) "
              f"{entry['organization'][:40]} — {entry['url'][:55]}")

        result = process_entry(entry)

        status_label = "OK" if result["status"] == "success" else f"FAIL:{result['error']}"
        fmt = result.get("format") or "-"
        size_kb = result.get("bytes", 0) / 1024
        print(f"           → {status_label} [{fmt}] {size_kb:.1f}KB")

        results.append(result)

        if result["status"] == "success":
            if fmt in format_counts:
                format_counts[fmt] += 1
        else:
            err = result.get("error", "unknown")
            # Bucket errors
            if "blocked" in err:
                bucket = "blocked"
            elif "404" in err or "dead_link" in err:
                bucket = "dead_link"
            elif "timeout" in err:
                bucket = "timeout"
            elif "http_" in err:
                bucket = "http_error"
            elif "url_error" in err:
                bucket = "connection_error"
            else:
                bucket = "other"
            error_counts[bucket] = error_counts.get(bucket, 0) + 1

        # Polite delay between requests
        if entry["category"] != "blocked":
            time.sleep(REQUEST_DELAY)

    # PID-scoped output file
    pid = os.getpid()
    out_path = LOGS_DIR / f"20260321-download-results-{pid}.json"
    tmp_path = LOGS_DIR / f".tmp.{pid}.json"
    output = {
        "agent_range": [start, end],
        "total": len(batch),
        "success": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "format_counts": format_counts,
        "error_counts": error_counts,
        "results": results,
    }
    tmp_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), "utf-8")
    os.replace(str(tmp_path), str(out_path))

    success_count = output["success"]
    fail_count = output["failed"]

    print(f"\n{'='*60}")
    print(f"Agent [{start}–{end}] complete: {success_count}/{len(batch)} succeeded "
          f"({100*success_count/max(len(batch),1):.1f}%)")
    print(f"Format: {format_counts['pdf']} PDF, {format_counts['html']} HTML")
    if error_counts:
        print(f"Errors: {error_counts}")
    print(f"Output: {out_path}")


if __name__ == "__main__":
    main()
