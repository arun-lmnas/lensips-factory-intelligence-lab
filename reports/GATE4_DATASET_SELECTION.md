# Gate 4 Dataset Selection — Object-Centric Manufacturing Intelligence Research

## Why this document exists

The first Gate 4 attempt
([reports/GATE4_MULTI_OBJECT_RECONNAISSANCE.md](GATE4_MULTI_OBJECT_RECONNAISSANCE.md),
commits `76a411c..4902fd3`) reused the Gate 2/3 machine-shop event log
(`datasets/production_analysis/Production_Data.csv`). That log has an
order, an operation, a machine and a worker per event, but no material,
supplier, or genuinely independent quality-event object — everything
reduces to attributes of a single case-centric trace. It could not
properly test the object-centric hypothesis. That report and its
conclusions are not rewritten here; this document explains the dataset
used for the restarted experiment
([reports/GATE1_TO_GATE4_RESEARCH_SUMMARY.md](GATE1_TO_GATE4_RESEARCH_SUMMARY.md)).

## 1. Dataset name

**BPI Challenge 2019 (OCEL)** — an OCEL 1.0-format transformation of the
original BPI Challenge 2019 event log.

## 2. Source / provenance

- OCEL transformation: Shahrzad Khayatbashi, Olaf Hartig, Amin Jalali
  (Linköping University / Stockholm University), published via 4TU.ResearchData,
  DOI `10.4121/46a7e15b-10c7-4ab2-988d-ee67d8ea515a`. Produced with the
  open-source `neo4pm` transformation tool as part of Khayatbashi's PhD
  thesis work, documented in "Transforming Event Knowledge Graph to
  Object-Centric Event Logs: A Comparative Study for Multi-dimensional
  Process Analysis."
- Original event log: BPI Challenge 2019, DOI
  `10.4121/uuid:d06aff4b-79f0-45e6-8ec8-e19730c248f1`, released for the
  2019 Business Process Intelligence Challenge (IEEE Task Force on Process
  Mining).
- Downloaded directly from 4TU.ResearchData
  (`https://data.4tu.nl/datasets/46a7e15b-10c7-4ab2-988d-ee67d8ea515a`) —
  not re-hosted or modified upstream of our own sampling step (§16).

## 3. License

CC BY 4.0, as stated on the 4TU.ResearchData landing page. Attribution
above.

## 4. Manufacturing context

Real operational data from **a large multinational company headquartered
in the Netherlands, operating in coatings and paints**, covering the
**purchase order handling ("purchase-to-pay") process for some of its 60
subsidiaries**. This is a real manufacturer's real procurement process —
not a synthetic or lab dataset, and not shop-floor production data. It
supplies the material/vendor/supplier-relationship dimension the Gate 4 v1
dataset lacked; it does not supply machine/work-centre shop-floor
operations (see §14).

## 5. Event count

Full log: **1,595,923 events**, 42 distinct activities, 627 users (607
human, 20 batch/automated). Our working sample (§16): **20,011 events**,
35 distinct activities.

## 6. Case / object counts

Full log: 76,349 purchase documents, 251,734 purchase-order line items
(the classical "case" notion used by the original, non-OCEL BPIC19
log). Distributed across only 4 distinct company IDs in this OCEL
transformation, heavily skewed to one subsidiary
(`companyID_0000`: 1,590,010 of 1,595,923 events, 99.6%; the other three
combined account for 15 events and were excluded from sampling as too
small to represent a coherent process on their own).

Our sample: 1,011 purchase orders (of 75,962 available for
`companyID_0000`), 4,780 objects total.

## 7. Object types

Four genuine OCEL object types, confirmed by loading the file with
`pm4py.read_ocel` and inspecting `ocel.objects`:

| Object type | Count in full sample | What it represents |
|---|---|---|
| `PO` | 1,011 | Purchase order / purchase document |
| `POItem` | 3,044 | A line item within a purchase order (the classical "case") |
| `Vendor` | 409 | The supplier the purchase order was sent to |
| `Resource` | 316 | The human user or automated batch process that performed an event |

