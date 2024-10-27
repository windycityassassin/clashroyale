document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('player-form');
    const analysisDiv = document.getElementById('battle-analysis');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const playerTag = document.getElementById('player-tag').value;
        analysisDiv.innerHTML = 'Loading...';

        console.log('Submitting player tag:', playerTag);  // Debug log

        fetch('/api/battle_replay', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({player_tag: playerTag}),
        })
        .then(response => {
            console.log('Response status:', response.status);  // Debug log
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data);  // Debug log
            if (data.error) {
                analysisDiv.innerHTML = `<p class="error">${data.error}</p>`;
            } else {
                let html = '<h2>Battle Analysis</h2>';
                data.forEach((battle, index) => {
                    html += `
                        <div class="battle">
                            <h3>Battle ${index + 1}</h3>
                            <p>Time: ${battle.battleTime}</p>
                            <p>Game Mode: ${battle.gameMode}</p>
                            <p>Arena: ${battle.arena}</p>
                            <p>Result: ${battle.result}</p>
                            <p>Crowns Earned: ${battle.crownsEarned}</p>
                            <p>Crowns Lost: ${battle.crownsLost}</p>
                            <p>Trophy Change: ${battle.trophyChange}</p>
                        </div>
                    `;
                });
                analysisDiv.innerHTML = html;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            analysisDiv.innerHTML = '<p class="error">An error occurred while fetching battle data.</p>';
        });
    });
});