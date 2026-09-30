"""One-off scan (not part of the final experiment): stream the full BPIC19
OCEL jsonocel and count events per cCompany, to choose a real subsidiary
company as the basis for a manageable, real-data subsample."""
import ijson
from collections import Counter

PATH = "/workspace/datasets/bpic2019_ocel/BPIC19.jsonocel"

company_counts = Counter()
po_counts = Counter()
n = 0
with open(PATH, "rb") as f:
    for event_id, event in ijson.kvitems(f, "ocel:events"):
        n += 1
        vmap = event.get("ocel:vmap", {})
        company_counts[vmap.get("cCompany")] += 1
        po_counts[vmap.get("cPOID")] += 0  # placeholder, not used
        if n % 200000 == 0:
            print(f"...{n} events scanned")

print("Total events:", n)
print("Top 15 companies by event count:")
for company, cnt in company_counts.most_common(15):
    print(f"  {company}: {cnt}")
print("Number of distinct companies:", len(company_counts))
