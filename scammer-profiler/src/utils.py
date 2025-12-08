"""
Shared utilities for config, logging, randomness, text normalization, entity/PII helpers,
and small dataframe/IO helpers used across the pipeline.

Usage:
    from src.utils import (
        load_config, deep_update, get_logger, seed_everything, normalize_text,
        EMAIL_RE, PHONE_RE, WALLET_RE, URL_RE, DOMAIN_RE,
        extract_domains, hash_token, pii_tokenize, ensure_dir, batch, ensure_columns
    )
"""

from __future__ import annotations
import os
import re
import sys
import json
import math
import yaml
import hashlib
import random
import logging
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Tuple, Any, Optional

# ---------- Regexes (shared across modules) ----------
EMAIL_RE  = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}\b")
PHONE_RE  = re.compile(r"\b(?:\+?\d[\s\-()]?){7,}\d\b")
# Basic BTC (legacy/segwit) – extend if needed:
WALLET_RE = re.compile(r"\b(?:bc1|[13])[a-km-zA-HJ-NP-Z1-9]{25,39}\b")
URL_RE    = re.compile(r"https?://[^\s)>\]]+")
DOMAIN_RE = re.compile(r"https?://([^/\s)>\]]+)")

# ---------- Config ----------
_DEFAULT_CONFIG_PATH = Path("configs/app.yaml")

def deep_update(base: dict, overrides: dict) -> dict:
    """Recursively update nested dicts (overrides wins)."""
    out = dict(base)
    for k, v in (overrides or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_update(out[k], v)
        else:
            out[k] = v
    return out

def load_config(path: Optional[str | Path] = None, default_if_missing: bool = True) -> dict:
    """
    Load YAML config and merge onto sane defaults so the app runs even if fields are absent.
    """
    defaults = {
        "app": {"title": "Scammer Persona Profiler", "theme": "light"},
        "logging": {"level": "INFO"},
        "random_seed": 42,
        "data": {"expected_fields": ["id","source","text","timestamp","channel","sender_id","recipient_id","meta"],
                 "language": "en"},
        "preprocessing": {
            "lang_filter": True,
            "target_lang": "en",
            "pii_mask": True,
            "dedupe": {"enabled": False, "threshold": 0.9}
        },
        "features": {
            "tfidf_char": {"ngram_range": [3,5], "min_df": 5, "max_features": 60000},
            "tfidf_word": {"ngram_range": [1,2], "min_df": 5, "max_features": 60000, "stop_words": "english"}
        },
        "umap": {"n_neighbors": 30, "min_dist": 0.1, "n_components": 10, "metric": "cosine"},
        "hdbscan": {"min_cluster_size": 30, "min_samples": None, "cluster_selection_epsilon": 0.0},
        "network": {"text_sim_tau": 0.75, "cooccurrence_min": 1},
        "ui": {"max_text_len": 500, "enable_bias_panel": True},
        "ethics": {
            "public_data_only": True,
            "false_positive_disclaimer": (
                "Archetypes are probabilistic; manual analyst review is required before enforcement."
            )
        },
        "export": {"dir": "exports", "rules_filename": "persona_rules.json"}
    }

    cfg_path = Path(path) if path else _DEFAULT_CONFIG_PATH
    if not cfg_path.exists():
        if default_if_missing:
            return defaults
        raise FileNotFoundError(f"Config not found at {cfg_path}")

    with open(cfg_path, "r", encoding="utf-8") as f:
        user_cfg = yaml.safe_load(f) or {}
    return deep_update(defaults, user_cfg)

# ---------- Logging ----------
_LOGGERS: Dict[str, logging.Logger] = {}

def get_logger(name: str = "scammer_profiler", level: Optional[str] = None) -> logging.Logger:
    if name in _LOGGERS:
        return _LOGGERS[name]
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        fmt = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
    logger.propagate = False
    logger.setLevel(getattr(logging, (level or "INFO").upper(), logging.INFO))
    _LOGGERS[name] = logger
    return logger

# ---------- Reproducibility ----------
def seed_everything(seed: int = 42) -> None:
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except Exception:
        pass
    os.environ["PYTHONHASHSEED"] = str(seed)

# ---------- Text ----------
def normalize_text(text: str) -> str:
    """
    Unicode normalize + strip + collapse whitespace.
    Keeps case (don’t .lower() here; TF-IDF vectorizer handles case by config).
    """
    if text is None:
        return ""
    t = unicodedata.normalize("NFKC", str(text))
    t = re.sub(r"\s+", " ", t).strip()
    return t

# ---------- Entities / PII ----------
def extract_domains(text: str) -> List[str]:
    return DOMAIN_RE.findall(text or "")

def _blake2s(data: str, salt: str = "") -> str:
    h = hashlib.blake2s(digest_size=16, person=b"scam-profiler")
    h.update(salt.encode("utf-8"))
    h.update(data.encode("utf-8"))
    return h.hexdigest()

def hash_token(value: str, salt: str = "pii") -> str:
    """Stable, non-reversible token for PII surfaces (emails/phones/wallets)."""
    return _blake2s(value, salt=salt)

def pii_tokenize(text: str, salt: str = "pii") -> Tuple[str, Dict[str, List[str]]]:
    """
    Replace emails/phones/wallets with stable tokens, return redacted text and a mapping
    (kept in memory or local secure store if needed).
    """
    mapping = {"EMAIL": [], "PHONE": [], "WALLET": []}
    def _sub(pattern, tag, s):
        def repl(m):
            raw = m.group(0)
            tok = f"[{tag}:{hash_token(raw, salt)[:8]}]"
            mapping[tag].append(raw)
            return tok
        return pattern.sub(repl, s)
    out = text or ""
    out = _sub(EMAIL_RE,  "EMAIL",  out)
    out = _sub(PHONE_RE,  "PHONE",  out)
    out = _sub(WALLET_RE, "WALLET", out)
    return out, mapping

# ---------- Data / IO helpers ----------
def ensure_dir(p: str | Path) -> Path:
    path = Path(p)
    path.mkdir(parents=True, exist_ok=True)
    return path

def batch(it: Iterable[Any], n: int) -> Iterator[List[Any]]:
    buf = []
    for x in it:
        buf.append(x)
        if len(buf) >= n:
            yield buf
            buf = []
    if buf:
        yield buf

def ensure_columns(df, required: List[str]) -> None:
    """Raise an informative error if required columns are missing."""
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Got: {list(df.columns)}")

# ---------- Safe JSON dump ----------
def safe_json_dump(obj: Any, path: str | Path, indent: int = 2) -> None:
    ensure_dir(Path(path).parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)
