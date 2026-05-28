document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('synergy-form');
    const out = document.getElementById('synergy-result');

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const card = document.getElementById('card-name').value.trim();
        out.innerHTML = 'Fetching top-200 decks (may take ~40s on cold cache)...';

        fetch('/api/synergy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ card: card }),
        })
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    out.innerHTML = `<p class="error">${data.error}</p>`;
                    return;
                }
                out.innerHTML = renderSynergy(data);
            })
            .catch(err => {
                out.innerHTML = `<p class="error">${err}</p>`;
            });
    });
});

function renderSynergy(d) {
    if (!d.partners || !d.partners.length) {
        return `<p>${escapeHtml(d.note || 'No partners found.')}</p>`;
    }
    const max = d.partners[0].pair_rate;
    const rows = d.partners.map(p => `
        <tr>
            <td>${escapeHtml(p.name)}</td>
            <td>${p.co_occurrences}</td>
            <td>${p.pair_rate}%</td>
            <td><div class="bar" style="width:${(p.pair_rate / max) * 100}%"></div></td>
        </tr>
    `).join('');

    return `
        <p><strong>${escapeHtml(d.card)}</strong> appears in <strong>${d.decks_with_card}</strong> of ${d.total_decks} top-200 decks (${d.card_pick_rate}% pick rate).</p>
        <table class="synergy-table">
            <thead><tr><th>Partner card</th><th>Co-occurrences</th><th>Pair rate</th><th></th></tr></thead>
            <tbody>${rows}</tbody>
        </table>
    `;
}

function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
}
