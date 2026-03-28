# Green-Truth Auditor: The Intent-Aware Sustainability Engine
### *Combating Greenwashing through Hybrid NLP, Verified Data, and Competitive Analysis*

[![Theme: Responsible Consumption](https://img.shields.io/badge/Theme-Climate%20Action-green)](#)
[![Accuracy: 87.5%](https://img.shields.io/badge/System_Accuracy-87.5%25-blueviolet)](#)
[![Model: BART-MNLI](https://img.shields.io/badge/Model-BART--MNLI-blue)](#)
[![Status: Live MVP](https://img.shields.io/badge/Status-Hackathon_Prototype-orange)](#)

## The Challenge: "Marketing Fluff" vs. Reality
In the modern market, **"Greenwashing"** creates a massive trust deficit. Brands often use vague marketing buzzwords like *"eco-friendly"* or *"natural"* to mask high-carbon supply chains. The **Green-Truth Auditor** is a transparency tool that uses an **Intent-Aware logic system** to parse product descriptions, extract metadata from URLs, and verify claims against global sustainability databases.

---

##  Key Features & Innovations
* **URL Metadata Scraper:** Beyond simple text input, the tool can ingest URLs from major e-commerce platforms, automatically extracting product descriptions for seamless auditing.
* **Weighted Scoring Dashboard:** A professional UI featuring **Real-time Gauge Charts** that translate complex NLP outputs into an intuitive 0-100 Trust Score.
* **Visual Reasoning Breakdown:** Every audit provides a human-readable "Reasoning Summary" explaining exactly *why* a product failed (e.g., "Uses vague terms," "No certification found").
* **Future Promise Penalty:** A custom logic-gate that detects and penalizes vague long-term goals (e.g., "Net Zero by 2050") that lack immediate transparency or roadmaps.

---

## Datasets used and Preprocessing
To provide a "Source of Truth," we integrated three major certification databases:
1.  **B-Corp Global Directory:** Companies verified for high social and environmental performance.
2.  **GOTS (Global Organic Textile Standard):** The gold standard for organic fiber processing.
3.  **Indian Certification Registry:** A curated list of regional sustainability markers.

### Preprocessing Steps:
* **Database Standardization:** Unified inconsistent column names across different CSV formats to ensure accurate brand-matching.
* **Relevance Gating:** Segmented descriptions into sentences and filtered out non-environmental text (e.g., shipping info, sizing) to reduce model noise.
* **Keyword Normalization:** Handled case-insensitivity and special characters to ensure robust database cross-referencing.

---

## Model Used & Performance Metrics
Our system uses a **Hybrid Architecture** combining a deep-learning transformer model with deterministic environmental logic.

* **Core Model:** `facebook/bart-large-mnli` (Zero-Shot Classification).
* **Classification Strategy:** Classifies sentence intent as *"Objective Environmental Fact"* vs. *"Vague Marketing Fluff."*

---

### Demo Video:
https://drive.google.com/file/d/1Onlr5d5nSulAsQcqy3LX6YhUJlwTDNCW/view?usp=sharing

---

### Performance Metrics:
| Metric | Value | Note |
| :--- | :--- | :--- |
| **System Accuracy** | **87.5%** | Measured by correct classification of "Legitimate" vs "Greenwashing" labels. |
| **Precision** | **0.80** | Demonstrates high reliability in identifying true evidence without over-penalizing. |

> **Strategic Achievement:** Our **Hybrid Logic Gate** (Logic-based overrides) improved the accuracy from a baseline of 50% (raw NLP) to a final system accuracy of **87.5%**.

---

## Tech Stack
* **Frontend:** Streamlit (Visual Dashboards)
* **NLP:** HuggingFace Transformers (BART-MNLI)
* **Visuals:** Plotly (Dynamic Gauges & Distribution Charts)
* **Data Handling:** Pandas, NumPy

---

## Future Scope
* **Browser Extension:** A Chrome plugin to provide real-time trust scores while shopping on Amazon or Flipkart.
* **Agentic RAG:** Using AI Agents to browse the web for a company’s latest Annual Sustainability Report in real-time.
* **Mobile App with OCR:** Allowing users to scan physical product barcodes in stores to get an instant sustainability audit.
* **Competitor Comparison (The Unique Edge):** If a brand scores poorly, the system suggests a verified competitor (e.g., suggesting a B-Corp brand over a fast-fashion brand) to guide ethical purchasing decisions.
* **Blockchain Integration:** Connecting to immutable ledgers for verified supply chain "Proof of Origin."

---
**Developed for the Synapse 3.O Hackathon | Theme: Responsible Consumption & Climate Action**
