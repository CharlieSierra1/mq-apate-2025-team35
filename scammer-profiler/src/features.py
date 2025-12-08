# src/features.py
import pandas as pd, numpy as np, re
from sklearn.feature_extraction.text import TfidfVectorizer
THREAT = re.compile(r'\b(arrest|lawsuit|suspend|immediately|final notice)\b', re.I)
PAYMENT = re.compile(r'\b(steam|itunes|gift\s?card|bitcoin|wallet|wire|zelle|western union)\b', re.I)

def keyword_flags(s):
    return pd.Series({
      'kw_threat': int(bool(THREAT.search(s))),
      'kw_payment': int(bool(PAYMENT.search(s))),
      'url_count': s.count('http'),
      'upper_ratio': sum(c.isupper() for c in s)/max(len(s),1),
      'punct_ratio': sum(c in '!?.,' for c in s)/max(len(s),1)
    })

def build_text_matrix(texts):
    tfidf_char = TfidfVectorizer(analyzer='char', ngram_range=(3,5), min_df=5, max_features=60_000)
    tfidf_word = TfidfVectorizer(analyzer='word', ngram_range=(1,2), min_df=5, max_features=60_000, stop_words='english')
    Xc = tfidf_char.fit_transform(texts)
    Xw = tfidf_word.fit_transform(texts)
    return (Xc, tfidf_char), (Xw, tfidf_word)
