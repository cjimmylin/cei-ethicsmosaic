# EthicsMosaic

**A cross-industry synthesis of professional codes of ethics for AI alignment**

## What is this?

EthicsMosaic is a systematic effort to collect, analyze, and synthesize professional codes of ethics and conduct from every major industry sector. The goal is to distill the accumulated ethical wisdom of human professions into a unified framework that can guide the alignment of AI systems.

Professions have spent decades — in some cases centuries — codifying ethical norms through lived experience, case law, regulatory feedback, and professional consensus. These codes represent humanity's best attempt at formalizing "how to behave well" in specific domains of practice. By mapping the convergence across these codes, we can identify principles that are genuinely universal to professional conduct, and distinguish them from domain-specific norms that apply only in particular contexts.

## Why professional ethics codes?

Most AI alignment work draws from moral philosophy (utilitarianism, deontology, virtue ethics) or from purpose-built AI ethics principles. EthicsMosaic takes a different approach: **grounding alignment in the empirical ethics of professional practice**.

Professional codes of ethics are:
- **Battle-tested** — refined through decades of real-world application and failure
- **Consensus-based** — represent agreement among practitioners, not a single philosopher's view
- **Actionable** — designed to guide concrete decisions, not abstract theorizing
- **Enforceable** — many have disciplinary mechanisms, showing what society actually penalizes
- **Domain-aware** — they understand that ethics is contextual, not one-size-fits-all

## Methodology

### Phase 1: Collection
Download and catalog professional codes of ethics from 20+ industry sectors covering healthcare, engineering, law, finance, journalism, education, technology, social work, psychology, public service, research, environment, and more.

### Phase 2: Extraction
Parse each code into structured principles — discrete ethical statements that can be compared across codes. Each principle is tagged with:
- The originating organization and sector
- Whether it is prescriptive (you must), prohibitive (you must not), or aspirational (you should strive to)
- The stakeholders it protects (clients, public, colleagues, profession, environment)

### Phase 3: Mapping
Use semantic clustering to identify equivalent principles across industries. For example, "patient confidentiality" (medicine), "attorney-client privilege" (law), and "source protection" (journalism) are all expressions of a common principle: **protect information entrusted to you by those you serve**.

### Phase 4: Synthesis
Produce a tiered combined code:
- **Tier 1 — Universal Principles**: Found in 80%+ of industries. These represent the floor of professional ethics.
- **Tier 2 — Broadly Shared Principles**: Found in 40-79% of industries. Context-dependent but widely endorsed.
- **Tier 3 — Domain-Specific Principles**: Found in <40% of industries. Essential in their domain but not generalizable.

### Phase 5: AI Alignment Format
Express the synthesized code in a machine-readable format suitable for:
- Constitutional AI (Anthropic-style principle lists)
- RLHF reward model training
- System prompt guidelines
- Evaluation benchmarks

## Target Industries

| Sector | Key Organizations | Priority |
|--------|-------------------|----------|
| Healthcare & Medicine | AMA, WHO, ICN, WMA | High |
| Engineering | IEEE, NSPE, ASCE | High |
| Law & Legal | ABA, IBA, CCBE | High |
| Finance & Banking | CFA Institute, AICPA | High |
| Journalism & Media | SPJ, IFJ, BBC | High |
| Education | NEA, UNESCO | High |
| Technology & Computing | ACM, IEEE-CS, BCS | High |
| Social Work | NASW, IFSW | Medium |
| Psychology & Counseling | APA, BPS | Medium |
| Public Service | ASPA, UN Ethics, OECD | Medium |
| Research & Academia | NAS, COPE | Medium |
| Environment | IEMA, NAEP | Medium |
| Architecture & Planning | AIA, RIBA | Lower |
| Accounting & Auditing | IESBA, AICPA, ACCA | Lower |
| Real Estate | NAR, RICS | Lower |
| Human Resources | SHRM, CIPD | Lower |
| Marketing & Advertising | AMA (Marketing), ASA | Lower |
| Pharmacy | FIP, APhA | Lower |
| Military & Defense | Uniform Code, NATO | Lower |
| Religious & Interfaith | Parliament of World Religions | Lower |

## Expected Outputs

1. **Source catalog** (`data/source-catalog.json`) — Metadata for every collected code
2. **Principle database** (`data/principles.json`) — All extracted principles with provenance
3. **Cluster map** (`data/cluster-map.json`) — Cross-industry principle clusters
4. **Universality scores** (`data/universality-scores.json`) — Per-principle coverage metrics
5. **Synthesized Code of Conduct** (`synthesis/combined-code-of-conduct.md`) — The final unified framework
6. **AI Alignment Spec** (`synthesis/alignment-principles.json`) — Machine-readable format for AI training

## Relation to CEI Literature Vault

EthicsMosaic is a subproject of the CEI (Computational Ethics Initiative) Literature Vault. It complements:
- **CEI-Lit-WS** — Academic papers on AI ethics (2,043 papers)
- **CEI-AI-Statements** (Tapestry) — AI governance policy documents (1,405 statements from governments and organizations)
- **EthicsMosaic** (this project) — Professional codes of ethics from industry practice

Together, these three collections cover the full spectrum: **theory** (academic papers), **policy** (governance statements), and **practice** (professional codes).

## License & Citation

This is an academic research project. Source documents are collected under fair use for research purposes. The synthesized outputs are original analytical work.

Citation: `EthicsMosaic (Lin, 2026). A cross-industry synthesis of professional codes of ethics for AI alignment.`
