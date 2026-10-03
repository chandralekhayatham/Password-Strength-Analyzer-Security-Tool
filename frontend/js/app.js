const password = document.getElementById('password');
const toggle = document.getElementById('toggle');
const generate = document.getElementById('generate');
const firstName = document.getElementById('firstName');
const birthYear = document.getElementById('birthYear');
const college = document.getElementById('college');
let timer;

toggle.addEventListener('click', () => {
  password.type = password.type === 'password' ? 'text' : 'password';
  toggle.textContent = password.type === 'password' ? 'Show' : 'Hide';
});

async function analyze() {
  clearTimeout(timer);
  timer = setTimeout(async () => {
    const response = await fetch('/api/analyze', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        password: password.value,
        context: {first_name:firstName.value, birth_year:birthYear.value, college_company:college.value}
      })
    });
    const data = await response.json();
    renderResult(data);
    loadDashboard();
  }, 180);
}

function renderResult(data) {
  document.getElementById('classification').textContent = data.classification || '—';
  document.getElementById('score').textContent = `${data.score ?? 0}/100`;
  document.getElementById('meterFill').style.width = `${data.score ?? 0}%`;
  const m = data.metrics || {};
  document.getElementById('metrics').innerHTML = [
    ['Length', `${m.length ?? 0} (${m.band || '—'})`],
    ['Entropy-style estimate', `${m.entropy_bits ?? 0} bits`],
    ['Character types', m.character_type_count ?? 0],
    ['Unique ratio', m.unique_character_ratio ?? 0],
    ['Sequences', m.sequence_count ?? 0],
    ['Repetition', m.repetition_count ?? 0]
  ].map(([a,b]) => `<div class="metric"><strong>${escapeHtml(a)}</strong><br>${escapeHtml(String(b))}</div>`).join('');
  document.getElementById('findings').innerHTML = (data.findings?.length ? data.findings : ['No major weakness detected by this project-defined heuristic.']).map(x=>`<li>⚠ ${escapeHtml(x)}</li>`).join('');
  document.getElementById('suggestions').innerHTML = (data.suggestions || []).map(x=>`<li>💡 ${escapeHtml(x)}</li>`).join('');
}

function escapeHtml(value) { const d = document.createElement('div'); d.textContent = value; return d.innerHTML; }

password.addEventListener('input', analyze); firstName.addEventListener('input', analyze); birthYear.addEventListener('input', analyze); college.addEventListener('input', analyze);

generate.addEventListener('click', async () => {
  const response = await fetch('/api/generate-password?length=20');
  const data = await response.json();
  password.value = data.password;
  await navigator.clipboard?.writeText(data.password);
  analyze();
});

document.getElementById('refreshDashboard').addEventListener('click', loadDashboard);

async function loadDashboard() {
  const response = await fetch('/api/dashboard/stats');
  const data = await response.json();
  const d = data.strength_distribution || {};
  document.getElementById('stats').innerHTML = [
    ['Total', data.total_analyses], ['Average score', data.average_score],
    ['Very Weak', d['VERY WEAK'] || 0], ['Weak', d['WEAK'] || 0],
    ['Moderate', d['MODERATE'] || 0], ['Strong+', (d['STRONG'] || 0) + (d['VERY STRONG'] || 0)]
  ].map(([a,b])=>`<div class="stat"><span>${a}</span><strong>${b}</strong></div>`).join('');

  const maxD = Math.max(1, ...Object.values(d));
  document.getElementById('distribution').innerHTML = Object.entries(d).map(([k,v])=>`<div class="bar-row"><div class="bar-label"><span>${escapeHtml(k)}</span><span>${v}</span></div><div class="bar"><span style="width:${v/maxD*100}%"></span></div></div>`).join('') || '<p class="small">No analyses yet.</p>';
  const weaknesses = data.weakness_frequency || [];
  const maxW = Math.max(1, ...weaknesses.map(x=>x.count));
  document.getElementById('weaknesses').innerHTML = weaknesses.map(x=>`<div class="bar-row"><div class="bar-label"><span>${escapeHtml(x.type)}</span><span>${x.count}</span></div><div class="bar"><span style="width:${x.count/maxW*100}%"></span></div></div>`).join('') || '<p class="small">No findings yet.</p>';
}
loadDashboard();
