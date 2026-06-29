"""
TNEA Data Pipeline
==================
Extracts cutoff data from TNEA PDFs (2022-2024) and produces:
  - data/cutoff_data.csv  → one row per college-branch-year-category
  - data/colleges.csv     → master college info (code, name, district, type, fees estimate)

Run: python data_pipeline.py
"""

import pdfplumber
import pandas as pd
import numpy as np
import re
import os

PDF_DIR = os.path.join(os.path.dirname(__file__), "raw_pdfs", "tnea_pdf")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

CATEGORIES = ['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']

# MBC/DNC is stored as MBC in PDFs; map it for display
CATEGORY_DISPLAY = {
    'OC': 'OC', 'BC': 'BC', 'BCM': 'BCM',
    'MBC': 'MBC/DNC', 'SC': 'SC', 'SCA': 'SCA', 'ST': 'ST'
}


def extract_district(college_name: str) -> str:
    name = college_name.replace('\n', ' ')

    # Explicit "XYZ District" pattern
    m = re.search(r'(\w[\w\s]{2,30}?)\s+District', name, re.IGNORECASE)
    if m:
        d = m.group(1).strip().title()
        for noise in ['Peelamedu', 'Peel']:
            d = d.replace(noise, '').strip()
        if 'Coimbatore' in d:
            return 'Coimbatore'
        # Remove trailing "Taluk" etc
        d = re.sub(r'\s+(Taluk|Tk|Post|Village).*', '', d).strip()
        return d

    city_map = {
        r'Chennai|Guindy|Tambaram|Porur|Poonamallee|Ambattur|Avadi|Sriperumbudur|Chrompet': 'Chennai',
        r'Coimbatore|Pollachi|Peelamedu': 'Coimbatore',
        r'Madurai|Tiruparankundram|Tirupparankundram': 'Madurai',
        r'Trichy|Tiruchirappalli|Tiruchirapalli': 'Tiruchirappalli',
        r'Salem': 'Salem',
        r'Tirunelveli': 'Tirunelveli',
        r'Vellore': 'Vellore',
        r'Erode': 'Erode',
        r'Thanjavur|Tanjore': 'Thanjavur',
        r'Namakkal': 'Namakkal',
        r'Kanyakumari|Nagercoil': 'Kanyakumari',
        r'Dindigul': 'Dindigul',
        r'Virudhunagar': 'Virudhunagar',
        r'Nagapattinam': 'Nagapattinam',
        r'Cuddalore': 'Cuddalore',
        r'Villupuram': 'Villupuram',
        r'Krishnagiri': 'Krishnagiri',
        r'Dharmapuri': 'Dharmapuri',
        r'Tiruppur|Tirupur': 'Tiruppur',
        r'Theni': 'Theni',
        r'Sivagangai': 'Sivagangai',
        r'Pudukkottai': 'Pudukkottai',
        r'Ariyalur': 'Ariyalur',
        r'Perambalur': 'Perambalur',
        r'Thoothukudi|Tuticorin': 'Thoothukudi',
        r'Ramanathapuram': 'Ramanathapuram',
        r'Tiruvannamalai': 'Tiruvannamalai',
        r'Karur': 'Karur',
        r'Nilgiris|Ooty': 'Nilgiris',
        r'Chengalpattu': 'Chengalpattu',
        r'Ranipet': 'Ranipet',
        r'Tirupattur': 'Tirupattur',
        r'Kallakurichi': 'Kallakurichi',
        r'Tenkasi': 'Tenkasi',
    }
    for pattern, district in city_map.items():
        if re.search(pattern, name, re.IGNORECASE):
            return district
    return 'Tamil Nadu'


def get_college_type(college_name: str) -> str:
    gov = ['University Departments', 'Government', 'Govt.', 'National Institute',
           'NIT', 'Anna University', 'IIT', 'Central University']
    if any(k.lower() in college_name.lower() for k in gov):
        return 'Government'
    return 'Private'


