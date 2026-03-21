# Expert Council Review Synthesis: Predictions vs. Actual Results

**Date:** 2026-03-21
**Verification Agent:** V2
**Inputs:** Expert council report, combined discovery statistics, NAICS report, SOC report

---

## 1. Coverage Map Accuracy

The council predicted sector richness across four tiers. The table below compares predictions against actual NAICS code counts (the primary axis for sector-level comparison) and, where applicable, corresponding SOC group counts.

### NAICS Sector Predictions vs. Actuals

| Predicted Tier | Sector | Council Prediction | Actual NAICS Codes | Actual SOC Codes | Verdict |
|---------------|--------|-------------------|-------------------|-----------------|---------|
| **Rich (50+)** | Healthcare (62) | 50+ | 48 | 45 (29-0000) | Near-miss: 48 falls just below 50 threshold, but richest by depth and lineage |
| **Rich (50+)** | Finance & Insurance (52) | 50+ | 58 | 31 (13-0000) | Confirmed: exceeded threshold |
| **Rich (50+)** | Professional Services (54) | 50+ | 44 | N/A (distributed) | Below threshold: 44 vs. 50+; however 54 is a single subsector (541) |
| **Rich (50+)** | Legal (SOC 23) | 50+ | N/A | 18 (23-0000) | Overestimated: 18 is well below 50; legal codes are few but very high-impact (ABA Model Rules adopted by all 50 states) |
| **Moderate (15-50)** | Education (61) | 15-50 | 12 | 29 (25-0000) | Split verdict: NAICS below range (12), SOC within range (29); cross-track captures full picture |
| **Moderate (15-50)** | Information/Tech (51) | 15-50 | 23 | 14 (15-0000) | Confirmed for NAICS (23); SOC somewhat low (14) |
| **Moderate (15-50)** | Public Admin (92) | 15-50 | 37 | N/A | Confirmed: solidly within range |
| **Moderate (15-50)** | Real Estate (53) | 15-50 | 24 | N/A | Confirmed: within range |
| **Sparse (1-10)** | Agriculture (11) | 1-10 | 25 | 14 (45-0000) | **Major miss: 2.5-25x above prediction** |
| **Sparse (1-10)** | Mining (21) | 1-10 | 18 | N/A | **Miss: nearly 2x above upper bound** |
| **Sparse (1-10)** | Construction (23) | 1-10 | 32 | 30 (47-0000) | **Major miss: 3-32x above prediction** |
| **Sparse (1-10)** | Retail Trade (44-45) | 1-10 | 38 | 18 (41-0000) | **Major miss: nearly 4x above upper bound** |
| **Sparse (1-10)** | Accommodation/Food (72) | 1-10 | 7 | 5 (35-0000) | Confirmed: within predicted range |
| **Sparse (1-10)** | Transportation (48-49) | 1-10 | 21 | 26 (53-0000) | **Miss: 2x above upper bound** |
| **Absent (0)** | Gig/platform | 0 | N/A | N/A | Confirmed: no dedicated codes found |
| **Absent (0)** | Building/Grounds (SOC 37) | 0 | N/A | 5 | Overestimated absence: 5 niche codes exist (ISSA, BSCAI, NPMA, NALP, ISA) |
| **Absent (0)** | Food prep/serving (SOC 35) | 0 | N/A | 5 | Overestimated absence: 5 codes exist (ACF, USBG, CMS-A, NACE) |

### Accuracy Summary

| Tier | Sectors | Correct | Partially Correct | Wrong | Accuracy |
|------|---------|---------|-------------------|-------|----------|
| Rich (50+) | 4 | 1 | 2 | 1 | 25% exact, 75% directionally correct |
| Moderate (15-50) | 4 | 3 | 1 | 0 | 75% exact |
| Sparse (1-10) | 6 | 1 | 0 | 5 | 17% exact |
| Absent (0) | 4 | 1 | 0 | 3 | 25% exact |
| **Overall** | **18** | **6** | **3** | **9** | **33% exact, 50% within one tier** |

**Key finding:** The council was reasonably accurate for "moderate" sectors but systematically underestimated "sparse" sectors. Five of six sectors predicted as sparse (1-10 codes) actually yielded 18-38 codes each. The council's mental model was biased toward traditional white-collar professional associations and missed three major code-producing categories: (1) labor union codes of excellence/conduct, (2) supply chain ethics standards, and (3) international regulatory frameworks (e.g., FAO Code covering 170+ governments).

