"""
TNEA College Advisor – Flask Application
=========================================
Routes:
  GET  /                → Landing page
  GET  /recommend       → Recommendation form page
  POST /api/recommend   → JSON API for recommendations
  GET  /api/branches    → List of all branches
  GET  /api/districts   → List of all districts
"""

from flask import Flask, render_template, request, jsonify
import os
import sys

# Make sure the model package resolves correctly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from model.recommender import TNEARecommender

app = Flask(__name__)

# ── Initialise model once at startup ────────────────────────────────────────
print("Loading TNEA Recommender model…")
recommender = TNEARecommender()
print("✅  Model ready")


# ─────────────────────────── HTML routes ────────────────────────────────────

@app.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@app.route('/recommend')
def recommend_page():
    """Full recommendation form page."""
    branches  = recommender.get_branches()
    districts = recommender.get_districts()
    return render_template('recommend.html',
                           branches=branches,
                           districts=districts)


# ─────────────────────────── JSON API routes ────────────────────────────────

@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    """
    Accepts JSON or form data:
    {
        "cutoff"       : 170.5,
        "category"     : "OC",        # OC / BC / BCM / MBC/DNC / SC / SCA / ST
        "branch_code"  : "CS",        # branch code or "ANY"
        "district"     : "Chennai",   # district name or "ANY"
        "college_type" : "Private",   # Government / Private / ANY
        "top_n"        : 20
    }
    """
    data = request.get_json(silent=True) or request.form

    # ── Validate ────────────────────────────────────────────────────────────
    try:
        cutoff = float(data.get('cutoff', 0))
    except (TypeError, ValueError):
        return jsonify({'error': 'cutoff must be a number'}), 400

    if not (0 < cutoff <= 200):
        return jsonify({'error': 'cutoff must be between 1 and 200'}), 400

    category     = str(data.get('category', 'OC')).strip()
    branch_code  = str(data.get('branch_code', 'ANY')).strip() or 'ANY'
    district     = str(data.get('district', 'ANY')).strip()    or 'ANY'
    college_type = str(data.get('college_type', 'ANY')).strip()

    valid_categories = ['OC', 'BC', 'BCM', 'MBC/DNC', 'SC', 'SCA', 'ST']
    if category not in valid_categories:
        return jsonify({'error': f'category must be one of {valid_categories}'}), 400

    try:
        top_n = int(data.get('top_n', 20))
        top_n = min(max(top_n, 5), 50)
    except (TypeError, ValueError):
        top_n = 20

    # ── Call model ──────────────────────────────────────────────────────────
    results = recommender.recommend(
        student_cutoff=cutoff,
        category=category,
        branch_code=branch_code,
        district=district,
        college_type=college_type,
        top_n=top_n,
    )

    return jsonify({
        'count'  : len(results),
        'inputs' : {
            'cutoff'      : cutoff,
            'category'    : category,
            'branch_code' : branch_code,
            'district'    : district,
            'college_type': college_type,
        },
        'results': results,
    })


@app.route('/api/branches')
def api_branches():
    return jsonify(recommender.get_branches())


@app.route('/api/districts')
def api_districts():
    return jsonify(recommender.get_districts())


# ─────────────────────────── run ────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, port=5000)
