// ── Dark / Light theme toggle ──────────────────────────────
(function () {
  const root = document.documentElement;
  const stored = localStorage.getItem('tnea-theme') || 'dark';
  root.setAttribute('data-theme', stored);
  updateIcon(stored);

  function updateIcon(theme) {
    const icon = document.querySelector('.theme-icon');
    if (icon) icon.textContent = theme === 'dark' ? '☀️' : '🌙';
  }

  window.toggleTheme = function () {
    const current = root.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('tnea-theme', next);
    updateIcon(next);
  };
})();
