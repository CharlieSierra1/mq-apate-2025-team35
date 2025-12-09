import requests
import pandas as pd
import traceback

CLOUDFLARE_URL = "https://shrill-firefly-47b8.talented-interpreter.workers.dev/analyze"
THRESHOLD = 0.80


def call_cloudflare(df_clustered: pd.DataFrame):
    print("Calling Cloudflare worker from pipeline...")

    items = [
        {
            "id": str(i),
            "subject": row.get("subject", "") or "",
            "text": row.get("text", "") or "",
        }
        for i, row in df_clustered.iterrows()
    ]

    payload = {
        "clusterThreshold": THRESHOLD,
        "items": items
    }

    try:
        response = requests.post(
            CLOUDFLARE_URL,
            json=payload,
            headers={"content-type": "application/json"},
            timeout=120
        )
        response.raise_for_status()

        data = response.json()
    except Exception as e:
        print("Cloudflare error:", e)
        traceback.print_exc()
        raise

    cf_rows = []
    for item in data.get("items", []):
        cf_rows.append({
            "id": item["id"],
            "cf_archetype": item.get("archetype"),
            "cf_risk": item.get("risk_score"),
            "cf_is_scam": item.get("is_scam"),
            "cf_conf": item.get("scam_confidence"),
        })

    return pd.DataFrame(cf_rows)
