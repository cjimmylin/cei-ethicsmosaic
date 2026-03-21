#!/usr/bin/env python3
"""
recover_documents.py
9-strategy waterfall to recover the 190 ethics codes not downloaded in Phase 2.

Strategies (in order):
  1. Plain retry  — clean curl attempt (catches all no-log records)
  2. Alt URL variants — URL path mutation / query-param stripping
  3. Wayback Machine — CDX API → archive snapshot download
  4. Google Cache — webcache.googleusercontent.com fetch + PDF scan
  5. Sitemap probe — parse DOMAIN/sitemap.xml for PDF links
  6. robots.txt probe — discover /documents/, /files/ etc paths
  7. Domain alt patterns — root-domain PDF guessing
  8. Playwright — headless Chromium for JS-rendered pages
  9. Google filetype search — "ORG" "code of ethics" filetype:pdf

Usage (run from EthicsMosaic/ISIC/):
  python PYTHON/recover_documents.py                      # all 190 missing
  python PYTHON/recover_documents.py --ids ISIC-K64-010,ISIC-M71-014
  python PYTHON/recover_documents.py --sections A,B,C
  python PYTHON/recover_documents.py --strategy wayback   # single strategy only
  python PYTHON/recover_documents.py --dry-run

Output:
  DOCUMENTS/{id}.pdf  or  DOCUMENTS/{id}.html
  DOCUMENTS/recovery-log-{PID}.json   (shard — merge after all agents complete)
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
BASE     = Path(__file__).parent.parent          # EthicsMosaic/ISIC/
REGISTRY = BASE / "data" / "ethics-codes-registry.json"
DOCS_DIR = BASE / "DOCUMENTS"
LOG_FILE = DOCS_DIR / "download-log.json"
SHARD_LOG = DOCS_DIR / f"recovery-log-{os.getpid()}.json"

DOCS_DIR.mkdir(exist_ok=True)

# ── HTTP settings ─────────────────────────────────────────────────────────────
CONNECT_TIMEOUT = 30
READ_TIMEOUT    = 60
DELAY_BASE      = 2.0       # more conservative than download_documents.py
DELAY_JITTER    = 0.8
SAME_DOMAIN_DELAY = 5.0     # extra wait when hitting same domain again
WAYBACK_DELAY   = 2.0       # CDX API rate limit
GOOGLE_DELAY    = 12.0      # Google search rate limit
MAX_RETRIES     = 1

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

LOGIN_MARKERS = [
    "sign in", "log in", "login required", "members only", "member login",
    "please login", "access denied", "subscription required", "create an account",
    "register to access", "restricted access", "join to access", "member benefit",
]

# Common document paths on org websites
DOC_PATH_PATTERNS = [
    "/documents/", "/files/", "/media/", "/download/", "/downloads/",
    "/wp-content/uploads/", "/sites/default/files/", "/content/dam/",
    "/resources/", "/publications/", "/library/", "/s/",
]

# Common ethics code PDF filename patterns
ETHICS_PDF_NAMES = [
    "code-of-ethics.pdf", "code_of_ethics.pdf", "codeofethics.pdf",
    "code-of-conduct.pdf", "code_of_conduct.pdf", "ethics-code.pdf",
    "ethics.pdf", "conduct.pdf", "professional-code.pdf",
    "standards-of-conduct.pdf", "ethical-principles.pdf",
]

# ── Log helpers ───────────────────────────────────────────────────────────────

def load_log() -> dict:
    if LOG_FILE.exists():
        try:
            return json.loads(LOG_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def load_shard() -> dict:
    if SHARD_LOG.exists():
        try:
            return json.loads(SHARD_LOG.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_shard(shard: dict) -> None:
    tmp = SHARD_LOG.with_suffix(f".tmp.{os.getpid()}.json")
    tmp.write_text(json.dumps(shard, indent=2, ensure_ascii=False))
    os.replace(tmp, SHARD_LOG)


def log_entry(record_id: str, status: str, fmt: str, filename: str,
              size: int, url: str, strategy: str = "",
              original_url: str = "", notes: str = "") -> dict:
    return {
        "status": status,
        "format": fmt,
        "filename": filename,
        "file_size_bytes": size,
        "source_url": url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "recovery_strategy": strategy,
        "original_url": original_url,
        "notes": notes,
    }

# ── Download helpers ──────────────────────────────────────────────────────────

def pick_ua() -> str:
    return random.choice(USER_AGENTS)


def curl_download(url: str, dest: Path, retries: int = MAX_RETRIES,
                  referer: str = "") -> bool:
    """Download url to dest using curl. Returns True on success."""
    for attempt in range(retries + 1):
        cmd = [
            "curl", "-L", "--silent", "--show-error",
            "--connect-timeout", str(CONNECT_TIMEOUT),
            "--max-time", str(READ_TIMEOUT),
            "-A", pick_ua(),
            "-o", str(dest),
        ]
        if referer:
            cmd += ["--referer", referer]
        cmd.append(url)

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and dest.exists() and dest.stat().st_size > 500:
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


def fetch_html(url: str, referer: str = "") -> Optional[str]:
    """Fetch HTML content of a URL using curl, return text or None."""
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
        ]
        if referer:
            cmd += ["--referer", referer]
        cmd.append(url)

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
    for attr in ["href", "data-href", "src"]:
        pattern = re.compile(
            rf'{attr}=["\']([^"\']*\.pdf[^"\']*)["\']',
            re.IGNORECASE
        )
        for m in pattern.finditer(html):
            href = m.group(1).strip()
            if not href:
                continue
            full = urllib.parse.urljoin(base_url, href)
            if full.startswith("http"):
                candidates.append(full)
    # Deduplicate
    seen: set = set()
    result = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            result.append(c)
    return result


def save_html(html: str, dest: Path) -> bool:
    """Save HTML content to dest. Returns True if size is acceptable."""
    dest.write_text(html, encoding="utf-8")
    size = dest.stat().st_size
    if size < 1000:
        dest.unlink()
        return False
    return True


def get_domain(url: str) -> str:
    return urllib.parse.urlparse(url).netloc

# ── Strategy implementations ──────────────────────────────────────────────────

def strategy_plain_retry(record: dict, rid: str) -> Optional[dict]:
    """Strategy 1: Plain curl retry — same logic as download_documents.py."""
    url = record.get("url", "").strip()
    if not url:
        return None

    # Direct PDF URL
    if url.lower().split("?")[0].endswith(".pdf"):
        dest = DOCS_DIR / f"{rid}.pdf"
        if curl_download(url, dest):
            size = dest.stat().st_size
            return log_entry(rid, "success", "pdf", dest.name, size, url, "plain_retry")
        return None

    # HTML page → look for PDF links
    html = fetch_html(url)
    if html is None:
        return None
    if is_login_wall(html):
        return log_entry(rid, "restricted", "none", "", 0, url, "plain_retry",
                        notes="login wall on retry")

    pdf_links = extract_pdf_links(html, url)
    for pdf_url in pdf_links[:3]:
        dest = DOCS_DIR / f"{rid}.pdf"
        if curl_download(pdf_url, dest):
            size = dest.stat().st_size
            return log_entry(rid, "success", "pdf", dest.name, size, pdf_url,
                            "plain_retry", original_url=url,
                            notes=f"PDF extracted from page")

    # HTML fallback
    dest = DOCS_DIR / f"{rid}.html"
    if save_html(html, dest):
        size = dest.stat().st_size
        return log_entry(rid, "success", "html", dest.name, size, url, "plain_retry")

    return None


def generate_url_variants(url: str) -> list[str]:
    """Generate alternative URL candidates from a base URL."""
    parsed = urllib.parse.urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path

    variants = []

    # 1. Strip query params (try clean URL)
    if parsed.query:
        variants.append(f"{base}{path}")

    # 2. Try .aspx → .pdf
    if path.lower().endswith(".aspx"):
        variants.append(f"{base}{path[:-5]}.pdf")

    # 3. Common path segment replacements
    path_replacements = [
        ("code-of-ethics", v) for v in [
            "ethics", "ethics-code", "codeofethics", "conduct", "code-of-conduct",
            "about/ethics", "governance/ethics", "professionals/ethics",
            "membership/ethics", "about/code-of-ethics",
        ]
    ] + [
        ("code-of-conduct", v) for v in [
            "ethics", "code-of-ethics", "conduct",
        ]
    ] + [
        ("codeofethics", v) for v in ["code-of-ethics", "ethics"]
    ]
    for old, new in path_replacements:
        if old in path.lower():
            variants.append(urllib.parse.urljoin(url, path.lower().replace(old, new)))

    # 4. Root domain + common ethics PDF names
    for name in ETHICS_PDF_NAMES[:5]:  # Top 5 only
        variants.append(f"{base}/{name}")

    # 5. Remove trailing path component, try from parent
    parent = "/".join(path.rstrip("/").split("/")[:-1])
    if parent:
        for name in ETHICS_PDF_NAMES[:3]:
            variants.append(f"{base}{parent}/{name}")

    # Deduplicate and exclude original
    seen = {url}
    result = []
    for v in variants:
        if v not in seen and v.startswith("http"):
            seen.add(v)
            result.append(v)
    return result


def strategy_alt_url(record: dict, rid: str) -> Optional[dict]:
    """Strategy 2: Try URL variants — path mutation, query stripping, .aspx→.pdf."""
    url = record.get("url", "").strip()
    if not url:
        return None

    variants = generate_url_variants(url)
    for variant_url in variants:
        time.sleep(0.5)  # Brief delay between variants

        if variant_url.lower().split("?")[0].endswith(".pdf"):
            dest = DOCS_DIR / f"{rid}.pdf"
            if curl_download(variant_url, dest):
                size = dest.stat().st_size
                return log_entry(rid, "success", "pdf", dest.name, size,
                                variant_url, "alt_url", original_url=url)
        else:
            html = fetch_html(variant_url)
            if html and not is_login_wall(html):
                pdf_links = extract_pdf_links(html, variant_url)
                for pdf_url in pdf_links[:2]:
                    dest = DOCS_DIR / f"{rid}.pdf"
                    if curl_download(pdf_url, dest):
                        size = dest.stat().st_size
                        return log_entry(rid, "success", "pdf", dest.name, size,
                                        pdf_url, "alt_url", original_url=url,
                                        notes=f"via variant {variant_url}")
                # HTML fallback on variant
                dest = DOCS_DIR / f"{rid}.html"
                if save_html(html, dest):
                    size = dest.stat().st_size
                    return log_entry(rid, "success", "html", dest.name, size,
                                    variant_url, "alt_url", original_url=url)
    return None


def strategy_wayback(record: dict, rid: str) -> Optional[dict]:
    """Strategy 3: Wayback Machine CDX API → find snapshot → download."""
    url = record.get("url", "").strip()
    if not url:
        return None

    # Query CDX API
    cdx_url = (
        "http://web.archive.org/cdx/search/cdx"
        f"?url={urllib.parse.quote(url, safe='')}"
        "&output=json&limit=5&fl=timestamp,statuscode&filter=statuscode:200"
        "&collapse=digest"
    )
    time.sleep(WAYBACK_DELAY)

    html = fetch_html(cdx_url)
    if not html:
        return None

    try:
        cdx_data = json.loads(html)
        # First row is header ["timestamp","statuscode"]
        if len(cdx_data) < 2:
            return None
        # Get most recent timestamp (last entry)
        snapshots = cdx_data[1:]  # Skip header
        if not snapshots:
            return None
        # Try most recent first, then oldest (more likely to be before paywall)
        candidates = [snapshots[-1], snapshots[0]]
        candidates = list({s[0]: s for s in candidates}.values())  # Deduplicate
    except (json.JSONDecodeError, IndexError, TypeError):
        return None

    for snap in candidates:
        timestamp = snap[0]
        wayback_url = f"https://web.archive.org/web/{timestamp}/{url}"
        time.sleep(WAYBACK_DELAY)

        if url.lower().split("?")[0].endswith(".pdf"):
            dest = DOCS_DIR / f"{rid}.pdf"
            if curl_download(wayback_url, dest):
                size = dest.stat().st_size
                return log_entry(rid, "success", "pdf", dest.name, size,
                                wayback_url, "wayback", original_url=url)
        else:
            html_content = fetch_html(wayback_url)
            if html_content and not is_login_wall(html_content):
                # Look for PDF links in archived page
                pdf_links = extract_pdf_links(html_content, wayback_url)
                for pdf_url in pdf_links[:3]:
                    dest = DOCS_DIR / f"{rid}.pdf"
                    # Try original URL version of the PDF first
                    orig_pdf = re.sub(r"web\.archive\.org/web/\d+/", "", pdf_url)
                    for try_url in [orig_pdf, pdf_url]:
                        if curl_download(try_url, dest):
                            size = dest.stat().st_size
                            return log_entry(rid, "success", "pdf", dest.name, size,
                                            try_url, "wayback", original_url=url,
                                            notes=f"PDF from Wayback snapshot {timestamp}")

                # HTML fallback from Wayback
                dest = DOCS_DIR / f"{rid}.html"
                if save_html(html_content, dest):
                    size = dest.stat().st_size
                    return log_entry(rid, "success", "html", dest.name, size,
                                    wayback_url, "wayback", original_url=url,
                                    notes=f"HTML from Wayback snapshot {timestamp}")
    return None


def strategy_google_cache(record: dict, rid: str) -> Optional[dict]:
    """Strategy 4: Google Cache fetch → scan for PDF links or save HTML."""
    url = record.get("url", "").strip()
    if not url:
        return None

    cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{urllib.parse.quote(url, safe='')}"

    html = fetch_html(cache_url)
    if not html or is_login_wall(html):
        return None

    # Reject Google Cache JS redirect stubs (curl can't execute JS)
    # These are ~3-4KB files with onload= JS that loads the real content dynamically
    if len(html) < 10000 and "onload=" in html and "webcache" in html.lower():
        return None  # Stub — let Playwright strategy handle it

    # Look for PDF links in cached page
    pdf_links = extract_pdf_links(html, url)
    for pdf_url in pdf_links[:3]:
        dest = DOCS_DIR / f"{rid}.pdf"
        if curl_download(pdf_url, dest):
            size = dest.stat().st_size
            return log_entry(rid, "success", "pdf", dest.name, size,
                            pdf_url, "google_cache", original_url=url)

    # HTML fallback
    dest = DOCS_DIR / f"{rid}.html"
    if save_html(html, dest):
        size = dest.stat().st_size
        return log_entry(rid, "success", "html", dest.name, size,
                        cache_url, "google_cache", original_url=url)
    return None


def strategy_sitemap(record: dict, rid: str) -> Optional[dict]:
    """Strategy 5: Fetch DOMAIN/sitemap.xml, search for PDF links matching org."""
    url = record.get("url", "").strip()
    doc_title = record.get("document_title", "").lower()
    org = record.get("organization", "").lower()
    if not url:
        return None

    parsed = urllib.parse.urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    for sitemap_path in ["/sitemap.xml", "/sitemap_index.xml", "/sitemap/"]:
        sitemap_url = base + sitemap_path
        html = fetch_html(sitemap_url)
        if not html:
            continue

        # Extract all URLs from sitemap
        url_pattern = re.compile(r"<loc>(.*?)</loc>", re.IGNORECASE | re.DOTALL)
        all_urls = [m.group(1).strip() for m in url_pattern.finditer(html)]

        # Find PDF candidates matching "ethics" or "conduct"
        ethics_keywords = ["ethics", "conduct", "code", "principles", "standards"]
        pdf_candidates = [
            u for u in all_urls
            if u.lower().endswith(".pdf") and
            any(kw in u.lower() for kw in ethics_keywords)
        ]

        for pdf_url in pdf_candidates[:5]:
            dest = DOCS_DIR / f"{rid}.pdf"
            if curl_download(pdf_url, dest):
                size = dest.stat().st_size
                return log_entry(rid, "success", "pdf", dest.name, size,
                                pdf_url, "sitemap", original_url=url,
                                notes=f"Found in {sitemap_url}")

        # Also check nested sitemaps
        sitemap_refs = [
            u for u in all_urls
            if "sitemap" in u.lower() and u.endswith(".xml")
        ]
        for nested_url in sitemap_refs[:3]:
            time.sleep(1)
            nested_html = fetch_html(nested_url)
            if not nested_html:
                continue
            nested_pdfs = [
                m.group(1).strip()
                for m in url_pattern.finditer(nested_html)
                if m.group(1).strip().lower().endswith(".pdf") and
                any(kw in m.group(1).lower() for kw in ethics_keywords)
            ]
            for pdf_url in nested_pdfs[:3]:
                dest = DOCS_DIR / f"{rid}.pdf"
                if curl_download(pdf_url, dest):
                    size = dest.stat().st_size
                    return log_entry(rid, "success", "pdf", dest.name, size,
                                    pdf_url, "sitemap", original_url=url,
                                    notes=f"Found in nested sitemap {nested_url}")

        time.sleep(1)

    return None


def strategy_robots_probe(record: dict, rid: str) -> Optional[dict]:
    """Strategy 6: Parse robots.txt for doc directories, try ethics PDF names."""
    url = record.get("url", "").strip()
    if not url:
        return None

    parsed = urllib.parse.urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    robots_url = base + "/robots.txt"
    robots = fetch_html(robots_url)

    # Extract all paths from robots.txt (Allow: and Disallow: lines)
    doc_paths = set(DOC_PATH_PATTERNS)  # Start with known patterns
    if robots:
        for line in robots.splitlines():
            if line.startswith(("Allow:", "Disallow:")):
                path = line.split(":", 1)[1].strip()
                if any(kw in path.lower() for kw in ["doc", "file", "media", "upload", "pdf"]):
                    doc_paths.add(path)

    # Try root domain + known ethics PDF names
    candidates = []
    for doc_path in list(doc_paths)[:8]:
        for pdf_name in ETHICS_PDF_NAMES[:4]:
            candidates.append(f"{base}{doc_path}{pdf_name}")
    # Also try bare root
    for pdf_name in ETHICS_PDF_NAMES[:4]:
        candidates.append(f"{base}/{pdf_name}")

    for candidate_url in candidates[:20]:  # Limit to 20 candidates
        dest = DOCS_DIR / f"{rid}.pdf"
        if curl_download(candidate_url, dest):
            size = dest.stat().st_size
            return log_entry(rid, "success", "pdf", dest.name, size,
                            candidate_url, "robots_probe", original_url=url)
        time.sleep(0.3)

    return None


def strategy_alt_domain_patterns(record: dict, rid: str) -> Optional[dict]:
    """Strategy 7: Try systematic domain/path permutations."""
    url = record.get("url", "").strip()
    if not url:
        return None

    parsed = urllib.parse.urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path.rstrip("/")

    # Generate path permutations
    path_parts = [p for p in path.split("/") if p]
    candidates = []

    # Try alternate path segments for ethics-related terms
    ethics_paths = [
        "/about/ethics", "/about/code-of-ethics", "/about/code-of-conduct",
        "/governance/code-of-ethics", "/governance/ethics",
        "/membership/code-of-ethics", "/members/code-of-ethics",
        "/professional-development/ethics", "/resources/ethics",
        "/our-principles", "/principles", "/code", "/conduct",
        "/ethics-policy", "/ethical-guidelines", "/professional-standards",
    ]
    for p in ethics_paths:
        candidates.append(f"{base}{p}")
        candidates.append(f"{base}{p}.pdf")

    # Try index-style URLs
    if path_parts:
        parent_path = "/" + "/".join(path_parts[:-1])
        if parent_path != "/":
            candidates.append(f"{base}{parent_path}/")
            candidates.append(f"{base}{parent_path}")

    # Try with/without trailing slash
    candidates.append(url.rstrip("/") + "/")
    candidates.append(url.rstrip("/"))

    seen = {url}
    for candidate_url in candidates:
        if candidate_url in seen or not candidate_url.startswith("http"):
            continue
        seen.add(candidate_url)

        time.sleep(0.5)
        if candidate_url.lower().endswith(".pdf"):
            dest = DOCS_DIR / f"{rid}.pdf"
            if curl_download(candidate_url, dest):
                size = dest.stat().st_size
                return log_entry(rid, "success", "pdf", dest.name, size,
                                candidate_url, "alt_domain", original_url=url)
        else:
            html = fetch_html(candidate_url)
            if html and not is_login_wall(html):
                pdf_links = extract_pdf_links(html, candidate_url)
                for pdf_url in pdf_links[:2]:
                    dest = DOCS_DIR / f"{rid}.pdf"
                    if curl_download(pdf_url, dest):
                        size = dest.stat().st_size
                        return log_entry(rid, "success", "pdf", dest.name, size,
                                        pdf_url, "alt_domain", original_url=url,
                                        notes=f"via alt path {candidate_url}")
                # HTML fallback if promising
                if any(kw in html.lower() for kw in ["code of ethics", "code of conduct", "professional standards"]):
                    dest = DOCS_DIR / f"{rid}.html"
                    if save_html(html, dest):
                        size = dest.stat().st_size
                        return log_entry(rid, "success", "html", dest.name, size,
                                        candidate_url, "alt_domain", original_url=url)

    return None


def strategy_playwright(record: dict, rid: str) -> Optional[dict]:
    """Strategy 8: Headless Chromium — handles JS-rendered pages, soft paywalls,
    and Google Cache JS redirect stubs (curl can't execute JS, Playwright can)."""
    url = record.get("url", "").strip()
    if not url:
        return None

    # Build list of URLs to try: original URL + Google Cache URL
    # Google Cache JS stubs need Playwright to execute their onload redirect
    cache_url = (
        f"https://webcache.googleusercontent.com/search?q=cache:"
        f"{urllib.parse.quote(url, safe='')}"
    )
    urls_to_try = [url, cache_url]

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=pick_ua(),
                viewport={"width": 1280, "height": 800},
            )
            page = context.new_page()

            # Track any PDF navigation
            pdf_urls_found = []

            def handle_request(request):
                if ".pdf" in request.url.lower():
                    pdf_urls_found.append(request.url)

            page.on("request", handle_request)

            try:
                # Try original URL first, then Google Cache URL
                nav_url = url
                for try_url in urls_to_try:
                    try:
                        page.goto(try_url, timeout=30000, wait_until="domcontentloaded")
                        page.wait_for_timeout(3000)  # Let JS render
                        nav_url = try_url
                        break
                    except Exception:
                        continue

                # Try to dismiss cookie banners / modals
                for selector in ["button:has-text('Accept')", "button:has-text('OK')",
                                  "button:has-text('Close')", "[class*='cookie'] button",
                                  "[id*='cookie'] button", ".modal-close", ".close-button"]:
                    try:
                        page.click(selector, timeout=1000)
                        page.wait_for_timeout(500)
                    except Exception:
                        pass

                # Get page content
                html_content = page.content()

                # Check for login wall
                if is_login_wall(html_content):
                    # Try to find and download the actual PDF without going through login
                    pdf_links = extract_pdf_links(html_content, url)
                    for pdf_url in pdf_links[:3]:
                        dest = DOCS_DIR / f"{rid}.pdf"
                        if curl_download(pdf_url, dest):
                            size = dest.stat().st_size
                            browser.close()
                            return log_entry(rid, "success", "pdf", dest.name, size,
                                            pdf_url, "playwright", original_url=url,
                                            notes="PDF direct link found behind login wall")
                    browser.close()
                    return log_entry(rid, "restricted", "none", "", 0, url,
                                    "playwright", notes="login wall confirmed by Playwright")

                # Look for PDF links in rendered DOM
                pdf_links = extract_pdf_links(html_content, url)

                # Also check links found via page.evaluate
                try:
                    js_hrefs = page.evaluate("""
                        () => Array.from(document.querySelectorAll('a[href*=".pdf"]'))
                              .map(a => a.href)
                    """)
                    pdf_links = list(dict.fromkeys(pdf_links + (js_hrefs or [])))
                except Exception:
                    pass

                # Try to click download/view buttons
                for btn_selector in [
                    "a:has-text('Download PDF')", "a:has-text('View PDF')",
                    "a:has-text('Download')", "button:has-text('Download PDF')",
                    "[class*='download']", "[class*='pdf-link']",
                ]:
                    try:
                        btn = page.query_selector(btn_selector)
                        if btn:
                            href = btn.get_attribute("href")
                            if href and ".pdf" in href.lower():
                                full = urllib.parse.urljoin(url, href)
                                pdf_links.insert(0, full)
                    except Exception:
                        pass

                # Also check captured network requests
                pdf_links = list(dict.fromkeys(pdf_links + pdf_urls_found))

                for pdf_url in pdf_links[:5]:
                    dest = DOCS_DIR / f"{rid}.pdf"
                    if curl_download(pdf_url, dest):
                        size = dest.stat().st_size
                        browser.close()
                        return log_entry(rid, "success", "pdf", dest.name, size,
                                        pdf_url, "playwright", original_url=url)

                # HTML fallback with rendered content
                if html_content and len(html_content) > 1000:
                    dest = DOCS_DIR / f"{rid}.html"
                    if save_html(html_content, dest):
                        size = dest.stat().st_size
                        browser.close()
                        return log_entry(rid, "success", "html", dest.name, size,
                                        url, "playwright", original_url=url,
                                        notes="JS-rendered HTML")

            except Exception as e:
                pass
            finally:
                try:
                    browser.close()
                except Exception:
                    pass

    except Exception:
        pass

    return None


