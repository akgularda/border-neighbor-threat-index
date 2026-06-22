function renderRankings(filter = '') {
  const el = document.getElementById('rankings-table');
  if (!el || !WTI.data) return;

  const rows = (WTI.data.rankings_table || []).filter(r => {
    if (!filter) return true;
    const q = filter.toLowerCase();
    return (r.name || '').toLowerCase().includes(q) || (r.iso2 || '').toLowerCase().includes(q);
  });

  el.innerHTML = `<table>
    <thead><tr><th>#</th><th>Country</th><th>ISO</th><th>Index</th><th>Status</th></tr></thead>
    <tbody>${rows.map((r, i) => `
      <tr data-iso="${r.iso2}">
        <td>${i + 1}</td>
        <td>${WTI.escapeHtml(r.name)}</td>
        <td>${r.iso2}</td>
        <td style="color:${WTI.colorForIndex(r.index)}">${Number(r.index).toFixed(2)}</td>
        <td>${r.status || ''}</td>
      </tr>`).join('')}
    </tbody></table>`;

  el.querySelectorAll('tr[data-iso]').forEach(row => {
    row.addEventListener('click', () => {
      if (window.WTIMap?.selectCountry) window.WTIMap.selectCountry(row.dataset.iso);
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  renderRankings();
  const search = document.getElementById('country-search');
  if (search) search.addEventListener('input', e => renderRankings(e.target.value));
});