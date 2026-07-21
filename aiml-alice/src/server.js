#!/usr/bin/env node
/**
 * AIML-ALICE Web Server — zero-dependency chat web app.
 *
 * Serves a minimal single-page chat UI and a JSON chat API backed by the
 * full AIMLEngine (brain + bot properties + substitutions + sets + maps).
 *
 * Usage:
 *   node src/server.js                 # http://localhost:8080
 *   PORT=3000 node src/server.js       # custom port
 *   node src/server.js --aiml ./brain  # custom AIML directory
 *
 * No npm dependencies — uses only Node built-ins.
 */

import { createServer } from 'node:http';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { AIMLEngine } from './engine.js';
import { createRouter } from './router.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, '..');

// ---- Parse args / env ----
const args = process.argv.slice(2);
let aimlDir = resolve(root, 'aiml');
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--aiml' && args[i + 1]) {
    aimlDir = resolve(args[i + 1]);
    i++;
  }
}
const PORT = Number(process.env.PORT) || 8080;
const HOST = process.env.HOST || '127.0.0.1';

// ---- Initialize engine (same load sequence as the CLI) ----
const engine = new AIMLEngine({
  substitutions: {
    normal: resolve(root, 'substitutions/normal.txt'),
    person: resolve(root, 'substitutions/person.txt'),
  },
});
engine.loadBotProperties(resolve(root, 'bot.properties'));
engine.loadSet('number', resolve(root, 'sets/number.txt'));
engine.loadSet('color', resolve(root, 'sets/color.txt'));
engine.loadMap('successor', resolve(root, 'maps/successor.txt'));
const categoryCount = engine.loadDirectory(aimlDir);
const botName = engine.getBotProperty('name') || 'Alice';

// Precache router: AIML handles confident hits; misses fall through to the agent.
// Wire a real LLM by passing { agent: async (msg, sessionId, gate) => reply }.
const router = createRouter(engine, {
  minSpecificity: Number(process.env.MIN_SPECIFICITY) || 1,
});

console.log(`[aiml-alice] loaded ${categoryCount} categories from ${engine.loadedFiles.length} file(s)`);

// ---- Chat page (self-contained, no external assets) ----
const PAGE = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${botName} — AIML Chat</title>
<style>
  :root { --bg:#0f1220; --panel:#171b2e; --me:#2b6cff; --bot:#242a44; --text:#e8eaf2; --muted:#8b93b0; }
  * { box-sizing:border-box; }
  html,body { height:100%; margin:0; }
  body { background:var(--bg); color:var(--text); font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
         display:flex; flex-direction:column; align-items:center; }
  header { width:100%; max-width:680px; padding:18px 16px 8px; }
  header h1 { margin:0; font-size:18px; }
  header p { margin:2px 0 0; color:var(--muted); font-size:13px; }
  #log { width:100%; max-width:680px; flex:1; overflow-y:auto; padding:12px 16px; }
  .msg { max-width:80%; padding:9px 13px; border-radius:14px; margin:6px 0; white-space:pre-wrap; word-wrap:break-word; }
  .me  { background:var(--me); color:#fff; margin-left:auto; border-bottom-right-radius:4px; }
  .bot { background:var(--bot); border-bottom-left-radius:4px; }
  .typing { color:var(--muted); font-style:italic; }
  .tag { display:inline-block; font-size:11px; margin:0 0 6px 2px; padding:1px 7px; border-radius:8px; color:#fff; }
  .tag.precache { background:#1f9d6b; }
  .tag.agent { background:#a25bff; }
  form { width:100%; max-width:680px; display:flex; gap:8px; padding:12px 16px 20px; }
  input { flex:1; padding:11px 14px; border-radius:12px; border:1px solid #2a3050; background:var(--panel); color:var(--text); font-size:15px; }
  input:focus { outline:none; border-color:var(--me); }
  button { padding:0 18px; border:0; border-radius:12px; background:var(--me); color:#fff; font-size:15px; cursor:pointer; }
  button:disabled { opacity:.5; cursor:default; }
</style>
</head>
<body>
  <header>
    <h1>${botName}</h1>
    <p>${categoryCount} categories · AIML 2.0 · pure JavaScript</p>
  </header>
  <div id="log" aria-live="polite"></div>
  <form id="form" autocomplete="off">
    <input id="input" placeholder="Say something…" autofocus>
    <button id="send" type="submit">Send</button>
  </form>
<script>
  const log = document.getElementById('log');
  const form = document.getElementById('form');
  const input = document.getElementById('input');
  const send = document.getElementById('send');
  const sessionId = 'web-' + Math.random().toString(36).slice(2) + Date.now().toString(36);

  function add(text, who, source) {
    if (source) {
      const tag = document.createElement('div');
      tag.className = 'tag ' + source;
      tag.textContent = source === 'precache' ? 'precache · AIML' : 'agent';
      log.appendChild(tag);
    }
    const el = document.createElement('div');
    el.className = 'msg ' + who;
    el.textContent = text;
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return el;
  }

  add("Hi, I'm ${botName}. Ask me anything.", 'bot');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    add(text, 'me');
    input.value = '';
    send.disabled = true;
    const typing = add('…', 'bot');
    typing.classList.add('typing');
    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, sessionId })
      });
      const data = await res.json();
      typing.remove();
      add(data.reply || '(no response)', 'bot', data.source);
    } catch (err) {
      typing.remove();
      add('⚠️ Connection error.', 'bot');
    } finally {
      send.disabled = false;
      input.focus();
    }
  });
