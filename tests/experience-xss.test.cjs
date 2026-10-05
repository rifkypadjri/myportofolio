const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
// Optional absolute package path allows dependencies to stay outside the repo.
const { JSDOM, VirtualConsole } = require(process.argv[2] || 'jsdom');
const source = fs.readFileSync(path.join(__dirname, '../static/js/experience.js'), 'utf8');
const payload = `<img src="x" onerror="alert('XSS!')">`;
const id = '12345678-1234-1234-1234-123456789abc';
const defaultFields = {
  title: 'Research & Development', description: `A < B, "quotes", O'Brien & café`,
  category_display: 'Research', thumbnail: null,
  star_count: 3, is_starred: true, is_ongoing: true,
};

async function render(fields = {}, pk = id) {
  const virtualConsole = new VirtualConsole();
  const errors = [];
  virtualConsole.on('jsdomError', error => errors.push(error));
  virtualConsole.on('error', (...args) => errors.push(args));
  const dom = new JSDOM(`<!doctype html>
    <div id="experience-loading"></div>
    <div id="experience-empty" class="hide"></div>
    <div id="experience-error" class="hide"></div>
    <div id="experience-list" class="hide"
      data-endpoint="/api/experiences/"
      data-edit-url="/experiences/00000000-0000-0000-0000-000000000000/edit/"
      data-delete-url="/experiences/00000000-0000-0000-0000-000000000000/delete/"
      data-can-edit="true" data-can-delete="true" data-csrf-token="test-token"></div>`, {
    url: 'https://portfolio.example/experience/', runScripts: 'dangerously', virtualConsole,
  });
  const { window } = dom;
  const alerts = [];
  window.alert = value => alerts.push(value);
  // Prohibit parsing sinks: production JSON must only go through DOM setters.
  for (const name of ['innerHTML', 'outerHTML']) {
    const descriptor = Object.getOwnPropertyDescriptor(window.Element.prototype, name);
    Object.defineProperty(window.Element.prototype, name, {
      ...descriptor, set() { throw new Error(`Forbidden HTML sink: ${name}`); },
    });
  }
  window.Element.prototype.insertAdjacentHTML = () => { throw new Error('Forbidden HTML sink'); };
  window.document.write = window.document.writeln = () => { throw new Error('Forbidden HTML sink'); };
  window.fetch = async endpoint => {
    assert.equal(endpoint, '/api/experiences/');
    return { ok: true, json: async () => [{ pk, fields: { ...defaultFields, ...fields } }] };
  };
  window.eval(source);
  await new Promise(resolve => setImmediate(resolve));
  // Failed images can trigger injected event handlers in a real page.
  window.document.querySelectorAll('img').forEach(image => image.dispatchEvent(new window.Event('error')));
  assert.deepEqual(alerts, []);
  assert.equal(window.document.querySelectorAll('script, [onerror], [onload], [onclick]').length, 0);
  return { dom, document: window.document, errors };
}

test('test environment detects execution of the supplied payload in an unsafe HTML sink', () => {
  const dom = new JSDOM('<!doctype html><body></body>', { runScripts: 'dangerously' });
  const alerts = [];
  dom.window.alert = value => alerts.push(value);
  dom.window.document.body.innerHTML = payload;
  dom.window.document.querySelector('img').dispatchEvent(new dom.window.Event('error'));
  assert.deepEqual(alerts, ['XSS!']);
  dom.window.close();
});

test('malicious title, description and category stay literal in cards and delete confirmation', async () => {
  const result = await render({ title: payload, description: payload, category_display: payload });
  assert.deepEqual(result.errors, []);
  assert.equal(result.document.querySelector('.experience-title').textContent, payload);
  assert.equal(result.document.querySelector('.experience-description').textContent, payload);
  assert.equal(result.document.querySelector('.experience-category').textContent, payload);
  assert.equal(result.document.querySelector('.experience-thumb-placeholder span').textContent, payload.slice(0, 11));
  assert.equal(result.document.querySelector('.project-delete-modal strong').textContent, payload);
  assert.equal(result.document.querySelector('[popovertarget]').getAttribute('aria-label'), `Hapus ${payload}`);
  assert.equal(result.document.querySelectorAll('img').length, 0);
  result.dom.window.close();
});

test('image alt text and URLs cannot introduce an event-handler attribute', async () => {
  const thumbnail = `https://example.com/image.png?caption=" onerror="alert('XSS!')`;
  const result = await render({ title: payload, thumbnail });
  assert.deepEqual(result.errors, []);
  const image = result.document.querySelector('img');
  assert.equal(image.alt, payload);
  assert.equal(image.src, new URL(thumbnail).href);
  assert.equal(image.hasAttribute('onerror'), false);
  result.dom.window.close();
});

test('unsafe thumbnail protocols and HTML use the existing placeholder', async () => {
  for (const thumbnail of [payload, "javascript:alert('XSS!')", 'data:image/svg+xml,<svg onload=alert(1)>', 'vbscript:msgbox(1)']) {
    const result = await render({ thumbnail });
    assert.deepEqual(result.errors, []);
    assert.equal(result.document.querySelector('img'), null);
    assert(result.document.querySelector('.experience-thumb-placeholder'));
    result.dom.window.close();
  }
});

test('valid display text and HTTP URLs retain punctuation, accents and query strings', async () => {
  const thumbnail = 'https://example.com/photo.png?width=200&height=130';
  const result = await render({ thumbnail });
  assert.deepEqual(result.errors, []);
  assert.equal(result.document.querySelector('.experience-title').textContent, defaultFields.title);
  assert.equal(result.document.querySelector('.experience-description').textContent, defaultFields.description);
  assert.equal(result.document.querySelector('img').getAttribute('src'), thumbnail);
  assert.equal(result.document.querySelector('.star-count').textContent, '3');
  assert(result.document.querySelector('.experience-star.is-starred'));
  assert.equal(result.document.querySelector('form').getAttribute('action'), `/experiences/${id}/delete/`);
  result.dom.window.close();
});

test('malicious count and boolean values cannot supply markup or dynamic classes', async () => {
  const result = await render({ star_count: payload, is_starred: payload, is_ongoing: payload });
  assert.deepEqual(result.errors, []);
  assert.equal(result.document.querySelector('.star-count').textContent, '0');
  assert.equal(result.document.querySelector('.experience-star').getAttribute('aria-label'), 'Belum diberi star, 0 star');
  assert.equal(result.document.querySelector('.experience-star.is-starred'), null);
  assert.equal(result.document.querySelector('.experience-status').textContent, 'Selesai');
  result.dom.window.close();
});

test('invalid IDs show the error state without creating links or modal IDs', async () => {
  for (const invalidId of [payload, `${id}/../delete`, 123]) {
    const result = await render({}, invalidId);
    assert.equal(result.errors.length, 1);
    assert.equal(result.document.querySelector('#experience-error').classList.contains('hide'), false);
    assert.equal(result.document.querySelectorAll('article, a, form').length, 0);
    result.dom.window.close();
  }
});
