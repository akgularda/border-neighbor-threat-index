/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   BNTI v2.0 — Core Engine
   Data loading, state, poller
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

const BNTI = {
  data: window.BNTI_DATA || null,
  trendChart: null,

  // ── Helpers ──
  getIndexValue(obj) {
    if (!obj) return 0;
    const value = obj.main_index ?? obj.index;
    const num = Number(value);
    return Number.isFinite(num) ? num : 0;
  },

  parsePoints(list) {
    if (!Array.isArray(list)) return [];
    return list
      .map(item => {
        const value = this.getIndexValue(item);
        const ts = item.timestamp ? new Date(item.timestamp) : null;
        if (!ts || Number.isNaN(ts.getTime())) return null;
        return { ts, value, type: item.type || 'historical', confidence: item.confidence };
      })
      .filter(Boolean)
      .sort((a, b) => a.ts - b.ts);
  },

  formatTime(date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  },

  formatDateTime(date) {
    return date.toLocaleString([], { year: 'numeric', month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' });
  },

  setStatusClasses(element, status) {
    element.classList.remove('critical', 'elevated', 'stable');
    if (status === 'CRITICAL') element.classList.add('critical');
    else if (status === 'ELEVATED') element.classList.add('elevated');
    else element.classList.add('stable');
  },

  // ── Header Update ──
  updateHeader() {
    const status = (this.data?.meta?.status || 'STABLE').toUpperCase();
    const statusClass = status.includes('CRITICAL') ? 'CRITICAL' : status.includes('ELEVATED') ? 'ELEVATED' : 'STABLE';
    const statusPill = document.getElementById('status-pill');
    statusPill.textContent = status;
    this.setStatusClasses(statusPill, statusClass);

    // Add live dot
    if (!statusPill.querySelector('.live-dot')) {
      statusPill.insertAdjacentHTML('afterbegin', '<span class="live-dot"></span>');
    }

    const lastUpdate = this.data?.meta?.generated_at ? new Date(this.data.meta.generated_at) : null;
    const nextUpdate = this.data?.meta?.next_update ? new Date(this.data.meta.next_update) : null;
    document.getElementById('last-update').textContent = lastUpdate && !Number.isNaN(lastUpdate.getTime()) ? this.formatDateTime(lastUpdate) : '--';
    document.getElementById('next-update').textContent = nextUpdate && !Number.isNaN(nextUpdate.getTime()) ? this.formatDateTime(nextUpdate) : '--';
  },

  // ── Metrics Update ──
  updateMetrics(historyPoints) {
    const status = (this.data?.meta?.status || 'STABLE').toUpperCase();
    const statusClass = status.includes('CRITICAL') ? 'CRITICAL' : status.includes('ELEVATED') ? 'ELEVATED' : 'STABLE';

    const idx = this.getIndexValue(this.data?.meta);
    const metricEl = document.getElementById('main-index');
    metricEl.textContent = idx.toFixed(2);
    metricEl.className = `metric-value ${statusClass.toLowerCase()}`;

    document.getElementById('status-text').textContent = status;

    let trendText = 'Trend: --';
    if (historyPoints.length >= 2) {
      const latest = historyPoints[historyPoints.length - 1];
      const prev = historyPoints[historyPoints.length - 2];
      const delta = latest.value - prev.value;
      const arrow = delta > 0 ? '▲' : delta < 0 ? '▼' : '━';
      trendText = `${arrow} ${delta >= 0 ? '+' : ''}${delta.toFixed(2)}`;
    }
    document.getElementById('trend-text').textContent = trendText;

    const totalSignals = Object.values(this.data?.countries || {}).reduce((sum, c) => {
      return sum + (Array.isArray(c.events) ? c.events.length : 0);
    }, 0);
    document.getElementById('signal-text').textContent = `SIGNALS: ${totalSignals}`;
  },

  // ── Weights Update ──
  updateWeights() {
    const weightsEl = document.getElementById('weights-table');
    weightsEl.innerHTML = '';
    const weights = this.data?.methodology?.weights || {};

    Object.entries(weights)
      .sort(([, a], [, b]) => b - a)
      .forEach(([label, value]) => {
        const row = document.createElement('div');
        row.className = 'weight-row';
        const pretty = label.replace(/_/g, ' ').toUpperCase();
        const val = Number(value);
        const valClass = val >= 0 ? 'positive' : 'negative';
        row.innerHTML = `<div>${pretty}</div><div class="weight-value ${valClass}">${val > 0 ? '+' : ''}${val.toFixed(1)}</div>`;
        weightsEl.appendChild(row);
      });
  },

  // ── Render All ──
  renderAll() {
    if (!this.data) return;
    const historyPoints = this.parsePoints(this.data.history);
    const forecastPoints = this.parsePoints(this.data.forecast);
    this.updateHeader();
    this.updateMetrics(historyPoints);
    this.updateWeights();
    BNTIMap.update(this.data);
    BNTIStream.update(this.data);
    BNTICharts.init(historyPoints, forecastPoints);
  },

  // ── Data Poller ──
  startDataPoller() {
    setInterval(async () => {
      try {
        const res = await fetch(`bnti_data.json?t=${Date.now()}`);
        if (!res.ok) return;
        const newData = await res.json();
        if (newData?.meta?.generated_at && newData.meta.generated_at !== this.data?.meta?.generated_at) {
          this.data = newData;
          this.renderAll();
        }
      } catch (e) {
        console.log('Poll:', e.message);
      }
    }, 60000);
  },

  // ── UTC Clock ──
  startClock() {
    const el = document.getElementById('utc-clock');
    if (!el) return;
    const tick = () => {
      const now = new Date();
      el.textContent = now.toUTCString().slice(17, 25) + ' UTC';
    };
    tick();
    setInterval(tick, 1000);
  },

  // ── Init ──
  init() {
    this.renderAll();
    this.startDataPoller();
    this.startClock();
    this.initModal();
  },

  // ── Modal ──
  initModal() {
    const link = document.getElementById('methodology-link');
    const modal = document.getElementById('methodology-modal');
    const close = document.getElementById('close-modal');
    if (!link || !modal) return;

    link.addEventListener('click', e => {
      e.preventDefault();
      modal.style.display = 'block';
      document.body.style.overflow = 'hidden';
    });
    close?.addEventListener('click', () => {
      modal.style.display = 'none';
      document.body.style.overflow = '';
    });
    modal.addEventListener('click', e => {
      if (e.target === modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
      }
    });
  }
};
