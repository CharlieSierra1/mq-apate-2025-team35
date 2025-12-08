# src/cluster.py
import umap, hdbscan, numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
def embed_umap(X, n_neighbors=30, min_dist=0.1, n_components=10):
    reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, n_components=n_components, metric='cosine', random_state=42)
    return reducer, reducer.fit_transform(X)
def cluster_hdbscan(emb, min_cluster_size=30, min_samples=None):
    cl = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples, metric='euclidean', cluster_selection_epsilon=0.0)
    labels = cl.fit_predict(emb)
    return cl, labels
