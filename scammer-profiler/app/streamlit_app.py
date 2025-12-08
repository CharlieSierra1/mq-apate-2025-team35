# app/streamlit_app.py
import streamlit as st
import pandas as pd
from src.ingest import load_any
from src.clean import scrub, filter_lang
from src.features import build_text_matrix, keyword_flags
from src.cluster import embed_umap, cluster_hdbscan
from src.networks import build_graph, louvain_partition
import plotly.express as px

st.set_page_config(page_title="Scammer Persona Profiler", layout="wide")

st.sidebar.header("Pipeline")
uploaded = st.sidebar.file_uploader("Upload CSV/JSON/NDJSON", type=["csv","json","ndjson"])
if uploaded:
    df = load_any(uploaded)
    df['text'] = df['text'].fillna('').apply(scrub)
    df = filter_lang(df, 'en')
    flags = df['text'].apply(keyword_flags)
    df = pd.concat([df, flags], axis=1)

    (Xc, vchar), (Xw, vword) = build_text_matrix(df['text'])
    from scipy.sparse import hstack
    X = hstack([Xc, Xw])

    reducer, emb = embed_umap(X, n_neighbors=st.sidebar.slider("UMAP n_neighbors",5,80,30))
    cl, labels = cluster_hdbscan(emb, min_cluster_size=st.sidebar.slider("Min cluster size",10,100,30))
    df['cluster'] = labels

    st.subheader("Cluster Map")
    fig = px.scatter(x=emb[:,0], y=emb[:,1], color=df['cluster'].astype(str), hover_data={'text':True})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Persona Cards")
    for c in sorted(df['cluster'].unique()):
        if c==-1: continue
        sub = df[df.cluster==c]
        st.markdown(f"### Cluster {c} · n={len(sub)}")
        st.write({
            "threat_rate": float(sub['kw_threat'].mean()),
            "payment_rate": float(sub['kw_payment'].mean()),
            "top_domains": sub['text'].str.extractall(r'https?://([^/\s]+)').value_counts().head(5).to_dict()
        })

    st.subheader("Network")
    G = build_graph(df)
    st.write(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()} (use PyVis / streamlit-pyvis for interactive view)")
