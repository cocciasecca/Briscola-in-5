// Browser client for the Italian LAN interface. The server remains authoritative.

const $ = (id) => document.getElementById(id);
let token = localStorage.getItem('briscola5_token');
let playerName = localStorage.getItem('briscola5_name') || '';
let socket = null;
let state = null;
$('name').value = playerName;

const suitNames = { denari:'Denari', coppe:'Coppe', spade:'Spade', bastoni:'Bastoni' };
const rankNames = { '1':'Asso', '2':'2', '3':'3', '4':'4', '5':'5', '6':'6', '7':'7', '8':'Fante', '9':'Cavallo', '10':'Re' };
const suitOrder = ['denari', 'coppe', 'spade', 'bastoni'];
const handRankOrder = ['2', '4', '5', '6', '7', '8', '9', '10', '3', '1'];
const handRankPosition = Object.fromEntries(handRankOrder.map((rank, index) => [rank, index]));
const phaseNames = { lobby:'Sala d’attesa', auction:'Asta', dead_trick_play:'Gioco', dead_trick_call:'Chiamata', trick_play:'Partita', game_over:'Fine partita' };

async function api(path, body) {
  const response = await fetch(path, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body) });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || 'Errore del server');
  return payload;
}
function toast(message) { $('toast').textContent = message; $('toast').classList.remove('hidden'); setTimeout(() => $('toast').classList.add('hidden'), 3300); }

async function join() {
  const name = $('name').value.trim() || 'Giocatore';
  try {
    const result = await api('/api/join', {name, token});
    token = result.token; playerName = name;
    localStorage.setItem('briscola5_token', token); localStorage.setItem('briscola5_name', name);
    $('join-screen').classList.add('hidden'); $('game-screen').classList.remove('hidden'); connect();
  } catch (e) { if (token) { localStorage.removeItem('briscola5_token'); token = null; } toast(e.message); }
}
$('join-btn').onclick = join; $('name').addEventListener('keydown', e => { if(e.key === 'Enter') join(); });

function connect() {
  if (!token) return;
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  socket = new WebSocket(`${proto}://${location.host}/ws?token=${encodeURIComponent(token)}`);
  socket.onopen = () => { $('connection').textContent = 'Connesso'; socket.send('hello'); };
  socket.onmessage = ev => { state = JSON.parse(ev.data); render(); };
  socket.onclose = () => { $('connection').textContent = 'Disconnesso, riconnessione…'; setTimeout(connect, 1500); };
}

// Render a local card scan; card.index is the original server hand index.
function cardElement(card, clickable=false) {
  const el = document.createElement('div'); el.className = `card ${card.suit}`;
  const img = document.createElement('img');
  img.src = `/static/cards/${card.suit}_${card.rank}.jpg`;
  img.alt = `${rankNames[card.rank]} di ${suitNames[card.suit]}`;
  img.draggable = false;
  el.appendChild(img);
  if (clickable) el.onclick = async () => { try { await api('/api/play', {token, card_index:card.index}); } catch(e) { toast(e.message); } };
  return el;
}
function hideControls() { ['lobby-controls','auction-controls','call-controls','play-help','waiting-controls','result-controls'].forEach(id => $(id).classList.add('hidden')); }

