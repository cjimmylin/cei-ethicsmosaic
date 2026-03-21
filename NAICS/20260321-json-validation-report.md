# EthicsMosaic JSON Validation Report

**Date:** 2026-03-21
**Agent:** V3 (Verification)
**Scope:** All 25 JSON files in `EthicsMosaic/NAICS/data/`

---

## 1. JSON Parse Validation

**Result: 25/25 PASS**

All files parse cleanly with no malformed JSON.

| File | Size | Status |
|------|------|--------|
| `crosswalk-naics-soc.json` | 195.0 KB | PASS |
| `naics-all-ethics-codes.json` | 334.8 KB | PASS |
| `naics-sector-11-21-ethics-codes.json` | 15.9 KB | PASS |
| `naics-sector-22-23-ethics-codes.json` | 29.5 KB | PASS |
| `naics-sector-31-33-pt1-ethics-codes.json` | 19.3 KB | PASS |
| `naics-sector-31-33-pt2-ethics-codes.json` | 13.6 KB | PASS |
| `naics-sector-42-44-45-ethics-codes.json` | 44.7 KB | PASS |
| `naics-sector-48-49-51-ethics-codes.json` | 31.1 KB | PASS |
| `naics-sector-52-53-ethics-codes.json` | 38.3 KB | PASS |
| `naics-sector-54-55-56-ethics-codes.json` | 40.7 KB | PASS |
| `naics-sector-61-62-ethics-codes.json` | 41.4 KB | PASS |
| `naics-sector-71-72-81-92-ethics-codes.json` | 51.3 KB | PASS |
| `naics-sectors.json` | 12.7 KB | PASS |
| `soc-all-ethics-codes.json` | 429.0 KB | PASS |
| `soc-group-11-13-ethics-codes.json` | 46.5 KB | PASS |
| `soc-group-15-17-ethics-codes.json` | 32.5 KB | PASS |
| `soc-group-19-21-ethics-codes.json` | 53.3 KB | PASS |
| `soc-group-23-25-ethics-codes.json` | 42.8 KB | PASS |
| `soc-group-27-29-ethics-codes.json` | 46.8 KB | PASS |
| `soc-group-31-33-ethics-codes.json` | 46.7 KB | PASS |
| `soc-group-35-37-39-ethics-codes.json` | 35.7 KB | PASS |
| `soc-group-41-43-45-ethics-codes.json` | 41.4 KB | PASS |
| `soc-group-47-49-51-ethics-codes.json` | 59.8 KB | PASS |
| `soc-group-53-55-ethics-codes.json` | 36.7 KB | PASS |
| `soc-major-groups.json` | 10.5 KB | PASS |

---

## 2. Required Fields Check

**Result: ALL PASS** -- every entry across all files has all 5 required fields populated.

| Field | Status | Notes |
|-------|--------|-------|
| `organization` | PASS | Present in all 1,074 individual-file entries |
| `document_title` | PASS | Present in all entries; none shorter than 5 characters |
| `url` | PASS | Present in all entries; none empty; all start with `http://` or `https://` |
| `document_type` | PASS | Present in all entries |
| `geographic_scope` | PASS | Present in all entries |

No placeholder URLs (e.g., `example.com`, `placeholder`, `todo`) were found.

---

## 3. Duplicate Organization Audit

### 3a. Within-File Exact Duplicates (same org + same document in same file)

**54 duplicate entries total** (11 NAICS + 43 SOC)

These are the same organization/document pair appearing 2-3 times within a single file, likely because the entry is relevant to multiple subsectors or minor groups within the file.

**NAICS within-file duplicates (11 excess entries across 10 sector files):**
- `ETI / ETI Base Code` (2x in sector-31-33-pt1)
- `amfori / amfori BSCI Code of Conduct` (2x in sector-31-33-pt1)
- `SAI / SA8000 Standard` (2x in sector-31-33-pt1)
- `NSPE / NSPE Code of Ethics for Engineers` (2x in sector-22-23)
- `FIDIC / FIDIC Code of Ethics` (2x in sector-22-23)
- `Responsible Business Alliance (RBA) / RBA Code of Conduct` (2x in sector-42-44-45)
- And 5 others

**SOC within-file duplicates (43 excess entries across 10 group files):**
- Worst offender: `soc-group-47-49-51` with 14 within-file duplicates
- `soc-group-11-13` with 10 within-file duplicates
- Notable: `ATD Code of Ethics` appears 3x, `ASQ Code of Ethics` 3x, `ASME Code of Ethics` 3x, `SME Code of Ethics` 3x

