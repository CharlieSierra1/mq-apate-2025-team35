# compare_clusters.py
import pandas as pd
import requests
import math
from collections import Counter

# ==============================
# CONFIG
# ==============================
CSV_PATH = "emails_clustered.csv"    # from your UMAP+HDBSCAN script
CLOUDFLARE_URL = "https://shrill-firefly-47b8.talented-interpreter.workers.dev/analyze"
BATCH_SIZE = 100                     # how many emails per API call
CLUSTER_THRESHOLD = 0.80             # same as your curl example

# ==============================
# 1) Load clustered data
# ==============================
df = pd.read_csv(CSV_PATH)
print("Loaded clustered CSV:", df.shape)

# Ensure we have an ID column we can roundtrip via API
if "id" not in df.columns:
    df["id"] = df.index.astype(str)

# We'll send subject + text (or subject + body) to the Worker
if "text" not in df.columns:
    df["text"] = df["subject"].fillna("") + " " + df["body"].fillna("")

# ==============================
# 2) Helper: call Cloudflare API for a batch
# ==============================
def call_cloudflare_batch(batch_df):
    items = []
    for _, row in batch_df.iterrows():
        items.append({
            "id": str(row["id"]),
            "subject": row.get("subject", "") or "",
            "text": row.get("text", "") or "",
        })

    payload = {
        "clusterThreshold": CLUSTER_THRESHOLD,
        "items": items,
    }

    resp = requests.post(
        CLOUDFLARE_URL,
        json=payload,
        headers={"content-type": "application/json"},
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return data

# ==============================
# 3) Call Cloudflare in batches
# ==============================
cf_rows = []

n = len(df)
num_batches = math.ceil(n / BATCH_SIZE)
print(f"Sending {n} emails to Cloudflare in {num_batches} batches...")

for b in range(num_batches):
    start = b * BATCH_SIZE
    end = min(n, (b + 1) * BATCH_SIZE)
    batch = df.iloc[start:end]
    print(f"Batch {b+1}/{num_batches}: rows {start}–{end-1}")

    data = call_cloudflare_batch(batch)

    # `data["items"]` contains annotations we care about
    for item in data.get("items", []):
        cf_rows.append({
            "id": item.get("id"),
            "cf_archetype": item.get("archetype"),
            "cf_is_scam": item.get("is_scam"),
            "cf_scam_confidence": item.get("scam_confidence"),
            "cf_risk_score": item.get("risk_score"),
            "cf_cluster_cf": item.get("cluster"),
            "cf_warning": item.get("warning"),
        })

cf_df = pd.DataFrame(cf_rows)
print("Cloudflare annotations:", cf_df.shape)

# ==============================
# 4) Merge HDBSCAN clusters + CF archetypes
# ==============================
merged = df.merge(cf_df, on="id", how="left")
print("Merged shape:", merged.shape)

# Save for later use in your React app / dashboard
merged.to_csv("emails_with_cf_and_hdbscan.csv", index=False)
print("Saved merged CSV: emails_with_cf_and_hdbscan.csv")

# ==============================
# 5) Compute majority archetype per HDBSCAN cluster
# ==============================
cluster_summary = []

for c in sorted(merged["cluster"].unique()):
    sub = merged[merged["cluster"] == c]
    cf_arches = sub["cf_archetype"].dropna().tolist()

    if len(cf_arches) == 0:
        majority = None
        majority_pct = 0.0
    else:
        counts = Counter(cf_arches)
        majority, majority_count = counts.most_common(1)[0]
        majority_pct = majority_count / len(cf_arches) * 100.0

    cluster_summary.append({
        "hdb_cluster": c,
        "size": len(sub),
        "majority_cf_archetype": majority,
        "majority_cf_share_pct": round(majority_pct, 1),
    })

summary_df = pd.DataFrame(cluster_summary).sort_values("size", ascending=False)
print("\n=== HDBSCAN cluster → CF archetype alignment ===")
print(summary_df.head(20))

# ==============================
# 6) Per-email agreement flag
# ==============================
# Option 1: define persona per HDBSCAN cluster as that majority CF archetype
cluster_to_persona = {
    row["hdb_cluster"]: row["majority_cf_archetype"]
    for _, row in summary_df.iterrows()
}

merged["hdb_persona_from_cf"] = merged["cluster"].map(cluster_to_persona)
merged["persona_agree"] = merged["hdb_persona_from_cf"] == merged["cf_archetype"]

overall_agree = merged["persona_agree"].mean() * 100.0
print(f"\nOverall persona agreement between HDBSCAN cluster and CF archetype: {overall_agree:.1f}%")

# Save again with persona info
merged.to_csv("emails_with_personas_and_agreement.csv", index=False)
print("Saved: emails_with_personas_and_agreement.csv")
