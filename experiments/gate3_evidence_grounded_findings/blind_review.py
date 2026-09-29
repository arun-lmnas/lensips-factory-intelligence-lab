"""
Gate 3 follow-up: strips confidence_status out of the 21 finding objects in
results/results.json, so a reviewer can classify each finding from only the
question, supporting_evidence, evidence_coverage, missing_evidence,
logical_inconsistencies, and limitations fields, without seeing the
algorithm's own label. Used to produce the blinded view reviewed in
reports/GATE3_EVIDENCE_GROUNDED_FINDINGS.md section 6. Does not itself do
any classification -- that judgment is recorded separately in
results/human_validation.json.
"""
import json
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent / "results"


def main():
    with open(RESULTS_DIR / "results.json") as f:
        data = json.load(f)

    blind = {
        scenario: {
            question: {k: v for k, v in finding.items() if k != "confidence_status"}
            for question, finding in findings.items()
        }
        for scenario, findings in data.items()
    }

    out_path = RESULTS_DIR / "blind_review.json"
    with open(out_path, "w") as f:
        json.dump(blind, f, indent=2)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
