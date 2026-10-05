# Experience AJAX rendering: XSS audit

The renderer in `static/js/experience.js` treats API values as data. It creates
elements with `document.createElement()` and never puts API values into
`innerHTML`, `outerHTML`, `insertAdjacentHTML`, or inline event handlers.

| JSON value | DOM use | Protection |
| --- | --- | --- |
| `fields.title` | Card heading, delete-confirmation text, delete button accessibility label, image alt text | `element()` uses `textContent`; `textValue()` converts attribute text before DOM setters. Quotes and tags remain literal text. |
| `fields.description` | Description paragraph | `element()` uses `textContent`. |
| `fields.category_display` | Category badge and truncated image placeholder | `element()` uses `textContent`; truncation happens on the original string. |
| `fields.star_count` | Count badge and accessibility label | Only nonnegative safe integers are accepted; other values display `0`. The badge still uses `textContent`. |
| `fields.is_starred`, `fields.is_ongoing` | Select fixed CSS classes and fixed status labels | Only the boolean `true` selects the corresponding state. API text is never used as a class name or status label. |
| `fields.thumbnail` | Image `src` | `safeImageUrl()` allows only absolute HTTP/HTTPS URLs, matching the model's URLField, then assigns the result through the `src` property. HTML payloads, JavaScript, data and other protocols use the existing placeholder. Quotes cannot create attributes through a DOM property setter. |
| `pk` | Edit/delete URLs, modal IDs and popover references | Must be a string matching the complete UUID pattern before use. URLs use Django-generated route templates; API values cannot supply arbitrary links or form actions. |
| `model`, `fields.category`, `fields.started_at`, `fields.ended_at` | No DOM use | These values are not rendered. |

## Escaping and legitimate content

Projects' Tutorial 05 implementation in `templates/project.html` has an
`escapeHtml()` helper that replaces `&`, `<`, `>`, double quotes and apostrophes
before interpolating values into an HTML string. That pattern is appropriate
when assigning generated HTML to `innerHTML`.

Experience uses DOM setters instead. `textValue()` centralizes conversion and
`element()` centralizes text insertion. Applying `escapeHtml()` before
`textContent` would display entities such as `&amp;` literally. Text nodes safely
preserve punctuation, accents, quotes, ampersands and text such as `A < B`.
Attribute text uses DOM property setters or `setAttribute()` on fixed,
non-executable attributes (`alt`, `aria-label`). URL values receive separate
protocol/UUID validation because HTML escaping alone cannot make URLs safe.

## Input sanitization and output escaping

`ExperienceForm.clean_title()` and `clean_description()` call Django's
`strip_tags()` before storing the two free-text fields. Normal text is retained;
HTML tags and their attributes are removed. For example, a title containing
`Research <img src="x" onerror="alert('XSS!')">` saves as `Research`.
Tag-only input becomes empty and is rejected to preserve the required-field
rules. The shared ModelForm applies this to AJAX creation, the existing create
view and the update view.

`category` is a validated choice, `thumbnail` is a validated URL, and `ended_at`
is a datetime; their existing validation is retained without tag stripping.
IDs, generated dates and star relations are not free-text form fields.

This is defense in depth: input sanitization reduces stored HTML, while DOM
text insertion prevents remaining text from being interpreted as executable
markup. `strip_tags()` is not an output-safety guarantee: script contents can
remain as plain text, and old records or writes outside the ModelForm may still
contain tags. JavaScript therefore continues to use `textContent`, safe
attribute setters and URL validation. Do not mark sanitized strings as safe HTML.

## Regression test

`tests/experience-xss.test.cjs` runs the production renderer in jsdom with script
execution enabled. The positive control confirms the supplied malicious payload
would execute in an unsafe HTML sink. The production-rendering tests prohibit
HTML parsing sinks and assert that the payload stays literal in headings,
descriptions, category text, confirmation text, accessibility labels and image
alt text. They also dispatch image error events and assert that no alert runs.
Tests cover unsafe URL schemes, malformed IDs/counts/booleans, and legitimate
display text and URLs.

Django's `ExperienceFormTest` and `ExperienceAjaxCreateTest` also verify stripped
values in the database and JSON response, rejection of tag-only required text,
update sanitization, normal punctuation/Unicode, and existing field validation.

```powershell
.\env\Scripts\python.exe manage.py test main.tests.ExperienceFormTest main.tests.ExperienceAjaxCreateTest
```

Install the test dependency outside the repository and run in PowerShell:

```powershell
npm.cmd install --prefix "$env:TEMP\experience-xss-tests" --no-save --no-package-lock jsdom
node tests/experience-xss.test.cjs "$env:TEMP\experience-xss-tests\node_modules\jsdom"
```

jsdom verifies DOM rendering and event-handler behavior; it is not a live browser
visual or console inspection.
