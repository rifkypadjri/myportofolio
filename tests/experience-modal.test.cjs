const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const { JSDOM, VirtualConsole } = require(process.argv[2] || 'jsdom');
const source = fs.readFileSync(path.join(__dirname, '../static/js/experience.js'), 'utf8');
const toastSource = fs.readFileSync(path.join(__dirname, '../static/js/toast.js'), 'utf8');
const flush = () => new Promise(resolve => setImmediate(resolve));

async function setup(t, privileged = true) {
  const errors = [];
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('error', (...args) => errors.push(args));
  virtualConsole.on('jsdomError', error => errors.push(error));
  const dom = new JSDOM(`<!doctype html>
    <form id="experience-search-form"><input id="experience-search-input" type="search" value="research"></form>
    <div id="experience-loading"></div><div id="experience-empty" class="hide"></div>
    <div id="experience-error" class="hide"></div>
    <div id="experience-list" class="hide" data-endpoint="/api/experiences/"
         data-can-edit="false" data-can-delete="false"></div>
    ${privileged ? `<div id="add-experience-modal" popover="auto">
      <form id="experience-add-form" action="/experiences/add-ajax/" method="post">
        <input name="csrfmiddlewaretoken" type="hidden" value="csrf-test-token">
        <div id="experience-form-error" role="alert" tabindex="-1" hidden></div>
        <input name="title" value="New research">
        <div id="title-errors" data-field-error="title" hidden></div>
        <textarea name="description">Research work</textarea>
        <div id="description-errors" data-field-error="description" hidden></div>
        <select name="category"><option value="research">Research</option></select>
        <input name="thumbnail"><input name="ended_at">
        <button type="submit">Tambah Pengalaman</button>
      </form></div>` : ''}
    <div id="toast-component" class="toast-hidden">
      <h3 id="toast-title"></h3><p id="toast-message"></p>
    </div>`, {
    url: 'https://portfolio.example/experience/', runScripts: 'outside-only', virtualConsole,
  });
  t.after(() => dom.window.close());
  const { window } = dom;
  const document = window.document;
  const requests = [];
  const toast = document.getElementById('toast-component');
  let toastOpen = false;
  const originalMatches = toast.matches.bind(toast);
  toast.matches = selector => selector === ':popover-open' ? toastOpen : originalMatches(selector);
  toast.showPopover = () => { toastOpen = true; };
  toast.hidePopover = () => { toastOpen = false; };
  window.eval(toastSource);
  let closed = 0;
  const modal = document.getElementById('add-experience-modal');
  if (modal) {
    // jsdom lacks native popover opening; simulate an already-open dialog.
    modal.removeAttribute('popover');
    modal.hidePopover = () => { closed += 1; };
  }
  window.fetch = (url, options) => new Promise((resolve, reject) => requests.push({ url, options, resolve, reject }));
  window.eval(source);
  requests[0].resolve({ ok: true, json: async () => [] });
  await flush();
  return {
    document, window, errors, requests,
    closed: () => closed,
    form: document.getElementById('experience-add-form'),
    submit() {
      const event = new window.Event('submit', { cancelable: true });
      document.getElementById('experience-add-form').dispatchEvent(event);
      assert.equal(event.defaultPrevented, true);
    },
  };
}

async function respond(request, status, data) {
  request.resolve({ status, ok: status >= 200 && status < 300, json: async () => data });
  await flush();
}

test('anonymous page runs normally with no modal or modal event listeners', async t => {
  const page = await setup(t, false);
  assert.deepEqual(page.errors, []);
  assert.equal(page.requests.length, 1);
  assert.equal(page.form, null);
  assert.equal(page.document.getElementById('toast-title').textContent, '');
});

test('POST sends FormData and CSRF, then resets/closes/refetches with the latest query', async t => {
  const page = await setup(t);
  page.form.elements.namedItem('title').value = 'Edited title';
  page.submit();
  const post = page.requests[1];
  assert.equal(post.url, 'https://portfolio.example/experiences/add-ajax/');
  assert.equal(post.options.method, 'POST');
  assert.equal(post.options.body.get('csrfmiddlewaretoken'), 'csrf-test-token');
  assert.equal(post.options.body.get('title'), 'Edited title');
  assert.equal(post.options.body.get('category'), 'research');
  assert.equal(page.form.querySelector('button').disabled, true);
  page.document.getElementById('experience-search-input').value = 'new search';
  await respond(post, 201, { success: true, pk: 'created-id' });
  assert.equal(page.closed(), 1);
  assert.equal(page.document.getElementById('toast-title').textContent, 'Berhasil');
  assert(page.document.getElementById('toast-component').classList.contains('toast-success'));
  assert.equal(page.form.elements.namedItem('title').value, 'New research');
  assert.equal(page.form.querySelector('button').disabled, false);
  assert.equal(new URL(page.requests[2].url).searchParams.get('q'), 'new search');
  await respond(page.requests[2], 200, []);
  assert.deepEqual(page.errors, []);
  assert.equal(page.window.location.pathname, '/experience/');
});

