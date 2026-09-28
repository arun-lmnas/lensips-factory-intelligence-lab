"""
Gate 2 follow-up experiment (the "next smallest experiment" proposed at the
end of reports/GATE2_DATA_REALISM_EXPERIMENT.md, section 8).

The main Gate 2 experiment found that conformance/fitness scores did not
change meaningfully even when an entire decision-relevant activity category
(quality inspection) vanished from the data (the `missing_quality_events`
scenario) -- the bottleneck finding silently disappeared with no warning
from any metric already in use.

This script builds the smallest possible fix: a category-level coverage
check that compares, for a named category of activities, how many events
were observed in a given log against how many were observed in a trusted
baseline. It is deliberately simple (substring match + count comparison) --
the point of this experiment is only to confirm the *mechanism* works, not
to build a production data-quality module.

Scope, per the Gate 2 brief: no OCEL, no OFacT/digital twin, no LLM
reasoning, no customer-specific transformer modeling. Reuses the exact
scenario-generation and data-loading code from run_experiment.py so results
are directly comparable to the main experiment's results.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_experiment import SCENARIOS, load_raw  # noqa: E402

RESULTS_DIR = Path("/workspace/experiments/gate2_data_realism/results")

# Category name -> substrings that identify it in the Activity column.
# "quality_inspection" mirrors QUALITY_ACTIVITY_SUBSTRINGS from
# run_experiment.py (the category degraded by scenario_missing_quality_events).
# "turning_milling" and "packing" are controls: high- and low-volume
# categories that no scenario deliberately targets, used to check the coverage
# check does not cry wolf on categories that were not specifically degraded.
CATEGORIES = {
    "quality_inspection": ["Q.C.", "Inspection", "MRB"],
    "turning_milling": ["Turning & Milling"],
    "packing": ["Packing"],
}

SEVERE_THRESHOLD_PCT = 20.0


def category_counts(df, categories: dict) -> dict:
    counts = {}
    for name, substrings in categories.items():
        pattern = "|".join(substrings)
        mask = df["Activity"].str.contains(pattern, case=False, na=False)
        counts[name] = int(mask.sum())
    return counts


def coverage_report(baseline_counts: dict, variant_counts: dict) -> dict:
    """For each category, compare variant event count against the baseline
    (trusted) event count and classify the result. This is the check the
    main Gate 2 experiment identified as missing: it looks at coverage of a
    *specific, named category*, not overall event retention, so it can catch
    a category disappearing even when overall retention still looks
    reasonable (as happened with `missing_quality_events`: 73.7% of ALL
    events retained, but 0% of quality-inspection events retained)."""
    report = {}
    for name, expected in baseline_counts.items():
        observed = variant_counts.get(name, 0)
        coverage_pct = round(100.0 * observed / expected, 1) if expected > 0 else None
        if expected == 0:
            flag = "NOT_APPLICABLE"  # category did not exist in the baseline either
        elif observed == 0:
            flag = "MISSING"
        elif coverage_pct < SEVERE_THRESHOLD_PCT:
            flag = "SEVERELY_DEGRADED"
        else:
            flag = "OK"
        report[name] = {
            "expected_count": expected,
            "observed_count": observed,
            "coverage_pct": coverage_pct,
            "flag": flag,
        }
    return report


def main():
    raw = load_raw()
    baseline_counts = category_counts(raw, CATEGORIES)
    print(f"Baseline category counts: {baseline_counts}", file=sys.stderr)

    results = {}
    for scenario_name, fn in SCENARIOS.items():
        variant_df = fn(raw.copy())
        variant_counts = category_counts(variant_df, CATEGORIES)
        report = coverage_report(baseline_counts, variant_counts)
        results[scenario_name] = report
        flags = {cat: r["flag"] for cat, r in report.items()}
        print(f"[{scenario_name}] {flags}", file=sys.stderr)

    out_path = RESULTS_DIR / "coverage_check_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote {out_path}", file=sys.stderr)

    # Explicit pass/fail check against the one scenario this experiment was
    # designed to catch: does the coverage check flag the vanishing quality
    # bottleneck that fitness (in run_experiment.py) missed?
    caught = results["missing_quality_events"]["quality_inspection"]["flag"] == "MISSING"
    print(f"\nDid the coverage check catch the missing_quality_events gap? {caught}",
          file=sys.stderr)
    # And a false-positive check: control categories should NOT be flagged
    # MISSING/SEVERELY_DEGRADED in scenarios that did not target them.
    false_positives = []
    for scenario_name, report in results.items():
        if scenario_name == "missing_quality_events":
            continue  # this scenario is expected to affect quality_inspection only
        for cat in ("turning_milling", "packing"):
            if report[cat]["flag"] in ("MISSING", "SEVERELY_DEGRADED"):
                false_positives.append((scenario_name, cat, report[cat]))
    print(f"False positives on control categories: {false_positives}", file=sys.stderr)


if __name__ == "__main__":
    main()