</script>
</body>
</html>`;

// ---- Helpers ----
function sendJSON(res, status, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body),
  });
  res.end(body);
}

async function parseJsonBody(req) {
  const raw = await readBody(req);
  try {
    return JSON.parse(raw || '{}');
  } catch {
    const err = new Error('invalid JSON');
    err.status = 400;
    throw err;
  }
}

function readMessage(payload) {
  const message = typeof payload.message === 'string' ? payload.message.trim() : '';
  const sessionId = typeof payload.sessionId === 'string' && payload.sessionId
    ? payload.sessionId
    : 'anon';
  return { message, sessionId };
}

function statusForError(err) {
  if (err.status) return err.status;
  if (err.message === 'payload too large') return 413;
  return 500;
}

function readBody(req, limit = 1_000_000) {
  return new Promise((resolve, reject) => {
    let data = '';
    let size = 0;
    req.on('data', (chunk) => {
      size += chunk.length;
      if (size > limit) {
        reject(new Error('payload too large'));
        req.destroy();
        return;
      }
      data += chunk;
    });
    req.on('end', () => resolve(data));
    req.on('error', reject);
  });
}

// ---- Server ----
const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  if (req.method === 'GET' && (url.pathname === '/' || url.pathname === '/index.html')) {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(PAGE);
    return;
  }

  if (req.method === 'GET' && url.pathname === '/health') {
    sendJSON(res, 200, { ok: true, bot: botName, ...engine.stats(), router: router.metrics() });
    return;
  }

  // Chat: precache router — AIML hit served directly, miss routed to the agent.
  if (req.method === 'POST' && url.pathname === '/chat') {
    try {
      const payload = await parseJsonBody(req);
      const { message, sessionId } = readMessage(payload);
      if (!message) {
        sendJSON(res, 400, { error: 'empty message' });
        return;
      }
      const result = await router.handle(message, sessionId);
      sendJSON(res, 200, { ...result, sessionId });
    } catch (err) {
      sendJSON(res, statusForError(err), { error: err.message });
    }
    return;
  }

  // Pure precache gate — returns the hit/miss decision without invoking the agent.
  // This is the endpoint a separate agent-routing layer would consult.
  if (req.method === 'POST' && url.pathname === '/precache') {
    try {
      const payload = await parseJsonBody(req);
      const { message, sessionId } = readMessage(payload);
      if (!message) {
        sendJSON(res, 400, { error: 'empty message' });
        return;
      }
      const gate = engine.tryRespond(message, sessionId, {
        minSpecificity: Number(process.env.MIN_SPECIFICITY) || 1,
      });
      sendJSON(res, 200, { ...gate, source: gate.matched ? 'precache' : 'miss', sessionId });
    } catch (err) {
      sendJSON(res, statusForError(err), { error: err.message });
    }
    return;
  }

  sendJSON(res, 404, { error: 'not found' });
});

server.listen(PORT, HOST, () => {
  console.log(`[aiml-alice] chat web app running at http://${HOST}:${PORT}`);
});
