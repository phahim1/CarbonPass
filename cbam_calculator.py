"""
CBAM Embedded Emissions Calculator (hackathon prototype)
---------------------------------------------------------
Deterministic tool for the "Emissions Calculator Agent". The LLM never does the
maths: it extracts activity data into JSON, then calls calculate(data).

Method (simplified, illustrative):
  Direct emissions  = fuel combustion + process (carbon mass balance)
  Indirect emissions = electricity MWh x emission factor
  Specific embedded emissions (SEE) = attributed emissions / tonnes produced
  Complex goods add precursor embedded emissions (e.g. billets -> rebar).

All factors in the sample data are ILLUSTRATIVE. Real CBAM reporting must use
the methodology and values in the EU CBAM implementing rules.
"""

import json
import sys

CO2_PER_C = 44.0 / 12.0  # tCO2 per tonne of carbon
GJ_PER_MMBTU = 1.055056


DEFAULT_EF_NATURAL_GAS = 56.1  # tCO2/TJ, IPCC 2006 default


def _fuel_emissions(fuels, flags=None):
    total, lines = 0.0, []
    for f in fuels:
        if f.get("ef_tco2_per_tj") is None:
            f["ef_tco2_per_tj"] = DEFAULT_EF_NATURAL_GAS
            if flags is not None:
                flags.append(f"[MEDIUM] No documented emission factor for '{f['name']}'. "
                             f"IPCC default {DEFAULT_EF_NATURAL_GAS} tCO2/TJ used; document it in a factor register.")
        if f.get("quantity") is None:
            if flags is not None:
                flags.append(f"[HIGH] Fuel quantity missing for '{f['name']}'.")
            continue
        gj = f["quantity"] * (GJ_PER_MMBTU if f["unit"] == "MMBTU" else 1.0)
        t = gj / 1000.0 * f["ef_tco2_per_tj"]
        total += t
        lines.append({"source": f["name"], "tCO2": round(t, 1)})
    return total, lines


def _process_emissions(carbon_inputs, flags=None):
    total, lines = 0.0, []
    for c in carbon_inputs:
        if c.get("tonnes") is None or c.get("carbon_fraction") is None:
            if flags is not None:
                flags.append(f"[HIGH] Quantity or carbon content missing for '{c['name']}'; "
                             f"process emissions from it are not counted.")
            continue
        t = c["tonnes"] * c["carbon_fraction"] * CO2_PER_C
        total += t
        lines.append({"source": c["name"], "tCO2": round(t, 1)})
    return total, lines


def calculate(data, ets_price_eur=75.0, cbam_factor=0.025):
    flags = []
    results = {}
    see_by_process = {}

    for proc in data["processes"]:
        fuel_t, fuel_lines = _fuel_emissions(proc.get("fuels", []), flags)
        proc_t, proc_lines = _process_emissions(proc.get("carbon_inputs", []), flags)
        elec_mwh = proc.get("electricity_mwh") or 0.0
        indirect = elec_mwh * (data.get("grid_ef_tco2_per_mwh") or 0.0)

        prod = proc["output_tonnes"]
        direct_own = fuel_t + proc_t

        # Precursors: own (from an earlier process) or purchased
        precursor_direct, precursor_indirect = 0.0, 0.0
        for p in proc.get("precursors", []):
            if p.get("source") == "own":
                key = p.get("process")
                if key not in see_by_process:  # LLM may name it differently: use latest own process
                    key = list(see_by_process)[-1] if see_by_process else None
                s = see_by_process.get(key, {"see_direct": 0.0, "see_indirect": 0.0})
                d, i, basis = s["see_direct"], s["see_indirect"], "own process"
            elif p.get("supplier_see_direct") is not None:  # actual supplier data
                d = p["supplier_see_direct"]
                i = p.get("supplier_see_indirect", 0.0)
                basis = "supplier actual data"
            else:
                d = p.get("default_see_direct")
                if d is None:
                    d = 1.9  # illustrative fallback default for billets
                i = p.get("default_see_indirect") or 0.0
                basis = "EU DEFAULT VALUE (no supplier data)"
                flags.append(
                    f"[HIGH] {proc['name']}: no actual emissions data from supplier "
                    f"'{p.get('supplier', 'unknown supplier')}' for {p['tonnes']} t {p['name']}. Default value "
                    f"used, which usually raises reported emissions. Request supplier data."
                )
            precursor_direct += p["tonnes"] * d
            precursor_indirect += p["tonnes"] * i
            p["_basis"] = basis

        see_direct = (direct_own + precursor_direct) / prod
        see_indirect = (indirect + precursor_indirect) / prod
        see_by_process[proc["name"]] = {"see_direct": see_direct, "see_indirect": see_indirect}

        results[proc["name"]] = {
            "cn_code": proc.get("cn_code"),
            "output_tonnes": prod,
            "direct_fuel_tCO2": round(fuel_t, 1),
            "direct_process_tCO2": round(proc_t, 1),
            "indirect_tCO2": round(indirect, 1),
            "precursor_direct_tCO2": round(precursor_direct, 1),
            "SEE_direct_tCO2_per_t": round(see_direct, 3),
            "SEE_indirect_tCO2_per_t": round(see_indirect, 3),
            "fuel_lines": fuel_lines,
            "process_lines": proc_lines,
            "precursor_basis": [
                {"name": p["name"], "tonnes": p["tonnes"], "basis": p["_basis"]}
                for p in proc.get("precursors", [])
            ],
        }

    # Data-quality checks
    for m in data.get("meters", []):
        if (m.get("calibration_status") or "unknown") != "valid":
            flags.append(
                f"[HIGH] Meter '{m['id']}' ({m['measures']}) calibration {m['calibration_status']}. "
                f"Activity data may be rejected by the verifier."
            )
    if data.get("carbon_price_paid_eur_per_t", 0) == 0:
        flags.append(
            "[INFO] No carbon price paid in country of origin, so no deduction can be claimed."
        )

    # Illustrative cost exposure for EU-exported goods (direct emissions only,
    # as for iron & steel). Simplified: ignores benchmark-based free-allocation
    # adjustment detail. For orientation, not a legal calculation.
    exposure = []
    for e in data.get("eu_exports", []):
        r = results.get(e.get("process")) or list(results.values())[-1]
        emb = r["SEE_direct_tCO2_per_t"] * e["tonnes"]
        exposure.append({
            "product": e.get("process"),
            "tonnes_to_eu": e["tonnes"],
            "embedded_direct_tCO2": round(emb, 1),
            "illustrative_cost_full_phase_in_EUR": round(emb * ets_price_eur),
            "illustrative_cost_this_year_EUR": round(emb * ets_price_eur * cbam_factor),
        })

    return {
        "installation": data["installation"],
        "reporting_period": data["reporting_period"],
        "results": results,
        "eu_cost_exposure": exposure,
        "assumptions": {"ets_price_eur": ets_price_eur, "cbam_factor": cbam_factor},
        "flags": flags,
    }


def what_if_supplier_data(data, process_name, precursor_name, see_direct):
    """Re-run with actual supplier data to show savings vs default values."""
    d = json.loads(json.dumps(data))
    for proc in d["processes"]:
        if proc["name"] == process_name:
            for p in proc.get("precursors", []):
                if p["name"] == precursor_name:
                    p["supplier_see_direct"] = see_direct
    return calculate(d)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_installation_data.json"
    with open(path) as f:
        data = json.load(f)
    out = calculate(data)
    print(json.dumps(out, indent=2))
