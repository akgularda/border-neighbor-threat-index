/* ━━━━━━━━━━━━━━━━━━━━━━━━━
   BNTI v2.0 — Map Module
   ━━━━━━━━━━━━━━━━━━━━━━━━━ */

const BNTIMap = {
    update(data) {
        const overlay = document.getElementById('map-overlay-stats');
        const countries = Object.entries(data?.countries || {})
            .map(([name, c]) => ({ name, score: BNTI.getIndexValue(c) }))
            .sort((a, b) => b.score - a.score);

        let overlayHtml = '<h4>Regional Threats</h4>';
        countries.forEach(c => {
            let color = 'var(--stable)';
            if (c.score >= 7) color = 'var(--critical)';
            else if (c.score >= 4) color = 'var(--elevated)';
            overlayHtml += `<div class="map-row"><span>${c.name.toUpperCase()}</span><span style="color:${color}">${c.score.toFixed(2)}</span></div>`;
        });
        overlay.innerHTML = overlayHtml;

        document.querySelectorAll('#map-svg .country-shape').forEach(el => {
            const name = el.getAttribute('data-country');
            const country = data?.countries?.[name];
            const score = country ? BNTI.getIndexValue(country) : 0;
            const status = score >= 7 ? 'critical' : score >= 4 ? 'elevated' : 'stable';
            el.classList.remove('critical', 'elevated', 'stable');
            el.classList.add(status);
            let title = el.querySelector('title');
            if (!title) {
                title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
                el.appendChild(title);
            }
            title.textContent = `${name}: ${score.toFixed(2)} (${status.toUpperCase()})`;
        });
    }
};
