# src/evaluation.py
from sklearn.metrics import silhouette_score
def evaluate_embeddings(emb, labels):
    mask = labels!=-1
    if mask.sum()>1 and len(set(labels[mask]))>1:
        return {"silhouette": float(silhouette_score(emb[mask], labels[mask]))}
    return {"silhouette": None}
