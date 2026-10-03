"""
CarbonPass pipeline: Extractor -> Calculator -> Auditor -> Reporter.

Run with no API key to use MOCK mode (deterministic demo outputs), so the UI
and integration can be built before the LLM is wired up:

    python3 pipeline.py                      # mock mode
    LLM_API_KEY=... python3 pipeline.py      # real LLM (OpenAI-compatible endpoint)

Env vars for real mode:
    LLM_API_KEY   your key (Groq, OpenAI, or Gemini's OpenAI-compatible endpoint)
    LLM_BASE_URL  e.g. https://api.groq.com/openai/v1   (default: OpenAI)
    LLM_MODEL     e.g. llama-3.3-70b-versatile
"""

import json
import os
import re

import cbam_calculator as calc
import prompts as P

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- LLM layer
def make_llm():
    key = os.environ.get("LLM_API_KEY")
    if not key:
        return mock_llm, "mock"
    from openai import OpenAI  # pip install openai

    client = OpenAI(api_key=key, base_url=os.environ.get("LLM_BASE_URL"))
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini")

    def real_llm(system, user):
        import time
        last = None
        for attempt in range(4):
            try:
                r = client.chat.completions.create(
                    model=model,
                    temperature=0,
                    response_format={"type": "json_object"},
                    messages=[{"role": "system", "content": system},
                              {"role": "user", "content": user}],
                )
                return r.choices[0].message.content
            except Exception as e:  # rate limit or transient error: wait and retry
                last = e
                msg = str(e).lower()
                if "rate" in msg or "429" in msg or "timeout" in msg or "503" in msg:
                    time.sleep(15 * (attempt + 1))
                    continue
                raise
        raise last

    return real_llm, model


