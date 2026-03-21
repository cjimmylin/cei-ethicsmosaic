"""
prepare_download_manifest.py — Phase 0
Extract all ethics-code URLs from NAICS + SOC JSONs, deduplicate by URL,
classify each as direct_pdf / blocked / html_page, assign stable filename stems.

Output: logs/20260321-download-manifest.json
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent          # EthicsMosaic/NAICS/
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

NAICS_ALL = DATA_DIR / "naics-all-ethics-codes.json"
SOC_ALL   = DATA_DIR / "soc-all-ethics-codes.json"

# Domains known to block automated access (from url-spot-check-results.json)
BLOCKED_DOMAINS = {
    "acm.org",
    "americanbar.org",
    "ieee.org",
    "aiga.org",
    "sagaftra.org",
    "apa.org",
    "datascienceassn.org",
}


def slugify(text: str, max_len: int = 60) -> str:
    """Convert text to a filesystem-safe slug: ASCII, hyphens, no trailing."""
    # Normalize unicode
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    # Replace non-alphanumeric with hyphens
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text)
    # Collapse multiple hyphens
    text = re.sub(r"-{2,}", "-", text)
    # Trim
    text = text.strip("-")
    if len(text) > max_len:
        text = text[:max_len].rstrip("-")
    return text


def extract_abbrev(org_name: str) -> str:
    """
    Extract abbreviation from parentheses: 'American Bar Association (ABA)' → 'ABA'.
    Falls back to first-letter acronym of first 3 words.
    """
    m = re.search(r"\(([A-Za-z0-9 /&-]{2,20})\)", org_name)
    if m:
        abbrev = m.group(1).strip()
        # Slugify the abbreviation
        return re.sub(r"[^a-zA-Z0-9]+", "-", abbrev).strip("-")
    # Fallback: first letters of up to 4 words
    words = re.findall(r"[A-Z][a-z]*|[A-Z]+", org_name)
    if words:
        return "".join(w[0] for w in words[:5])
    return slugify(org_name.split()[0]) if org_name.split() else "UNK"


def domain_root(url: str) -> str:
    """Extract root domain from URL (e.g., 'www.acm.org' → 'acm.org')."""
    try:
        host = urlparse(url).hostname or ""
    except Exception:
        return ""
    parts = host.split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return host


def classify_url(url: str) -> str:
    """Classify a URL as direct_pdf, blocked, or html_page."""
    if url.lower().rstrip("/").endswith(".pdf"):
        return "direct_pdf"
    root = domain_root(url)
    if root in BLOCKED_DOMAINS:
        return "blocked"
    return "html_page"


def extract_naics_entries(data: dict) -> list[dict]:
    """Extract all code entries from NAICS JSON."""
    entries = []
    for sector in data.get("sectors", []):
        sector_code = sector.get("sector_code", "")
        sector_name = sector.get("sector_name", "")
        for subsector in sector.get("subsectors", []):
            sub_code = subsector.get("code", "")
            sub_name = subsector.get("name", "")
            for code in subsector.get("codes", []):
                if not code.get("url"):
                    continue
                entries.append({
                    "source": "NAICS",
                    "sector_code": sector_code,
                    "sector_name": sector_name,
                    "subsector_code": sub_code,
                    "subsector_name": sub_name,
                    **code,
                })
    return entries


def extract_soc_entries(data: dict) -> list[dict]:
    """Extract all code entries from SOC JSON."""
    entries = []
    for group in data.get("major_groups", []):
        group_code = group.get("group_code", "")
        group_name = group.get("group_name", "")
        for minor in group.get("minor_groups", []):
            minor_code = minor.get("code", "")
            minor_name = minor.get("name", "")
            for code in minor.get("codes", []):
                if not code.get("url"):
                    continue
                entries.append({
                    "source": "SOC",
                    "group_code": group_code,
                    "group_name": group_name,
                    "minor_code": minor_code,
                    "minor_name": minor_name,
                    **code,
                })
    return entries


def main():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Load sources
    with open(NAICS_ALL, "r", encoding="utf-8") as f:
        naics_data = json.load(f)
    with open(SOC_ALL, "r", encoding="utf-8") as f:
        soc_data = json.load(f)

    naics_entries = extract_naics_entries(naics_data)
    soc_entries = extract_soc_entries(soc_data)

    print(f"NAICS entries: {len(naics_entries)}")
    print(f"SOC entries:   {len(soc_entries)}")

    # Deduplicate by URL — keep first occurrence, merge source tracks
    seen_urls: dict[str, dict] = {}
    for entry in naics_entries + soc_entries:
        url = entry["url"].strip()
        if url in seen_urls:
            existing = seen_urls[url]
            # Merge source info
            if entry["source"] not in existing.get("sources", []):
                existing.setdefault("sources", [existing["source"]]).append(entry["source"])
            continue
        seen_urls[url] = entry

    unique_entries = list(seen_urls.values())
    print(f"Unique URLs:   {len(unique_entries)}")

    # Build manifest with stable filename stems
    used_stems: set[str] = set()
    manifest: list[dict] = []

    for entry in unique_entries:
        url = entry["url"].strip()
        org = entry.get("organization", "Unknown")
        title = entry.get("document_title", "Ethics Code")
        category = classify_url(url)

        abbrev = extract_abbrev(org)
        slug = slugify(title)
        stem = f"{abbrev}-{slug}" if slug else abbrev

        # Deduplicate stems
        if stem in used_stems:
            counter = 2
            while f"{stem}-{counter}" in used_stems:
                counter += 1
            stem = f"{stem}-{counter}"
        used_stems.add(stem)

        manifest.append({
            "index": len(manifest) + 1,
            "url": url,
            "organization": org,
            "document_title": title,
            "filename_stem": stem,
            "category": category,
            "document_type": entry.get("document_type", ""),
            "geographic_scope": entry.get("geographic_scope", ""),
            "year_published": entry.get("year_published", "unknown"),
            "source_track": entry.get("sources", [entry.get("source", "unknown")]),
        })

    # Category counts
    cats = {}
    for m in manifest:
        cats[m["category"]] = cats.get(m["category"], 0) + 1

    print(f"\nCategories:")
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")

    # Domain distribution
    domains: dict[str, int] = {}
    for m in manifest:
        d = domain_root(m["url"])
        domains[d] = domains.get(d, 0) + 1
    unique_domains = len(domains)
    multi_url_domains = {d: c for d, c in domains.items() if c > 3}
    print(f"\nUnique domains: {unique_domains}")
    if multi_url_domains:
        print(f"Domains with >3 URLs:")
        for d, c in sorted(multi_url_domains.items(), key=lambda x: -x[1])[:15]:
            print(f"  {d}: {c}")

    # Write manifest
    output = {
        "generated": "2026-03-21",
        "total": len(manifest),
        "categories": cats,
        "unique_domains": unique_domains,
        "entries": manifest,
    }
    out_path = LOGS_DIR / "20260321-download-manifest.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nManifest written: {out_path} ({len(manifest)} entries)")


if __name__ == "__main__":
    main()