def strategy_google_search(record: dict, rid: str) -> Optional[dict]:
    """Strategy 9: Google filetype:pdf search for the organization's ethics code."""
    org = record.get("organization", "")
    doc_title = record.get("document_title", "")
    url = record.get("url", "").strip()

    if not org:
        return None

    # Construct search query
    domain = get_domain(url) if url else ""
    if domain:
        query = f'site:{domain} filetype:pdf "code of ethics" OR "code of conduct"'
    else:
        # Fallback: search by org name
        short_org = org[:40]  # Trim long org names
        query = f'"{short_org}" "code of ethics" filetype:pdf'

    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num=5"
    time.sleep(GOOGLE_DELAY)  # Respect Google rate limits

    html = fetch_html(search_url)
    if not html:
        return None

    # Parse Google results for PDF URLs
    # Look for URLs in Google result links
    pdf_pattern = re.compile(r'https?://[^\s"<>]+\.pdf', re.IGNORECASE)
    pdf_candidates = list(dict.fromkeys(pdf_pattern.findall(html)))

    # Filter out Google's own URLs and obvious non-matches
    pdf_candidates = [
        u for u in pdf_candidates
        if "google.com" not in u and "webcache" not in u
    ]

    for pdf_url in pdf_candidates[:5]:
        dest = DOCS_DIR / f"{rid}.pdf"
        if curl_download(pdf_url, dest):
            size = dest.stat().st_size
            return log_entry(rid, "success", "pdf", dest.name, size,
                            pdf_url, "google_search", original_url=url,
                            notes=f"Found via Google: {query[:80]}")

    return None

