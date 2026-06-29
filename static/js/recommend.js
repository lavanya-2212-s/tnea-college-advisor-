/* ── TNEA Advisor: Recommendation Page JS ─────────────────── */

let allResults = [];   // holds the full API response for client-side sort/filter

// ── Main: fetch recommendations ──────────────────────────────
async function getRecommendations() {
  const cutoff      = document.getElementById('cutoff').value.trim();
  const category    = document.getElementById('category').value;
  const branch_code = document.getElementById('branch_code').value;
  const district    = document.getElementById('district').value;
  const college_type = document.querySelector('input[name="college_type"]:checked').value;
  const top_n       = document.getElementById('top_n').value;

  // Basic validation
  if (!cutoff || isNaN(cutoff) || cutoff <= 0 || cutoff > 200) {
    showError('Please enter a valid cutoff mark between 1 and 200.');
    return;
  }

  showLoading();

  try {
    const resp = await fetch('/api/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cutoff, category, branch_code, district, college_type, top_n }),
    });

    const data = await resp.json();

    if (!resp.ok) {
      showError(data.error || 'Server error. Please try again.');
      return;
    }

    allResults = data.results || [];
    renderResults(allResults, data.inputs);

  } catch (err) {
    showError('Network error. Is the server running?');
    console.error(err);
  }
}

// ── Render ────────────────────────────────────────────────────
function renderResults(results, inputs) {
  hideAll();

  const header = document.getElementById('results-header');
  const grid   = document.getElementById('cards-grid');

  header.classList.remove('hidden');
  grid.innerHTML = '';

  if (!results || results.length === 0) {
    grid.innerHTML = `
      <div style="grid-column:1/-1; text-align:center; padding:60px 20px; color:var(--text-secondary);">
        <div style="font-size:3rem; margin-bottom:16px;">😕</div>
        <h3 style="color:var(--text-primary); margin-bottom:8px;">No matches found</h3>
        <p>Try broadening your search — choose "Any Branch" or "Any District".</p>
      </div>`;
    document.getElementById('results-count').textContent = '0 colleges';
    return;
  }

  document.getElementById('results-count').textContent = `${results.length} college${results.length !== 1 ? 's' : ''}`;

  const tpl = document.getElementById('card-template');
  results.forEach((rec, idx) => {
    const card = tpl.content.cloneNode(true).querySelector('.college-card');
    card.classList.add(`chance-${rec.admission_chance.toLowerCase()}`);
    card.style.animationDelay = `${idx * 40}ms`;

    // Type badge
    const typeBadge = card.querySelector('.card-type-badge');
    typeBadge.textContent = rec.college_type;
    typeBadge.classList.add(rec.college_type === 'Government' ? 'badge-gov' : 'badge-priv');

    // Chance badge
    const chanceBadge = card.querySelector('.card-chance-badge');
    chanceBadge.textContent = chanceEmoji(rec.admission_chance) + ' ' + rec.admission_chance;
    chanceBadge.classList.add(`badge-${rec.admission_chance.toLowerCase()}`);

    card.querySelector('.card-year').textContent     = `Data: ${rec.data_year}`;
    card.querySelector('.card-college-name').textContent = rec.college_name;
    card.querySelector('.branch-code').textContent   = rec.branch_code;
    card.querySelector('.branch-name').textContent   = rec.branch_name;
    card.querySelector('.card-district').textContent = rec.district;
    card.querySelector('.card-fees').textContent     = formatFees(rec.annual_fees);
    card.querySelector('.card-cutoff').textContent   = rec.closing_cutoff.toFixed(2);
    card.querySelector('.card-margin').textContent   = formatMargin(rec.margin);

    grid.appendChild(card);
  });
}

// ── Sort + Filter (client-side, instant) ─────────────────────
function applySort() {
  let results = [...allResults];

  // Type filter
  const typeFilter = document.getElementById('filter-select').value;
  if (typeFilter !== 'ALL') {
    results = results.filter(r => r.college_type === typeFilter);
  }

  // Chance filter
  const chanceFilter = document.getElementById('chance-filter').value;
  if (chanceFilter !== 'ALL') {
    results = results.filter(r => r.admission_chance === chanceFilter);
  }

  // Sort
  const sort = document.getElementById('sort-select').value;
  const chanceOrder = { Safe: 0, Target: 1, Dream: 2 };

  results.sort((a, b) => {
    switch (sort) {
      case 'chance':      return (chanceOrder[a.admission_chance] - chanceOrder[b.admission_chance]) || (b.closing_cutoff - a.closing_cutoff);
      case 'cutoff_desc': return b.closing_cutoff - a.closing_cutoff;
      case 'cutoff_asc':  return a.closing_cutoff - b.closing_cutoff;
      case 'fees_asc':    return a.annual_fees - b.annual_fees;
      case 'fees_desc':   return b.annual_fees - a.annual_fees;
      case 'district':    return a.district.localeCompare(b.district);
      default:            return 0;
    }
  });

  renderResults(results, null);
}

// ── Helpers ───────────────────────────────────────────────────
function chanceEmoji(chance) {
  return { Safe: '✅', Target: '🎯', Dream: '⭐' }[chance] || '';
}

function formatFees(fees) {
  if (!fees) return '—';
  return '₹' + (fees / 1000).toFixed(0) + ',000 / yr';
}

function formatMargin(margin) {
  if (margin === undefined || margin === null) return '—';
  const sign = margin >= 0 ? '+' : '';
  return sign + margin.toFixed(2);
}

// ── UI state helpers ──────────────────────────────────────────
function hideAll() {
  document.getElementById('empty-state').classList.add('hidden');
  document.getElementById('loading-state').classList.add('hidden');
  document.getElementById('error-state').classList.add('hidden');
  document.getElementById('results-header').classList.add('hidden');
}

function showLoading() {
  hideAll();
  document.getElementById('loading-state').classList.remove('hidden');
}

function showError(msg) {
  hideAll();
  document.getElementById('error-msg').textContent = msg;
  document.getElementById('error-state').classList.remove('hidden');
}

// ── Allow Enter key to submit ─────────────────────────────────
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && e.target.id === 'cutoff') {
    getRecommendations();
  }
});