test('400 shows field and non-field validation as inert text while retaining entered data', async t => {
  const page = await setup(t);
  const payload = `<img src="x" onerror="alert('XSS!')">`;
  page.form.elements.namedItem('title').value = 'Keep this';
  page.submit();
  await respond(page.requests[1], 400, { success: false, errors: {
    title: [{ message: payload, code: 'required' }],
    __all__: [{ message: 'Other validation error', code: 'invalid' }],
  } });
  assert.equal(page.document.getElementById('title-errors').textContent, payload);
  assert.equal(page.document.getElementById('title-errors').hidden, false);
  assert.equal(page.form.elements.namedItem('title').getAttribute('aria-invalid'), 'true');
  assert.equal(page.document.activeElement, page.form.elements.namedItem('title'));
  assert(page.document.getElementById('experience-form-error').textContent.includes('Other validation error'));
  assert.equal(page.document.querySelectorAll('img, [onerror]').length, 0);
  assert.equal(page.form.elements.namedItem('title').value, 'Keep this');
  assert.equal(page.closed(), 0);
  assert.equal(page.requests.length, 2);
  assert.deepEqual(page.errors, []);
  assert.equal(page.document.getElementById('toast-title').textContent, 'Data belum valid');
  assert(page.document.getElementById('toast-component').classList.contains('toast-error'));
});

test('403 JSON and HTML CSRF failures show permission/session errors without closing', async t => {
  const page = await setup(t);
  const payload = '<img src=x onerror=alert(1)>';
  page.submit();
  await respond(page.requests[1], 403, { message: payload });
  assert.equal(page.document.getElementById('experience-form-error').textContent, payload);
  assert.equal(page.document.getElementById('toast-message').textContent, payload);
  assert.equal(page.document.getElementById('toast-title').textContent, 'Akses ditolak');
  assert.equal(page.document.querySelector('img'), null);
  page.submit();
  page.requests[2].resolve({ status: 403, json: async () => { throw new SyntaxError('HTML response'); } });
  await flush();
  assert(page.document.getElementById('experience-form-error').textContent.includes('izin'));
  assert.equal(page.closed(), 0);
  assert.equal(page.form.querySelector('button').disabled, false);
  assert.deepEqual(page.errors, []);
});

test('server/network failures preserve inputs and permit retry', async t => {
  const page = await setup(t);
  page.form.elements.namedItem('title').value = 'Retain title';
  page.submit();
  await respond(page.requests[1], 500, {});
  assert(page.document.getElementById('experience-form-error').textContent.includes('Server'));
  assert.equal(page.document.getElementById('toast-title').textContent, 'Gagal menambahkan pengalaman');
  page.submit();
  page.requests[2].reject(new Error('Network unavailable'));
  await flush();
  assert(page.document.getElementById('experience-form-error').textContent.includes('koneksi'));
  assert.equal(page.document.getElementById('toast-title').textContent, 'Gangguan koneksi');
  assert(page.document.getElementById('toast-component').classList.contains('toast-error'));
  assert.equal(page.form.elements.namedItem('title').value, 'Retain title');
  assert.equal(page.closed(), 0);
  assert.equal(page.form.querySelector('button').disabled, false);
  assert.equal(page.errors.length, 1);
});

test('duplicate submissions are ignored and validation clears on retry', async t => {
  const page = await setup(t);
  page.submit();
  page.submit();
  assert.equal(page.requests.length, 2);
  await respond(page.requests[1], 400, { errors: { title: [{ message: 'Required' }] } });
  page.submit();
  assert.equal(page.document.getElementById('title-errors').hidden, true);
  assert.equal(page.form.elements.namedItem('title').hasAttribute('aria-invalid'), false);
  assert.equal(page.form.getAttribute('aria-busy'), 'true');
  await respond(page.requests[2], 201, {});
  assert.equal(page.form.hasAttribute('aria-busy'), false);
  assert.equal(page.closed(), 1);
});

test('a failed list refresh after creation uses the list error state', async t => {
  const page = await setup(t);
  page.submit();
  await respond(page.requests[1], 201, {});
  await respond(page.requests[2], 500, {});
  assert.equal(page.closed(), 1);
  assert.equal(page.document.getElementById('experience-error').classList.contains('hide'), false);
  assert.equal(page.document.getElementById('experience-form-error').hidden, true);
  assert.equal(page.document.getElementById('toast-title').textContent, 'Gagal memuat pengalaman');
  assert.equal(page.errors.length, 1);
});

test('anonymous network failures show the shared toast without modal errors', async t => {
  const page = await setup(t, false);
  page.document.getElementById('experience-search-form').dispatchEvent(
    new page.window.Event('submit', { cancelable: true })
  );
  page.requests[1].reject(new Error('Network unavailable'));
  await flush();
  assert.equal(page.form, null);
  assert.equal(page.errors.length, 1);
  assert.equal(page.document.getElementById('toast-title').textContent, 'Gagal memuat pengalaman');
  assert(page.document.getElementById('toast-component').classList.contains('toast-error'));
});
