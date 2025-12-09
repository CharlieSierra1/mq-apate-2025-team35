# src/clean.py
import re
from langdetect import detect
EMAIL = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}\b')
PHONE = re.compile(r'\b(?:\+?\d[\s-]?){7,}\b')
WALLET = re.compile(r'\b(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b')
def scrub(text):
    text = EMAIL.sub('[EMAIL]', text)
    text = PHONE.sub('[PHONE]', text)
    text = WALLET.sub('[WALLET]', text)
    return text
def filter_lang(df, lang='en'):
    mask = df['text'].fillna('').apply(lambda t: (detect(t) if t else 'unknown')==lang)
    return df[mask]

