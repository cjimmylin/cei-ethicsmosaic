# EthicsMosaic — Project Configuration

**Mission:** Collect, analyze, and synthesize professional codes of ethics/conduct from diverse industries into a unified framework for AI alignment
**Parent Vault:** CEI Literature Vault
**Working Directory:** `EthicsMosaic/`

## Project Goals

1. **Collect** — Download and catalog professional codes of ethics and conduct from every major industry sector (healthcare, engineering, law, finance, journalism, education, etc.)
2. **Extract** — Parse each code into structured principles, obligations, and norms
3. **Map** — Identify cross-industry convergence (universal ethical principles) and divergence (domain-specific obligations)
4. **Synthesize** — Produce a combined professional code of conduct distilled from real-world practice
5. **Align** — Format the synthesized code as machine-readable alignment guidance for AI systems

## Directory Structure

```
EthicsMosaic/
  CLAUDE.md              # This file — project configuration
  README.md              # Project overview and methodology
  sources/               # Raw PDFs and documents of ethics codes
    healthcare/
    engineering/
    law/
    finance/
    journalism/
    education/
    technology/
    social-work/
    psychology/
    public-service/
    research/
    environment/
    ...
  extracts/              # Structured extracts from each code
  analysis/              # Cross-industry analysis and mapping
  synthesis/             # Combined/unified code of conduct
  PYTHON/                # Processing and analysis scripts
  data/                  # Structured data (JSON/YAML)
  STATISTICS/            # Reports with YYYYMMDD- prefix
  logs/                  # Processing logs with YYYYMMDD- prefix
```

## Critical Safety Rules

Inherited from parent vault:

### 1. NO FILE DELETIONS
**NEVER use `rm`, `unlink`, or any delete command.** Always `mv` to `../RECYCLE-BIN/`.

### 2. Report Immutability
**NEVER overwrite or regenerate existing reports.** Old reports are historical snapshots.
Always create NEW reports with NEW `YYYYMMDD-` date prefixes.

### 3. Source Provenance
Every downloaded code of ethics MUST be tracked with:
- Original URL
- Organization name
- Industry/sector classification
- Date published (or date accessed if undated)
- Document format (PDF, HTML, etc.)

## Naming Conventions

- Source documents: `sources/{sector}/{Organization-Name}-Code-of-Ethics.pdf`
- Extracts: `extracts/{Organization-Name}-extract.md`
- Reports/logs: `YYYYMMDD-descriptive-name.{md,json}`
- Data files: `data/{descriptive-name}.json`

## Industry Taxonomy (Initial Target Sectors)

| # | Sector | Example Organizations |
|---|--------|-----------------------|
| 1 | Healthcare & Medicine | AMA, WHO, ICN, WMA |
| 2 | Engineering | IEEE, NSPE, ASCE, ACM |
| 3 | Law & Legal | ABA, IBA, CCBE |
| 4 | Finance & Banking | CFA Institute, AICPA, IIF |
| 5 | Journalism & Media | SPJ, IFJ, BBC Editorial Guidelines |
| 6 | Education | NEA, UNESCO, NAEYC |
| 7 | Technology & Computing | ACM, IEEE-CS, BCS |
| 8 | Social Work | NASW, IFSW, BASW |
| 9 | Psychology & Counseling | APA, BPS, EFPA |
| 10 | Public Service & Government | ASPA, UN Ethics Office, OECD |
| 11 | Research & Academia | NAS, COPE, ICMJE |
| 12 | Environment & Sustainability | IEMA, NAEP |
| 13 | Architecture & Planning | AIA, RIBA, RTPI |
| 14 | Accounting & Auditing | IESBA, AICPA, ACCA |
| 15 | Real Estate & Property | NAR, RICS |
| 16 | Human Resources | SHRM, CIPD |
| 17 | Marketing & Advertising | AMA (Marketing), IAB, ASA |
| 18 | Pharmacy | FIP, APhA |
| 19 | Military & Defense | Uniform Code, NATO Ethics |
| 20 | Religious & Interfaith | Parliament of World Religions |

## Synthesis Methodology

The synthesis pipeline will:

1. **Principle Extraction** — For each code, identify discrete ethical principles/norms
2. **Semantic Clustering** — Group equivalent principles across industries using embeddings
3. **Universality Scoring** — Score each principle by how many industries endorse it
4. **Specificity Tagging** — Tag domain-specific principles with their industry context
5. **Hierarchy Construction** — Organize principles into a tiered framework:
   - Tier 1: Universal (present in 80%+ of industries)
   - Tier 2: Broadly shared (present in 40-79%)
   - Tier 3: Domain-specific (present in <40%, with sector tags)
6. **Conflict Resolution** — Where principles conflict across industries, document both positions and the contextual factors

## Key Utilities (to be created)

| Utility | Purpose |
|---------|---------|
| `PYTHON/download_codes.py` | Automated download of ethics codes from known URLs |
| `PYTHON/extract_principles.py` | Parse codes into structured principle lists |
| `PYTHON/cluster_principles.py` | Semantic clustering across industries |
| `PYTHON/score_universality.py` | Universality scoring pipeline |
| `PYTHON/generate_synthesis.py` | Produce the combined code of conduct |
| `PYTHON/validate_sources.py` | Validate source metadata completeness |
