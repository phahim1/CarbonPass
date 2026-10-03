# CarbonPass — Agentic AI for CBAM-Ready Exporters

**Hackathon:** HEC–NCEAC & PEC Generative & Agentic AI Training, Cohort 11 — Final Hackathon
**Team lead:** Engr. Fahimullah Khanzada, PE
**Deadline:** Sunday 4 October 2026, 11:59 PM PKT

## The problem

Since 1 January 2026 the EU's Carbon Border Adjustment Mechanism (CBAM) is in its definitive phase. EU importers of steel, aluminium, cement, fertilisers, hydrogen and electricity must declare the embedded emissions of 2026 imports by 30 September 2027 and pay for them with CBAM certificates.

EU buyers are now asking their suppliers in Pakistan and across the Global South for verifiable emissions data. Suppliers that can't provide it get EU default values applied, which raise costs and put contracts at risk. Most small and mid-sized exporters have no monitoring plan, no emissions data system, and can't afford consultants.

## The solution

CarbonPass is a multi-agent AI workflow. An exporter uploads its bills, production logs and existing documents, and receives:

1. Its specific embedded emissions per product, calculated deterministically
2. A gap analysis against a CBAM supplier-readiness checklist
3. A prioritised action plan to get verification-ready
4. A ready-to-send emissions communication for its EU buyer
5. A "what-if" showing how much cost exposure falls when actual data replaces default values

**Pitch line:** Built in Pakistan, for every exporter in the Global South facing CBAM.

## Architecture

```
  Exporter uploads: bills, production logs, purchase register, meter register, EU buyer email
                                        │
                                ┌───────▼───────┐
                                │ 1. INTAKE     │  parse PDF/DOCX/XLSX → chunks + vector DB
                                └───────┬───────┘
                                ┌───────▼───────┐
                                │ ORCHESTRATOR  │  plans the run, routes tasks
                                └─┬─────┬─────┬─┘
            ┌─────────────────────┘     │     └─────────────────────┐
   ┌────────▼─────────┐      ┌──────────▼─────────┐      ┌──────────▼─────────┐
   │ 2. DATA EXTRACTOR│      │ 3. EMISSIONS CALC  │      │ 4. GAP AUDITOR     │
   │ LLM → structured │ ───► │ calls Python tool  │      │ RAG vs checklist   │
   │ JSON + citations │      │ cbam_calculator.py │      │ Met/Partial/Missing│
   └──────────────────┘      └──────────┬─────────┘      └──────────┬─────────┘
                                        └─────────────┬─────────────┘
                                              ┌───────▼───────┐
                                              │ 5. REPORTER   │  action plan, buyer
                                              │ & ADVISOR     │  communication, what-if
                                              └───────┬───────┘
                                                      │
                                     Human review (plant manager approves)
```

| Agent | Job | Guardrail |
|---|---|---|
| Intake | Parse and index all uploads | Keep file name and page for every chunk |
| Data Extractor | Turn documents into `sample_installation_data.json` format | Every number cites its source document; unknowns marked `null` |
| Emissions Calculator | Call `calculate()` and `what_if_supplier_data()` | The LLM never does arithmetic |
| Gap Auditor | Rate each item in `cbam_checklist.json` | Must cite evidence or say "No evidence found" |
| Reporter & Advisor | Action plan, buyer email, cost what-if | Every output marked "DRAFT – requires review"; figures labelled illustrative |

## Files in this starter kit

| File | Purpose | Owner |
|---|---|---|
| `cbam_calculator.py` | Deterministic emissions + cost-exposure tool (tested) | Agent engineer |
| `sample_installation_data.json` | Structured data for the fictional demo plant | Lead |
| `cbam_checklist.json` | 20-item paraphrased CBAM readiness checklist | Lead |
| `sample_dossier_margalla_steel.md` | Fictional plant's documents with deliberate gaps + answer key | Lead |

Run the calculator:

```bash
python3 cbam_calculator.py sample_installation_data.json
```

## Demo story (3 minutes)

1. **The hook:** Show the German buyer's email: "Send your emissions data by 31 October or we use default values and review pricing."
2. **Upload:** Drop in Margalla Steel's documents.
3. **Agents work:** Show the orchestrator routing tasks live.
4. **Results:** Rebar comes out at 0.704 tCO2/t direct emissions, with 6 gaps found, including an overdue gas meter and missing supplier data.
5. **The wow moment:** What-if with real supplier data for the purchased billets: illustrative full-phase-in exposure on 15,000 t falls from **€792,000 to €454,500 (−43%)**.
6. **Output:** An action plan and a draft emissions communication ready to send to the buyer.

## Demo scope

- **In:** one fictional steel plant, two processes (EAF billets → rebar), 20 checklist items, the buyer email, one what-if.
- **Out (roadmap slide):** aluminium, cement and fertiliser routes; the official EU communication template format; Urdu interface; multi-plant dashboard; ISO 14064 corporate inventory; supplier data-collection portal.

## Tech stack

Use what the course taught. Default:
- Agents: crewAI or LangGraph
- LLM: Gemini or Groq free tier, with a backup key
- RAG: LlamaIndex or LangChain with Chroma/FAISS
- UI: Streamlit, deployed on Streamlit Cloud or Hugging Face Spaces

## Team roles

| Role | Owns |
|---|---|
| Lead (Fahim) | Domain logic, checklist, sample data, pitch, judge Q&A |
| Agent engineer | Orchestrator, agent prompts, tool calling to the calculator |
| RAG engineer | Intake, vector DB, evidence retrieval with citations |
| UI / report dev | Streamlit app, upload flow, results view, what-if slider, deployment |
| QA + pitch (optional) | Test against the answer key, slides, demo video |

## Timeline

| When | What | Done when |
|---|---|---|
| Sat 5–7 PM | Register, recruit, create repo, share this kit | Form submitted, 4+ members |
| Sat 7–8 PM | Kickoff call, assign owners, share API keys | Everyone has a task |
| Sat 8 PM–1 AM | Thin slice: upload → extractor → calculator → results in UI | One end-to-end run works |
| Sun 9 AM–2 PM | Gap auditor, reporter, what-if, buyer email | Full run on Margalla Steel |
| Sun 2–6 PM | Integration, deployment, test against answer key | Live URL works |
| **Sun 7 PM** | **Feature freeze** | — |
| Sun 7–10 PM | Bug fixes, demo video (backup), slides | Video + slides ready |
| Sun 10–11 PM | Submit via edit link | Submitted |

## Honest caveats for judges

- All factors and figures are **illustrative**. Real CBAM reporting uses the EU's official methodology, default values and benchmark-based free-allocation adjustments, which this prototype simplifies.
- For iron and steel, the prototype prices only direct emissions; indirect emissions are reported but not costed.
- Pakistan's direct CBAM exposure today is concentrated in a few sectors (mainly steel and aluminium). The same engine scales to exporters in India, Turkey, Egypt and beyond, and to ISO 14064 corporate GHG inventories that EU buyers increasingly request from all suppliers.