### 3b. Cross-File Duplicates (same org + document across different sector/group files)

**NAICS: 18 org+document pairs appear in 2+ sector files** (expected -- organizations span sectors):
- `APA / Ethical Principles` in sector-54-55-56 and sector-61-62
- `APhA / Code of Ethics for Pharmacists` in sector-42-44-45 and sector-61-62
- `CFA Institute / Code of Ethics` in sector-52-53 and sector-54-55-56
- `ETI / ETI Base Code` in sector-31-33-pt1 and sector-42-44-45
- `FLA / FLA Workplace Code` in sector-31-33-pt1 and sector-42-44-45
- And 13 others

**SOC: 14 org+document pairs appear in 2+ group files** (expected -- roles span groups):
- `APA / Ethical Principles` in 3 group files (19-21, 27-29)
- `ASSP / Code of Professional Conduct` in 2 group files (19-21, 47-49-51)
- `ISM / Principles of Ethical Supply Management` in 3 group files (11-13, 41-43-45, 47-49-51)
- And 11 others

### 3c. Cross-Track Duplicates (NAICS vs SOC)

**157 organizations appear in both NAICS and SOC tracks** (independently computed).

The crosswalk file reports 163 shared organizations. The discrepancy of 6 is due to minor org name normalization differences between tracks (e.g., abbreviation-only in one track vs full name in the other).

### 3d. Near-Duplicate Organization Names

**15 groups of near-duplicate org names detected** (same entity, different string representations):

| Variant 1 | Variant 2 | Issue |
|-----------|-----------|-------|
| `AIAA` | `AIAA (American Institute of Aeronautics and Astronautics)` | Abbreviated vs full |
| `CFA Institute` | `CFA Institute (as applied to corporate treasury...)` | Context qualifier |
| `CompTIA` | `CompTIA (Computing Technology Industry Association)` | Abbreviated vs full |
| `FAO` | `FAO (Food and Agriculture Organization...)` | Abbreviated vs full |
| `ISACA` | `ISACA (Information Systems Audit and Control Association)` | Abbreviated vs full |
| `SAE International` | `SAE International (Society of Automotive Engineers)` | Short vs full |
| `SAG-AFTRA` | `SAG-AFTRA (Screen Actors Guild...)` | 4 variants with punctuation differences |
| `ASCM, formerly APICS` | `ASCM/APICS` | Different former-name notation |
| `AITP` | `AITP/CompTIA` | Different qualifier |
| `IESBA` | `IESBA/IFAC` | Different qualifier |
| `NALP` | `NALP, formerly PLANET` | Former-name notation |
| `SOA / American Academy of Actuaries` | `SOA / AAA` | Abbreviated component |
| `AICP / American Planning Association` | `AICP / APA` | Abbreviated component |
| `Specialty Food Association` | `Specialty Food Association (SFA)` | With/without abbreviation |
| `U.S. Department of Defense` | `U.S. Department of Defense (DoD)` | With/without abbreviation |

### 3e. Shared Abbreviations (different organizations, same acronym)

**46 abbreviations are shared across genuinely different organizations.** Most notable:

| Abbrev | Organizations |
|--------|---------------|
| ABA | American Bar Assn, American Bankers Assn, American Barber Assn, American Bus Assn |
| ACA | American Chiropractic Assn, American Counseling Assn, American Correctional Assn |
| AMA | American Medical Assn, American Marketing Assn, American Management Assn |
| ASA | 9 different orgs (Automotive Service, Subcontractors, Appraisers, Anesthesiologists, Staffing, Agronomy, Sociological, Statistical) |
| AGA | American Gas Assn, American Gaming Assn, Assn of Government Accountants |
| PMI | Plumbing Manufacturers Intl, Philip Morris Intl, Project Management Institute |

These are legitimate different organizations sharing common abbreviations -- not data errors.

---

## 4. Placeholder/Suspicious Data Check

| Check | Result |
|-------|--------|
| Placeholder URLs | PASS -- none found |
| Empty/very short titles | PASS -- none found |
| Suspicious org names | PASS -- none found |
| Non-HTTP URLs | PASS -- all valid HTTP/HTTPS |

### Data Quality Observations

