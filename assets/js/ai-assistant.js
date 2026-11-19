/* Ask-about-Bo assistant: floating chat bar at the bottom of the page.
   Markup comes from _includes/ai-assistant.html; answers come from the
   Cloudflare Worker in tools/ai-assistant-worker (data-endpoint).
   If data-endpoint is empty and window.BoAiMock is a function, it is used
   instead (local preview only). */
(function () {
  'use strict';

  var root = document.getElementById('bo-ai');
  if (!root) return;

  var endpoint = root.getAttribute('data-endpoint') || '';
  var MAX_INPUT = 800;
  var MAX_TURNS = 12;

  var form = root.querySelector('.bo-ai__form');
  var input = root.querySelector('.bo-ai__input');
  var send = root.querySelector('.bo-ai__send');
  var log = root.querySelector('.bo-ai__log');
  var closeBtn = root.querySelector('[data-bo-ai-close]');
  var minBtn = root.querySelector('[data-bo-ai-min]');
  var fab = root.querySelector('.bo-ai__fab');
  var history = [];
  var busy = false;

  document.body.classList.add('has-bo-ai');

  function store(key, value) {
    try {
      if (value === undefined) return window.localStorage.getItem(key);
      if (value === null) window.localStorage.removeItem(key);
      else window.localStorage.setItem(key, value);
    } catch (e) { return null; }
    return null;
  }

  function setMin(min) {
    root.classList.toggle('is-min', min);
    document.body.classList.toggle('bo-ai-min', min);
    store('bo-ai-min', min ? '1' : null);
    if (!min) input.focus();
  }

  function open() {
    if (!root.classList.contains('is-open')) root.classList.add('is-open');
  }
  function close() { root.classList.remove('is-open'); }

  if (store('bo-ai-min') === '1') {
    root.classList.add('is-min');
    document.body.classList.add('bo-ai-min');
  }

  // Minimal, safe rendering: escape everything, then allow https links,
  // **bold**, bullet lines and paragraphs.
  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function inline(s) {
    s = escapeHtml(s);
    s = s.replace(/\[([^\]]+)\]\((https:\/\/[^\s)]+)\)/g, function (m, text, url) {
      return '<a href="' + url + '" target="_blank" rel="noopener">' + text + '</a>';
    });
    s = s.replace(/(^|[\s(])(https:\/\/[^\s<)]+[^\s<).,;:])/g, function (m, pre, url) {
      return pre + '<a href="' + url + '" target="_blank" rel="noopener">' + url + '</a>';
    });
    s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    return s;
  }
  function render(text) {
    var out = [];
    var list = null;
    text.split(/\n/).forEach(function (line) {
      var t = line.trim();
      var bullet = /^[-*•]\s+(.*)$/.exec(t);
      if (bullet) {
        if (!list) { list = []; }
        list.push('<li>' + inline(bullet[1]) + '</li>');
        return;
      }
      if (list) { out.push('<ul>' + list.join('') + '</ul>'); list = null; }
      if (t) out.push('<p>' + inline(t) + '</p>');
    });
    if (list) out.push('<ul>' + list.join('') + '</ul>');
    return out.join('');
  }

  function addMessage(role, text, extraClass) {
    var el = document.createElement('div');
    el.className = 'bo-ai__msg bo-ai__msg--' + role + (extraClass ? ' ' + extraClass : '');
    if (role === 'user') el.textContent = text;
    else el.innerHTML = render(text);
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return el;
  }

  function typing() {
    var el = document.createElement('div');
    el.className = 'bo-ai__msg bo-ai__msg--bot';
    el.setAttribute('aria-label', 'Assistant is typing');
    el.innerHTML = '<span class="bo-ai__typing"><span></span><span></span><span></span></span>';
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return el;
  }

  function autosize() {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 140) + 'px';
    send.disabled = busy || !input.value.trim();
  }

  function fetchAnswer(messages) {
    if (!endpoint && typeof window.BoAiMock === 'function') {
      return Promise.resolve(window.BoAiMock(messages));
    }
    return fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: messages })
    }).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (data) {
        if (!res.ok || typeof data.reply !== 'string') {
          throw new Error(data.error || 'The assistant is unavailable right now. Please try again later.');
        }
        return data.reply;
      });
    });
  }

  function ask(question) {
    question = question.trim().slice(0, MAX_INPUT);
    if (!question || busy) return;
    open();
    var intro = root.querySelector('.bo-ai__welcome');
    if (intro) intro.remove();
    addMessage('user', question);
    history.push({ role: 'user', content: question });
    history = history.slice(-MAX_TURNS);
    if (history[0] && history[0].role !== 'user') history.shift();
    input.value = '';
    busy = true;
    autosize();
    var wait = typing();
    fetchAnswer(history.slice()).then(function (reply) {
      wait.remove();
      addMessage('bot', reply);
      history.push({ role: 'assistant', content: reply });
    }).catch(function (err) {
      wait.remove();
      history.pop();
      addMessage('bot', err && err.message ? err.message : 'Something went wrong. Please try again.', 'bo-ai__msg--error');
    }).then(function () {
      busy = false;
      autosize();
      input.focus();
    });
  }

  form.addEventListener('submit', function (e) { e.preventDefault(); ask(input.value); });
  input.addEventListener('input', autosize);
  input.addEventListener('focus', open);
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); ask(input.value); }
  });
  root.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { close(); input.blur(); }
  });
  root.querySelectorAll('.bo-ai__chip').forEach(function (chip) {
    chip.addEventListener('click', function () { ask(chip.textContent); });
  });
  closeBtn.addEventListener('click', close);
  minBtn.addEventListener('click', function () { close(); setMin(true); });
  fab.addEventListener('click', function () { setMin(false); open(); });
  document.addEventListener('click', function (e) {
    if (root.classList.contains('is-open') && !root.contains(e.target) && !history.length) close();
  });

  autosize();
})();
