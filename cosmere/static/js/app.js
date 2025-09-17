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
    const stats = {
        strength: parseInt(document.getElementById('stat-strength').value, 10) || 0,
        speed: parseInt(document.getElementById('stat-speed').value, 10) || 0,
        intellect: parseInt(document.getElementById('stat-intellect').value, 10) || 0,
        willpower: parseInt(document.getElementById('stat-willpower').value, 10) || 0,
        awareness: parseInt(document.getElementById('stat-awareness').value, 10) || 0,
        persuasion: parseInt(document.getElementById('stat-persuasion').value, 10) || 0,
    };
    fetch('/api/characters', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name, heritage, path, origin, stats })
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
    getSession();
    loadTalents();
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
            sel.onchange = onCharacterSelected;
            onCharacterSelected();

            const saveSel = document.getElementById('save-char-select');
            if (saveSel) {
                saveSel.innerHTML = data.characters.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
            }

            const tSel = document.getElementById('talent-char-select');
            if (tSel) {
                tSel.innerHTML = data.characters.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
            }

            const pSel = document.getElementById('combat-participants');
            if (pSel) {
                pSel.innerHTML = data.characters.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
            }
        });
}

function onCharacterSelected() {
    // Could fetch and display current pool if a per-character GET existed; for now, pool updates via Save Investiture.
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
    // Optionally filter by type if a type is entered
    const type = (document.getElementById('inv-type')?.value || '').trim();
    const url = type ? ('/api/investiture/powers?type=' + encodeURIComponent(type)) : '/api/investiture/powers';
    fetch(url)
        .then(r => r.json())
        .then(data => {
            if (!data.success) return;
            const sel = document.getElementById('power-select');
            sel.innerHTML = data.powers.map(p => `<option value="${p.name}">${p.name}${p.type ? ' ['+p.type+']' : ''} (cost ${p.cost})</option>`).join('');
        });
}

// Talents
function loadTalents() {
    const path = (document.getElementById('talent-path')?.value || '').trim();
    const url = path ? ('/api/talents?path=' + encodeURIComponent(path)) : '/api/talents';
    fetch(url)
        .then(r => r.json())
        .then(data => {
            if (!data.success) return;
            const list = document.getElementById('talent-list');
            const sel = document.getElementById('talent-select');
            const items = data.talents || [];
            if (list) list.innerHTML = items.map(t => `<div><strong>${t.name}</strong>${t.path ? ' ['+t.path+']' : ''}<br><small>${t.description||''}</small></div>`).join('');
            if (sel) sel.innerHTML = items.map(t => `<option value="${t.name}">${t.name}</option>`).join('');
        });
}

function applyTalent() {
    const tSel = document.getElementById('talent-select');
    const name = tSel.value; if (!name) return;
    const cSel = document.getElementById('talent-char-select');
    const id = cSel.value; if (!id) return;
    fetch(`/api/characters/${id}/talents`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ name }) })
        .then(r => r.json())
        .then(data => {
            const s = document.getElementById('talent-status');
            if (data.success) s.textContent = `Applied ${name} to ${data.character.name}`; else s.textContent = 'Error: ' + data.error;
        });
}

// Combat
function startCombat() {
    const sel = document.getElementById('combat-participants');
    const ids = Array.from(sel.selectedOptions).map(o => o.value);
    if (ids.length === 0) { alert('Select at least one participant'); return; }
    fetch('/api/combat/start', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ character_ids: ids }) })
        .then(r => r.json()).then(data => { if (data.success) renderCombatState(data.state); });
}

function getCombatState() {
    fetch('/api/combat/state').then(r => r.json()).then(data => { if (data.success) renderCombatState(data.state); });
}

function combatActSkill() {
    const state = document.getElementById('combat-state').dataset;
    const actor = state.turnId; if (!actor) return;
    fetch('/api/combat/act', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ actor_id: actor, action: 'skill_check', payload: { modifier: 0 } }) })
        .then(r => r.json()).then(data => { if (data.success) renderCombatState(data.state); });
}

function combatActPower() {
    const state = document.getElementById('combat-state').dataset;
    const actor = state.turnId; if (!actor) return;
    const power = (document.getElementById('power-select')?.value) || '';
    if (!power) { alert('Select a power in Investiture section'); return; }
    fetch('/api/combat/act', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ actor_id: actor, action: 'use_power', payload: { power } }) })
        .then(r => r.json()).then(data => { if (data.success) renderCombatState(data.state); });
}

