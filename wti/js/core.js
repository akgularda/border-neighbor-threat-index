const WTI = {
  data: window.WTI_DATA || null,

  getIndex(obj) {
    const v = Number(obj?.index ?? obj?.main_index);
    return Number.isFinite(v) ? v : 0;
  },

  statusClass(status) {
    const s = (status || 'STABLE').toUpperCase();
    if (s.includes('CRITICAL')) return 'critical';
    if (s.includes('ELEVATED')) return 'elevated';
    return 'stable';
  },

  colorForIndex(index) {
    if (index > 7) return '#e74c3c';
    if (index > 4) return '#f39c12';
    return '#27ae60';
  },

  escapeHtml(v) {
    return String(v ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  },

  init() {
    if (!this.data) return;
    const meta = this.data.meta || {};
    const pill = document.getElementById('status-pill');
    pill.textContent = meta.status || 'STABLE';
    pill.className = `status-pill ${this.statusClass(meta.status)}`;
    document.getElementById('main-index').textContent = this.getIndex(meta).toFixed(2);
    document.getElementById('status-text').textContent = meta.status || '--';
    document.getElementById('countries-active').textContent =
      `ACTIVE: ${meta.countries_active || 0} / ${meta.countries_total || 0}`;
    document.getElementById('coverage-text').textContent =
      `${Math.round((meta.coverage_ratio || 0) * 100)}%`;
    const last = meta.generated_at ? new Date(meta.generated_at) : null;
    document.getElementById('last-update').textContent =
      last && !Number.isNaN(last.getTime()) ? last.toLocaleString() : '--';
  },
};

document.addEventListener('DOMContentLoaded', () => WTI.init());