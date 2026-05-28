document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('scan-form');
    const out = document.getElementById('scan-result');

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const tag = document.getElementById('player-tag').value.trim();
        out.innerHTML = 'Scanning... this takes about 10 seconds.';

        fetch('/api/recent_opponents', {
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
                out.innerHTML = renderScan(data);
            })
            .catch(err => {
                out.innerHTML = `<p class="error">${err}</p>`;
            });
    });
});

function renderScan(d) {
    if (!d.opponents.length) {
        return '<p>No opponents scored.</p>';
    }
    const rows = d.opponents.map(o => {
        const verdictClass = {
            'very likely bot': 'verdict-high',
            'likely bot': 'verdict-mid',
            'suspicious': 'verdict-low',
            'unlikely bot': 'verdict-ok',
        }[o.verdict] || '';
        const fired = o.signals.filter(s => s.fired).map(s => s.name).join(', ') || '(none)';
        return `
            <tr>
                <td><strong class="${verdictClass}">${o.score}</strong></td>
                <td>${o.verdict}</td>
                <td>${escapeHtml(o.name || '')}</td>
                <td><code>${escapeHtml(o.tag || '')}</code></td>
                <td>L${o.exp_level} / ${o.trophies}</td>
                <td>${o.your_result}</td>
                <td>${escapeHtml(fired)}</td>
            </tr>
        `;
    }).join('');

    return `
        <p>Scanned ${d.scanned} unique opponents from <code>${escapeHtml(d.your_tag)}</code>'s recent battles.</p>
        <table class="scan-table">
            <thead><tr><th>Score</th><th>Verdict</th><th>Name</th><th>Tag</th><th>Lvl/Trophies</th><th>You</th><th>Signals fired</th></tr></thead>
            <tbody>${rows}</tbody>
        </table>
    `;
}

function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
}