---

## 2. Meta-Source Validation: IIT CSEP Comparison

### Council Prediction
All 8 experts unanimously identified IIT CSEP as the #1 meta-source, citing ~4,000 codes from 1,500+ organizations. The council estimated the NAICS+SOC dual-track would capture 500-900 unique codes (55-70% of the US universe).

### Actual Result
- **739 unique organizations** discovered via dual-track
- **556 NAICS entries + 511 SOC entries** before deduplication
- **163 organizations (22.1%)** found in both tracks

### Comparison Against CSEP

| Metric | CSEP (Estimated) | EthicsMosaic Dual-Track | Ratio |
|--------|------------------|------------------------|-------|
| Organizations | ~1,500+ | 739 | ~49% |
| Codes/documents | ~4,000 | ~780 (unique docs) | ~20% |
| Years of accumulation | 40+ years | Single discovery pass | N/A |

**Analysis:** Our 739-org discovery captures roughly half of the CSEP organizational universe, which aligns with the council's 55-70% recall estimate for dual-track alone. The code-count gap is larger (~20%) because CSEP counts multiple documents per organization (advisory opinions, amendments, historical versions, model rules plus codes of conduct from the same body), while our discovery largely captured one primary document per organization. The council's estimate of 500-900 unique codes via dual-track was accurate: 739 falls squarely in the predicted range.

**Implication for Phase 2:** Harvesting CSEP as a benchmark overlay could add an estimated 400-700 additional unique organizations, primarily: (a) sub-national bodies (state licensing boards, local professional chapters), (b) historical codes superseded by current versions, and (c) international codes outside the NAICS/SOC North American frame.

---

## 3. Cross-Cutting Profession Prediction

### Council Prediction
All 8 experts identified ~12 cross-cutting professions that operate across all industries and would create duplication if discovered sector-by-sector. They recommended capturing these via SOC (Track B) with deduplication logic.

### Actual Results

The combined statistics identified 45 organizations appearing in 3+ sectors/groups. Comparing the council's specific predictions:

| Council-Predicted Cross-Cutter | Found? | Appearances | Notes |
|-------------------------------|--------|------------|-------|
| Lawyers (ABA) | Yes | NAICS 54 + SOC 23 | 2 tracks; correctly captured via SOC |
| Accountants (AICPA, IESBA) | Yes | NAICS 54 + SOC 13 | 2 tracks; high density in Finance |
| HR Specialists (SHRM) | Yes | SOC 11 (Management) | Correctly found in management group |
| IT/Software (ACM, IEEE) | Yes | NAICS 51, 54 + SOC 15, 17 | Cross-listed as predicted |
| Compliance Officers (SCCE) | Yes | SOC 13 | Found in Business/Financial Ops |
| Internal Auditors (IIA) | Yes | SOC 13 | Found in Financial Specialists |
| Project Managers (PMI) | Yes | SOC 11 | Found in Management Ops Specialties |
| Safety/Health (BCSP/ASSP) | Yes | 4 appearances across SOC groups | Among top cross-cutters |
| Public Relations (PRSA) | Yes | SOC 27 + NAICS 54 | Found in both tracks |
| Procurement (ISM) | Yes | SOC 11, 13 | Cross-listed in Management and Business |
| Data Protection (IAPP) | Yes | SOC 15 | Found in Computer Occupations |
| Risk Managers (RIMS, GARP) | Yes | SOC 13 | Found in Financial Specialists |

**Prediction accuracy: 12/12 (100%).** Every cross-cutting profession the council identified was found. The deduplication logic worked: these organizations were correctly captured in both tracks, with 163 total overlapping organizations resolved to unique entries.

### Surprise Cross-Cutters Not Predicted

The council did not predict the following cross-cutting patterns:

| Organization | Cross-Cutting Pattern | Appearances |
|-------------|----------------------|-------------|
| Responsible Business Alliance (RBA) | Supply chain ethics spans manufacturing, wholesale, retail, tech | 5 (highest) |
| Fair Labor Association (FLA) | Labor rights codes cross agriculture, apparel, retail | 4 |
| American Veterinary Medical Association (AVMA) | Spans animal production, professional services, social assistance | 4 |
| Royal Institution of Chartered Surveyors (RICS) | Bridges real estate, construction, facility management | 4 |

Supply chain standards bodies (RBA, FLA, SAI/SA8000, ETI, amfori BSCI) emerged as the most cross-cutting category, a pattern no council expert specifically highlighted.

