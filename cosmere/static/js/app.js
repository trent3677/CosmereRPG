// Cosmere RPG App JavaScript
const socket = io();

socket.on('connect', function() {
    console.log('Connected to server');
});

socket.on('dice_rolled', function(data) {
    displayDiceResult(data);
});

function createNewCharacter() {
    // TODO: Implement character creation dialog
    alert('Character creation coming soon!');
}

function rollSkillCheck() {
    fetch('/api/roll', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            type: 'skill',
            modifier: 0
        })
    }).then(r => r.json()).then(console.log);
}

function rollDamage() {
    fetch('/api/roll', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            type: 'damage',
            dice: 2,
            bonus: 0
        })
    }).then(r => r.json()).then(console.log);
}

function displayDiceResult(result) {
    const resultsDiv = document.getElementById('dice-results');
    resultsDiv.innerHTML = '<strong>Latest Roll:</strong><br>' + result.formatted;
}

// Load characters on page load
window.onload = function() {
    loadCharacters();
};

function loadCharacters() {
    fetch('/api/characters')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayCharacters(data.characters);
            }
        });
}

function displayCharacters(characters) {
    const listDiv = document.getElementById('character-list');
    if (characters.length === 0) {
        listDiv.innerHTML = '<p>No characters yet. Create your first character!</p>';
    } else {
        listDiv.innerHTML = characters.map(char => 
            `<div class="character-card">
                <h3>${char.name}</h3>
                <p>${char.heritage} ${char.path} - Level ${char.level}</p>
            </div>`
        ).join('');
    }
}

function searchRules() {
    const q = document.getElementById('rule-query').value.trim();
    if (!q) return;
    fetch('/api/rules/search?q=' + encodeURIComponent(q))
        .then(r => r.json())
        .then(data => {
            const out = document.getElementById('rule-results');
            if (!data.success || !data.results || data.results.length === 0) {
                out.innerHTML = 'No results.';
                return;
            }
            out.innerHTML = data.results.map(r => {
                return `<div class="rule-item"><strong>${r.title || r.type || 'Entry'}</strong><br><small>Page: ${r.page || '?'}</small><br>${(r.content||'').slice(0,180)}...</div>`
            }).join('');
        })
        .catch(() => {
            document.getElementById('rule-results').innerHTML = 'Search error.';
        });
}
