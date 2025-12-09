# 🚀 Scam Email Intelligence Dashboard  
### *AI-powered clustering, scam detection, and SOC-grade analytics.*

![Status](https://img.shields.io/badge/status-active-brightgreen)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688?logo=fastapi)
![React](https://img.shields.io/badge/frontend-React-61DBFB?logo=react)
![Cloudflare](https://img.shields.io/badge/LLM-Cloudflare%20Workers%20AI-orange?logo=cloudflare)
![Clustering](https://img.shields.io/badge/Clustering-UMAP%20%2B%20HDBSCAN-purple)
[![API Docs](https://img.shields.io/badge/API_DOCS-Available-blue)](https://github.com/CharlieSierra1/mq-apate-2025-team35/blob/varun/cluster_Backend/backend/APIDOC.md)

---

# 📌 Overview

The **Scam Email Intelligence Dashboard** is an end-to-end AI system that:

### 🔍 **1. Clusters emails automatically**  
Powered by **SentenceTransformer → UMAP → HDBSCAN**, the system groups semantically similar emails — perfect for SOC analysts, cyber fraud teams, and research.

### 🤖 **2. Detects scam archetypes using Cloudflare Workers AI**  
Emails are labeled as *Financial Fraud, Legal Threat, Government Scam, Tax Scam*, etc., with risk scoring and confidence levels.

### 🧠 **3. Provides a SOC-grade Analyst Dashboard**  
Filters, pagination, scam highlighting, clustering insights — all included in a clean React + Tailwind interface.

### 📊 **4. Returns enriched metadata**  
Each email comes with:
- scam/not scam  
- archetype  
- risk score  
- confidence  
- cluster ID  
- sender/receiver processing  
- UMAP coordinates  

---

# 🔗 **API Documentation**

📘 **Full API Documentation:**  
👉 https://github.com/CharlieSierra1/mq-apate-2025-team35/blob/varun/cluster_Backend/backend/APIDOC.md

This includes:
- Endpoint descriptions  
- Request/Response formats  
- Example curl commands  
- Error handling  
- Cloudflare AI integration details  

---

# 🏗️ System Architecture

Here is the full pipeline visual:

![Architecture Diagram](./arch.png)