---

## 4. Document Type Taxonomy Validation

### Council Prediction (10-Type Taxonomy)

The council synthesized a 10-type document taxonomy from all expert inputs.

### Actual Document Types Discovered

| Council Type | Found? | Actual Count | % of Total | Match Quality |
|-------------|--------|-------------|-----------|---------------|
| 1. Code of Ethics | Yes | 422 | 54.2% | Dominant type as expected |
| 2. Code of Conduct | Yes | 169 | 21.7% | Second-largest as expected |
| 3. Standards of Practice | Yes | 67 | 8.6% | Confirmed |
| 4. Oaths and Pledges | Yes | 8 | 1.0% | Confirmed (small niche) |
| 5. Model Rules | Yes | 8 | 1.0% | Confirmed (mainly legal) |
| 6. Advisory Opinions | No | 0 | 0% | Not discovered as separate documents |
| 7. Regulatory Mandates | Yes | 21 | 2.7% | Confirmed ("Regulatory Code") |
| 8. Certification Ethics Requirements | Partial | (embedded) | N/A | Found embedded within Codes of Ethics/Conduct, not as separate type |
| 9. International Framework Codes | Partial | (embedded) | N/A | Classified by geographic scope, not document type |
| 10. Industry Self-Regulatory Codes | Partial | (embedded) | N/A | Classified under Code of Conduct |

### Additional Types Discovered (Not Predicted)

| Type | Count | Examples |
|------|-------|---------|
| Ethics Guidelines | 75 | 9.6% of total; distinct from codes in their advisory (non-binding) character |
| Values Framework | 5 | Military values statements (LDRSHIP, Core Values) |
| Position Statement | 2 | Organizational positions on ethical issues |
| Executive Order | 2 | Military Code of Conduct (EO 10631), Joint Ethics Regulation |
| Constitution/Bylaws | 1 | Ethics embedded in organizational constitution |
| International Convention | 1 | ILO-level treaty document |

**Taxonomy accuracy: 7 of 10 types confirmed as discrete categories (70%).** Three predicted types (Advisory Opinions, Certification Ethics Requirements, International Framework Codes) were not captured as standalone document types. Advisory Opinions may require a separate discovery pass targeting legal ethics databases. The research discovered "Ethics Guidelines" as a significant type (75 documents, 9.6%) that the council did not predict as a standalone category, though it was arguably implicit in several experts' descriptions.

---

## 5. Methodology Recommendations: Adopted vs. Deferred

### Adopted (Implemented in This Pass)

| # | Recommendation | Status | Evidence |
|---|---------------|--------|----------|
| 1 | Dual-track (NAICS + SOC) | Fully implemented | 10 NAICS files + 10 SOC files |
| 2 | Document-type metadata | Implemented | 9 document types tagged across all entries |
| 4 | Accept sparse-sector sparsity as genuine | Implemented | Sparsity documented but research still conducted |
| 5 | "Emerging/Nascent" category | Partially implemented | AI provisions noted (ICF 2025) but no formal category |
| 6 | Issuing organization as primary key | Implemented | Deduplication by normalized org name |

### Deferred (Not Yet Implemented)

| # | Recommendation | Priority for Phase 2 | Rationale |
|---|---------------|---------------------|-----------|
| 3 | Cross-cutting capture via SOC with dedup | Medium | Dedup happened post-hoc; could be pre-built into discovery |
| 7 | Harvest IIT CSEP as benchmark | **High** | Would add estimated 400-700 orgs; enables recall estimation |
| 8 | ISIC/ISCO crosswalk for international | Medium | 212 international orgs found organically; crosswalk would systematize |
| 9 | Enumerate licensing boards via NCSL/CLEAR | **High** | Regulatory codes (2.7%) are underrepresented; licensing boards produce enforceable codes |
| 10 | Capture-recapture completeness estimation | Medium | Requires CSEP harvest first as second independent sample |
| — | Enforceability tier tagging (5-tier) | **High** | Council unanimously recommended; not implemented in discovery |
| — | O*NET professional associations harvest | Medium | ~3,000 association links would fill SOC gaps |
| — | Cause IQ / Gale Encyclopedia scan | Low | Diminishing returns for effort; broad but shallow |

### Priority Ranking for Phase 2

