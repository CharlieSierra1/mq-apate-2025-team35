# backend/main.py
import io
import pandas as pd
import traceback
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from full_clustering import full_clustering_pipeline
from cloudflare_client import call_cloudflare

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/process")
async def process_file(files: list[UploadFile] = File(...)):

    try:
        # Read CSV
        file = files[0]
        raw = await file.read()
        df = pd.read_csv(io.BytesIO(raw))

        print(f"Loaded {len(df)} rows.")

        # 1) Run clustering
        df_clustered = full_clustering_pipeline(df)
        df_clustered["id"] = df_clustered.index.astype(str)

        # 2) Call Cloudflare (WAIT HERE)
        print("\n=== CALLING CLOUDFLARE (FINAL) ===")
        cf_df = call_cloudflare(df_clustered)
        print("Cloudflare analysis done.")

        # 3) Merge clustering + CF
        print("Merging...")
        final = df_clustered.merge(cf_df, on="id", how="left")

        # 4) Return JSON
        return JSONResponse(
            content={
                "meta": {
                    "rows": len(final),
                    "clusters": final["cluster"].nunique(),
                },
                "data": final.to_dict(orient="records"),
            }
        )

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace": traceback.format_exc()}
        )
