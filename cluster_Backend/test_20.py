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

# Ensure text exists
if "text" not in df.columns:
    df["text"] = df["subject"].fillna("") + " " + df["body"].fillna("")

# Add ID column for Cloudflare Worker
df["id"] = df.index.astype(str)

# Build Cloudflare request items
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

try:
    resp = requests.post(
        CLOUDFLARE_URL,
        json=payload,
        headers={"content-type": "application/json"},
        timeout=40
    )
    resp.raise_for_status()
    data = resp.json()
except Exception as e:
    print("\n❌ ERROR calling Cloudflare Worker:", e)
    exit(1)

print("\nCloudflare response received.")

# ==============================
# 3) Extract Cloudflare metadata
# ==============================
cf_rows = []
for item in data.get("items", []):
    cf_rows.append({
        "id": item["id"],
        "cf_archetype": item.get("archetype"),
        "cf_risk": item.get("risk_score"),
        "cf_is_scam": item.get("is_scam"),
        "cf_conf": item.get("scam_confidence"),
        "cf_cluster_cf": item.get("cluster"),
        "cf_indicators": ", ".join(item.get("indicators", [])),
    })

cf_df = pd.DataFrame(cf_rows)

# ==============================
# 4) Merge HDBSCAN clusters + CF output
# ==============================
merged = df.merge(cf_df, on="id", how="left")

print("\nMerged results (first 20 emails):\n")
print(merged[[
    "id",
    "subject",
    "cluster",
    "cf_archetype",
    "cf_conf",
    "cf_risk",
    "cf_is_scam"
]])

# ==============================
# 5) Summary per cluster
# ==============================
print("\n================ CLUSTER → CF ARCHETYPE SUMMARY ================\n")

for cluster_id in merged["cluster"].unique():
    sub = merged[merged["cluster"] == cluster_id]
    print(f"\n🔷 HDBSCAN Cluster {cluster_id} — {len(sub)} emails")

    # Most common CF archetypes for this cluster
    arch_counts = sub["cf_archetype"].value_counts()

    print("Most common CF archetypes:")
    print(arch_counts.to_string())
    print()

    # Confidence average
    avg_conf = sub["cf_conf"].mean()
    print(f"Average CF scam confidence: {avg_conf:.2f}\n")

    print("Emails & their CF classifications:")
    print(sub[["subject", "cf_archetype", "cf_conf"]].to_string(index=False))
    print("\n--------------------------------------------------------------")

print("\nDone.\n")