// Rebuild the visible table from the latest viewer-specific state snapshot.
function render() {
  $('phase-label').textContent = phaseNames[state.phase] || state.phase;
  $('event-line').textContent = state.last_event;
  $('start-btn').classList.toggle('hidden', !(state.is_host && !state.started));
  $('game-meta').textContent = state.started ? `Mano ${Math.min(state.trick_index + 1, 8)}/8${state.trump ? ` · Briscola: ${state.trump}` : ''}${state.target ? ` · Obiettivo: ${state.target}` : ''}` : 'In attesa che l’host avvii la partita';

  const calledBox = $('called-card-box');
  const calledSlot = $('called-card');
  calledSlot.innerHTML = '';
  if (state.called_card) {
    calledBox.classList.remove('hidden');
    calledSlot.appendChild(cardElement(state.called_card));
    $('called-card-label').textContent = `${rankNames[state.called_card.rank]} di ${suitNames[state.called_card.suit]}`;
  } else {
    calledBox.classList.add('hidden');
  }

  const players = $('players'); players.innerHTML = '';
  state.players.forEach((p, i) => {
    if (!p) return;
    const el = document.createElement('div');
    el.className = `player p${i}${state.current_player === i ? ' current':''}${state.viewer_id === i ? ' me':''}${!p.connected ? ' disconnected':''}${state.trick_result?.winner_id === i ? ' winner':''}`;
    const badges = [p.is_bot ? 'BOT' : '', state.caller === i ? 'CHIAMANTE' : '', state.partner === i ? 'SOCIO' : ''].filter(Boolean).join(' · ');
    el.innerHTML = `<div class="name">${escapeHtml(p.name)}</div><div class="details">${badges || `Giocatore ${i+1}`}<br>${state.started ? `${p.cards} carte · ${p.points} pt` : (p.connected ? 'connesso' : 'disconnesso')}</div>`;
    players.appendChild(el);
  });

  const played = $('played-cards'); played.innerHTML = '';
  state.table.forEach(c => { const wrap = document.createElement('div'); wrap.className=`played-card pc${c.player_id}`; wrap.appendChild(cardElement(c)); played.appendChild(wrap); });

  const trickResult = $('trick-result');
  if (state.trick_result) {
    trickResult.textContent = `PRENDE: ${state.trick_result.winner_name} (+${state.trick_result.points} punti)`;
    trickResult.classList.remove('hidden');
  } else {
    trickResult.classList.add('hidden');
  }

  const myTurn = state.viewer_id === state.current_player && !state.paused;
  const canPlay = myTurn && state.phase === 'trick_play';
  const hand = $('hand'); hand.innerHTML=''; hand.classList.toggle('disabled', !canPlay);
  // Group cards by suit, then apply the requested Briscola value ordering.
  suitOrder.forEach(suit => {
    const cards = state.hand
      .filter(card => card.suit === suit)
      .sort((a, b) => handRankPosition[a.rank] - handRankPosition[b.rank]);
    if (!cards.length) return;

    const group = document.createElement('div');
    group.className = `suit-group ${suit}`;
    group.setAttribute('aria-label', suitNames[suit]);
    cards.forEach((card, index) => {
      const el = cardElement(card, canPlay);
      el.style.transform = `rotate(${(index - (cards.length - 1) / 2) * 1.8}deg)`;
      group.appendChild(el);
    });
    hand.appendChild(group);
  });

  hideControls();
  if (!state.started) $('lobby-controls').classList.remove('hidden');
  else if (state.phase === 'auction' && myTurn) { $('auction-controls').classList.remove('hidden'); $('bid-value').min = (state.last_bid || 70)+1; $('bid-value').value = Math.min(120,(state.last_bid || 70)+1); }
  else if (state.phase === 'dead_trick_call' && state.viewer_id === state.caller && !state.paused) $('call-controls').classList.remove('hidden');
  else if (canPlay) { $('play-help').classList.remove('hidden'); $('play-title').textContent = 'Il tuo turno'; }
  else if (state.phase === 'game_over') renderResult();
  else { $('waiting-controls').classList.remove('hidden'); $('waiting-title').textContent = state.resolving_trick ? 'Presa in corso…' : 'Attendi il tuo turno'; }

  $('pause-banner').classList.toggle('hidden', !state.paused); $('pause-reason').textContent = state.pause_reason;
  const repl = $('replace-actions'); repl.innerHTML='';
  if (state.paused && state.is_host) state.players.filter(p => p && !p.is_bot && !p.connected).forEach(p => { const b=document.createElement('button'); b.textContent=`Sostituisci ${p.name} con un bot`; b.onclick=async()=>{try{await api('/api/replace',{token,player_id:p.id});}catch(e){toast(e.message)}}; repl.appendChild(b); });
}
function renderResult(){ const box=$('result-controls'); box.classList.remove('hidden'); const r=state.result; if(!r){box.innerHTML='<h2>Partita terminata</h2>';return;} box.innerHTML=`<h2>Risultato finale</h2><div class="result ${r.won?'win':'lose'}">La squadra del chiamante ha totalizzato <strong>${r.team_points}</strong> punti su ${r.target}: <strong>${r.won?'VITTORIA':'SCONFITTA'}</strong></div>`; }
function escapeHtml(s){ return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }

$('start-btn').onclick=async()=>{try{await api('/api/start',{token});}catch(e){toast(e.message)}};
$('bid-btn').onclick=async()=>{try{await api('/api/bid',{token,offer:Number($('bid-value').value)});}catch(e){toast(e.message)}};
$('pass-btn').onclick=async()=>{try{await api('/api/bid',{token,offer:null});}catch(e){toast(e.message)}};
$('call-btn').onclick=async()=>{try{await api('/api/call',{token,suit:$('call-suit').value,rank:$('call-rank').value});}catch(e){toast(e.message)}};

fetch('/api/info').then(r=>r.json()).then(i=>$('server-address').textContent=`Indirizzo LAN: http://${i.lan_ip}:${i.port}`).catch(()=>{});
if (token && playerName) join();