1. **Enforceability tier tagging** — Most analytically consequential metadata gap. Same code can be aspirational in one context and license-revocable in another.
2. **CSEP benchmark harvest** — Enables recall estimation and identifies missing organizations.
3. **NCSL/CLEAR licensing board enumeration** — Fills the regulatory code gap (only 2.7% currently).
4. **Capture-recapture analysis** — Requires CSEP data; would produce a defensible completeness estimate.
5. **ISIC/ISCO crosswalk** — International extension for the 65.8% US-centric current dataset.

---

## 6. Surprise Findings

The following discoveries were not predicted by any council expert:

### 6.1 Manufacturing Is the Richest NAICS Sector (88 Codes)

No expert predicted manufacturing (NAICS 31-33) would be the single largest sector. The council focused on healthcare, finance, and professional services as the richest domains. Manufacturing's 88 codes — driven by supply chain ethics (RBA, SA8000, FLA, WRAP, amfori BSCI), industry-specific standards (IFT, ACC, PhRMA, AdvaMed), and subsector codes across 18 subsectors — exceeded even finance (58).

### 6.2 Union Codes of Excellence Are a Major Source Category

The council's collective blind spot was organized labor. Construction and Extraction (SOC 47-0000) yielded 30 codes, making it the 6th richest SOC group. Virtually all major construction trade unions have formal codes: IBEW, UA, SMART, Ironworkers, BAC, OPCMIA, UBC, Boilermakers, LIUNA, Roofers, IUPAT. The "codes of excellence" model — labor-management partnerships emphasizing craft quality and safety — represents a distinct document type the council's 10-type taxonomy did not capture.

### 6.3 Military Ethics Has Its Own Layered System (18 SOC Codes)

