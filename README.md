# 🌍 CarbonPass — Agentic AI for CBAM-Ready Exporters

**Built in Pakistan, for every exporter in the Global South facing the EU's carbon border tax.**

🔗 **Live demo:** _https://carboncompass.streamlit.app/_
🎥 **Demo video:** _add link here_
📄 **Product Requirements Document:** [PRD.md](PRD.md)

*HEC–NCEAC & PEC Generative & Agentic AI Training, Cohort 11 — Final Hackathon*

---

## The problem

Since 1 January 2026 the EU's **Carbon Border Adjustment Mechanism (CBAM)** is in its definitive phase. EU importers of steel, aluminium, cement, fertilisers, hydrogen and electricity must declare the embedded emissions of every 2026 import by 30 September 2027 and pay for them with CBAM certificates.

So EU buyers are asking their suppliers **now** for verifiable emissions data. Suppliers who can't provide it get **EU default values** applied, which raise costs and put contracts at risk. Most small and mid-sized exporters have no monitoring plan, no emissions data system, and can't afford consultants.

## What CarbonPass does

Upload your plant's existing documents (bills, production logs, purchase and meter registers, the buyer's request). In minutes, four AI agents give you:

| Output | |
|---|---|
| 📊 **Embedded emissions per product** | Direct, indirect and precursor emissions in tCO2 per tonne |
| ✅ **Readiness audit** | 20-item CBAM checklist rated Met / Partial / Missing, with evidence |
| 🎯 **Readiness score + action plan** | What to fix first, who owns it, by when |
| 🔁 **What-if** | How much cost exposure falls when actual supplier data replaces default values |
| 📧 **Draft reply to the EU buyer** | Product emissions, route, data basis and open issues |

## How it works

```
 Plant documents ──► 1. DATA EXTRACTOR ──► 2. EMISSIONS CALCULATOR ──► 3. GAP AUDITOR ──► 4. REPORTER & ADVISOR
                     LLM → structured       deterministic Python        LLM vs 20-item     LLM → action plan,
                     JSON with citations    tool (no LLM maths)         checklist          buyer email, what-if
                                                                                                   │
                                                                              Human review (plant manager approves)
```

| Agent | Job | Guardrail against hallucination |
|---|---|---|
| **Data Extractor** | Turns documents into structured plant data | Unknown values become `null`; every number cites its source |
| **Emissions Calculator** | Computes emissions, flags data problems, estimates cost exposure | Pure Python; the LLM never does arithmetic |
| **Gap Auditor** | Rates the plant against the checklist like a verifier | Must quote evidence or say "No evidence found"; cannot pass an item the calculator flagged |
| **Reporter & Advisor** | Summary, action plan, what-if message, buyer email | May only use numbers the calculator produced; everything marked DRAFT |

The readiness score is computed in code, not by the LLM. Agents run in a fixed sequence so results are reproducible.

## Demo: Margalla Steel Works (fictional)

A Sheikhupura mini-mill: an EAF melt shop makes billets, and a rolling mill makes rebar, also using 24,000 t of billets bought from a local induction-furnace mill. Its German buyer demands CBAM data by 31 October 2026.

| Result | Value |
|---|---|
| Rebar direct embedded emissions | **0.704 tCO2/t** |
| Readiness score | **38 / 100** (6 met, 4 partial, 10 missing) |
| Key flags | No supplier data for purchased billets · gas meter calibration overdue |
| Illustrative exposure, 15,000 t rebar to EU | **€792,000 → €454,500 (−43%)** with actual supplier data |

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

With no API key, the app runs in **demo mode** with fixed sample outputs. For live AI, set these (or add them to Streamlit Cloud → Secrets):

```toml
LLM_API_KEY  = "gsk_..."
LLM_BASE_URL = "https://api.groq.com/openai/v1"
LLM_MODEL    = "llama-3.3-70b-versatile"
```

Any OpenAI-compatible endpoint works (Groq, OpenAI, Gemini).

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit interface |
| `pipeline.py` | Runs the four agents in sequence; demo mode |
| `prompts.py` | System prompts for each agent |
| `cbam_calculator.py` | Deterministic emissions and cost-exposure tool |
| `cbam_checklist.json` | 20-item CBAM supplier-readiness checklist (paraphrased, editable) |
| `sample_installation_data.json` | Structured data for the demo plant |
| `sample_dossier_margalla_steel.md` | Demo plant's documents, with deliberate gaps and an answer key |
| `PRD.md` | Product Requirements Document |

## Tech stack

Python · Streamlit · Groq (Llama 3.3 70B) via OpenAI-compatible API · pandas · pypdf · python-docx · openpyxl · Streamlit Cloud

## Roadmap

Aluminium, cement and fertiliser routes · official EU communication template · Urdu interface · supplier data-collection portal · multi-plant dashboard · ISO 14064-1 corporate GHG inventory · verifier workspace

## Limitations

- All factors and cost figures are **illustrative**. Real CBAM reporting must follow the EU's official methodology, default values and benchmark-based free-allocation adjustments, which this prototype simplifies.
- For iron and steel, only direct emissions are costed; indirect emissions are reported.
- Outputs are drafts for expert review, not legal or compliance advice.

## License

MIT
