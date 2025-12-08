# src/personas.py
import numpy as np, pandas as pd
from collections import Counter
def persona_from_cluster(df_cluster, tfidf_vocab, top_k=12):
    # naive top terms from a precomputed per-doc word tfidf list (pass in as df col if needed)
    terms = Counter()
    for row in df_cluster.get('top_terms', []): terms.update(row)
    top_terms = [t for t,_ in terms.most_common(top_k)]
    flags = df_cluster[['kw_threat','kw_payment']].mean().round(2).to_dict()
    return {
      "name": f"{'Tech-Support' if flags['kw_threat']>0.3 else 'Romance'} Impersonator #{int(df_cluster.name) if hasattr(df_cluster,'name') else 0}",
      "top_terms": top_terms,
      "signals": flags,
      "n_samples": len(df_cluster),
      "narrative": "Targets victims via urgent account-suspension claims, pushes gift cards/crypto with short deadlines.",
      "mitigations": [
        "Hold payments pending verified callback to official numbers.",
        "Block listed domains/shorteners; alert on gift-card lexicon.",
        "Template responses to stall + collect artifacts without engagement."
      ]
    }