# ── Main recovery waterfall ───────────────────────────────────────────────────

STRATEGIES = [
    ("plain_retry",        strategy_plain_retry),
    ("alt_url",            strategy_alt_url),
    ("wayback",            strategy_wayback),
    ("google_cache",       strategy_google_cache),
    ("sitemap",            strategy_sitemap),
    ("robots_probe",       strategy_robots_probe),
    ("alt_domain",         strategy_alt_domain_patterns),
    ("playwright",         strategy_playwright),
    ("google_search",      strategy_google_search),
]

# Domains that only need certain strategies (skip expensive ones for known hard cases)
SKIP_WAYBACK_DOMAINS = set()   # Fill in if Wayback is consistently slow for a domain
SKIP_PLAYWRIGHT_DOMAINS = set()  # Hard member-only portals — playwright won't help


def recover_record(record: dict, dry_run: bool = False,
                   only_strategy: Optional[str] = None) -> dict:
    """Run the strategy waterfall for one record. Returns log entry."""
    rid   = record["id"]
    url   = record.get("url", "").strip()
    title = record.get("document_title", "")
    org   = record.get("organization", "")
    domain = get_domain(url) if url else ""

    print(f"  [{rid}] {org[:50]}")
    if not url:
        return log_entry(rid, "skipped", "none", "", 0, url, notes="no URL")

    if dry_run:
        strategies_to_run = [only_strategy] if only_strategy else [s[0] for s in STRATEGIES]
        print(f"    → DRY RUN: would try strategies: {strategies_to_run}")
        return log_entry(rid, "dry_run", "none", "", 0, url, "dry_run")

    strategies_to_run = STRATEGIES
    if only_strategy:
        strategies_to_run = [(name, fn) for name, fn in STRATEGIES if name == only_strategy]
        if not strategies_to_run:
            print(f"    → Unknown strategy: {only_strategy}")
            return log_entry(rid, "error", "none", "", 0, url, notes=f"unknown strategy {only_strategy}")

    saw_login_wall = False

    for strategy_name, strategy_fn in strategies_to_run:
        # Skip Playwright for known hard-member-only portals
        if strategy_name == "playwright" and domain in SKIP_PLAYWRIGHT_DOMAINS:
            continue

        print(f"    → Trying {strategy_name}...", end=" ")
        try:
            result = strategy_fn(record, rid)
        except Exception as e:
            print(f"ERROR: {e}")
            result = None

        if result is not None:
            status = result.get("status", "?")
            if status == "success":
                fmt = result.get("format", "?")
                size = result.get("file_size_bytes", 0)
                print(f"SUCCESS ({fmt}, {size:,} bytes)")
                return result
            elif status == "restricted":
                # Don't stop — continue waterfall. Wayback/Google Cache/Playwright
                # can often retrieve the document even when the live page is gated.
                saw_login_wall = True
                print(f"restricted (continuing waterfall...)")
            else:
                print(f"{status}")
        else:
            print("failed")

        # Delay between strategies
        time.sleep(DELAY_BASE + random.uniform(-DELAY_JITTER, DELAY_JITTER))

    # Exhausted all strategies
    final_status = "restricted" if saw_login_wall else "permanently_failed"
    notes = "login wall — all bypass strategies failed" if saw_login_wall else "exhausted all 9 strategies"
    print(f"    → All strategies exhausted — {final_status}")
    return log_entry(rid, final_status, "none", "", 0, url, notes=notes)

