# Product Requirements Document — CarbonPass

**Product:** CarbonPass: Agentic AI for CBAM-Ready Exporters
**Event:** HEC–NCEAC & PEC Generative & Agentic AI Training, Cohort 11 — Final Hackathon
**Version:** 1.0 · 4 October 2026

---

## 1. Problem

The EU's Carbon Border Adjustment Mechanism (CBAM) entered its definitive phase on 1 January 2026. EU importers of steel, aluminium, cement, fertilisers, hydrogen and electricity must declare the embedded emissions of every 2026 import by 30 September 2027 and pay for them with CBAM certificates.

EU importers are therefore asking their non-EU suppliers for verifiable emissions data now. When a supplier cannot provide it, EU default values are applied. These are typically higher than actual values, so they raise costs and put contracts at risk.

Most small and mid-sized exporters in Pakistan and across the Global South:
- have no monitoring plan or emissions data system,
- don't know which of their documents count as evidence,
- can't afford international carbon consultants.

## 2. Users

| User | Need |
|---|---|
| **Plant / export manager** (primary) | "My EU buyer wants emissions data by month-end. What do I send, and what's missing?" |
| **QA / environment officer** | A clear list of gaps and fixes before a verifier visits |
| **EU buyer** (receiver) | Product-level emissions data in a consistent, traceable format |

## 3. Solution

A multi-agent AI workflow. The exporter uploads its existing documents (bills, production logs, purchase and meter registers, the buyer's request) and receives, in minutes:

1. Specific embedded emissions per product (tCO2/t), calculated deterministically
2. A readiness audit against a 20-item CBAM supplier checklist, with evidence citations
3. A readiness score and prioritised action plan
4. A draft reply to the EU buyer with the emissions data
5. A what-if showing the cost saved when actual supplier data replaces default values

## 4. Agents

| Agent | Input | Output | Guardrail |
|---|---|---|---|
| **Data Extractor** | Uploaded documents | Structured installation JSON with citations | Missing values = `null`; never guesses |
| **Emissions Calculator** (tool) | Installation JSON | Emissions per product, data-quality flags, cost exposure | Python code; the LLM does no arithmetic |
| **Gap Auditor** | Documents + checklist + flags | Met / Partial / Missing per item, with evidence and fixes | Must quote evidence or state "No evidence found" |
| **Reporter & Advisor** | All outputs above | Summary, action plan, what-if message, buyer email | Uses only calculator numbers; marks output DRAFT |

Agents run in a fixed sequence (Extractor → Calculator → Auditor → Reporter) for reliability. The readiness score is computed in code, not by the LLM.

## 5. Core features (MVP)

| # | Feature | Priority |
|---|---|---|
| F1 | Upload documents (PDF, DOCX, XLSX, TXT, MD) or load demo plant | Must |
| F2 | Extract activity data with source citations | Must |
| F3 | Calculate direct, indirect and precursor emissions per product | Must |
| F4 | Flag data-quality problems (missing supplier data, overdue meter calibration) | Must |
| F5 | Readiness audit table and score | Must |
| F6 | Prioritised action plan | Must |
| F7 | What-if: actual supplier data vs EU default values | Must |
| F8 | Draft email reply to EU buyer | Should |
| F9 | Download full report | Should |

## 6. Out of scope (roadmap)

- Aluminium, cement, fertiliser and hydrogen production routes
- Official EU communication template and registry integration
- Urdu interface
- Multi-plant dashboard and supplier data-collection portal
- ISO 14064-1 corporate GHG inventory
- Verifier collaboration workspace

## 7. Tech stack

| Layer | Choice |
|---|---|
| LLM | Groq (Llama 3.3 70B) or Gemini, via OpenAI-compatible API |
| Agents | Python pipeline (crewAI-compatible prompts) |
| Calculation | Deterministic Python tool |
| UI | Streamlit |
| Deployment | GitHub → Streamlit Cloud |

## 8. Demo scenario

**Margalla Steel Works (fictional)**, Sheikhupura: an EAF melt shop producing billets, and a rolling mill producing rebar that also uses 24,000 t of purchased billets. Its German buyer demands emissions data by 31 October 2026.

Expected results:
- Rebar direct embedded emissions: **0.704 tCO2/t**
- Readiness score: **38/100**, with 10 items missing
- Key flags: no supplier data for purchased billets; gas meter calibration overdue
- What-if: illustrative full-phase-in exposure on 15,000 t rebar falls from **€792,000 to €454,500 (−43%)** with actual supplier data

## 9. Success metrics

| Metric | Target |
|---|---|
| Time from upload to report | < 2 minutes |
| Extraction accuracy on demo plant | All numbers match source documents |
| Audit agreement with expert answer key | All 6 seeded gaps found |
| Hallucinated numbers in report | Zero |

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| LLM invents numbers | Extractor returns `null` for unknowns; calculator in code; reporter limited to given numbers |
| Regulatory detail changes | Checklist and factors held in editable JSON, not hard-coded |
| Users treat output as legal advice | All outputs marked DRAFT and illustrative; human review step |
| API limits during demo | Backup key, cached demo run, recorded video |

## 11. Impact

- **Pakistan:** helps steel and other CBAM-sector exporters keep EU contracts and avoid default-value penalties.
- **Global South:** the same engine serves exporters in any country facing CBAM, because the EU rules are the same for all.
- **Climate:** measured emissions create a baseline for real reductions, not just compliance.

> All figures are illustrative. Real CBAM reporting must follow the EU's official methodology, default values and free-allocation adjustments.
