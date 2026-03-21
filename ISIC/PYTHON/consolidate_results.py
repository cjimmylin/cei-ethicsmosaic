"""
consolidate_results.py
Merges all per-section JSON result files into a single master registry.
Generates summary statistics and gap analysis.
Usage: python consolidate_results.py
Working directory: EthicsMosaic/ISIC/
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

BASE = Path(__file__).parent.parent  # EthicsMosaic/ISIC/
DATA_DIR = BASE / "data"
STATS_DIR = BASE / "STATISTICS"
STATS_DIR.mkdir(exist_ok=True)

# All per-section JSON files (alphabetical by section)
SECTION_FILES = [
    ("A", "Agriculture, Forestry and Fishing",           "section-a-results.json"),
    ("B", "Mining and Quarrying",                         "section-b-results.json"),
    ("C1","Manufacturing (Part 1, Div 10-19)",            "section-c-pt1-results.json"),
    ("C2","Manufacturing (Part 2, Div 20-33)",            "section-c-pt2-results.json"),
    ("D", "Electricity, Gas, Steam & Air Conditioning",  "section-d-results.json"),
    ("E", "Water Supply; Sewerage; Waste Management",    "section-e-results.json"),
    ("F", "Construction",                                 "section-f-results.json"),
    ("G", "Wholesale and Retail Trade",                   "section-g-results.json"),
    ("H", "Transportation and Storage",                   "section-h-results.json"),
    ("I", "Accommodation and Food Service",               "section-i-results.json"),
    ("J", "Information and Communication",                "section-j-results.json"),
    ("K", "Financial and Insurance Activities",           "section-k-results.json"),
    ("L", "Real Estate Activities",                       "section-l-results.json"),
    ("M", "Professional, Scientific and Technical",       "section-m-results.json"),
    ("N", "Administrative and Support Services",          "section-n-results.json"),
    ("O", "Public Administration and Defence",            "section-o-results.json"),
    ("P", "Education",                                    "section-p-results.json"),
    ("Q", "Human Health and Social Work",                 "section-q-results.json"),
    ("R", "Arts, Entertainment and Recreation",           "section-r-results.json"),
    ("S", "Other Service Activities",                     "section-s-results.json"),
    ("T", "Activities of Households as Employers",        "section-t-results.json"),
    ("U", "Activities of Extraterritorial Organizations", "section-u-results.json"),
]

# ISIC Rev 4 divisions per section (for gap analysis)
ISIC_DIVISIONS = {
    "A": ["01", "02", "03"],
    "B": ["05", "06", "07", "08", "09"],
    "C": ["10","11","12","13","14","15","16","17","18","19",
          "20","21","22","23","24","25","26","27","28","29","30","31","32","33"],
    "D": ["35"],
    "E": ["36", "37", "38", "39"],
    "F": ["41", "42", "43"],
    "G": ["45", "46", "47"],
    "H": ["49", "50", "51", "52", "53"],
    "I": ["55", "56"],
    "J": ["58", "59", "60", "61", "62", "63"],
    "K": ["64", "65", "66"],
    "L": ["68"],
    "M": ["69", "70", "71", "72", "73", "74", "75"],
    "N": ["77", "78", "79", "80", "81", "82"],
    "O": ["84"],
    "P": ["85"],
    "Q": ["86", "87", "88"],
    "R": ["90", "91", "92", "93"],
    "S": ["94", "95", "96"],
    "T": ["97", "98"],
    "U": ["99"],
}


def load_all() -> list[dict]:
    all_records = []
    for section, name, filename in SECTION_FILES:
        path = DATA_DIR / filename
        if not path.exists():
            print(f"  [MISSING] {filename}")
            continue
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            print(f"  [JSON ERROR] {filename}: {e}")
            continue
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict) and "records" in data:
            records = data["records"]
        else:
            records = []
        print(f"  {section:3s}  {len(records):3d}  {filename}")
        all_records.extend(records)
    return all_records


def compute_stats(records: list[dict]) -> dict:
    # Per-section counts (map C1/C2 → C)
    by_section: defaultdict[str, int] = defaultdict(int)
    by_division: defaultdict[str, int] = defaultdict(int)
    by_scope: defaultdict[str, int] = defaultdict(int)
    by_org_type: defaultdict[str, int] = defaultdict(int)
    by_enforcement: defaultdict[str, int] = defaultdict(int)
    by_doc_type: defaultdict[str, int] = defaultdict(int)
    orgs: set[str] = set()

    for r in records:
        sec = r.get("isic_section", "?")
        # Normalise C1/C2 → C
        if sec in ("C1", "C2"):
            sec = "C"
        div = str(r.get("isic_division", "?"))
        by_section[sec] += 1
        by_division[div] += 1
        by_scope[r.get("scope", "Unknown")] += 1
        by_org_type[r.get("org_type", "Unknown")] += 1
        by_enforcement[r.get("enforcement_level", "Unknown")] += 1
        by_doc_type[r.get("document_type", r.get("document_type_detailed", "Unknown"))] += 1
        org = r.get("organization", "")
        if org:
            orgs.add(org)

    # Gap analysis: divisions with 0 entries
    covered_divisions: set[str] = set(by_division.keys())
    all_divisions: set[str] = set()
    for divs in ISIC_DIVISIONS.values():
        all_divisions.update(divs)
    zero_divisions = sorted(all_divisions - covered_divisions)

    return {
        "total_documents": len(records),
        "total_organizations": len(orgs),
        "by_section": dict(sorted(by_section.items())),
        "by_division": dict(sorted(by_division.items(), key=lambda x: x[0].zfill(3))),
        "by_scope": dict(sorted(by_scope.items(), key=lambda x: -x[1])),
        "by_org_type": dict(sorted(by_org_type.items(), key=lambda x: -x[1])),
        "by_enforcement": dict(sorted(by_enforcement.items(), key=lambda x: -x[1])),
        "by_doc_type": dict(sorted(by_doc_type.items(), key=lambda x: -x[1])),
        "zero_divisions": zero_divisions,
    }


def write_registry(records: list[dict], stats: dict) -> None:
    registry = {
        "metadata": {
            "version": "1.0",
            "created": str(date.today()),
            "isic_version": "Rev4",
            "total_documents": stats["total_documents"],
            "total_organizations": stats["total_organizations"],
            "sections_covered": 21,
            "divisions_covered": 88,
            "divisions_with_zero_entries": len(stats["zero_divisions"]),
        },
        "records": records,
    }
    out = DATA_DIR / "ethics-codes-registry.json"
    out.write_text(json.dumps(registry, indent=2, ensure_ascii=False))
    print(f"\nMaster registry written: {out}  ({len(records)} records)")


def write_summary(stats: dict) -> None:
    today = date.today().strftime("%Y%m%d")
    out = STATS_DIR / f"{today}-isic-ethics-codes-summary.md"

    lines = [
        "# ISIC Ethics Codes Registry — Summary Statistics",
        f"\n**Generated:** {date.today().isoformat()}",
        f"**Total documents:** {stats['total_documents']}",
        f"**Total organizations:** {stats['total_organizations']}",
        f"**ISIC sections covered:** 21 (A–U)",
        f"**Divisions with zero entries:** {len(stats['zero_divisions'])}",
        "\n---\n",
        "## Documents by ISIC Section\n",
        "| Section | Name | Documents |",
        "|---------|------|-----------|",
    ]
    section_names = {s: n for s, n, _ in SECTION_FILES}
    # Merge C1+C2 for display
    sec_display = dict(stats["by_section"])
    c_total = sec_display.pop("C1", 0) + sec_display.pop("C2", 0)
    if c_total:
        sec_display["C"] = c_total
    for sec in sorted(sec_display.keys()):
        name = section_names.get(sec, "Manufacturing")
        if sec == "C":
            name = "Manufacturing"
        lines.append(f"| {sec} | {name} | {sec_display[sec]} |")
    lines.append(f"| **Total** | | **{stats['total_documents']}** |")

    lines += [
        "\n---\n",
        "## Documents by Geographic Scope\n",
        "| Scope | Count | % |",
        "|-------|-------|---|",
    ]
    total = stats["total_documents"]
    for scope, cnt in stats["by_scope"].items():
        pct = round(100 * cnt / total, 1)
        lines.append(f"| {scope} | {cnt} | {pct}% |")

    lines += [
        "\n---\n",
        "## Documents by Organization Type\n",
        "| Org Type | Count | % |",
        "|----------|-------|---|",
    ]
    for ot, cnt in stats["by_org_type"].items():
        pct = round(100 * cnt / total, 1)
        lines.append(f"| {ot} | {cnt} | {pct}% |")

    lines += [
        "\n---\n",
        "## Documents by Enforcement Level\n",
        "| Enforcement Level | Count | % |",
        "|-------------------|-------|---|",
    ]
    for el, cnt in stats["by_enforcement"].items():
        pct = round(100 * cnt / total, 1)
        lines.append(f"| {el} | {cnt} | {pct}% |")

    lines += [
        "\n---\n",
        "## Documents by Document Type\n",
        "| Document Type | Count | % |",
        "|---------------|-------|---|",
    ]
    for dt, cnt in stats["by_doc_type"].items():
        pct = round(100 * cnt / total, 1)
        lines.append(f"| {dt} | {cnt} | {pct}% |")

    lines += [
        "\n---\n",
        "## Gap Analysis — Divisions with Zero Entries\n",
        f"**{len(stats['zero_divisions'])} divisions** had no standalone ethics codes found:\n",
    ]
    if stats["zero_divisions"]:
        for div in stats["zero_divisions"]:
            lines.append(f"- Division {div}")
    else:
        lines.append("- None — all divisions have at least one entry.")

    lines += [
        "\n---\n",
        "## Notes\n",
        "- Sections C is split across two agent files (Pt1: Div 10-19, Pt2: Div 20-33).",
        "- Cross-listings (where a code appears in multiple sections) are noted in research files but counted once in the registry.",
        "- 'Zero entry' divisions typically rely on engineering or management codes from Section M.",
    ]

    out.write_text("\n".join(lines))
    print(f"Summary written: {out}")


def main() -> None:
    print("Loading per-section JSON files...")
    records = load_all()
    print(f"\nTotal records loaded: {len(records)}")

    print("\nComputing statistics...")
    stats = compute_stats(records)

    print("\nWriting master registry...")
    write_registry(records, stats)

    print("\nWriting summary statistics...")
    write_summary(stats)

    # Print quick summary to stdout
    print("\n=== QUICK SUMMARY ===")
    print(f"Total documents : {stats['total_documents']}")
    print(f"Total orgs      : {stats['total_organizations']}")
    print(f"Zero divisions  : {len(stats['zero_divisions'])} — {stats['zero_divisions']}")
    print("\nBy section:")
    sec_display = dict(stats["by_section"])
    c_total = sec_display.pop("C1", 0) + sec_display.pop("C2", 0)
    if c_total:
        sec_display["C"] = c_total
    for sec in sorted(sec_display.keys()):
        print(f"  {sec}: {sec_display[sec]}")


if __name__ == "__main__":
    main()
