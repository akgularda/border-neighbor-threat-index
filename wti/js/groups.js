function renderGroups() {
  const grid = document.getElementById('groups-grid');
  const top = document.getElementById('top-threats');
  if (!grid || !WTI.data) return;

  const groups = WTI.data.groups || {};
  grid.innerHTML = Object.entries(groups)
    .sort((a, b) => WTI.getIndex(b[1]) - WTI.getIndex(a[1]))
    .map(([id, g]) => `
      <div class="group-card">
        <div class="group-name">${WTI.escapeHtml(g.name || id)}</div>
        <div class="group-index" style="color:${WTI.colorForIndex(WTI.getIndex(g))}">
          ${WTI.getIndex(g).toFixed(2)} <span class="status-pill ${WTI.statusClass(g.status)}" style="font-size:0.65rem;padding:2px 6px;">${g.status || ''}</span>
        </div>
      </div>`)
    .join('');

  const highest = WTI.data.rankings?.highest_threat || [];
  const countries = WTI.data.countries || {};
  top.innerHTML = highest.slice(0, 8).map(iso2 => {
    const c = countries[iso2] || {};
    return `<div>${WTI.escapeHtml(c.name || iso2)} — <strong style="color:${WTI.colorForIndex(WTI.getIndex(c))}">${WTI.getIndex(c).toFixed(2)}</strong></div>`;
  }).join('') || '<div class="briefing-empty">NO DATA</div>';
}

document.addEventListener('DOMContentLoaded', renderGroups);