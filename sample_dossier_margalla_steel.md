# Margalla Steel Works (Pvt) Ltd — Sample Dossier (FICTIONAL)

> Demo input for CarbonPass. Company, people and figures are invented. Deliberate gaps are included so the agents have something to find.

---

## Document 1 — Email from EU buyer

**From:** procurement@hanse-baustahl.example (fictional German importer)
**To:** exports@margallasteel.example
**Date:** 15 September 2026
**Subject:** CBAM emissions data required for your rebar shipments

Dear Margalla team,

As an authorised CBAM declarant we must report the embedded emissions of all rebar we import from you in 2026. Please send the specific embedded emissions (tCO2e per tonne) for CN 7214 rebar, with your production route and the basis of your data, by 31 October 2026.

If we do not receive verifiable installation data, we will have to use EU default values, which will increase our CBAM costs. In that case we may need to review pricing for 2027 contracts.

Regards,
Procurement Department

---

## Document 2 — Company profile

- **Legal name:** Margalla Steel Works (Pvt) Ltd
- **Location:** Industrial Estate, Sheikhupura, Punjab, Pakistan
- **Products:** Steel billets (CN 7207), deformed rebar (CN 7214)
- **Capacity:** about 160,000 t/year rebar
- **EU exports (H1 2026):** 15,000 t rebar to one German importer
- **Contact:** Plant Manager, Engr. (name withheld)

*(Gap: no geo-coordinates, no named CBAM focal person.)*

---

## Document 3 — "Emissions Note" (the company's only monitoring document)

1. We produce billets in a 40 t electric arc furnace using local and imported scrap.
2. Billets are reheated in a gas-fired furnace and rolled into rebar.
3. Some billets are purchased from local suppliers when the EAF is down.
4. Gas consumption is taken from SNGPL monthly bills. Electricity from LESCO bills.
5. We use standard IPCC factors for gas.

*(Gaps: no process boundaries or source-stream list, no factor register, no data-control procedure, no uncertainty assessment, no verification plan, electrode and coal carbon content not documented.)*

---

## Document 4 — Production and consumption summary (Jan–Jun 2026)

| Item | EAF Melt Shop | Rolling Mill |
|---|---|---|
| Output | 60,000 t billets | 80,000 t rebar |
| Natural gas | 40,000 MMBTU | 105,000 MMBTU |
| Grid electricity | 33,000 MWh | 8,000 MWh |
| Graphite electrodes | 120 t | — |
| Injection coal | 600 t | — |
| Own billets charged | — | 58,000 t |
| Purchased billets charged | — | 24,000 t (Supplier B) |

---

## Document 5 — Purchase register extract (billets)

| Supplier | Route | Quantity | Emissions data received? |
|---|---|---|---|
| Supplier B — local induction-furnace mill | Induction furnace | 24,000 t | **No** |

---

## Document 6 — Meter register

| Meter | Measures | Last calibration | Interval | Status |
|---|---|---|---|---|
| EM-01 | Grid electricity, melt shop | Jan 2026 | 12 months | Valid |
| GM-02 | Natural gas, reheating furnace | Mar 2025 | 12 months | **Overdue since Mar 2026** |

---

## Expected findings (answer key for testing)

1. **No actual data for purchased billets** → EU default values used; costs inflated.
2. **Gas meter GM-02 calibration overdue** → reheating-furnace data at risk at verification.
3. **No proper monitoring plan** → boundaries, factor register, data control missing.
4. **No verification plan** → EU buyer's deadline at risk.
5. **No carbon price paid in Pakistan** → no deduction available (informational).
6. **Carbon content of electrodes and coal undocumented** → process emissions unsupported.