def estimate_fees(college_type: str, district: str) -> int:
    """
    Rough annual tuition fee estimate (INR) based on type and location.
    Government colleges follow Tamil Nadu govt-regulated fees.
    Private fees vary widely; this is an approximation for UX purposes.
    """
    if college_type == 'Government':
        return 50000
    metro = ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli']
    if district in metro:
        return 90000
    return 70000


def extract_pdf_data(pdf_path: str, year: int) -> list:
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 7:
                        continue
                    code = str(row[0]).strip() if row[0] else ''
                    # Skip header rows
                    if not code or not re.match(r'^\d+$', code):
                        continue

                    college_name = str(row[1]).replace('\n', ' ').strip() if row[1] else ''
                    branch_code  = str(row[2]).strip() if row[2] else ''
                    branch_name  = str(row[3]).replace('\n', ' ').strip() if row[3] else ''

                    if not college_name or not branch_code:
                        continue

                    cutoffs = {}
                    for i, cat in enumerate(CATEGORIES):
                        val = str(row[4 + i]).strip() if (4 + i) < len(row) and row[4 + i] else ''
                        try:
                            cutoffs[cat] = float(val)
                        except ValueError:
                            cutoffs[cat] = None

                    district     = extract_district(college_name)
                    college_type = get_college_type(college_name)

                    rows.append({
                        'year'        : year,
                        'college_code': code,
                        'college_name': college_name,
                        'branch_code' : branch_code,
                        'branch_name' : branch_name,
                        'district'    : district,
                        'college_type': college_type,
                        **cutoffs,
                    })
    return rows


def build_datasets():
    pdf_files = {
        'Vocational_2022_Mark_Cutoff.pdf'    : 2022,
        'Vocational_2023_Mark_Cutoff (1).pdf': 2023,
        'Vocational_2024_Mark_Cutoff.pdf'    : 2024,
    }

    all_rows = []
    for fname, year in pdf_files.items():
        path = os.path.join(PDF_DIR, fname)
        if not os.path.exists(path):
            print(f"  [SKIP] {fname} not found")
            continue
        rows = extract_pdf_data(path, year)
        all_rows.extend(rows)
        print(f"  {year}: {len(rows):,} rows extracted")

    df = pd.DataFrame(all_rows)

    # ── Cutoff data (long format): one row per college-branch-year-category ──
    id_cols = ['year', 'college_code', 'college_name', 'branch_code',
               'branch_name', 'district', 'college_type']
    cutoff_long = df.melt(id_vars=id_cols, value_vars=CATEGORIES,
                          var_name='category', value_name='cutoff')
    cutoff_long = cutoff_long.dropna(subset=['cutoff'])
    cutoff_long['category_display'] = cutoff_long['category'].map(CATEGORY_DISPLAY)
    cutoff_long.to_csv(os.path.join(DATA_DIR, 'cutoff_data.csv'), index=False)
    print(f"\n  cutoff_data.csv  → {len(cutoff_long):,} rows")

    # ── College master (one row per college) ──
    colleges = (df[['college_code', 'college_name', 'district', 'college_type']]
                .drop_duplicates(subset=['college_code'])
                .reset_index(drop=True))
    colleges['annual_fees'] = colleges.apply(
        lambda r: estimate_fees(r['college_type'], r['district']), axis=1)
    colleges.to_csv(os.path.join(DATA_DIR, 'colleges.csv'), index=False)
    print(f"  colleges.csv     → {len(colleges):,} colleges")

    # ── Branch master ──
    branches = (df[['branch_code', 'branch_name']]
                .drop_duplicates()
                .sort_values('branch_code')
                .reset_index(drop=True))
    branches.to_csv(os.path.join(DATA_DIR, 'branches.csv'), index=False)
    print(f"  branches.csv     → {len(branches):,} branches")

    print("\n✅  Pipeline complete. CSVs saved to /data/")
    return cutoff_long, colleges, branches


if __name__ == '__main__':
    print("Running TNEA Data Pipeline...\n")
    build_datasets()
