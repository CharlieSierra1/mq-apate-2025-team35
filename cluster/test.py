# ---------------------------------------------------------
# SIMPLE EMAIL CLUSTERING (NO TF-IDF)
# UMAP + HDBSCAN using SentenceTransformer embeddings
# + Cluster Summary Outputs
# ---------------------------------------------------------

import pandas as pd
from sentence_transformers import SentenceTransformer
import umap
import hdbscan
import matplotlib.pyplot as plt

# ================================================
# 1) Load dataset
# ================================================
df = pd.read_csv("./25432108/Assassin.csv")   # your dataset
print("Loaded:", df.shape)

# Use body text (or subject+body if you want)
df["text"] = df["subject"].fillna("") + " " + df["body"].fillna("")

# Remove empty rows
df = df[df["text"].str.strip().str.len() > 5].reset_index(drop=True)

# ================================================
# 2) Convert text → embeddings using ST model
# ================================================
print("Embedding email text...")

model = SentenceTransformer("all-MiniLM-L6-v2")  # small + accurate

embeddings = model.encode(
    df["text"].tolist(),
    show_progress_bar=True,
    convert_to_numpy=True
)

print("Embeddings shape:", embeddings.shape)

# ================================================
# 3) UMAP dimensionality reduction to 2D
# ================================================
print("Running UMAP...")

umap_model = umap.UMAP(
    n_neighbors=15,
    min_dist=0.1,
    metric="cosine",
    random_state=42
)

X_2d = umap_model.fit_transform(embeddings)

df["umap_x"] = X_2d[:, 0]
df["umap_y"] = X_2d[:, 1]

# ================================================
# 4) HDBSCAN clustering
# ================================================
print("Running HDBSCAN...")

clusterer = hdbscan.HDBSCAN(
    min_cluster_size=20,     # adjust based on dataset size
    min_samples=10,
    metric="euclidean",
    cluster_selection_method="eom"
)

labels = clusterer.fit_predict(X_2d)
df["cluster"] = labels

print("\nCluster counts:")
print(df["cluster"].value_counts())
print("\nUnique clusters:", df["cluster"].unique())

# ================================================
# 5) Save clustered output
# ================================================
df.to_csv("emails_clustered.csv", index=False)
print("\nSaved to emails_clustered.csv")

# ================================================
# 6) Visualize clusters (optional)
# ================================================
plt.figure(figsize=(10, 7))
plt.scatter(df["umap_x"], df["umap_y"], c=df["cluster"], cmap="Spectral", s=10)
plt.title("Email Clusters (UMAP + HDBSCAN)")
plt.show()

# ================================================
# 7) Print HEAD of each cluster
# ================================================
print("\n========== HEAD OF EACH CLUSTER ==========")

for c in sorted(df["cluster"].unique()):
    print("\n----------------------------------------")
    print(f"CLUSTER {c} (first 5 samples)")
    print("----------------------------------------")
    print(df[df["cluster"] == c][["subject", "body"]].head(5))

# ================================================
# 8) Representative sample per cluster
# ================================================
print("\n========== REPRESENTATIVE SAMPLE PER CLUSTER ==========")

for c in sorted(df["cluster"].unique()):
    sub = df[df["cluster"] == c]
    if len(sub) > 0:
        print("\n----------------------------------------")
        print(f"CLUSTER {c} — {len(sub)} emails")
        print("----------------------------------------")
        print("Subject:", sub.iloc[0]["subject"])
        print("Body snippet:", sub.iloc[0]["body"][:300], "...")


from collections import Counter
import re

def clean_text(x):
    x = str(x).lower()
    x = re.sub(r"[^a-z0-9 ]", " ", x)
    return x

cluster_names = {}

for c in sorted(df["cluster"].unique()):
    if c == -1:
        continue  # skip noise
    
    subset = df[df["cluster"] == c]
    text = (subset["subject"].fillna("") + " " + subset["body"].fillna("")).apply(clean_text)

    # Get top words ignoring boring email words
    stopwords = set([
        "the","and","to","in","from","of","for","is","on","at","this","that","with",
        "you","your","are","be","by","it","as","we","i","a","an","or"
    ])

    words = []
    for t in text:
        for w in t.split():
            if len(w) > 3 and w not in stopwords:
                words.append(w)

    top_keywords = [w for w, _ in Counter(words).most_common(10)]

    # Save summary
    cluster_names[c] = {
        "count": len(subset),
        "keywords": top_keywords,
        "sample_subject": subset.iloc[0]["subject"],
        "sample_body": subset.iloc[0]["body"][:300],
    }

# Print summaries
for c, info in cluster_names.items():
    print("\n=========================")
    print(f"CLUSTER {c}")
    print("=========================")
    print("Emails:", info["count"])
    print("Top keywords:", info["keywords"])
    print("Sample subject:", info["sample_subject"])
    print("Sample body snippet:", info["sample_body"])

