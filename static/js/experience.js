(() => {
  const listContainer = document.getElementById('experience-list');
  const states = {
    loading: document.getElementById('experience-loading'),
    empty: document.getElementById('experience-empty'),
    error: document.getElementById('experience-error'),
    loaded: listContainer,
  };
  const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  const placeholderId = '00000000-0000-0000-0000-000000000000';
  const searchForm = document.getElementById('experience-search-form');
  const searchInput = document.getElementById('experience-search-input');
  const clearSearchButton = document.getElementById('experience-clear-search');
  const resultCount = document.getElementById('experience-result-count');
  const SEARCH_DEBOUNCE_DELAY = 300;
  let requestVersion = 0;
  let requestController;

  function notifyExperience(title, message, type) {
    // base.html loads Tutorial 05's shared toast; no separate toast UI is needed.
    if (typeof window.showToast === 'function') window.showToast(title, message, type);
  }

  function invalidateRequest() {
    requestVersion += 1;
    if (requestController) requestController.abort();
  }

  function debounce(callback, delay) {
    let timer;
    const debounced = (...args) => {
      debounced.cancel();
      timer = setTimeout(() => callback(...args), delay);
    };
    debounced.cancel = () => clearTimeout(timer);
    return debounced;
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

  function renderLoadingState() {
    if (resultCount) resultCount.hidden = true;
    showState('loading');
  }

  function renderResultCount(count, query) {
    if (!resultCount) return;
    resultCount.textContent = `${count} pengalaman${query ? ' ditemukan' : ''}.`;
    resultCount.hidden = false;
  }

  function renderEmptyState(query) {
    states.empty.textContent = query
      ? 'Tidak ada pengalaman yang cocok dengan pencarian.'
      : 'Belum ada pengalaman yang ditambahkan.';
    listContainer.replaceChildren();
    renderResultCount(0, query);
    showState('empty');
  }

  function renderErrorState() {
    if (resultCount) resultCount.hidden = true;
    listContainer.replaceChildren();
    showState('error');
    notifyExperience('Gagal memuat pengalaman', 'Data pengalaman tidak dapat dimuat. Silakan coba lagi.', 'error');
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
    form.action = itemUrl(listContainer.dataset.deleteUrl, id);
    const csrf = element('input');
    csrf.type = 'hidden';
    csrf.name = 'csrfmiddlewaretoken';
    csrf.value = listContainer.dataset.csrfToken;
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

    content.append(buildExperienceStar(isStarred, starCount));
    if (listContainer.dataset.canEdit === 'true' || listContainer.dataset.canDelete === 'true') {
      content.append(buildExperienceActions(id, data.title));
    }
    article.append(content, buildExperienceThumbnail(data));
    return article;
  }

  function buildExperienceStar(isStarred, starCount) {
    const star = element('span', `button button-star experience-star${isStarred ? ' is-starred' : ''}`);
    star.setAttribute('aria-label', `${isStarred ? 'Sudah diberi star' : 'Belum diberi star'}, ${starCount} star`);
    star.append(
      element('span', '', '★'),
      document.createTextNode(isStarred ? ' Starred ' : ' Unstarred '),
      element('span', 'star-count', starCount),
    );
    star.firstChild.setAttribute('aria-hidden', 'true');
    return star;
  }

  function buildExperienceActions(id, title) {
    const actions = element('div', 'experience-actions');
    if (listContainer.dataset.canEdit === 'true') {
      const edit = element('a', 'button button-secondary', 'Edit Pengalaman');
      edit.href = itemUrl(listContainer.dataset.editUrl, id);
      actions.append(edit);
    }
    if (listContainer.dataset.canDelete === 'true') addDeleteControl(actions, id, textValue(title));
    return actions;
  }

  function buildExperienceThumbnail(data) {
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
    return thumb;
  }

  function renderExperienceItems(items, query) {
    if (items.length === 0) {
      renderEmptyState(query);
      return;
    }
    const fragment = document.createDocumentFragment();
    items.forEach(item => fragment.append(buildExperience(item)));
    listContainer.replaceChildren(fragment);
    renderResultCount(items.length, query);
    showState('loaded');
  }

  async function fetchExperienceData(query, signal) {
    let endpoint = listContainer.dataset.endpoint;
    if (query) {
      const url = new URL(endpoint, window.location.href);
      url.searchParams.set('q', query);
      endpoint = url.href;
    }
    const response = await fetch(endpoint, {
      headers: { Accept: 'application/json' }, signal,
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const items = await response.json();
    if (!Array.isArray(items)) throw new Error('Invalid experience response');
    return items;
  }

  async function loadExperienceList(query = '') {
    invalidateRequest();
    const version = requestVersion;
    requestController = new AbortController();
    renderLoadingState();
    try {
      const items = await fetchExperienceData(query, requestController.signal);
      // Cancellation may be ignored; stale responses must never update the UI.
      if (version !== requestVersion) return;
      renderExperienceItems(items, query);
    } catch (error) {
      if (version !== requestVersion || error.name === 'AbortError') return;
      console.error('Error loading experiences:', error);
      renderErrorState();
    }
  }

  const debouncedSearch = debounce(() => loadExperienceList(searchInput.value.trim()), SEARCH_DEBOUNCE_DELAY);

  function refreshExperienceList() {
    debouncedSearch.cancel();
    loadExperienceList(searchInput.value.trim());
  }

  function initializeExperienceSearch() {
    function updateClearSearchButton() {
      if (clearSearchButton) clearSearchButton.disabled = searchInput.value.length === 0;
    }

    updateClearSearchButton();
    searchInput.addEventListener('input', () => {
      updateClearSearchButton();
      // Invalidate immediately, including while the next query is debouncing.
      invalidateRequest();
      renderLoadingState();
      debouncedSearch();
    });
    searchForm.addEventListener('submit', event => {
      event.preventDefault();
      refreshExperienceList();
    });
    if (clearSearchButton) {
      clearSearchButton.addEventListener('click', () => {
        searchInput.value = '';
        updateClearSearchButton();
        searchInput.focus();
        refreshExperienceList();
      });
    }
  }

  async function postExperienceForm(form) {
    const response = await fetch(form.action, {
      method: 'POST',
      headers: { Accept: 'application/json' },
      // Includes the hidden csrfmiddlewaretoken rendered by Django.
      body: new FormData(form),
    });
    const result = await response.json().catch(() => ({})) || {};
    return { status: response.status, result };
  }

  function initializeExperienceForm() {
    const addModal = document.getElementById('add-experience-modal');
    const addForm = document.getElementById('experience-add-form');
    // These elements are intentionally absent for guests and non-creator roles.
    if (!addModal || !addForm) return;
    const formError = document.getElementById('experience-form-error');
    const submitButton = addForm.querySelector('button[type="submit"]');
    const submitLabel = submitButton.textContent;
    const fieldErrors = new Map();
    let isSubmitting = false;

    addForm.querySelectorAll('[data-field-error]').forEach(container => {
      const name = container.dataset.fieldError;
      fieldErrors.set(name, container);
      const control = addForm.elements.namedItem(name);
      if (control) control.setAttribute('aria-describedby', container.id);
    });

    function clearFormErrors() {
      formError.replaceChildren();
      formError.hidden = true;
      fieldErrors.forEach((container, name) => {
        container.replaceChildren();
        container.hidden = true;
        const control = addForm.elements.namedItem(name);
        if (control) control.removeAttribute('aria-invalid');
      });
    }

    function showFormError(message) {
      formError.textContent = textValue(message);
      formError.hidden = false;
      formError.focus();
    }

    function displayValidationErrors(errors) {
      showFormError('Periksa dan perbaiki data yang ditandai di bawah ini.');
      let firstInvalid;
      Object.entries(errors || {}).forEach(([name, messages]) => {
        const container = fieldErrors.get(name) || formError;
        const entries = Array.isArray(messages) ? messages : [messages];
        entries.forEach(error => container.append(element('p', '', error?.message ?? error)));
        container.hidden = false;
        const control = addForm.elements.namedItem(name);
        if (control) {
          control.setAttribute('aria-invalid', 'true');
          if (!firstInvalid) firstInvalid = control;
        }
      });
      if (firstInvalid) firstInvalid.focus();
    }

    function setFormSubmitting(submitting) {
      isSubmitting = submitting;
      submitButton.disabled = submitting;
      submitButton.textContent = submitting ? 'Menyimpan...' : submitLabel;
      if (submitting) addForm.setAttribute('aria-busy', 'true');
      else addForm.removeAttribute('aria-busy');
    }

    function showFormFailure(title, message) {
      showFormError(message);
      notifyExperience(title, message, 'error');
    }

    function handleCreateResponse(status, result) {
      if (status === 201) {
        addForm.reset();
        clearFormErrors();
        addModal.hidePopover();
        refreshExperienceList();
        notifyExperience('Berhasil', 'Pengalaman berhasil ditambahkan.', 'success');
      } else if (status === 400) {
        displayValidationErrors(result.errors);
        notifyExperience('Data belum valid', 'Periksa dan perbaiki kolom yang ditandai pada form.', 'error');
      } else if (status === 403) {
        const message = result.message || 'Anda tidak memiliki izin atau sesi telah kedaluwarsa. Silakan muat ulang halaman.';
        showFormFailure('Akses ditolak', message);
      } else {
        const message = 'Server gagal menyimpan pengalaman. Silakan coba lagi.';
        showFormFailure('Gagal menambahkan pengalaman', message);
      }
    }

    async function submitExperienceForm(event) {
      event.preventDefault();
      if (isSubmitting) return;
      clearFormErrors();
      setFormSubmitting(true);
      try {
        const { status, result } = await postExperienceForm(addForm);
        handleCreateResponse(status, result);
      } catch (error) {
        console.error('Error adding experience:', error);
        const message = 'Tidak dapat terhubung ke server. Periksa koneksi dan coba lagi.';
        showFormFailure('Gangguan koneksi', message);
      } finally {
        setFormSubmitting(false);
      }
    }

    addForm.addEventListener('submit', submitExperienceForm);
  }

  initializeExperienceSearch();
  initializeExperienceForm();
  refreshExperienceList();
})();