No `Material` or standalone `Quality` object type exists in this dataset
(see §14).

## 8. Event types

35 activities present in the sample (of 42 in the full log), covering the
full purchase-to-pay lifecycle: `Create Purchase Requisition Item`,
`Create Purchase Order Item`, `Receive Order Confirmation`,
`Record Goods Receipt` / `Cancel Goods Receipt`,
`Record Invoice Receipt` / `Cancel Invoice Receipt`,
`Vendor creates invoice` / `Vendor creates debit memo`, `Clear Invoice`,
`Remove Payment Block` / `Set Payment Block`, `Change Price` /
`Change Quantity` / `Change Currency`, several `SRM:` sourcing-workflow
events, and others. Full counts are in
[experiments/gate4b_object_centric_research/results/results.json](../experiments/gate4b_object_centric_research/results/results.json)
under `dataset_summary.activity_counts`.

## 9. Relationships available

Each event is linked (via the OCEL `omap`) to a subset of `PO`, `POItem`,
`Vendor`, and `Resource` objects simultaneously — e.g. a single
`Record Goods Receipt` event is linked to the PO, the specific item, the
vendor that shipped it, and the user/batch process that recorded it. This
is a genuine multi-object relationship structure, not a flattened table
with foreign-key-shaped columns: `pm4py.discover_objects_graph` (object
co-occurrence) and `pm4py.discover_ocdfg` (per-object-type
directly-follows) both operate directly on it. See
[reports/GATE1_TO_GATE4_RESEARCH_SUMMARY.md](GATE1_TO_GATE4_RESEARCH_SUMMARY.md)
§7 for what these relationships actually revealed.

## 10. Timestamp quality

Sampled events span **2016-04-04 to 2019-01-17**, consistent, parseable
ISO timestamps at minute granularity. One known artefact: the very first
record physically in the full 1.5 GB source file carries an anonymized
timestamp of `1948-01-26` — a known date-shift/anonymization artefact of
the original BPIC19 release, not a data-quality issue in our sample (the
sampled 20,011-event subset does not include that record; verified by the
min/max check above).

## 11. Resource information

The `Resource` object type is populated on 14,858 of 20,011 sampled events
(74.3%); the remainder record `resource == "NONE"`, meaning the source SAP
system did not log a user for that event (documented in the BPIC19
README, not a defect we introduced). 316 distinct resources appear,
mixing named human users (`user_NNN`) and automated batch processes
(`batch_NN`).

## 12. Quality / material / supplier information

- **Supplier (Vendor)**: present and central to the dataset — 409 distinct
  vendors in the sample, each linked to the POs/items it supplied. This is
  the object type the Gate 4 v1 dataset entirely lacked.
