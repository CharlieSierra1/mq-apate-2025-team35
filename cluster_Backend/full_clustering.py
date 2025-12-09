# full_clustering.py
import pandas as pd
from sentence_transformers import SentenceTransformer
import umap
import hdbscan
import re
from collections import Counter
from langdetect import detect
import tldextract
import traceback

# ====================================================
# 1) Full clustering pipeline (no Cloudflare here)
# ====================================================
def full_clustering_pipeline(df: pd.DataFrame):
    print("Running FULL clustering pipeline...")

    # -------------------------
    # Combine subject + body
    # -------------------------
    df["text"] = df["subject"].fillna("") + " " + df["body"].fillna("")
    df = df[df["text"].str.strip().str.len() > 5].reset_index(drop=True)

    # -------------------------
    # Embeddings
    # -------------------------
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(
        df["text"].tolist(),
        show_progress_bar=False,
        convert_to_numpy=True
    )

    # -------------------------
    # UMAP
    # -------------------------
    reducer = umap.UMAP(
        n_neighbors=15,
        min_dist=0.1,
        metric="cosine",
        random_state=42
    )
    X_2d = reducer.fit_transform(embeddings)
    df["umap_x"] = X_2d[:, 0]
    df["umap_y"] = X_2d[:, 1]

    # -------------------------
    # HDBSCAN
    # -------------------------
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=20,
        min_samples=10,
        metric="euclidean",
        cluster_selection_method="eom"
    )
    df["cluster"] = clusterer.fit_predict(X_2d)

    print("Clustering done.")
    return df
