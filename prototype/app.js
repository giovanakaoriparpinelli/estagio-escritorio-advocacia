'use strict';
// Quando aberto direto do disco (file://), fala com o serviço local; servido por ele, usa caminhos relativos.
const API = location.protocol === 'file:' ? 'http://127.0.0.1:8765' : '';
const $ = (s) => document.querySelector(s);
const ROTULO = {rascunho: 'Rascunho', em_revisao: 'Em revisão', aprovada: 'Aprovada', devolvida: 'Devolvida'};
let token = null, usuario = null, editandoId = null;
try { token = sessionStorage.getItem('token'); } catch (e) { /* armazenamento indisponível */ }

function esc(t) { // todo texto vindo da API é inserido como texto, nunca como HTML
  const d = document.createElement('div'); d.textContent = String(t ?? ''); return d.innerHTML;
}
function quando(s) { return s ? new Date(s.replace(' ', 'T') + 'Z').toLocaleString('pt-BR') : ''; }

async function api(metodo, caminho, corpo, bruto) {
  const resp = await fetch(API + caminho, {
    method: metodo,
    headers: Object.assign({'Content-Type': 'application/json'}, token ? {Authorization: 'Bearer ' + token} : {}),
    body: corpo === undefined ? undefined : JSON.stringify(corpo)
  });
  if (resp.status === 401 && caminho !== '/api/login') { sair(false); throw new Error('Sessão expirada. Entre novamente.'); }
  if (!resp.ok) {
    let msg = 'Erro ' + resp.status;
    try { msg = (await resp.json()).erro || msg; } catch (e) { /* sem corpo */ }
    throw new Error(msg);
  }
  if (bruto) return resp.blob();
  return resp.status === 204 ? null : resp.json();
}

function aviso(texto, tipo) {
  const box = $('#status'); box.hidden = false; box.className = 'result ' + (tipo || ''); box.textContent = texto;
}

// ---- sessão -------------------------------------------------------------------------
function mostrarLogin(sim) { $('#login-overlay').hidden = !sim; }
function sair(avisarServidor = true) {
  if (avisarServidor && token) api('POST', '/api/logout', {}).catch(() => {});
  token = usuario = null;
  try { sessionStorage.removeItem('token'); } catch (e) { /* ignora */ }
  mostrarLogin(true);
}
$('#logout').addEventListener('click', () => sair(true));

$('#login-form').addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const f = new FormData(ev.target), erro = $('#login-erro'); erro.hidden = true;
  try {
    const r = await api('POST', '/api/login', {email: f.get('email'), senha: f.get('senha')});
    token = r.token;
    try { sessionStorage.setItem('token', token); } catch (e) { /* ignora */ }
    ev.target.reset();
    await iniciar();
  } catch (e) { erro.hidden = false; erro.textContent = e.message; }
});

async function iniciar() {
  try { usuario = await api('GET', '/api/me'); } catch (e) { mostrarLogin(true); return; }
  mostrarLogin(false);
  $('#user-name').textContent = usuario.nome;
  $('#user-role').textContent = usuario.perfil === 'advogado' ? 'Advogado' : 'Estagiária';
  $('#avatar').textContent = usuario.nome.split(' ').map((p) => p[0]).slice(0, 2).join('').toUpperCase();
  $('#saudacao').textContent = 'Bem-vindo(a), ' + usuario.nome.split(' ')[0] + '.';
  const adv = usuario.perfil === 'advogado';
  $('#auditoria').hidden = !adv; $('#nav-auditoria').hidden = !adv;
  await atualizar();
}

async function atualizar() {
  try {
    const p = await api('GET', '/api/painel');
    for (const k of ['rascunho', 'em_revisao', 'aprovada']) $('#m-' + k).textContent = String(p.minutas[k]).padStart(2, '0');
    $('#lista-prazos').innerHTML = p.prazos.length ? p.prazos.map((z) =>
      `<div class="activity"><span class="file-icon ${z.vencido ? 'late' : ''}">${z.vencido ? 'VENC' : z.dias_restantes + 'd'}</span>` +
      `<div><strong>${esc(z.descricao)}</strong><small>${esc(z.cliente)} · ${esc(z.processo)} · ${esc(z.data.split('-').reverse().join('/'))}</small></div>` +
      `<button class="outline small" data-prazo="${z.id}">Cumprido</button></div>`).join('') :
      '<p class="intro">Nenhum prazo nos próximos 15 dias.</p>';
    const minutas = await api('GET', '/api/minutas');
    $('#lista-minutas').innerHTML = minutas.length ? minutas.map(linhaMinuta).join('') : '<p class="intro">Nenhuma minuta ainda.</p>';
    if (usuario.perfil === 'advogado') {
      const ev = await api('GET', '/api/auditoria');
      $('#lista-auditoria').innerHTML = ev.slice(0, 15).map((e) =>
        `<div class="activity"><span class="file-icon">LOG</span><div><strong>${esc(e.acao)}</strong>` +
        `<small>${esc(e.usuario || 'anônimo')} · ${esc(quando(e.criado_em))} ${e.detalhe ? '· ' + esc(e.detalhe) : ''}</small></div></div>`).join('');
    }
  } catch (e) { aviso(e.message, 'error'); }
}

