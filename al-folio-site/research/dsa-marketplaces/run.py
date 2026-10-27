"""Approved finite-snapshot arithmetic; no fitting, resampling or inference."""
import collections as co
import csv
import datetime as dt
import gzip
import json
import math
from pathlib import Path
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE / "results"
INPUT = BASE / "data"


def read(path):
    stream = gzip.open(path, "rt", newline="") if path.suffix == ".gz" else path.open(newline="")
    with stream as f:
        return list(csv.DictReader(f))


def sha(path):
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


OUTCOMES = ("visibility", "account", "monetary", "service", "multiple_domains")


def writecsv(name, rows):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    stream = gzip.open(path, "xt", newline="") if path.suffix == ".gz" else path.open("x", newline="")
    with stream as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def savejson(name, obj):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)


def outcomes(r):
    flags = [any(v == "true" for k, v in r.items() if k.startswith("DECISION_VISIBILITY_")),
             r["decision_account"] != "", r["decision_monetary"] != "", r["decision_provision"] != ""]
    return tuple(map(int, flags)) + (int(sum(flags) >= 2),)


def summarize(rows):
    n = sum(int(r["count"]) for r in rows)
    result = dict(source_cells=len(rows), statements=n)
    for j, name in enumerate(OUTCOMES):
        events = sum(int(r["count"]) * r["_outcomes"][j] for r in rows)
        result[name + "_n"] = events
        result[name + "_pct"] = 100 * events / n if n else None
    return result


