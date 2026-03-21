# Verification Report: EthicsMosaic NAICS + SOC Dual-Track Discovery

**Date:** 2026-03-21
**Verification Agents:** V1 (URL spot-check), V2 (Council review), V3 (JSON validation)

---

## V1: URL Spot-Check Results

- **25 URLs checked** across 5 strata (high/medium/low coverage, international, SOC-only)
- **Resolution rate:** 64% raw (16/25), **~88% adjusted** (excluding bot-blocked sites)
- **Bot-blocked (work in browser):** 5 URLs (ACM, ABA, IEEE, AIGA, SAG-AFTRA)
- **Genuinely broken:** 3 URLs
  - CFA Institute — 404, URL path changed during site redesign
  - BIS — 404, website restructured
  - Data Science Association — TLS certificate invalid, domain may be defunct
- **Best stratum:** Low-coverage sectors (Agriculture/Mining/Construction) — 5/5 resolve

## V2: Council Prediction Accuracy

- **Coverage map accuracy:** 33% exact tier match, 50% within one tier
- **Systematic bias:** Council underestimated "sparse" sectors
  - Agriculture: 25 actual vs 3-10 predicted
  - Construction: 32 actual vs 1-10 predicted
  - Retail: 38 actual vs 1-5 predicted
- **Cross-cutting professions:** 100% prediction accuracy (all 12 predicted were found)
- **CSEP comparison:** 739 orgs ≈ 49% of CSEP's ~1,500 organizations
- **Biggest surprise:** Manufacturing richest NAICS sector (88 codes), union codes of excellence as major category
- **Document type match:** 7/10 predicted types confirmed (70%)

### Phase 2 Priorities (from council review)
1. Enforceability tier tagging for all codes
2. IIT CSEP benchmark harvest (~4,000 codes)
3. NCSL/CLEAR licensing board enumeration
4. Capture-recapture completeness analysis
5. ISIC/ISCO international crosswalk

## V3: JSON Validation & Data Quality

- **Parse validation:** 25/25 files pass cleanly
- **Required fields:** All present in every entry (1,074 entries)
- **Within-file duplicates:** 54 (43 in SOC files, 11 in NAICS files)
- **Cross-track duplicates:** 157 organizations appear in both tracks
- **Near-duplicate names:** 15 groups needing normalization
- **Normalization issues:** 154 entries with inconsistent geographic scope casing; 3 entries with variant document_type
- **Statistics mismatches:** Minor discrepancies (4-17 entries) between metadata counts and actual counts
- **Overall data quality grade:** **B+** — structurally sound, no critical issues, needs dedup/normalization pass

## Combined Verification Summary

| Metric | Result |
|--------|--------|
| JSON integrity | 25/25 files valid |
| Required fields completeness | 100% |
| URL resolution (adjusted) | ~88% |
| Genuinely broken URLs | 3/25 (12%) |
| Within-file duplicates | 54 (~5% of entries) |
| Council prediction accuracy | 33-50% (systematically conservative) |
| Data quality grade | **B+** |
| Recommended cleanup effort | Low (normalization + dedup pass) |
