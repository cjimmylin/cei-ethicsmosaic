"""Parse 2022 NAICS Manual markdown into structured JSON.

Also accepts SOC major group data (from agent output) and writes soc-major-groups.json.

Usage:
    python parse_naics_sectors.py                    # Parse NAICS only
    python parse_naics_sectors.py --soc SOC_FILE     # Also write SOC JSON from agent file
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
NAICS_MANUAL = SCRIPT_DIR / "2022_NAICS_Manual.md"
DATA_DIR = SCRIPT_DIR / "data"


def parse_naics_manual(path: Path) -> dict:
    """Parse the markdown NAICS manual into structured sectors/subsectors."""
    text = path.read_text(encoding="utf-8")

    sectors = []
    # Match sector headings: ## Sector XX — Name  or  ## Sector XX-YY — Name
    sector_pattern = re.compile(
        r"^## Sector ([\d-]+) — (.+)$", re.MULTILINE
    )
    # Match subsector bullets: - **XXX** Name
    subsector_pattern = re.compile(
        r"^- \*\*(\d{3})\*\* (.+)$", re.MULTILINE
    )

    sector_matches = list(sector_pattern.finditer(text))
    for i, m in enumerate(sector_matches):
        sector_code = m.group(1).strip()
        sector_name = m.group(2).strip()

        # Get text between this sector and next (or end)
        start = m.end()
        end = sector_matches[i + 1].start() if i + 1 < len(sector_matches) else len(text)
        section_text = text[start:end]

        subsectors = []
        for sm in subsector_pattern.finditer(section_text):
            subsectors.append({
                "code": sm.group(1).strip(),
                "name": sm.group(2).strip(),
            })

        sectors.append({
            "sector_code": sector_code,
            "sector_name": sector_name,
            "subsector_count": len(subsectors),
            "subsectors": subsectors,
        })

    return {
        "source": "2022 NAICS Manual, U.S. Census Bureau",
        "total_sectors": len(sectors),
        "total_subsectors": sum(s["subsector_count"] for s in sectors),
        "sectors": sectors,
    }


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Parse NAICS
    naics = parse_naics_manual(NAICS_MANUAL)
    out_path = DATA_DIR / "naics-sectors.json"
    out_path.write_text(json.dumps(naics, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out_path}: {naics['total_sectors']} sectors, {naics['total_subsectors']} subsectors")

    # If --soc flag provided, parse SOC from agent-produced file
    if "--soc" in sys.argv:
        idx = sys.argv.index("--soc")
        if idx + 1 < len(sys.argv):
            soc_path = Path(sys.argv[idx + 1])
            if soc_path.exists():
                soc_data = json.loads(soc_path.read_text(encoding="utf-8"))
                soc_out = DATA_DIR / "soc-major-groups.json"
                soc_out.write_text(json.dumps(soc_data, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"Wrote {soc_out}: {len(soc_data.get('major_groups', []))} major groups")
            else:
                print(f"SOC file not found: {soc_path}")


if __name__ == "__main__":
    main()