function combatEndTurn() {
    const state = document.getElementById('combat-state').dataset;
    const actor = state.turnId; if (!actor) return;
    fetch('/api/combat/act', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ actor_id: actor, action: 'end_turn' }) })
        .then(r => r.json()).then(data => { if (data.success) renderCombatState(data.state); });
}

function finishCombat() {
    fetch('/api/combat/finish', { method: 'POST' }).then(r => r.json()).then(data => { if (data.success) renderCombatState(data.state); });
}

function renderCombatState(state) {
    const div = document.getElementById('combat-state');
    div.dataset.turnId = state.turn_character_id || '';
    let html = '';
    html += `<div><strong>Round:</strong> ${state.round || '-'} | <strong>Turn Index:</strong> ${state.turn_index || 0}</div>`;
    // Add a target selector for convenience
    html += '<div><label>Target<select id="combat-target">' + (state.order||[]).map(o => `<option value="${o.id}">${o.name}</option>`).join('') + '</select></label></div>';
    html += '<div><strong>Order:</strong><ul>' + (state.order||[]).map(o => `<li>${o.name} (${o.initiative}) ${o.conditions && o.conditions.length ? '['+o.conditions.join(', ')+']' : ''}</li>`).join('') + '</ul></div>';
    html += '<div><strong>Log:</strong><ul>' + (state.log||[]).map(e => `<li>${e.event}</li>`).join('') + '</ul></div>';
    div.innerHTML = html;
}

// Attack (damage) using current power dice selector from Investiture section
function combatActAttack() {
    const state = document.getElementById('combat-state').dataset;
    const actor = state.turnId; if (!actor) return;
    const tgtSel = document.getElementById('combat-target');
    const target_id = tgtSel ? tgtSel.value : '';
    if (!target_id) return;
    // Use 2d6 as a default example; could be refined via UI controls
    fetch('/api/combat/act', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ actor_id: actor, action: 'attack', payload: { target_id, dice: 2, bonus: 0 } }) })
        .then(r => r.json()).then(data => { if (data.success) renderCombatState(data.state); });
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
        if (data.success) s.textContent = `Saved. Points: ${data.character.investiture.investiture_points}/${data.character.investiture.max_investiture}`; else s.textContent = 'Error: ' + data.error;
        // Reload powers filtered by the saved type
        loadPowers();
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

// Session handling
function getSession() {
    fetch('/api/session')
        .then(r => r.json())
        .then(data => {
            const s = document.getElementById('session-status');
            if (data.success && data.username) {
                s.textContent = `Logged in as ${data.username}`;
            } else {
                s.textContent = 'Not logged in';
            }
        });
}

function login() {
    const username = document.getElementById('username').value.trim();
    if (!username) return;
    fetch('/api/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username })
    }).then(r => r.json()).then(() => getSession());
}

function logout() {
    fetch('/api/session', { method: 'DELETE' })
        .then(() => getSession());
}

// Save export/import/delete
function exportCharacter() {
    const sel = document.getElementById('save-char-select');
    const id = sel.value;
    if (!id) return;
    fetch(`/api/characters/${id}/export`)
        .then(r => r.json())
        .then(data => {
            if (!data.success) { alert('Export error: ' + data.error); return; }
            const blob = new Blob([JSON.stringify(data.character, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url; a.download = `${data.character.name}_${data.character.id}.json`;
            document.body.appendChild(a); a.click(); a.remove();
            URL.revokeObjectURL(url);
        });
}

function importCharacter() {
    const txt = document.getElementById('import-json').value.trim();
    if (!txt) return;
    let payload;
    try { payload = JSON.parse(txt); } catch { alert('Invalid JSON'); return; }
    fetch('/api/characters/import', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    }).then(r => r.json()).then(data => {
        if (!data.success) { alert('Import error: ' + data.error); return; }
        loadCharacters(); populateCharacterSelect();
        document.getElementById('import-json').value = '';
    });
}

function deleteCharacter() {
    const sel = document.getElementById('save-char-select');
    const id = sel.value; if (!id) return;
    if (!confirm('Delete this character?')) return;
    fetch(`/api/characters/${id}`, { method: 'DELETE' })
        .then(r => r.json())
        .then(data => {
            if (!data.success) { alert('Delete error: ' + (data.error || 'unknown')); return; }
            loadCharacters(); populateCharacterSelect();
        });
}
