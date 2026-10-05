(() => {
  const list = document.getElementById('experience-list');
  const states = {
    loading: document.getElementById('experience-loading'),
    empty: document.getElementById('experience-empty'),
    error: document.getElementById('experience-error'),
    loaded: list,
  };
  const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  const placeholderId = '00000000-0000-0000-0000-000000000000';
  const searchForm = document.getElementById('experience-search-form');
  const searchInput = document.getElementById('experience-search-input');
  const SEARCH_DEBOUNCE_DELAY = 300;
  let searchTimer;
  let requestVersion = 0;
  let requestController;

  function invalidateRequest() {
    requestVersion += 1;
    if (requestController) requestController.abort();
  }

  // Do not HTML-escape these values: DOM text/property setters preserve literal
  // characters without parsing markup. Never pass API values to an HTML sink.
  function textValue(value) {
    return String(value ?? '');
  }

  // Central path for JSON text, including titles, descriptions and categories.
  function element(tag, className, value) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = textValue(value);
    return node;
  }

  function showState(state) {
    Object.entries(states).forEach(([name, node]) => {
      node.classList.toggle('hide', name !== state);
    });
  }

  function itemUrl(template, id) {
    if (typeof id !== 'string' || !uuidPattern.test(id)) throw new Error('Invalid experience ID');
    return template.replace(placeholderId, id);
  }

  function safeImageUrl(value) {
    if (typeof value !== 'string' || !value) return null;
    try {
      // Experience.thumbnail is a URLField: accept absolute HTTP(S) URLs only.
      const url = new URL(value);
      return ['http:', 'https:'].includes(url.protocol) ? url.href : null;
    } catch (_) {
      return null;
    }
  }

  function addDeleteControl(actions, id, title) {
    const modalId = `delete-experience-${id}`;
    const headingId = `delete-experience-title-${id}`;
    const trigger = element('div', 'project-delete-trigger');
    const open = element('button', 'button button-danger', 'Hapus Pengalaman');
    open.type = 'button';
    open.setAttribute('popovertarget', modalId);
    open.setAttribute('aria-label', `Hapus ${title}`);
    open.title = 'Hapus pengalaman';
    trigger.append(open);

    const modal = element('div', 'project-delete-modal');
    modal.id = modalId;
    modal.setAttribute('popover', 'auto');
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-labelledby', headingId);
    const backdrop = element('button', 'project-delete-modal__backdrop');
    backdrop.type = 'button';
    backdrop.setAttribute('popovertarget', modalId);
    backdrop.setAttribute('popovertargetaction', 'hide');
    backdrop.setAttribute('aria-label', 'Tutup konfirmasi hapus');

    const content = element('div', 'project-delete-modal__content');
    const close = element('button', 'project-delete-modal__close', '×');
    close.type = 'button';
    close.setAttribute('popovertarget', modalId);
    close.setAttribute('popovertargetaction', 'hide');
    close.setAttribute('aria-label', 'Tutup konfirmasi hapus');
    const heading = element('h2', '', 'Hapus Pengalaman?');
    heading.id = headingId;
    const message = element('p', 'project-delete-modal__message', 'Apakah Anda yakin ingin menghapus ');
    message.append(element('strong', '', title), document.createTextNode('?'));
    const controls = element('div', 'project-delete-modal__actions');
    const cancel = element('button', 'button button-secondary', 'Batal');
    cancel.type = 'button';
    cancel.setAttribute('popovertarget', modalId);
    cancel.setAttribute('popovertargetaction', 'hide');
    const form = element('form');
    form.method = 'post';
    form.action = itemUrl(list.dataset.deleteUrl, id);
    const csrf = element('input');
    csrf.type = 'hidden';
    csrf.name = 'csrfmiddlewaretoken';
    csrf.value = list.dataset.csrfToken;
    const submit = element('button', 'button button-danger', 'Ya, Hapus');
    submit.type = 'submit';
    form.append(csrf, submit);
    controls.append(cancel, form);
    content.append(close, heading, message, controls);
    modal.append(backdrop, content);
    actions.append(trigger, modal);
  }

  function buildExperience(item) {
    if (!item || !item.fields || typeof item.fields !== 'object' || Array.isArray(item.fields)) {
      throw new Error('Invalid experience data');
    }
    const id = item.pk;
    if (typeof id !== 'string' || !uuidPattern.test(id)) throw new Error('Invalid experience ID');
    const data = item.fields;
    // Only validated primitives select classes/labels or supply numeric text.
    const isStarred = data.is_starred === true;
    const isOngoing = data.is_ongoing === true;
    const starCount = Number.isSafeInteger(data.star_count) && data.star_count >= 0
      ? data.star_count : 0;
    const article = element('article', 'experience-item timeline-item');
    const content = element('div', 'experience-content');
    content.append(
      element('span', 'experience-category', data.category_display),
      element('h3', 'experience-title', data.title),
      element('p', 'experience-description', data.description),
      element('p', 'experience-status', isOngoing ? 'Sedang berlangsung' : 'Selesai'),
    );

    const star = element('span', `button button-star experience-star${isStarred ? ' is-starred' : ''}`);
    star.setAttribute('aria-label', `${isStarred ? 'Sudah diberi star' : 'Belum diberi star'}, ${starCount} star`);
    star.append(
      element('span', '', '★'),
      document.createTextNode(isStarred ? ' Starred ' : ' Unstarred '),
      element('span', 'star-count', starCount),
    );
    star.firstChild.setAttribute('aria-hidden', 'true');
    content.append(star);

    if (list.dataset.canEdit === 'true' || list.dataset.canDelete === 'true') {
      const actions = element('div', 'experience-actions');
      if (list.dataset.canEdit === 'true') {
        const edit = element('a', 'button button-secondary', 'Edit Pengalaman');
        edit.href = itemUrl(list.dataset.editUrl, id);
        actions.append(edit);
      }
      if (list.dataset.canDelete === 'true') addDeleteControl(actions, id, textValue(data.title));
      content.append(actions);
    }

    const thumb = element('div', 'experience-thumb');
    const imageUrl = safeImageUrl(data.thumbnail);
    const frame = element('div', `photo-frame-polaroid${imageUrl ? '' : ' experience-thumb-placeholder'}`);
    if (imageUrl) {
      const image = element('img');
      image.src = imageUrl;
      image.alt = textValue(data.title);
      frame.append(image);
    } else {
      frame.append(element('span', '', textValue(data.category_display).slice(0, 11)));
    }
    thumb.append(frame);
    article.append(content, thumb);
    return article;
  }

  async function loadExperiences(query = '') {
    invalidateRequest();
    const version = requestVersion;
    requestController = new AbortController();
    showState('loading');
    try {
      let endpoint = list.dataset.endpoint;
      if (query) {
        const url = new URL(endpoint, window.location.href);
        url.searchParams.set('q', query);
        endpoint = url.href;
      }
      const response = await fetch(endpoint, {
        headers: { Accept: 'application/json' }, signal: requestController.signal,
      });
      if (version !== requestVersion) return;
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const items = await response.json();
      if (version !== requestVersion) return;
      if (!Array.isArray(items)) throw new Error('Invalid experience response');
      if (items.length === 0) {
        states.empty.textContent = query
          ? 'Tidak ada pengalaman yang cocok dengan pencarian.'
          : 'Belum ada pengalaman yang ditambahkan.';
        list.replaceChildren();
        showState('empty');
        return;
      }
      const fragment = document.createDocumentFragment();
      items.forEach(item => fragment.append(buildExperience(item)));
      list.replaceChildren(fragment);
      showState('loaded');
    } catch (error) {
      if (version !== requestVersion || error.name === 'AbortError') return;
      console.error('Error loading experiences:', error);
      list.replaceChildren();
      showState('error');
    }
  }

  searchInput.addEventListener('input', () => {
    clearTimeout(searchTimer);
    // Invalidate immediately, including while the next query is debouncing.
    invalidateRequest();
    showState('loading');
    searchTimer = setTimeout(() => loadExperiences(searchInput.value.trim()), SEARCH_DEBOUNCE_DELAY);
  });

  searchForm.addEventListener('submit', event => {
    event.preventDefault();
    clearTimeout(searchTimer);
    loadExperiences(searchInput.value.trim());
  });

  loadExperiences(searchInput.value.trim());
})();
