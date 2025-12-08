# src/ingest.py
import pandas as pd, json, pathlib
def load_any(path): 
    p = pathlib.Path(path)
    if p.suffix=='.csv': return pd.read_csv(p)
    if p.suffix in ('.json','.ndjson'):
        return pd.read_json(p, lines=(p.suffix=='.ndjson'))
    raise ValueError("Unsupported format")