def parse_json(text):
    """Tolerate code fences or stray prose around the JSON."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    start = min([i for i in (text.find("{"), text.find("[")) if i != -1], default=0)
    return json.loads(text[start:])


# ---------------------------------------------------------------- mock mode
def mock_llm(system, user):
    if system == P.EXTRACTOR_SYSTEM:
        with open(os.path.join(HERE, "sample_installation_data.json")) as f:
            d = json.load(f)
        d["_citations"] = [{"field": "processes[1].fuels[0].quantity", "value": 105000,
                            "source": "Document 4, table row 'Natural gas'"}]
        d["_missing"] = ["Supplier B embedded emissions", "Carbon content lab reports"]
        return json.dumps(d)

    if system == P.AUDITOR_SYSTEM:
        missing = {"ME-01", "PR-02", "MP-01", "BD-01", "EF-01", "VR-01", "QA-01",
                   "QA-02", "ME-02", "CM-01"}
        partial = {"ID-01", "AD-02", "AD-03", "EF-02"}
        items = json.loads(user.split("CHECKLIST:")[1].split("CALCULATOR FLAGS:")[0])["items"]
        out = []
        for it in items:
            r = "Missing" if it["id"] in missing else "Partial" if it["id"] in partial else "Met"
            out.append({"id": it["id"], "area": it["area"], "rating": r,
                        "severity": it["severity"],
                        "evidence": "No evidence found" if r == "Missing"
                        else 'Document 4: "summary table Jan-Jun 2026"',
                        "fix": None if r == "Met" else f"Address {it['area'].lower()} gap"})
        return json.dumps(out)

    if system == P.REPORTER_SYSTEM:
        return json.dumps({
            "readiness_summary": "DRAFT. Core production data exists, but the plant is not "
                                 "verification-ready. Biggest risk: overdue gas meter and no "
                                 "monitoring plan. Biggest opportunity: supplier data for "
                                 "purchased billets.",
            "readiness_score": 0,
            "action_plan": [
                {"priority": 1, "action": "Request emissions data from Supplier B",
                 "why": "Default values inflate reported emissions", "owner": "Procurement",
                 "by_when": "within 1 week"},
                {"priority": 2, "action": "Calibrate gas meter GM-02",
                 "why": "Activity data may be rejected", "owner": "Maintenance",
                 "by_when": "within 2 weeks"},
                {"priority": 3, "action": "Write a monitoring plan",
                 "why": "Required basis for verification", "owner": "QA Manager",
                 "by_when": "within 4 weeks"}],
            "what_if_message": "With actual emissions data from Supplier B instead of EU "
                               "default values, illustrative full-phase-in exposure on 15,000 t "
                               "of rebar falls from EUR 792,000 to EUR 454,500. Requesting "
                               "supplier data is the single most valuable action.",
            "buyer_email": {
                "subject": "DRAFT – CBAM emissions data for CN 7214 rebar (Jan–Jun 2026)",
                "body": "DRAFT – requires review before sending.\n\n"
                        "Dear Procurement Team,\n\n"
                        "Thank you for your request. Please find our preliminary CBAM data for "
                        "deformed rebar (CN 7214) produced January–June 2026:\n\n"
                        "- Production route: EAF billets from scrap, re-rolled; part of the "
                        "billets purchased from a local induction-furnace mill\n"
                        "- Specific direct embedded emissions: 0.704 tCO2/t\n"
                        "- Specific indirect embedded emissions: 0.344 tCO2/t\n"
                        "- Data basis: actual installation data; EU default values for "
                        "24,000 t of purchased billets\n\n"
                        "Open issues: we are obtaining actual emissions data from our billet "
                        "supplier and recalibrating one gas meter. We will send updated, "
                        "verification-ready figures by 31 October 2026.\n\n"
                        "Kind regards,\nExport Department\nMargalla Steel Works (Pvt) Ltd"}})
    raise ValueError("Unknown agent prompt")


# ---------------------------------------------------------------- scoring
WEIGHT = {"high": 3, "medium": 2, "low": 1}
CREDIT = {"Met": 1.0, "Partial": 0.5, "Missing": 0.0}


def readiness_score(audit):
    """Computed in Python, never trusted to the LLM."""
    total = sum(WEIGHT[a["severity"]] for a in audit)
    got = sum(WEIGHT[a["severity"]] * CREDIT[a["rating"]] for a in audit)
    return round(100 * got / total) if total else 0


# ---------------------------------------------------------------- pipeline
def run(documents_text, buyer_request="", supplier_whatif=None, llm=None, on_step=None):
    """
    documents_text : all uploaded documents as text (Intake/RAG output)
    supplier_whatif: {"process": ..., "precursor": ..., "see_direct": ...} or None
    """
    llm = llm or make_llm()[0]
    step = on_step or (lambda name: None)

    with open(os.path.join(HERE, "sample_installation_data.json")) as f:
        schema = f.read()
    with open(os.path.join(HERE, "cbam_checklist.json")) as f:
        checklist = f.read()

    # 1. Extract
    step("Data Extractor: reading documents and extracting activity data")
    data = parse_json(llm(P.EXTRACTOR_SYSTEM,
                          P.EXTRACTOR_USER.format(schema=schema, documents=documents_text)))

    # 2. Calculate (deterministic)
    step("Emissions Calculator: computing embedded emissions per product")
    result = calc.calculate(data)
    whatif = None
    if supplier_whatif:
        target = None
        for proc in data.get("processes", []):
            for pr in proc.get("precursors", []) or []:
                if pr.get("source") != "own" and pr.get("supplier_see_direct") is None:
                    target = (proc["name"], pr["name"])
                    break
            if target:
                break
        if target:
            whatif = calc.what_if_supplier_data(data, target[0], target[1],
                                                supplier_whatif["see_direct"])

    # 3. Audit
    step("Gap Auditor: checking readiness against the CBAM checklist")
    audit = parse_json(llm(P.AUDITOR_SYSTEM, P.AUDITOR_USER.format(
        checklist=checklist, flags="\n".join(result["flags"]), documents=documents_text)))
    if isinstance(audit, dict):
        audit = audit.get("items") or next((v for v in audit.values() if isinstance(v, list)), [])
    for a in audit:
        a["severity"] = a.get("severity", "medium") if a.get("severity") in WEIGHT else "medium"
        a["rating"] = a.get("rating") if a.get("rating") in CREDIT else "Missing"
    score = readiness_score(audit)

    # 4. Report
    step("Reporter & Advisor: writing action plan and buyer email")
    report = parse_json(llm(P.REPORTER_SYSTEM, P.REPORTER_USER.format(
        installation=result["installation"], period=result["reporting_period"],
        results=json.dumps(result["results"], indent=1),
        exposure_default=json.dumps(result["eu_cost_exposure"]),
        exposure_whatif=json.dumps(whatif["eu_cost_exposure"]) if whatif else "not run",
        audit=json.dumps(audit), buyer_request=buyer_request)))
    report["readiness_score"] = score  # override with deterministic score

    return {"extracted": data, "calculation": result, "what_if": whatif,
            "audit": audit, "report": report}


if __name__ == "__main__":
    llm, name = make_llm()
    with open(os.path.join(HERE, "sample_dossier_margalla_steel.md")) as f:
        docs = f.read()
    out = run(docs, buyer_request=docs.split("## Document 2")[0],
              supplier_whatif={"process": "Rolling Mill - Rebar",
                               "precursor": "Billets (purchased)", "see_direct": 0.9},
              llm=llm)
    print(f"Mode: {name}")
    print("Readiness score:", out["report"]["readiness_score"])
    print("Default exposure:", out["calculation"]["eu_cost_exposure"][0])
    print("What-if exposure:", out["what_if"]["eu_cost_exposure"][0])
    print("Audit:", {r: sum(a["rating"] == r for a in out["audit"])
                     for r in ("Met", "Partial", "Missing")})
    print("Flags:", *out["calculation"]["flags"], sep="\n  ")
