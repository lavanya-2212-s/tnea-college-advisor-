# 🎓 TNEA College Advisor

> AI-powered college recommendation system for Tamil Nadu engineering aspirants

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat&logo=flask)](https://flask.palletsprojects.com)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-KNN-orange?style=flat&logo=scikit-learn)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

---

## 📌 About

TNEA College Advisor helps Tamil Nadu engineering aspirants find the right college based on their **TNEA cutoff mark** and preferences. It uses a **KNN machine learning model** trained on **3 years of real TNEA historical cutoff data** (2022–2024) scraped directly from official government PDFs.

---

## ✨ Features

- 🤖 **KNN-based ML recommendation** using historical cutoff patterns
- 📄 **PDF Data Pipeline** — extracts real TNEA cutoff data using pdfplumber
- 🎯 **Admission Chance Labels** — Safe / Target / Dream
- 🏫 **362 colleges**, **92 branches**, **7 community categories**
- 🔍 Filter by district, branch, college type (Government/Private)
- 🌙 **Dark mode** + glassmorphism UI
- 📱 Fully **responsive** for mobile and desktop

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| ML Model | Scikit-learn (KNN) |
| Data Processing | Pandas, NumPy, pdfplumber |
| Data Storage | CSV files |

---

## 📊 Dataset

Extracted from official **TNEA Vocational Mark Cutoff PDFs**:
- 2022: 709 records
- 2023: 848 records
- 2024: 825 records
- **Total: 2,696 cutoff records across 362 colleges**

---

## 🚀 Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/lavanya-2212-s/tnea-college-advisor-.git
cd tnea-college-advisor-

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the app
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 🎯 Admission Chance Logic

| Label | Condition |
|-------|-----------|
| ✅ Safe | Your cutoff ≥ Closing cutoff + 5 marks |
| 🎯 Target | Within 5 marks of closing cutoff |
| ⭐ Dream | Slightly below closing cutoff |

---

## 📁 Project Structure

```
tnea_advisor/
├── app.py                 ← Flask app + REST API
├── data_pipeline.py       ← PDF scraping pipeline
├── requirements.txt
├── model/
│   └── recommender.py     ← KNN model logic
├── data/
│   ├── cutoff_data.csv    ← 2,696 cutoff records
│   ├── colleges.csv       ← 362 colleges
│   └── branches.csv       ← 92 branches
├── templates/
│   ├── base.html
│   ├── index.html         ← Landing page
│   └── recommend.html     ← Form + results
└── static/
    ├── css/main.css
    └── js/recommend.js
```

---

## 👩‍💻 Developer

**Lavanya S** — CSE Graduate, Vels University  
[GitHub](https://github.com/lavanya-2212-s)
