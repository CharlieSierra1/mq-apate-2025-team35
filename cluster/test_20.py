# test_20.py — Test Cloudflare + HDBSCAN comparison for first 20 emails

import pandas as pd
import requests

CSV_PATH = "emails_clustered.csv"
CLOUDFLARE_URL = "https://shrill-firefly-47b8.talented-interpreter.workers.dev/analyze"
CLUSTER_THRESHOLD = 0.80

# ==============================
# 1) Load only first 20 records
# ==============================
df = pd.read_csv(CSV_PATH).head(20).copy()
print("Loaded 20 emails")

# Ensure we have text for analysis
if "text" not in df.columns:
    df["text"] = df["subject"].fillna("") + " " + df["body"].fillna("")

# Ensure an ID column exists
df["id"] = df.index.astype(str)

# Build items for Cloudflare
items = [
    {
        "id": str(row["id"]),
        "subject": row.get("subject", "") or "",
        "text": row.get("text", "") or "",
    }
    for _, row in df.iterrows()
]

payload = {
    "clusterThreshold": CLUSTER_THRESHOLD,
    "items": items,
}

# ==============================
# 2) Call Cloudflare Worker
# ==============================
print("\nCalling Cloudflare Worker…")

resp = requests.post(
    CLOUDFLARE_URL,
    json=payload,
    headers={"content-type": "application/json"},
)

resp.raise_for_status()
data = resp.json()

print("\nCloudflare response received.")

# Extract CF annotations
cf_rows = []
for item in data["items"]:
    cf_rows.append({
        "id": item["id"],
        "cf_archetype": item.get("archetype"),
        "cf_risk": item.get("risk_score"),
        "cf_is_scam": item.get("is_scam"),
        "cf_conf": item.get("scam_confidence"),
        "cf_cluster_cf": item.get("cluster"),
    })

cf_df = pd.DataFrame(cf_rows)

# ==============================
# 3) Merge HDBSCAN clusters + Cloudflare output
# ==============================
merged = df.merge(cf_df, on="id", how="left")
print("\nMerged results:\n")
print(merged[[
    "id", "subject", "cluster", "cf_archetype", "cf_conf", "cf_risk", "cf_is_scam"
]])

# ==============================
# 4) Summarize cluster → archetype agreement
# ==============================
print("\nSummary (HDBSCAN cluster → CF archetype):\n")

for cluster_id in merged["cluster"].unique():
    sub = merged[merged["cluster"] == cluster_id]
    print(f"Cluster {cluster_id} — {len(sub)} emails")

    print(sub[["subject", "cf_archetype", "cf_conf"]])
    print("\n---\n")

print("\nDone.")
