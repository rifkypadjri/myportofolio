const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const { JSDOM, VirtualConsole } = require(process.argv[2] || 'jsdom');
const source = fs.readFileSync(path.join(__dirname, '../static/js/experience.js'), 'utf8');
const flush = () => new Promise(resolve => setImmediate(resolve));
const item = title => ({
  pk: '12345678-1234-1234-1234-123456789abc',
  fields: { title, description: 'Description', category_display: 'Research',
    star_count: 2, is_starred: true, is_ongoing: true },
});

function setup(t) {
  const errors = [];
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('error', (...args) => errors.push(args));
  virtualConsole.on('jsdomError', error => errors.push(error));
  const dom = new JSDOM(`<!doctype html>
    <form id="experience-search-form"><input id="experience-search-input" type="search"></form>
    <div id="experience-loading"></div><div id="experience-empty" class="hide"></div>
    <div id="experience-error" class="hide"></div>
    <div id="experience-list" class="hide" data-endpoint="/api/experiences/"
         data-can-edit="false" data-can-delete="false"></div>`, {
    url: 'https://portfolio.example/experience/', runScripts: 'outside-only', virtualConsole,
  });
  t.after(() => dom.window.close());
  const { window } = dom;
  const document = window.document;
  const timers = new Map();
  const requests = [];
  let timerId = 0;
  window.setTimeout = (callback, delay) => {
    timers.set(++timerId, { callback, delay });
    return timerId;
  };
  window.clearTimeout = id => timers.delete(id);
  window.fetch = (url, options) => new Promise((resolve, reject) => {
    // Deliberately ignore aborts to verify the request-version fallback too.
    requests.push({ url, signal: options.signal, resolve, reject });
  });
  window.eval(source);
  return {
    document, requests, errors, timers,
    input(value) {
      document.querySelector('input').value = value;
      document.querySelector('input').dispatchEvent(new window.Event('input'));
    },
    tick() {
      assert.equal(timers.size, 1);
      const [{ callback, delay }] = timers.values();
      assert.equal(delay, 300);
      timers.clear();
      callback();
    },
    submit() {
      const event = new window.Event('submit', { cancelable: true });
      document.querySelector('form').dispatchEvent(event);
      assert(event.defaultPrevented);
    },
  };
}

async function respond(request, items) {
  request.resolve({ ok: true, json: async () => items });
  await flush();
}

function visible(page, id) {
  return !page.document.getElementById(id).classList.contains('hide');
}

test('rapid keystrokes produce one request after 300 ms and clearing restores the full-list URL', async t => {
  const page = setup(t);
  await respond(page.requests[0], [item('All experiences')]);
  for (const value of ['r', 're', 'research & AI']) page.input(value);
  assert.equal(page.requests.length, 1);
  assert(visible(page, 'experience-loading'));
  page.tick();
  assert.equal(page.requests.length, 2);
  assert.equal(new URL(page.requests[1].url).searchParams.get('q'), 'research & AI');
  await respond(page.requests[1], [item('Matching experience')]);
  assert(visible(page, 'experience-list'));
  assert.equal(page.document.querySelector('.star-count').textContent, '2');
  assert(page.document.querySelector('.is-starred'));
  page.input('   ');
  page.tick();
  assert.equal(page.requests[2].url, '/api/experiences/');
  await respond(page.requests[2], [item('All experiences')]);
  assert.equal(page.document.querySelector('.experience-title').textContent, 'All experiences');
  assert.deepEqual(page.errors, []);
});

test('submit searches immediately without navigation or a duplicate debounce request', async t => {
  const page = setup(t);
  page.input('intern');
  page.submit();
  assert.equal(page.requests.length, 2);
  assert.equal(page.timers.size, 0);
  assert.equal(page.requests[0].signal.aborted, true);
  await respond(page.requests[1], [item('Intern')]);
  assert.equal(page.document.querySelector('.experience-title').textContent, 'Intern');
});

test('older JSON parsing cannot overwrite newer search results', async t => {
  const page = setup(t);
  let finishOldJson;
  page.requests[0].resolve({ ok: true, json: () => new Promise(resolve => { finishOldJson = resolve; }) });
  await flush();
  page.input('new');
  page.tick();
  await respond(page.requests[1], [item('New result')]);
  finishOldJson([item('Old result')]);
  await flush();
  assert.equal(page.document.querySelector('.experience-title').textContent, 'New result');
  assert.deepEqual(page.errors, []);
});

test('typing invalidates older responses even during the debounce delay', async t => {
  const page = setup(t);
  page.input('new');
  assert.equal(page.requests[0].signal.aborted, true);
  await respond(page.requests[0], [item('Old result')]);
  assert.equal(page.document.querySelector('article'), null);
  assert(visible(page, 'experience-loading'));
  page.tick();
  await respond(page.requests[1], [item('New result')]);
  assert(visible(page, 'experience-list'));
});

test('stale failures stay ignored and current network/server failures show the error state', async t => {
  const page = setup(t);
  page.input('new');
  page.tick();
  await respond(page.requests[1], [item('New result')]);
  page.requests[0].reject(new Error('Old network failure'));
  await flush();
  assert(visible(page, 'experience-list'));
  assert.deepEqual(page.errors, []);
  page.input('network');
  page.tick();
  page.requests[2].reject(new Error('Network failure'));
  await flush();
  assert(visible(page, 'experience-error'));
  page.input('server');
  page.tick();
  page.requests[3].resolve({ ok: false, status: 500 });
  await flush();
  assert(visible(page, 'experience-error'));
  assert.equal(page.errors.length, 2);
});

test('empty results use safe fixed text and later results reuse the XSS-safe renderer', async t => {
  const page = setup(t);
  page.input('<img src=x onerror=alert(1)>');
  page.tick();
  await respond(page.requests[1], []);
  assert(visible(page, 'experience-empty'));
  assert.equal(page.document.querySelector('img'), null);
  page.input('payload');
  page.tick();
  const payload = `<img src="x" onerror="alert('XSS!')">`;
  await respond(page.requests[2], [item(payload)]);
  assert.equal(page.document.querySelector('.experience-title').textContent, payload);
  assert.equal(page.document.querySelectorAll('img, [onerror]').length, 0);
  assert(visible(page, 'experience-list'));
  assert.deepEqual(page.errors, []);
});
