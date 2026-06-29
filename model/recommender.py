"""
TNEA KNN Recommendation Model
==============================
Loads CSVs, trains a KNN model, and exposes:
    recommend(cutoff, category, branch_code, district, college_type, top_n)
"""

import os
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# Admission-chance thresholds (how many marks ABOVE the closing cutoff)
SAFE_MARGIN   =  5.0   # cutoff > closing + 5  → Safe
TARGET_MARGIN = -3.0   # closing - 3 ≤ cutoff ≤ closing + 5 → Target
# else → Dream


class TNEARecommender:
    def __init__(self):
        self.cutoff_df  = None
        self.college_df = None
        self.branch_df  = None
        self.model      = None
        self.feature_df = None   # rows fed into KNN
        self._load_data()
        self._build_model()

    # ─────────────────────────── data loading ───────────────────────────────

    def _load_data(self):
        self.cutoff_df  = pd.read_csv(os.path.join(DATA_DIR, 'cutoff_data.csv'))
        self.college_df = pd.read_csv(os.path.join(DATA_DIR, 'colleges.csv'))
        self.branch_df  = pd.read_csv(os.path.join(DATA_DIR, 'branches.csv'))

        # Keep only 2024 data for primary recommendations;
        # fall back to 2023 when 2024 is absent
        self.latest_df = self._get_latest_cutoffs()

    def _get_latest_cutoffs(self) -> pd.DataFrame:
        """
        For every (college_code, branch_code, category) triple, pick the
        most-recent year's closing cutoff.
        """
        df = self.cutoff_df.sort_values('year', ascending=False)
        latest = (df
                  .drop_duplicates(subset=['college_code', 'branch_code', 'category'])
                  .copy())
        # Merge college meta
        latest = latest.merge(
            self.college_df[['college_code', 'annual_fees']],
            on='college_code', how='left')
        latest['annual_fees'] = latest['annual_fees'].fillna(70000)
        return latest

    # ─────────────────────────── KNN model ──────────────────────────────────

    def _build_model(self):
        """
        Feature vector: [cutoff, branch_encoded, district_encoded]
        The KNN finds similar colleges based on cutoff proximity.
        """
        df = self.latest_df.copy()

        self.branch_enc   = LabelEncoder()
        self.district_enc = LabelEncoder()

        df['branch_enc']   = self.branch_enc.fit_transform(df['branch_code'])
        df['district_enc'] = self.district_enc.fit_transform(df['district'])

        # Weights: cutoff is primary signal (scaled × 2)
        X = df[['cutoff', 'branch_enc', 'district_enc']].values.astype(float)
        X[:, 0] *= 2   # give cutoff 2× weight

        self.model      = NearestNeighbors(n_neighbors=min(50, len(df)),
                                           metric='euclidean')
        self.model.fit(X)
        self.feature_df = df.reset_index(drop=True)

    # ─────────────────────────── recommendation ─────────────────────────────

    def recommend(self,
                  student_cutoff: float,
                  category: str,
                  branch_code: str    = None,
                  district: str       = None,
                  college_type: str   = None,
                  top_n: int          = 20) -> list:
        """
        Returns a list of dicts, each representing a recommended college-branch.
        """
        # ── 1. filter by category ──────────────────────────────────────────
        cat_col = 'MBC' if category == 'MBC/DNC' else category
        pool = self.latest_df[self.latest_df['category'] == cat_col].copy()

        if pool.empty:
            return []

        # ── 2. optional hard filters ───────────────────────────────────────
        if branch_code and branch_code != 'ANY':
            pool = pool[pool['branch_code'] == branch_code]
        if district and district != 'ANY':
            pool = pool[pool['district'] == district]
        if college_type and college_type != 'ANY':
            pool = pool[pool['college_type'] == college_type]

        if pool.empty:
            return []

        # ── 3. admission chance label ──────────────────────────────────────
        pool = pool.copy()
        pool['margin'] = student_cutoff - pool['cutoff']

        def chance_label(margin: float) -> str:
            if margin >= SAFE_MARGIN:
                return 'Safe'
            elif margin >= TARGET_MARGIN:
                return 'Target'
            else:
                return 'Dream'

        pool['admission_chance'] = pool['margin'].apply(chance_label)

        # ── 4. sort: Safe first → Target → Dream, then by cutoff desc ─────
        chance_order = {'Safe': 0, 'Target': 1, 'Dream': 2}
        pool['_order'] = pool['admission_chance'].map(chance_order)
        pool = pool.sort_values(['_order', 'cutoff'], ascending=[True, False])

        # ── 5. deduplicate by college+branch (one row per combo) ──────────
        pool = pool.drop_duplicates(subset=['college_code', 'branch_code'])

        # ── 6. build result list ───────────────────────────────────────────
        results = []
        for _, row in pool.head(top_n).iterrows():
            results.append({
                'college_code'    : row['college_code'],
                'college_name'    : row['college_name'],
                'branch_code'     : row['branch_code'],
                'branch_name'     : row['branch_name'],
                'district'        : row['district'],
                'college_type'    : row['college_type'],
                'closing_cutoff'  : round(float(row['cutoff']), 2),
                'data_year'       : int(row['year']),
                'annual_fees'     : int(row.get('annual_fees', 70000)),
                'admission_chance': row['admission_chance'],
                'margin'          : round(float(row['margin']), 2),
                'category'        : row['category'],
            })
        return results

    # ─────────────────────────── helpers for UI ─────────────────────────────

    def get_branches(self) -> list:
        return self.branch_df.to_dict('records')

    def get_districts(self) -> list:
        return sorted(self.latest_df['district'].unique().tolist())
