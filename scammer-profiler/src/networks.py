# src/networks.py
import networkx as nx
def build_graph(df):
    G = nx.Graph()
    for _,r in df.iterrows():
        scammer = f"s:{r.get('sender_id','unknown')}"
        for ent_col in ['email_token','phone_token','wallet_token','domain_token']:
            ent = r.get(ent_col)
            if ent:
                G.add_edge(scammer, f"e:{ent}", kind=ent_col)
    return G
def louvain_partition(G):
    import community as community_louvain
    return community_louvain.best_partition(G)  # returns node->community