def main():
    start = time.perf_counter()
    assert not (ROOT / "scope.json").exists(), "Exclusive builder: results already exist"
    config = json.loads((INPUT / "prepared/analysis_config_v02.json").read_text())
    files = ["manifest.json", "prepared/analysis_config_v02.json", "prepared/source_cells.csv.gz",
             "prepared/support_strata.csv.gz", "prepared/supported_cell_membership.csv.gz", "prepared/sample_flow.csv"]
    baseline = {name: dict(bytes=(INPUT / name).stat().st_size, sha256=sha(INPUT / name)) for name in files}
    savejson("scope.json", dict(client_date="2026-10-27", approved_work="Frozen descriptive rates and standardized differences",
                                input_version=INPUT.name, input_files=baseline, seeds="Not applicable: deterministic",
                                model_fits_authorized=False, new_scientific_choices=False))
    cells = read(INPUT / "prepared/source_cells.csv.gz")
    assert len(cells) == 20528 and sum(int(r["count"]) for r in cells) == 346993630
    for r in cells:
        r["_outcomes"] = outcomes(r)
    byid = {r["source_cell_id"]: r for r in cells}
    platforms, populations = config["platforms"], config["populations"]
    contrasts = ["_vs_".join(pair) for pair in config["automation_pairs"]]
    overall, monthly, bundles, auto, detection, daily = [], [], [], [], [], []
    calendar = [(dt.date(2025, 9, 1) + dt.timedelta(days=i)).isoformat() for i in range(91)]
    views = {}
    for p in platforms:
        for pop in populations:
            rr = [r for r in cells if r["platform_name"] == p and (pop == "all_reported_types" or r["CONTENT_TYPE_PRODUCT"] == "true")]
            views[p, pop] = rr
            context = dict(platform=p, population=pop)
            overall.append(dict(**context, calendar_days=91, positive_volume_days=len({r["created_at"][:10] for r in rr}), **summarize(rr)))
            for month in config["source_months"]:
                monthly.append(dict(**context, month=month, **summarize([r for r in rr if r["created_at"].startswith(month)])))
            totals = co.Counter()
            for r in rr:
                bundle = "".join(k for k, flag in zip("VAMS", r["_outcomes"][:4]) if flag) or "NONE"
                totals[bundle] += int(r["count"])
            n = sum(totals.values())
            for mask in range(16):
                bundle = "".join(k for j, k in enumerate("VAMS") if mask & (1 << j)) or "NONE"
                bundles.append(dict(**context, bundle=bundle, statements=totals[bundle], population_statements=n, pct=100*totals[bundle]/n))
            for arm in ("FULLY", "PARTIALLY", "NOT_AUTOMATED"):
                ar = [r for r in rr if r["automated_decision"] == "AUTOMATED_DECISION_" + arm]
                auto.append(dict(**context, automated_decision=arm, **summarize(ar), population_pct=100*sum(int(r["count"]) for r in ar)/n))
                for detect in sorted({r["automated_detection"] for r in cells}):
                    nn = sum(int(r["count"]) for r in ar if r["automated_detection"] == detect)
                    detection.append(dict(**context, automated_decision=arm, automated_detection=detect, statements=nn, population_pct=100*nn/n))
            for day in calendar:
                dr = [r for r in rr if r["created_at"][:10] == day]
                status = "OBSERVED_POSITIVE_VOLUME" if dr else "NO_PRODUCT_TAGGED_RECORDS"
                if p == "Amazon" and day in config["Amazon_source_zero_days"]:
                    status = "PUBLISHED_SOURCE_ZERO_VOLUME"
                    assert not dr
                daily.append(dict(**context, date=day, calendar_status=status, **summarize(dr)))
    lookup = {(r["platform"], r["population"]): r for r in overall}
    capture = []
    for p in platforms:
        allr, pr = lookup[p, "all_reported_types"], lookup[p, "product_type_true"]
        for name in ("statements",) + OUTCOMES:
            field = name if name == "statements" else name + "_n"
            num, den = pr[field], allr[field]
            capture.append(dict(platform=p, outcome=name, product_positive_count=num, all_positive_count=den,
                                excluded_positive_count=den-num, captured_pct=100*num/den if den else None,
                                status="DEFINED" if den else "UNDEFINED_ZERO_DENOMINATOR"))
    strata = read(INPUT / "prepared/support_strata.csv.gz")
    members = read(INPUT / "prepared/supported_cell_membership.csv.gz")
    events = co.defaultdict(lambda: [0] * 5)
    for m in members:
        for j, flag in enumerate(byid[m["source_cell_id"]]["_outcomes"]):
            events[m["stratum_id"], m["arm"]][j] += int(m["count"]) * flag
    groups = co.defaultdict(list)
    stratum_results = []
    for s in strata:
        key = (s["platform_name"], s["population"], s["contrast"])
        groups[key].append(s)
        a, b = s["contrast"].split("_vs_")
        na, nb, wn, wd = (int(s[k]) for k in ("n_a", "n_b", "weight_numerator", "weight_denominator"))
        assert na > 0 and nb > 0 and wn == na + nb
        for j, name in enumerate(OUTCOMES):
            ya, yb = events[s["stratum_id"], a][j], events[s["stratum_id"], b][j]
            assert 0 <= ya <= na and 0 <= yb <= nb
            stratum_results.append(dict(stratum_id=s["stratum_id"], outcome=name, n_a=na, n_b=nb, events_a=ya, events_b=yb,
                                        weight_numerator=wn, weight_denominator=wd,
                                        rate_a=ya/na, rate_b=yb/nb, contribution_a=wn/wd*ya/na, contribution_b=wn/wd*yb/nb))
    flow, differences = read(INPUT / "prepared/sample_flow.csv"), []
    for f in flow:
        key = (f["platform"], f["population"], f["contrast"])
        a, b = f["contrast"].split("_vs_")
        ss = groups[key]
        na, nb = int(f["support_a_statements"]), int(f["support_b_statements"])
        for arm in (a, b):
            nn = sum(int(r["count"]) for r in views[key[:2]] if r["automated_decision"] == "AUTOMATED_DECISION_" + arm)
            f["before_support_" + ("a" if arm == a else "b")] = nn
        pairn, popn = int(f["contrast_arm_statements_before_support"]), int(f["source_statements"])
        f["supported_pair_pct"] = 100*(na+nb)/pairn if pairn else None
        f["supported_population_pct"] = 100*(na+nb)/popn
        f["a_retained_pct"] = 100*na/f["before_support_a"] if f["before_support_a"] else None
        f["b_retained_pct"] = 100*nb/f["before_support_b"] if f["before_support_b"] else None
        f["max_stratum_weight_pct"] = 100*max(int(s["weight_numerator"])/int(s["weight_denominator"]) for s in ss) if ss else None
        if ss:
            assert sum(int(s["weight_numerator"]) for s in ss) == na + nb
        for j, name in enumerate(OUTCOMES):
            ea = sum(events[s["stratum_id"], a][j] for s in ss)
            eb = sum(events[s["stratum_id"], b][j] for s in ss)
            ra = math.fsum(int(s["weight_numerator"])/int(s["weight_denominator"])*events[s["stratum_id"], a][j]/int(s["n_a"]) for s in ss) if ss else None
            rb = math.fsum(int(s["weight_numerator"])/int(s["weight_denominator"])*events[s["stratum_id"], b][j]/int(s["n_b"]) for s in ss) if ss else None
            differences.append(dict(platform=key[0], population=key[1], contrast=key[2], outcome=name, status=f["status"],
                                    arm_a=a, arm_b=b, support_strata=len(ss), n_a=na, n_b=nb,
                                    events_a=ea if ss else None, events_b=eb if ss else None,
                                    crude_support_a_pct=100*ea/na if ss else None, crude_support_b_pct=100*eb/nb if ss else None,
                                    standardized_a_pct=100*ra if ss else None, standardized_b_pct=100*rb if ss else None,
                                    difference_pp=100*(ra-rb) if ss else None))
    for name, rows in [("01_platform_population", overall), ("02_platform_month_domains", monthly),
                       ("03_restriction_bundles", bundles), ("04_automation_profile", auto),
                       ("04b_detection_decision_profile", detection), ("05_product_capture", capture),
                       ("06_common_support", flow), ("07_standardized_differences", differences), ("08_daily_domains", daily)]:
        writecsv("tables/" + name + ".csv", rows)
    writecsv("calculations/stratum_outcome_rates.csv.gz", stratum_results)
    assert len(differences) == 150 and sum(r["difference_pp"] is not None for r in differences) == 100
    assert len(stratum_results) == 38255
    assert sum(r["statements"] for r in overall if r["population"] == "all_reported_types") == 346993630
    for name, before in baseline.items():
        assert sha(INPUT / name) == before["sha256"]
    savejson("audit/calculation_receipt.json", dict(status="PASS", source_cells=20528, source_statements=346993630,
             supported_comparisons=20, unsupported_comparisons=10, standardized_outcome_differences=100,
             undefined_outcome_differences=50, stratum_outcome_rows=38255, model_fits=0, formal_tests=0,
             resamples=0, random_draws=0, count_rewrites=0, new_day_exclusions=0, weight_changes=0,
             wall_seconds=time.perf_counter()-start, python=sys.version, platform=sys.platform))
    print((ROOT / "audit/calculation_receipt.json").read_text())


def check_inputs():
    for name, record in json.loads((INPUT / "manifest.json").read_text()).items():
        path = INPUT / name
        assert path.stat().st_size == record["bytes"] and sha(path) == record["sha256"], name
    cells = read(INPUT / "prepared/source_cells.csv.gz")
    assert len(cells) == 20528 and sum(int(r["count"]) for r in cells) == 346993630
    print("INPUT CHECK PASS: 20,528 aggregation cells; statement frequency 346,993,630")


def compare_reference():
    for expected in sorted((BASE / "reference").glob("*.csv")):
        actual = ROOT / "tables" / expected.name
        assert actual.read_bytes() == expected.read_bytes(), expected.name
    print("REPRODUCTION PASS: all nine CSV tables match the supplied reference files byte for byte")


if __name__ == "__main__":
    check_inputs()
    if "--check" not in sys.argv:
        main()
        compare_reference()
