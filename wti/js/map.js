window.WTIMap = {
  isoToName: {},
  selected: null,

  async init() {
    if (!WTI.data) return;
    const svg = d3.select('#world-map');
    const width = 960;
    const height = 500;
    const projection = d3.geoNaturalEarth1().fitSize([width, height], { type: 'Sphere' });
    const path = d3.geoPath(projection);

    Object.entries(WTI.data.countries || {}).forEach(([iso, c]) => {
      this.isoToName[iso] = c.name || iso;
    });

    try {
      const world = await d3.json(
        'https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson'
      );
      const countries = world.features || [];

      const color = iso => {
        const data = WTI.data.countries?.[iso];
        return data ? WTI.colorForIndex(WTI.getIndex(data)) : '#2a3140';
      };

      svg.selectAll('path')
        .data(countries)
        .join('path')
        .attr('class', 'country')
        .attr('d', path)
        .attr('fill', d => color(d.properties?.['ISO_A2'] || d.properties?.['ISO_A2_EH']) || '#2a3140')
        .on('click', (_, d) => {
          const iso = d.properties?.['ISO_A2'] || d.properties?.['ISO_A2_EH'];
          if (iso && iso !== '-99') this.selectCountry(iso);
        });
    } catch (err) {
      svg.append('text').attr('x', 20).attr('y', 40).text('Map unavailable — use rankings table');
    }
  },

  selectCountry(iso2) {
    this.selected = iso2;
    const c = WTI.data?.countries?.[iso2];
    const el = document.getElementById('country-detail');
    if (!el) return;
    if (!c) {
      el.innerHTML = `<strong>${WTI.escapeHtml(iso2)}</strong><br/>No data`;
      return;
    }
    const events = (c.events || []).slice(0, 5);
    el.innerHTML = `
      <strong>${WTI.escapeHtml(c.name || iso2)}</strong>
      <span style="color:${WTI.colorForIndex(WTI.getIndex(c))};margin-left:8px;">${WTI.getIndex(c).toFixed(2)} ${c.status || ''}</span>
      <div style="margin-top:8px;font-size:0.85rem;">${events.map(e =>
        `<div style="margin:4px 0;">• ${WTI.escapeHtml(e.translated_title || e.title || '')} <em>(${e.category || 'neutral'})</em></div>`
      ).join('') || 'No events'}</div>`;
  },
};

document.addEventListener('DOMContentLoaded', () => window.WTIMap.init());