function linhaMinuta(m) {
  const adv = usuario.perfil === 'advogado', acoes = [];
  if (m.status === 'rascunho') acoes.push(['editar', 'Editar'], ['enviar', 'Enviar p/ revisão']);
  if (m.status === 'em_revisao' && adv) acoes.push(['aprovar', 'Aprovar'], ['devolver', 'Devolver']);
  if (m.status === 'devolvida' || m.status === 'aprovada') acoes.push(['versao', 'Nova versão']);
  acoes.push(['docx', 'DOCX']);
  return `<div class="activity" data-id="${m.id}"><span class="file-icon">v${m.versao}</span>` +
    `<div><strong>${esc(m.cliente)} · ${esc(m.processo)}</strong><small>${esc(m.titulo)} · ${esc(m.autor)} · ${esc(quando(m.criado_em))}` +
    `${m.motivo_devolucao ? ' · Motivo: ' + esc(m.motivo_devolucao) : ''}</small></div>` +
    `<span class="tag st-${m.status}">${ROTULO[m.status]}</span>` +
    `<div class="row-actions">${acoes.map(([a, t]) => `<button class="outline small" data-acao="${a}">${t}</button>`).join('')}</div></div>`;
}

// ---- ações da lista -----------------------------------------------------------------
document.addEventListener('click', async (ev) => {
  const b = ev.target.closest('button[data-acao],button[data-prazo]'); if (!b) return;
  try {
    if (b.dataset.prazo) { await api('POST', `/api/prazos/${b.dataset.prazo}/cumprido`, {}); return atualizar(); }
    const id = b.closest('[data-id]').dataset.id, a = b.dataset.acao;
    if (a === 'editar') {
      const m = await api('GET', '/api/minutas/' + id);
      for (const [k, v] of Object.entries(m.campos)) $('#manifest-form').elements[k].value = v;
      editandoId = m.id; $('#form-titulo').textContent = 'Editar rascunho (v' + m.versao + ')';
      $('#cancel-edit').hidden = false; location.hash = '#nova-minuta';
    } else if (a === 'enviar') await api('POST', `/api/minutas/${id}/enviar-revisao`, {});
    else if (a === 'aprovar') { if (confirm('Confirma a aprovação desta minuta?')) await api('POST', `/api/minutas/${id}/aprovar`, {}); }
    else if (a === 'devolver') {
      const motivo = prompt('Motivo da devolução:'); if (!motivo) return;
      await api('POST', `/api/minutas/${id}/devolver`, {motivo});
    } else if (a === 'versao') await api('POST', `/api/minutas/${id}/nova-versao`, {});
    else if (a === 'docx') {
      const blob = await api('GET', `/api/minutas/${id}/docx`, undefined, true);
      const l = document.createElement('a'); l.href = URL.createObjectURL(blob); l.download = `manifestacao-simples-${id}.docx`;
      l.click(); URL.revokeObjectURL(l.href); aviso('DOCX gerado. Documentos não aprovados saem marcados como RASCUNHO.', 'success'); return;
    }
    await atualizar();
  } catch (e) { aviso(e.message, 'error'); }
});

// ---- formulário -----------------------------------------------------------------------
function limparForm() {
  $('#manifest-form').reset(); editandoId = null;
  $('#form-titulo').textContent = 'Nova manifestação simples'; $('#cancel-edit').hidden = true;
}
$('#cancel-edit').addEventListener('click', limparForm);
$('#manifest-form').addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const dados = Object.fromEntries(new FormData(ev.target).entries());
  try {
    const m = editandoId ? await api('PUT', '/api/minutas/' + editandoId, dados) : await api('POST', '/api/minutas', dados);
    aviso(`Rascunho salvo (minuta ${m.id}, versão ${m.versao}). Envie para revisão quando estiver pronto.`, 'success');
    limparForm(); await atualizar();
  } catch (e) { aviso(e.message, 'error'); }
});

iniciar();
