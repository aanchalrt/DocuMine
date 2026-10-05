# ⛏️ DocuMine — AI-Powered Mining Document Intelligence Platform

> **Kranti Opencast Project (OCP) · Eastern Coalfields Limited (ECL)**  
> Built for Ministry of Coal / PSU Regulatory & Statutory Reporting Workflows  
> **Tech Stack:** React 18, Tailwind CSS, FastAPI, Google Gemini AI, Firebase Firestore

---

## 🌟 Overview

**DocuMine** is an end-to-end AI document intelligence and cross-validation platform built specifically for India's coal mining sector. It solves the critical bottleneck of extracting, auditing, cross-checking, and synthesizing multi-source statutory reports (geological assessments, monthly extraction sheets, environmental monitoring data, and land/forest clearance correspondences).

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────┐
│               React 18 + Tailwind CSS SPA              │
│       (Interactive Dashboards, Citations & Timelines)  │
└───────────────────────────┬────────────────────────────┘
                            │ REST APIs (/api/*)
┌───────────────────────────▼────────────────────────────┐
│                  FastAPI Backend Engine                │
│    Document Parsing, Schema Mapping & Business Rules   │
└─────────────┬────────────────────────────┬─────────────┘
              │                            │
   ┌──────────▼──────────┐      ┌──────────▼──────────┐
   │   Google Gemini AI  │      │  Persistence Layer  │
   │ Extraction, Q&A,    │      │  Firebase Firestore │
   │ Bilingual Synthesis │      │  Structured Data    │
   └─────────────────────┘      └─────────────────────┘
```

---

## 🚀 The 7 Core Modules

| # | Module | Key Features & Implementation |
|---|--------|-------------------------------|
| 1 | **Smart Ingestion** | Direct parsing of digital `.docx`, `.xlsx`, `.pdf` (pdfplumber, openpyxl, python-docx) + automatic OCR fallback (Tesseract) for scanned records. Schema-guided Gemini extraction with confidence tags and automatic **Needs Review** queue. |
| 2 | **Report Generation** | Multi-document synthesis into a **Mine Status Summary Report** with clickable `<citation>` references linked back to source documents and fields. Supports instant `.docx` export. |
| 3 | **Word Cloud & Topics** | Interactive canvas-based keyword visualizer powered by `wordcloud2.js` and Gemini domain-keyword extraction, showing term weights and thematic breakdown. |
| 4 | **Bilingual AI Chat** | Conversational Q&A in **English** and **Hindi (हिंदी)** with automatic language detection. Grounded strictly in the corpus with zero hallucinations and inline citations. |
| 5 | **Validation Engine** | Cross-document consistency checking engine. Flags numeric variance (>2%), unexplained categorical shifts (e.g., estimation methods, coal grades), and monthly breakdown vs. annual summary mismatches. |
| 6 | **Audit & Traceability** | Tamper-evident activity trail tracking document uploads, validations, reports generated, and user queries with dual-role access control (**Admin** vs. **Viewer**). |
| 7 | **Clearance Tracker** | Visual pipeline tracking land acquisition & forest clearance (Gram Panchayat NOC → DC → State Revenue → MoEFCC). Detects stalled steps and visually highlights critical bottlenecks (579+ days pending). |

---

## 🧪 Seed Data & Planted Discrepancies

DocuMine includes 10 realistic synthetic documents for Kranti OCP specifically engineered with deliberate inconsistencies to demonstrate validation capabilities:

1. **Reserve Estimate Drift**: Drops from **142.6 MT** (DocA) to **138.9 MT** (DocB) with method silently changing from *Cross-Sectional* to *Polygon* without explanatory justification.
2. **Production Reconciliation Mismatch**: DocB asserts annual production of **3.91 MT**, while DocC's monthly spreadsheet totals **3.85 MT** (provisional ledger disparity).
3. **Coal Grade Inconsistency**: Historical baseline (DocE, 2019) classifies reserve as **Grade G7**, while current reports (DocA/DocB) list **Grade G8** without documented re-gradation by CMPDI.
4. **Degraded Field OCR Flag**: DocD contains an illegible ink-smeared water discharge record (`??.?? MLD`), automatically assigned low confidence and routed to the **Needs Review** queue.
5. **Clearance Bottleneck**: MoEFCC Forest Clearance stage has remained unanswered for **579+ days**, flagged in red on the visual tracker.

---

## 💻 Local Setup & Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **Gemini API Key** ([Get free key](https://aistudio.google.com/app/apikey))

### 1. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Open .env and add:
# GEMINI_API_KEY=your_gemini_api_key_here
# GOOGLE_APPLICATION_CREDENTIALS=path/to/firebase-key.json

# Start FastAPI backend
python -m uvicorn main:app --port 8080
```
Backend API will be live at: `http://localhost:8080`  
Interactive Swagger docs: `http://localhost:8080/docs`

### 2. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
Frontend will be live at: `http://localhost:5173`

---

## 🌐 Production Deployment

### Frontend → Vercel
1. Push repository to GitHub.
2. Link project on [Vercel](https://vercel.com).
3. Set **Root Directory** to `frontend`.
4. Add Environment Variable:
   - `VITE_API_URL` = `https://your-backend-domain.com/api`
5. Click **Deploy**.

### Backend → Render / Railway / Cloud Run
1. Create a new Web Service from the same repo.
2. Set **Root Directory** to `backend`.
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `GEMINI_API_KEY`
   - `GOOGLE_APPLICATION_CREDENTIALS` (or Firebase credentials)

---

## 🔒 Security & Data Governance
- Strict isolation of prompt context with explicit boundaries (`<document id="...">...</document>`).
- Mandatory evidence grounding via structured `<citation>` tags.
- Role-based UI gating (**Admin** has write/approval permissions; **Viewer** has read-only access).
- Audit trail capturing timestamps, actor roles, and targeted document references.

---

## 📄 License
Demonstration prototype developed for academic & hackathon evaluation.
