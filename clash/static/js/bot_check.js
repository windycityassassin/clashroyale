document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('bot-form');
    const out = document.getElementById('bot-result');

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const tag = document.getElementById('player-tag').value.trim();
        out.innerHTML = 'Scoring...';

        fetch('/api/bot_check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_tag: tag }),
        })
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    out.innerHTML = `<p class="error">${data.error}</p>`;
                    return;
                }
                out.innerHTML = renderScore(data);
            })
            .catch(err => {
                out.innerHTML = `<p class="error">${err}</p>`;
            });
    });
});

function renderScore(d) {
    const verdictClass = {
        'very likely bot': 'verdict-high',
        'likely bot': 'verdict-mid',
        'suspicious': 'verdict-low',
        'unlikely bot': 'verdict-ok',
    }[d.verdict] || '';

    const rows = d.signals.map(s => `
        <tr class="${s.fired ? 'fired' : ''}">
            <td>${s.fired ? '✓' : ' '}</td>
            <td>${s.name}</td>
            <td>${s.weight}</td>
            <td>${escapeHtml(String(s.value === null || s.value === undefined ? '' : s.value))}</td>
            <td>${escapeHtml(s.description)}</td>
        </tr>
    `).join('');

    return `
        <div class="bot-summary">
            <h2>${escapeHtml(d.name || '')} <small>${escapeHtml(d.tag || '')}</small></h2>
            <p>King level ${d.exp_level} &middot; ${d.trophies} trophies (best ${d.best_trophies})</p>
            <p>Score: <strong class="${verdictClass}">${d.score} / 100 &mdash; ${d.verdict}</strong></p>
        </div>
        <table class="signals">
            <thead><tr><th>Fired</th><th>Signal</th><th>Weight</th><th>Value</th><th>Why it matters</th></tr></thead>
            <tbody>${rows}</tbody>
        </table>
    `;
}

function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
}
