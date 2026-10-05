# Experience add modal

The list view supplies an unbound `ExperienceForm` only when
`can_create_content(request.user)` is true. The template renders the add button
and `components/experience_form_modal.html` for that role. The button opens the
native popover on the list page; cancel, close and backdrop controls dismiss it.
The separate create-page link is replaced by this button.

`static/js/experience.js` checks that both the modal and form exist before
attaching their handler. Anonymous users, regular users and editors continue to
use the list and search without requiring modal elements.

Submission prevents navigation and sends `fetch()` with POST to the form's
`/experiences/add-ajax/` action. `new FormData(form)` includes the hidden
`csrfmiddlewaretoken` rendered by `{% csrf_token %}`. No cookie helper or manual
Content-Type header is needed. The backend still enforces permissions and
validates through `ExperienceForm`.

- 201: reset the form, clear errors, close the modal, cancel pending search
  debounce and call the existing `loadExperiences()` with the current search.
- 400: show field errors beside their controls and non-field errors in the
  summary; mark invalid controls and focus the first invalid field.
- 403: show the permission/session error inside the modal, including a fallback
  for non-JSON CSRF rejection responses.
- Network/server failures: show an inline error and keep the entered values for
  retry. A failed list refresh after a successful save uses the existing list
  error state.

The submit button is disabled while saving, and duplicate submissions are
ignored. Error messages use the same safe DOM text helper as list data, so a
malicious message cannot inject HTML. The existing global `showToast()` loaded by
`base.html` supplies concise success, validation, permission, server and network
notifications. Detailed validation stays in the modal. List-fetch errors also
use that shared toast; stale or aborted requests do not produce notifications.

`tests/experience-modal.test.cjs` covers CSRF FormData, search preservation,
reset/close/refetch, validation, permission and connection failures, duplicate
submissions, safe error text and absent privileged elements. Tests execute the
actual shared `toast.js` to check notification text/types, including anonymous
network failures. jsdom simulates the
popover lifecycle; native browser opening and visual layout are not covered by
these DOM tests. Django tests verify role visibility and rendered ModelForm
fields.

```powershell
node tests/experience-modal.test.cjs "$env:TEMP\experience-xss-tests\node_modules\jsdom"
```

The test dependency is installed as described in `docs/experience-xss.md`.
