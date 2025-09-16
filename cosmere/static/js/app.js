// Cosmere RPG App JavaScript
const socket = io();

socket.on('connect', function() {
    console.log('Connected to server');
});

socket.on('dice_rolled', function(data) {
    displayDiceResult(data);
});

function createNewCharacter() {
    const name = document.getElementById('new-char-name').value.trim();
    const heritage = document.getElementById('new-char-heritage').value.trim();
    const path = document.getElementById('new-char-path').value.trim();
    const origin = document.getElementById('new-char-origin').value.trim();
    if (!name || !heritage || !path || !origin) {
        alert('Please fill in name, heritage, path, and origin.');
        return;
    }
    fetch('/api/characters', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name, heritage, path, origin })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            loadCharacters();
            populateCharacterSelect();
        } else {
            alert('Error creating character: ' + data.error);
        }
    })
    .catch(err => alert('Create failed'));
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
    loadPowers();
};

function loadCharacters() {
    fetch('/api/characters')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayCharacters(data.characters);
                populateCharacterSelect(data.characters);
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

function populateCharacterSelect(chars) {
    fetch('/api/characters')
        .then(r => r.json())
        .then(data => {
            if (!data.success) return;
            const sel = document.getElementById('char-select');
            sel.innerHTML = data.characters.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        });
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

function loadPowers() {
    fetch('/api/investiture/powers')
        .then(r => r.json())
        .then(data => {
            if (!data.success) return;
            const sel = document.getElementById('power-select');
            sel.innerHTML = data.powers.map(p => `<option value="${p.name}">${p.name} (cost ${p.cost})</option>`).join('');
        });
}

function updateInvestiture() {
    const sel = document.getElementById('char-select');
    const id = sel.value;
    if (!id) return;
    const type = document.getElementById('inv-type').value.trim();
    const points = parseInt(document.getElementById('inv-points').value, 10) || 0;
    const max = parseInt(document.getElementById('inv-max').value, 10) || 0;
    fetch(`/api/characters/${id}/investiture`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ type, investiture_points: points, max_investiture: max })
    })
    .then(r => r.json())
    .then(data => {
        const s = document.getElementById('inv-status');
        if (data.success) s.textContent = 'Saved.'; else s.textContent = 'Error: ' + data.error;
    });
}

function applyPower() {
    const sel = document.getElementById('char-select');
    const id = sel.value;
    if (!id) return;
    const power = document.getElementById('power-select').value;
    fetch(`/api/characters/${id}/investiture/apply`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ power })
    })
    .then(r => r.json())
    .then(data => {
        const s = document.getElementById('inv-status');
        if (data.success) s.textContent = `Applied ${power}. Remaining points: ${data.character.investiture.investiture_points}`;
        else s.textContent = 'Error: ' + data.error;
    });
}