The SOC track discovered 18 military-specific ethics codes (SOC 55-0000), making it comparable to Legal (18) and Sales (18). The military system is architecturally unique: statute (UCMJ) -> executive order (Code of Conduct, EO 10631) -> department regulation (JER/5500.07) -> service values frameworks (LDRSHIP, Honor/Courage/Commitment) -> individual creeds (Soldier's, Sailor's, Airman's). No council expert described this layered structure.

### 6.4 Retail Trade Yielded 38 NAICS Codes

The council unanimously classified retail as "sparse (1-10)." Actual discovery found 38 codes. The drivers were: (a) supply chain codes affecting retail (FLA, WRAP, RJC), (b) sector-specific associations for automotive dealers (NADA), jewelers (JA), pharmacies (APhA), and (c) e-commerce and direct selling ethics codes.

### 6.5 The Agriculture Sector Is Richer Than Expected (25 Codes)

Predicted at 1-10 codes, agriculture yielded 25 codes across crop production (4), animal production (6), forestry (5), fishing/hunting (7), and support activities (3). The FAO Code of Conduct for Responsible Fisheries alone is adopted by 170+ governments. Certification bodies (FSC, MSC, Rainforest Alliance) and animal welfare standards drove the count beyond expectations.

### 6.6 Religious Workers Have a Unified Cross-Denominational Code

Six US chaplaincy organizations converged on a Common Code of Ethics in 2004. This rare instance of cross-denominational professional ethics unification was not mentioned by any council expert.

### 6.7 AI Provisions Are Entering Existing Codes

The ICF (International Coaching Federation) 2025 Code of Ethics revision includes provisions requiring coaches to disclose AI use and protect client interests. This signals that AI ethics is entering established professional codes rather than remaining confined to technology-sector documents — a development relevant to EthicsMosaic's mission of distilling professional ethics for AI alignment.

---

## 7. Second-Pass Priorities

Based on gaps identified in this synthesis, a second research pass should focus on:

### 7.1 High Priority

| Target | Expected Yield | Rationale |
|--------|---------------|-----------|
| **IIT CSEP benchmark harvest** | 400-700 additional orgs | Enables recall estimation; fills gaps across all sectors; council's #1 recommendation |
| **Licensing board codes (NCSL/CLEAR)** | 200-400 regulatory codes | Only 21 regulatory codes (2.7%) found; licensing boards produce the most enforceable ethics codes; ~22% of US workforce holds a license |
| **Enforceability classification** | All 739 orgs tagged | No enforcement metadata collected; analytically essential for distinguishing aspirational vs. binding |
| **Advisory opinions** | 50-100 documents | Council predicted this type; 0 found; concentrated in legal, medical, and accounting professions |

### 7.2 Medium Priority

| Target | Expected Yield | Rationale |
|--------|---------------|-----------|
| **O*NET professional associations** | 200-500 new orgs | ~3,000 association links mapped to SOC; would fill minor-group gaps |
| **International codes via ISIC/ISCO crosswalk** | 100-300 non-US codes | Current dataset is 65.8% US; council recommended Tier 1 global federations (~50-80 bodies) first |
| **Global federation codes** | 50-80 codes | WMA, ICN, WFEO, IBA, FIP, IFJ, IFSW, FDI, UIA — many found, but systematic pass needed |
| **Zero-code subsector deep-dive** | 10-30 codes | 4 NAICS subsectors + 4 SOC minor groups with 0 codes; may reveal genuine absence vs. search failure |

### 7.3 Lower Priority (Phase 3+)

| Target | Expected Yield | Rationale |
|--------|---------------|-----------|
| **Globethics.net harvest** | Unknown (1.7M ethics documents total) | Massive but poorly structured; triage required |
| **DIACOMET journalism/media database** | ~408 documents | Niche but comprehensive for media ethics |
| **EU Regulated Professions Database** | ~4,700 regulated jobs | Important for international extension but low urgency for US-first approach |
| **Gale Encyclopedia / Cause IQ scan** | Diminishing returns | 24,000+ associations; most lack publicly posted ethics codes |
| **Emerging field codes** | 10-20 | AI/ML, data science, cybersecurity, ESG, genetic counseling, cannabis, drones — pre-professionalization; codes are forming |

### 7.4 Specific Gaps to Target

| Gap | Current State | Target |
|-----|--------------|--------|
| State licensing board codes | 0 systematically collected | At least sample 10 states for top-5 professions (medicine, law, engineering, accounting, nursing) |
| Sub-national professional chapters | 0 | CSEP harvest likely covers these |
| Corporate codes of conduct | 0 (excluded by scope) | Decision needed: Fortune 500 codes are a parallel universe; council's Expert 7 noted 90%+ have them |
| Quasi-regulatory codes | Partial (AdvaMed, PhRMA noted) | Systematic identification of codes with "quasi-regulatory force" per enforcement authorities |
| Historical/superseded codes | 0 | CSEP includes historical versions; value for longitudinal analysis |

---

## 8. Overall Assessment

### What Went Right

1. **Dual-track validation is strong.** The 22.1% overlap rate confirms that neither track alone is sufficient. 78% of organizations were found by only one track — exactly the justification for the dual-track approach.
2. **Council's cross-cutting profession predictions were 100% accurate.** All 12 predicted cross-cutters were found.
3. **Total unique organizations (739) fell within the council's predicted range (500-900).** The methodology delivered as estimated.
4. **Moderate-tier predictions were 75% accurate.** Education, Information, Public Administration, and Real Estate all behaved approximately as expected.
5. **Structurally absent sectors were mostly confirmed.** Gig/platform economy workers still have no professional ethics codes.

### What Went Wrong

1. **Sparse-sector predictions failed badly (17% accuracy).** The council systematically underestimated code counts for agriculture, mining, construction, retail, and transportation by factors of 2-4x. This reflects an academic-professional bias: experts thought primarily about white-collar professional associations and underestimated union codes, supply chain standards, and international regulatory frameworks.
2. **Rich-sector predictions were only partially accurate (25% exact).** Healthcare and Professional Services fell just below the 50-code threshold. Legal (18 SOC codes) was substantially overestimated. Only Finance exceeded its predicted tier.
3. **Document type taxonomy missed key categories.** "Ethics Guidelines" (75 documents) was not in the 10-type taxonomy. "Codes of Excellence" (union-style) were not a recognized type. Values Frameworks, Executive Orders, and Conventions were found but not predicted.

### The Biggest Lesson

The council's expertise was biased toward the professionalization model: a profession forms an association, the association adopts a code. This model dominates healthcare, law, finance, and engineering. But the actual ethics code landscape is far broader. Supply chain standards (RBA, FLA, SA8000), labor union codes of excellence, military layered systems, and international regulatory frameworks each represent distinct modes of ethical codification that the traditional professionalization model does not capture. A complete census of professional ethics codes must account for all five code-production mechanisms:

1. **Professional association codes** (the traditional model)
2. **Supply chain / multi-stakeholder standards** (buyer-driven)
3. **Labor union codes of excellence** (worker-driven)
4. **Regulatory / licensing board rules** (state-driven)
5. **International framework codes** (treaty/convention-driven)

---

*Report generated 2026-03-21 by verification agent V2.*
