"""
One-off dataset preparation (not the analysis itself): build a manageable,
reproducible REAL-DATA subsample of the full BPI Challenge 2019 OCEL log
(datasets/bpic2019_ocel/BPIC19.jsonocel, 1.6M events, 251,734 purchase-order
items, 1.5 GB) for Gate 4b.

Method (documented in reports/GATE4_DATASET_SELECTION.md):
  1. Stream the full event log once, counting events per Purchase Order
     (cPOID) for the dominant subsidiary (cCompany == companyID_0000, which
     accounts for 1,590,010 of 1,595,923 events -- the other 3 subsidiaries
     are negligible and excluded so the sample reflects one coherent
     purchase-to-pay process rather than mixing four different-sized ones).
  2. Deterministically (fixed seed) sample whole purchase orders (not
     individual events) until a target event budget is reached, so every
     sampled PO's full event history -- all its items, all its
     goods-receipt/invoice events, all referenced vendors and users -- is
     kept intact. No event is fabricated, reordered, or altered.
  3. Stream the full log again, keeping only events belonging to a sampled
     PO, and collect every object id referenced by those events' omap.
  4. Stream the full ocel:objects section, keeping only referenced objects.
  5. Write the filtered result as a smaller, valid OCEL 1.0 jsonocel file.

This is a real-data subsample, not a synthetic dataset. It is
disclosed as such throughout the Gate 4b report.
"""
import ijson
import json
import random
from collections import defaultdict
from decimal import Decimal
from pathlib import Path


def _json_default(o):
    if isinstance(o, Decimal):
        return float(o)
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

SRC = Path("/workspace/datasets/bpic2019_ocel/BPIC19.jsonocel")
OUT_DIR = Path("/workspace/datasets/bpic2019_ocel/sample")
TARGET_COMPANY = "companyID_0000"
TARGET_EVENT_BUDGET = 20000
SEED = 42


def pass1_count_events_per_po():
    po_event_counts = defaultdict(int)
    with open(SRC, "rb") as f:
        for event_id, event in ijson.kvitems(f, "ocel:events"):
            vmap = event.get("ocel:vmap", {})
            if vmap.get("cCompany") != TARGET_COMPANY:
                continue
            po_event_counts[vmap.get("cPOID")] += 1
    return po_event_counts


def choose_pos(po_event_counts):
    pos = list(po_event_counts.keys())
    rng = random.Random(SEED)
    rng.shuffle(pos)
    chosen = set()
    total = 0
    for po in pos:
        if total >= TARGET_EVENT_BUDGET:
            break
        chosen.add(po)
        total += po_event_counts[po]
    return chosen, total


def pass2_extract_events(chosen_pos):
    kept_events = {}
    referenced_objects = set()
    with open(SRC, "rb") as f:
        for event_id, event in ijson.kvitems(f, "ocel:events"):
            vmap = event.get("ocel:vmap", {})
            if vmap.get("cCompany") != TARGET_COMPANY:
                continue
            if vmap.get("cPOID") not in chosen_pos:
                continue
            kept_events[event_id] = event
            for obj_id in event.get("ocel:omap", []):
                referenced_objects.add(obj_id)
    return kept_events, referenced_objects


def pass3_extract_objects(referenced_objects):
    kept_objects = {}
    with open(SRC, "rb") as f:
        for obj_id, obj in ijson.kvitems(f, "ocel:objects"):
            if obj_id in referenced_objects:
                kept_objects[obj_id] = obj
    return kept_objects


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Pass 1: counting events per PO for", TARGET_COMPANY, "...")
    po_event_counts = pass1_count_events_per_po()
    print(f"  {len(po_event_counts)} distinct POs found")

    chosen_pos, total_events_est = choose_pos(po_event_counts)
    print(f"Chose {len(chosen_pos)} POs, ~{total_events_est} events (target {TARGET_EVENT_BUDGET})")

    print("Pass 2: extracting events for chosen POs ...")
    kept_events, referenced_objects = pass2_extract_events(chosen_pos)
    print(f"  kept {len(kept_events)} events, {len(referenced_objects)} referenced objects")

    print("Pass 3: extracting referenced objects ...")
    kept_objects = pass3_extract_objects(referenced_objects)
    print(f"  kept {len(kept_objects)} objects")

    result = {
        "ocel:global-event": {"ocel:activity": "__INVALID__"},
        "ocel:global-object": {"ocel:type": "__INVALID__"},
        "ocel:global-log": {
            "ocel:object-types": ["PO", "POItem", "Resource", "Vendor"],
            "ocel:attribute-names": [
                "ID", "cCompany", "cDocType", "cGR", "cGRbasedInvVerif", "cID",
                "cItem", "cItemCat", "cItemType", "cPOID", "cPurDocCat",
                "cSpendAreaText", "cSpendClassText", "cSubSPendAreaText",
                "cVendor", "cVendorName", "eCumNetWorth", "idx", "resource",
            ],
            "ocel:version": "1.0",
            "ocel:ordering": "timestamp",
        },
        "ocel:events": kept_events,
        "ocel:objects": kept_objects,
    }

    out_path = OUT_DIR / "BPIC19_sample.jsonocel"
    out_path.write_text(json.dumps(result, default=_json_default))
    print(f"Wrote {out_path} ({out_path.stat().st_size / 1e6:.1f} MB)")

    manifest = {
        "source_file": "datasets/bpic2019_ocel/BPIC19.jsonocel",
        "source_dataset_doi": "10.4121/46a7e15b-10c7-4ab2-988d-ee67d8ea515a",
        "target_company": TARGET_COMPANY,
        "seed": SEED,
        "target_event_budget": TARGET_EVENT_BUDGET,
        "n_pos_available_for_company": len(po_event_counts),
        "n_pos_sampled": len(chosen_pos),
        "n_events_sampled": len(kept_events),
        "n_objects_sampled": len(kept_objects),
    }
    (OUT_DIR / "sample_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
