# 🎓 TNEA College Advisor

AI-powered college recommendation system for Tamil Nadu engineering aspirants.

## Project Structure

```
tnea_advisor/
├── app.py                  ← Flask app (routes + API)
├── data_pipeline.py        ← PDF extraction → CSV pipeline
├── requirements.txt        ← Python dependencies
├── README.md
│
├── model/
│   ├── __init__.py
│   └── recommender.py      ← KNN model + recommendation logic
│
├── data/                   ← Auto-generated CSVs
│   ├── cutoff_data.csv     ← 2,696 rows of cutoff records
│   ├── colleges.csv        ← 362 colleges master
│   └── branches.csv        ← 92 branches
│
├── raw_pdfs/               ← Place TNEA PDFs here
│   └── tnea_pdf/
│
├── templates/
│   ├── base.html           ← Navbar, footer, dark mode
│   ├── index.html          ← Landing page (hero, how-it-works)
│   └── recommend.html      ← Form + results page
│
└── static/
    ├── css/
    │   └── main.css        ← Full design system (glassmorphism, dark mode)
    └── js/
        ├── theme.js        ← Dark/light toggle
        └── recommend.js    ← API calls, card rendering, sort/filter
```

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Re-run pipeline if you add new PDFs
python data_pipeline.py

# 3. Start the app
python app.py
```

Then open http://localhost:5000

## Admission Chance Logic

| Label  | Condition |
|--------|-----------|
| Safe   | Student cutoff ≥ Closing cutoff + 5  |
| Target | Closing cutoff − 3 ≤ Student cutoff < Closing cutoff + 5 |
| Dream  | Student cutoff < Closing cutoff − 3  |

## Data Source
TNEA Vocational Mark Cutoff PDFs: 2022, 2023, 2024