# ── Entry point ───────────────────────────────────────────────────────────────

def get_missing_ids(registry_records: list, log: dict) -> list[str]:
    """Return IDs of records not yet in DOCUMENTS/ dir."""
    downloaded = set()
    for f in DOCS_DIR.iterdir():
        if f.suffix in (".pdf", ".html") and f.stem.startswith("ISIC-"):
            downloaded.add(f.stem)
    return [r["id"] for r in registry_records if r["id"] not in downloaded]


def main() -> None:
    args = sys.argv[1:]
    dry_run       = "--dry-run" in args
    only_strategy = next((a.split("=")[1] if "=" in a else args[args.index(a)+1]
                          for a in args if a == "--strategy"), None)
    if "--strategy" in args:
        idx = args.index("--strategy")
        only_strategy = args[idx + 1] if idx + 1 < len(args) else None

    # Parse --ids (comma-separated)
    target_ids = None
    if "--ids" in args:
        idx = args.index("--ids")
        if idx + 1 < len(args):
            target_ids = set(args[idx + 1].split(","))

    # Parse --sections (comma-separated)
    target_sections = None
    if "--sections" in args:
        idx = args.index("--sections")
        if idx + 1 < len(args):
            target_sections = set(args[idx + 1].split(","))

    # Load registry and log
    data = json.loads(REGISTRY.read_text())
    records = data["records"]
    log = load_log()

    # Build record lookup
    record_map = {r["id"]: r for r in records}

    # Determine which records to process
    missing_ids = get_missing_ids(records, log)
    print(f"Found {len(missing_ids)} records missing from DOCUMENTS/")

    if target_ids:
        process_ids = [rid for rid in target_ids if rid in record_map]
        print(f"Processing {len(process_ids)} specified IDs")
    elif target_sections:
        process_ids = [rid for rid in missing_ids
                       if record_map.get(rid, {}).get("isic_section") in target_sections]
        print(f"Processing {len(process_ids)} records in sections {target_sections}")
    else:
        process_ids = missing_ids
        print(f"Processing all {len(process_ids)} missing records")

    if not process_ids:
        print("Nothing to process.")
        return

    shard = load_shard()
    counts = {
        "success_pdf": 0, "success_html": 0, "restricted": 0,
        "permanently_failed": 0, "error": 0, "dry_run": 0, "skipped": 0,
    }

    last_domain = None
    last_domain_time = 0.0

    for i, rid in enumerate(process_ids, 1):
        record = record_map.get(rid)
        if not record:
            print(f"  [{rid}] NOT IN REGISTRY — skipping")
            continue

        url = record.get("url", "")
        domain = get_domain(url) if url else ""

        print(f"\n[{i}/{len(process_ids)}]", end=" ")

        # Extra delay for same-domain requests
        if domain and domain == last_domain:
            elapsed = time.time() - last_domain_time
            if elapsed < SAME_DOMAIN_DELAY:
                time.sleep(SAME_DOMAIN_DELAY - elapsed)

        entry = recover_record(record, dry_run=dry_run, only_strategy=only_strategy)
        shard[rid] = entry
        save_shard(shard)

        # Track domain timing
        if domain:
            last_domain = domain
            last_domain_time = time.time()

        # Count results
        status = entry.get("status", "error")
        fmt = entry.get("format", "none")
        if status == "success" and fmt == "pdf":
            counts["success_pdf"] += 1
        elif status == "success" and fmt == "html":
            counts["success_html"] += 1
        elif status in counts:
            counts[status] += 1
        else:
            counts["error"] += 1

        # Inter-record delay
        if i < len(process_ids):
            delay = DELAY_BASE + random.uniform(-DELAY_JITTER, DELAY_JITTER)
            time.sleep(max(0.5, delay))

    # Summary
    print(f"\n{'='*60}")
    print(f"RECOVERY COMPLETE — {len(process_ids)} records processed")
    print(f"  PDF success       : {counts['success_pdf']}")
    print(f"  HTML success      : {counts['success_html']}")
    print(f"  Restricted        : {counts['restricted']}")
    print(f"  Permanently failed: {counts['permanently_failed']}")
    print(f"  Errors            : {counts['error']}")
    print(f"  Shard log         : {SHARD_LOG}")
    if dry_run:
        print(f"  Dry run           : {counts['dry_run']}")


if __name__ == "__main__":
    main()
