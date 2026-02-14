/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   BNTI v2.0 — Intelligence Stream
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

const BNTIStream = {
    update(data) {
        const container = document.getElementById('stream-feed');
        container.innerHTML = '';
        const events = [];

        Object.entries(data?.countries || {}).forEach(([cName, cData]) => {
            if (Array.isArray(cData?.events)) {
                cData.events.forEach(e => events.push({ ...e, country: cName }));
            }
        });

        events.sort((a, b) => {
            const aScore = (Number(a.weight) || 0) * (Number(a.confidence) || 0.5);
            const bScore = (Number(b.weight) || 0) * (Number(b.confidence) || 0.5);
            return bScore - aScore;
        });

        events.slice(0, 30).forEach(e => {
            const weight = Number(e.weight) || 0;
            const badgeClass = weight >= 6 ? 'critical' : weight >= 3 ? 'elevated' : 'stable';

            const confValue = Number.isFinite(Number(e.confidence))
                ? Number(e.confidence)
                : parseFloat(String(e.ai_confidence_score || '').replace('%', '')) / 100;
            const confPct = Number.isFinite(confValue) ? Math.round(confValue * 100) : 0;

            const isEnglish = e.detected_lang === 'en';
            const translated = e.translated_title && e.translated_title !== e.title;
            const displayTitle = translated ? e.translated_title : e.title;
            const sourceLabel = isEnglish ? 'EN' : String(e.detected_lang || 'LOCAL').toUpperCase();

            const dateObj = e.date ? new Date(e.date) : null;
            const timeLabel = dateObj && !Number.isNaN(dateObj.getTime()) ? BNTI.formatTime(dateObj) : '--:--';

            const sourceLink = e.link ? `<a href="${e.link}" target="_blank" rel="noopener">SRC</a>` : '';
            const translateLink = !isEnglish && e.link
                ? `<a href="https://translate.google.com/translate?sl=auto&tl=en&u=${encodeURIComponent(e.link)}" target="_blank" rel="noopener">TL</a>`
                : '';

            const titleAttr = translated ? `title="${String(e.title).replace(/"/g, '&quot;')}"` : '';

            const html = `
        <div class="stream-item">
          <div class="stream-meta">
            <span>${timeLabel}</span>
            <span>${String(e.country || '').toUpperCase()}</span>
            <span class="badge ${badgeClass}">${String(e.category || '').toUpperCase().replace(/_/g, ' ')}</span>
          </div>
          <div class="stream-title" ${titleAttr}>${displayTitle}</div>
          <div class="stream-footer">
            <div class="conf-bar"><div class="conf-fill" style="width: ${confPct}%"></div></div>
            <span>${confPct}%</span>
            <span>${sourceLabel}</span>
          </div>
          <div class="stream-links">${sourceLink}${translateLink}</div>
        </div>
      `;
            container.insertAdjacentHTML('beforeend', html);
        });
    }
};
