# Scammer Clustering + Cloudflare Analysis API
### Endpoint: `POST /api/process`

Uploads a CSV file, runs local clustering + Cloudflare scam analysis, merges, sanitises output, and returns enriched JSON.

---

## Overview

This endpoint accepts a **CSV dataset**, performs:

1. **Clustering** via `full_clustering_pipeline`
2. **Cloudflare NLP phishing analysis** via `call_cloudflare`
3. **Dataset merge** on generated `id`
4. **JSON safety cleaning** (`NaN`, `inf`, `-inf` → `null`)
5. Returns structured JSON including clusters & scam scoring

---

## HTTP Request

### Method
`POST`

### URL
`/api/process`

### Content-Type
`multipart/form-data`

---

## Request Body

### Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `files` | list of `UploadFile` | ✔️ Yes | CSV upload; only `files[0]` is processed |

### Example cURL
```bash
curl -X POST http://localhost:8000/api/process \
  -F "files=@./emails.csv"
  ```

Expected CSV Example
```bash
subject,text,sender
"Security Alert","Your account will be suspended in 24 hours...","no-reply@fakebank.com"
"Delivery Notice","We tried to deliver your package, pay customs here...","courier@fakepost.com"
```
## Processing Workflow
| Step | Action                                           |
| ---- | ------------------------------------------------ |
| 1    | CSV loaded (`pandas.read_csv`)                   |
| 2    | Clustering executed (`full_clustering_pipeline`) |
| 3    | `id` column added (string index)                 |
| 4    | Cloudflare worker invoked (`call_cloudflare`)    |
| 5    | Scam classification + heuristics returned        |
| 6    | Merge clustering & Cloudflare output on `id`     |
| 7    | Convert `NaN`/`inf`/`-inf` → `null`              |
| 8    | JSON response returned with meta + enriched data |

## Successful Response (200)
```json
{
  "meta": {
    "rows": 2,
    "clusters": 2
  },
  "data": [
    {
      "subject": "Security Alert",
      "text": "Your account will be suspended in 24 hours...",
      "sender": "no-reply@fakebank.com",
      "id": "0",
      "cluster": 0,
      "archetype": "Tech Support / Account Suspension",
      "risk_score": 85,
      "is_scam": true,
      "scam_confidence": 90
    },
    {
      "subject": "Delivery Notice",
      "text": "We tried to deliver your package, pay customs here...",
      "sender": "courier@fakepost.com",
      "id": "1",
      "cluster": 1,
      "archetype": "Delivery / Invoice / Package",
      "risk_score": 78,
      "is_scam": true,
      "scam_confidence": 82
    }
  ]
}
```

## Response Schema
### ```meta``` object
| Key        | Type | Description                    |
| ---------- | ---- | ------------------------------ |
| `rows`     | int  | Count of returned dataset rows |
| `clusters` | int  | Count of unique cluster IDs    |
### ```data[]``` entries
| Field                | Provided By               | Description                                        |
| -------------------- | ------------------------- | -------------------------------------------------- |
| original CSV columns | input                     | untouched email/message data                       |
| `id`                 | backend                   | index for merging/traceability                     |
| `cluster`            | clustering                | numerical grouping                                 |
| `archetype`          | Cloudflare worker         | scam type (invoice, romance, delivery, govt, etc.) |
| `risk_score`         | Cloudflare worker         | heuristics score (10–95)                           |
| `scam_confidence`    | Cloudflare worker         | 0–100 probability                                  |
| `is_scam`            | Cloudflare worker         | boolean classification                             |
| + extras             | depends on worker version | e.g., tactics, payment methods                     |

## Error Responses
### Example(500)
```json
{
  "error": "ParserError: Error tokenizing data",
  "trace": "Traceback (most recent call last):\n ..."
}
```
## CORS Policy
Configured to allow public frontend use:
```python
allow_origins=["*"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```
## Versioning
| Component         | Notes                                               |
| ----------------- | --------------------------------------------------- |
| Clustering        | `full_clustering_pipeline` implementation-dependent |
| Cloudflare worker | acts as scam detection + persona engine             |
| CSV schema        | flexible, requires `text` column at minimum         |
