"""
wayback_recovery.py — Phase 1 of council-of-experts recovery
Query Wayback Machine for all 148 failures + SSL bypass for cert errors.
Run as: python wayback_recovery.py START END
START/END are 1-indexed over the failure list.
Output: logs/20260321-wayback-results-{PID}.json
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

RECOVERY_INPUT = LOGS_DIR / "20260321-recovery-input.json"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

MIN_FILE_SIZE = 500
WAYBACK_DELAY = 1.0  # seconds between Wayback API calls
DOWNLOAD_DELAY = 1.5  # seconds between downloads

WAYBACK_API = "https://archive.org/wayback/available?url={url}"

# ---------------------------------------------------------------------------
# HTML parser for PDF link detection (from batch_download_codes.py)
# ---------------------------------------------------------------------------

class PDFLinkExtractor(html.parser.HTMLParser):
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
# Download helpers
# ---------------------------------------------------------------------------

def download_pdf(url: str, dest_path: Path, timeout: int = 30,
                 insecure: bool = False) -> Tuple[bool, str]:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["curl", "-L", "-A", UA, "--max-time", str(timeout),
           "--silent", "--fail", "-o", str(dest_path), url]
    if insecure:
        cmd.insert(1, "-k")
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout + 30)
        if result.returncode != 0:
            return False, f"curl_error_{result.returncode}"
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)[:80]

    if not dest_path.exists() or dest_path.stat().st_size < MIN_FILE_SIZE:
        if dest_path.exists():
            try:
                dest_path.rename(RECYCLE_BIN / dest_path.name)
            except Exception:
                pass
        return False, "too_small"

    with open(dest_path, "rb") as f:
        header = f.read(5)
    if header[:4] != b"%PDF":
        try:
            dest_path.rename(RECYCLE_BIN / dest_path.name)
        except Exception:
            pass
        return False, "not_a_pdf"

    return True, ""


def download_html(url: str, dest_path: Path, timeout: int = 30,
                  insecure: bool = False) -> Tuple[bool, str, str]:
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if insecure:
        # Use curl with -k for SSL bypass
        cmd = ["curl", "-k", "-L", "-A", UA, "--max-time", str(timeout),
               "--silent", "-o", str(dest_path), url]
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=timeout + 30)
            if result.returncode != 0:
                return False, f"curl_error_{result.returncode}", ""
        except subprocess.TimeoutExpired:
            return False, "timeout", ""
        except Exception as e:
            return False, str(e)[:60], ""

        if not dest_path.exists() or dest_path.stat().st_size < MIN_FILE_SIZE:
            return False, "too_small", ""
        content = dest_path.read_text("utf-8", errors="replace")
    else:
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": UA,
                    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
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
        except Exception as e:
            return False, str(e)[:80], ""

        if not content.strip() or len(content) < MIN_FILE_SIZE:
            return False, "too_small", ""

        # Check for error pages
        content_lower = content[:2000].lower()
        error_markers = ["403 forbidden", "access denied", "page not found",
                         "404 not found", "error 404", "error 403"]
        if any(m in content_lower for m in error_markers) and len(content) < 3000:
            return False, "error_page_in_200", ""

        dest_path.write_text(content, "utf-8")

    return True, "", content


# ---------------------------------------------------------------------------
# Wayback Machine API
# ---------------------------------------------------------------------------

def query_wayback(url: str) -> Optional[str]:
    """Query Wayback Machine API for closest snapshot. Returns snapshot URL or None."""
    api_url = WAYBACK_API.format(url=urllib.parse.quote(url, safe=""))
    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        snap = data.get("archived_snapshots", {}).get("closest", {})
        if snap.get("available"):
            wb_url = snap.get("url", "")
            # Force HTTPS and id_ (original content, not framed)
            wb_url = wb_url.replace("http://web.archive.org", "https://web.archive.org")
            # Inject id_ to get raw content instead of framed page
            wb_url = re.sub(r'(/web/\d+)/', r'\1id_/', wb_url)
            return wb_url
    except Exception as e:
        print(f"  Wayback API error: {e}")
    return None


# ---------------------------------------------------------------------------
# Recovery logic per entry
# ---------------------------------------------------------------------------

def recover_entry(entry: dict) -> dict:
    """Try Wayback Machine + SSL bypass for one failure."""
    url = entry["url"]
    stem = entry["filename_stem"]
    error = entry["error"]

    result = {
        "index": entry["index"],
        "url": url,
        "organization": entry["organization"],
        "filename_stem": stem,
        "document_title": entry.get("document_title", ""),
        "original_error": error,
        "status": "failed",
        "strategy": None,
        "format": None,
        "local_file": None,
        "bytes": 0,
        "recovery_error": None,
    }

    # Skip if already recovered (another agent got it)
    for ext in (".pdf", ".html"):
        existing = DOCUMENTS_DIR / f"{stem}{ext}"
        if existing.exists() and existing.stat().st_size >= MIN_FILE_SIZE:
            result.update({
                "status": "already_exists",
                "strategy": "already_on_disk",
                "format": ext[1:],
                "local_file": existing.name,
                "bytes": existing.stat().st_size,
            })
            return result

    # ---------- Strategy 1: SSL bypass (for SSL cert failures) ----------
    is_ssl = "SSL" in error or "CERTIFICATE" in error
    if is_ssl:
        print(f"  Trying SSL bypass for {stem}...")
        url_lower = url.lower()
        is_pdf_url = url_lower.endswith(".pdf") or "/pdf/" in url_lower

        if is_pdf_url:
            dest = DOCUMENTS_DIR / f"{stem}.pdf"
            ok, err = download_pdf(url, dest, insecure=True)
            if ok:
                result.update({
                    "status": "success",
                    "strategy": "ssl_bypass_pdf",
                    "format": "pdf",
                    "local_file": dest.name,
                    "bytes": dest.stat().st_size,
                })
                return result

        dest = DOCUMENTS_DIR / f"{stem}.html"
        ok, err, content = download_html(url, dest, insecure=True)
        if ok:
            # Check for embedded PDF
            pdf_link = scrape_for_embedded_pdf(content, url)
            if pdf_link:
                pdf_dest = DOCUMENTS_DIR / f"{stem}.pdf"
                pdf_ok, _ = download_pdf(pdf_link, pdf_dest, insecure=True)
                if pdf_ok:
                    try:
                        dest.rename(RECYCLE_BIN / dest.name)
                    except Exception:
                        pass
                    result.update({
                        "status": "success",
                        "strategy": "ssl_bypass_embedded_pdf",
                        "format": "pdf",
                        "local_file": pdf_dest.name,
                        "bytes": pdf_dest.stat().st_size,
                    })
                    return result
            result.update({
                "status": "success",
                "strategy": "ssl_bypass_html",
                "format": "html",
                "local_file": dest.name,
                "bytes": dest.stat().st_size,
            })
            return result
        time.sleep(DOWNLOAD_DELAY)

    # ---------- Strategy 2: Wayback Machine ----------
    print(f"  Querying Wayback for {stem}...")
    wb_url = query_wayback(url)
    time.sleep(WAYBACK_DELAY)

    if not wb_url:
        result["recovery_error"] = "no_wayback_snapshot"
        return result

    print(f"  Found snapshot: {wb_url[:80]}...")

    # Determine if original was a PDF URL
    url_lower = url.lower()
    is_pdf_url = url_lower.endswith(".pdf") or "/pdf/" in url_lower

    if is_pdf_url:
        dest = DOCUMENTS_DIR / f"{stem}.pdf"
        ok, err = download_pdf(wb_url, dest)
        if ok:
            result.update({
                "status": "success",
                "strategy": "wayback_pdf",
                "format": "pdf",
                "local_file": dest.name,
                "bytes": dest.stat().st_size,
            })
            return result
        # Wayback might serve HTML wrapper even for PDF URLs
        time.sleep(DOWNLOAD_DELAY)

    # Try as HTML
    dest = DOCUMENTS_DIR / f"{stem}.html"
    ok, err, content = download_html(wb_url, dest)
    if ok:
        # Check for embedded PDF
        pdf_link = scrape_for_embedded_pdf(content, wb_url)
        if pdf_link:
            pdf_dest = DOCUMENTS_DIR / f"{stem}.pdf"
            pdf_ok, _ = download_pdf(pdf_link, pdf_dest)
            if pdf_ok:
                try:
                    dest.rename(RECYCLE_BIN / dest.name)
                except Exception:
                    pass
                result.update({
                    "status": "success",
                    "strategy": "wayback_embedded_pdf",
                    "format": "pdf",
                    "local_file": pdf_dest.name,
                    "bytes": pdf_dest.stat().st_size,
                })
                return result

        # Validate the HTML isn't just a Wayback error/redirect page
        if len(content) < 1000:
            content_lower = content.lower()
            if "wayback" in content_lower and ("error" in content_lower or "not available" in content_lower):
                try:
                    dest.rename(RECYCLE_BIN / dest.name)
                except Exception:
                    pass
                result["recovery_error"] = "wayback_error_page"
                return result

        result.update({
            "status": "success",
            "strategy": "wayback_html",
            "format": "html",
            "local_file": dest.name,
            "bytes": dest.stat().st_size,
        })
        return result

    result["recovery_error"] = f"wayback_download_failed:{err}"
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} START END")
        sys.exit(1)

    start = int(sys.argv[1])
    end = int(sys.argv[2])

    with open(RECOVERY_INPUT) as f:
        data = json.load(f)

    failures = data["failures"]
    batch = failures[start - 1 : end]

    print(f"=== Wayback Recovery: processing {len(batch)} entries ({start}-{end}) ===")
    print(f"PID: {os.getpid()}")

    results = []
    success_count = 0

    for i, entry in enumerate(batch, 1):
        idx = entry["index"]
        stem = entry["filename_stem"]
        print(f"\n[{i}/{len(batch)}] #{idx} {stem}")

        result = recover_entry(entry)
        results.append(result)

        if result["status"] == "success":
            success_count += 1
            print(f"  ✓ {result['strategy']} → {result['local_file']} ({result['bytes']} bytes)")
        elif result["status"] == "already_exists":
            print(f"  ⊘ Already on disk: {result['local_file']}")
        else:
            print(f"  ✗ {result['recovery_error']}")

        time.sleep(DOWNLOAD_DELAY)

    # Write PID-scoped results
    out_path = LOGS_DIR / f"20260321-wayback-results-{os.getpid()}.json"
    tmp_path = out_path.with_suffix(f".tmp.{os.getpid()}.json")
    with open(tmp_path, "w") as f:
        json.dump({
            "phase": "wayback",
            "pid": os.getpid(),
            "range": f"{start}-{end}",
            "total": len(batch),
            "success": success_count,
            "results": results,
        }, f, indent=2)
    os.replace(str(tmp_path), str(out_path))

    print(f"\n=== Done: {success_count}/{len(batch)} recovered ===")
    print(f"Results: {out_path}")


if __name__ == "__main__":
    main()