- **Material**: **not present as a distinct object**. The dataset carries
  material-adjacent event *attributes* (`cSpendAreaText`,
  `cSpendClassText`, `cSubSpendAreaText` — free-text spend classification)
  but no material-lot or BOM object that events reference the way they
  reference PO/POItem/Vendor/Resource. Any question requiring a true
  Material object (e.g. "which material lot's defect propagated to which
  orders") is out of scope for this dataset too — see §14 and the
  Demonstrated/Plausible/Unknown section of the main report.
- **Quality**: **not present**. This is a purchase-to-pay process; there
  is no inspection, defect, or rework event type. Quality-linked questions
  from the Gate 4 brief could not be tested here either, and are marked
  NOT DEMONSTRATED, same as material.

## 13. Why this dataset is suitable for Gate 4

- It is a **real** dataset (not synthetic), from a **real manufacturer**,
  with **public, citable provenance** and a **permissive license**.
- It already contains **four genuine, independently-identified object
  types** with real many-to-many relationships between them (a Vendor
  supplies many POs; a PO has many items; a Resource processes many items
  across many different POs) — the structural precondition the Gate 4 v1
  dataset failed to meet.
- It loads as a valid OCEL with `pm4py.read_ocel` with no relationship
  invention or reshaping required (see §15/§16) — object-centric analysis
  functions (`discover_ocdfg`, `discover_objects_graph`) run directly
  against it.
- It is large enough (1.6M events) to sample a meaningfully-sized,
  representative real-data subset (§16) rather than requiring synthetic
  extension.

## 14. What important information is still absent

- **No Material/BOM object** — supply-chain questions phrased in terms of
  "material shortage" rather than "vendor" cannot be tested here.
- **No Quality/inspection object** — quality-propagation questions from
  the original Gate 4 brief cannot be tested here either.
- **No shop-floor machine/operation object** — this is a back-office
  procurement process, not a production floor; "which machine is a
  cross-order bottleneck" (answerable on the Gate 4 v1 dataset) is not
  answerable on this one.
- No dataset we found combines real shop-floor production data (machine,
  operation) *and* real material/supplier/quality objects at the multi-
  object relationship level required — this is disclosed as a genuine gap
  in available public data, not resolved by inventing one.

## 15. Whether the dataset is already OCEL

Yes. The 4TU release is distributed as `*.jsonocel`, conforming to the
`ocel:version 1.0` schema (`ocel:events`, `ocel:objects`,
`ocel:global-log` with `ocel:object-types` and `ocel:attribute-names`).
Verified by loading it with `pm4py.read_ocel` and inspecting
`ocel.get_summary()` before any sampling was applied. It is OCEL 1.0, not
OCEL 2.0 (the object-type/attribute schema is flatter — objects carry no
own attributes, only events do); this does not affect suitability for
Gate 4, since the multi-object relationships (not the schema version) are
what the experiment tests, and `pm4py.discover_ocdfg` /
`pm4py.discover_objects_graph` both operate on OCEL 1.0 logs unchanged.

## 16. Sampling: exactly how it is performed

The full file (`BPIC19.jsonocel`, 1,526,253,626 bytes, 1,595,923 events)
is too large to process directly in a small, terminating reconnaissance
experiment. We built a **real-data subsample**, not a synthetic dataset,
using
[experiments/gate4b_object_centric_research/scripts/build_sample.py](../experiments/gate4b_object_centric_research/scripts/build_sample.py):

1. **Pass 1** — stream the full log once with `ijson` (a streaming JSON
   parser, so the 1.5 GB file is never loaded into memory at once), and
   count events per Purchase Order (`cPOID`), restricted to
   `cCompany == "companyID_0000"` (the dominant subsidiary; the other
   three were excluded as statistically negligible — 15 events total —
   rather than mixed in, which would have blurred one coherent process
   into a fragment of four).
2. **Choose POs** — with a fixed random seed (`42`), shuffle the 75,962
   eligible purchase orders and greedily add whole POs (never partial —
   every event belonging to a sampled PO is kept) until a 20,000-event
   budget is reached. Result: 1,011 POs, 20,011 events.
3. **Pass 2** — stream the full log again, keep only events belonging to
   a sampled PO, and record every object id referenced in their `omap`.
4. **Pass 3** — stream the `ocel:objects` section once, keep only objects
   referenced by a kept event.
5. Write the filtered result as a standard OCEL 1.0 `jsonocel` file:
   [datasets/bpic2019_ocel/sample/BPIC19_sample.jsonocel](../datasets/bpic2019_ocel/sample/BPIC19_sample.jsonocel)
   (13.8 MB), with a manifest recording the exact parameters used
   ([datasets/bpic2019_ocel/sample/sample_manifest.json](../datasets/bpic2019_ocel/sample/sample_manifest.json)).

No event was fabricated, reordered, merged, or altered. No relationship
was invented: every PO↔POItem↔Vendor↔Resource link in the sample is a
link that existed in the original real BPIC19 OCEL log. The only
transformation applied is *selection* (which whole purchase orders to
keep), which is disclosed here and reproducible from the script with the
same seed. The original 1.5 GB source file and its zip archives are not
committed to this repository (git is not suited to files that size); only
the 13 MB sample, its manifest, and the original dataset's `README.txt`
(kept for provenance) are checked in under `datasets/bpic2019_ocel/`.
Re-running `build_sample.py` requires re-downloading the source archive
from the DOI above.