**Geographic scope normalization issue (154 entries):**
- Values are inconsistently cased: `International` (121), `international` (110), `global` (44)
- Mixed compound values: `US/international` vs `US/International`
- Recommend normalizing to title case (`International`, `Global`)

**Document type normalization issue (3 entries):**
- `ethical_guidelines` (3 entries) vs `ethics_guidelines` (84 entries) -- should be consolidated

**Year published quality:**
- 200 of 1,074 entries (18.6%) have missing, empty, `unknown`, or `None` year values
- Breakdown: empty string (105), `unknown` (74), `None` (21)
- This is an expected limitation for many professional ethics codes that do not prominently date their documents

---

## 5. Statistics Verification

### NAICS Track

| Metric | Individual Files | Combined File (actual) | Combined File (metadata) | Match? |
|--------|-----------------|----------------------|-------------------------|--------|
| Raw entries | 563 | 563 | 559 | MISMATCH: metadata says 559, actual is 563 |
| Unique codes (org+doc) | 534 | 534 | 532 | CLOSE: off by 2 |
| Unique organizations | 492 | 492 | 491 | CLOSE: off by 1 |

The metadata `total_raw_entries` in `naics-all-ethics-codes.json` reports 559, but the actual entry count is 563 (4-entry discrepancy). The unique-code and unique-org counts are off by 1-2, likely from minor normalization differences in the assembly script.

### SOC Track

| Metric | Individual Files | Combined File (actual) | Combined File (metadata) | Match? |
|--------|-----------------|----------------------|-------------------------|--------|
| Raw entries | 511 | 511 | -- | N/A (no total_raw_entries field) |
| Unique codes (org+doc) | 453 | 453 | 511 | MISMATCH: metadata says 511, actual unique is 453 |
| Unique organizations | 421 | 421 | 421 | MATCH |

The SOC combined file metadata reports `total_unique_codes: 511`, but this appears to be the raw entry count, not deduplicated. The actual unique code count is 453 (58 are duplicates).

### Crosswalk

| Metric | Crosswalk File | Independently Computed | Match? |
|--------|---------------|----------------------|--------|
| Total unique orgs | 739 | 756 | OFF by 17 |
| Found in both | 163 | 157 | OFF by 6 |
| NAICS-only | 323 | 335 | OFF by 12 |
| SOC-only | 253 | 264 | OFF by 11 |

The crosswalk was likely assembled with slightly different org-name normalization than exact string matching. The internal arithmetic is consistent: 163 + 323 + 253 = 739.

---

## Summary of Findings

### Issues by Severity

**Critical (0):** None. All files parse, all required fields present.

**Moderate (3):**
1. **54 within-file exact duplicates** -- same org+document appearing 2-3x in a single file. SOC track has 43 (vs 11 for NAICS). File `soc-group-47-49-51` is the worst with 14 duplicates.
2. **NAICS metadata count mismatch** -- `total_raw_entries` reports 559 but actual count is 563 (off by 4).
3. **SOC metadata `total_unique_codes` is actually raw count** -- reports 511 but actual unique is 453.

**Minor (3):**
4. **Geographic scope inconsistency** -- 154 entries use lowercase `international` or `global` instead of title-case `International`.
5. **Document type inconsistency** -- 3 entries use `ethical_guidelines` vs 84 using `ethics_guidelines`.
6. **15 near-duplicate org names** -- same entity recorded with different string representations (abbreviated vs full).

**Informational (2):**
7. 18.6% of entries lack a published year (expected for undated ethics codes).
8. 46 shared abbreviations across different organizations (not errors, real-world ambiguity).

---

## Overall Data Quality Score

### Grade: B+

**Rationale:**
- **Structural integrity (A):** All 25 files parse, all required fields populated, no placeholders, no suspicious entries, no broken URLs at the format level.
- **Content completeness (B+):** 81.4% year coverage is solid given the domain. All entries have URLs, org names, and document types.
- **Deduplication (B):** 54 within-file duplicates (5.0% of 1,074 entries) is a moderate concern, especially in the SOC track. Cross-file duplicates are expected and handled via the crosswalk.
- **Normalization (B-):** Geographic scope casing and document type inconsistencies should be standardized. 15 near-duplicate org names need consolidation.
- **Metadata accuracy (B-):** Combined file metadata counts are off by small amounts (4 entries for NAICS; SOC conflates raw with unique). Crosswalk counts diverge by ~2% from independent calculation.

A round of deduplication within files, geographic-scope normalization, and metadata count correction would bring this to an A.
