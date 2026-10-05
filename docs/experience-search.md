# Experience AJAX search

The search form in `templates/experience.html` uses the existing Projects search
styles. JavaScript handles its input and submit events without navigating.

In `static/js/experience.js`, the input handler clears the previous timer and
sets a new timer using `SEARCH_DEBOUNCE_DELAY = 300`, matching the Projects
tutorial. It calls the existing `loadExperiences()` after typing pauses for
300 ms. Submitting the form cancels the timer and searches immediately.

There is one full-list request on page load. Typing a word with less than
300 ms between keystrokes produces one additional search request after the
pause, rather than one request per character. Each pause of at least 300 ms
can produce another request. Clearing the input restores the full dataset
after the same debounce delay.

Nonempty queries use `/api/experiences/?q=keyword`, encoded with
`URL.searchParams`. `get_experiences_json()` trims the query and filters with
Django ORM `Q(title__icontains=query) | Q(description__icontains=query)`.
Matching is case-insensitive. An absent, empty or whitespace-only `q` returns
the full list. The original `?title=` filter remains supported when `q` is
absent. Anonymous users can access the endpoint and use search.

Every input change immediately aborts and invalidates the previous request,
including during the debounce delay. Each fetch captures a request version;
responses and failures from older versions are ignored. Checks after both
fetch and JSON parsing prevent late responses from replacing newer results,
even if cancellation is ignored by the network.

Search reuses `buildExperience()`, preserving the star display, role controls,
safe text insertion and URL validation. Loading, empty and error states remain
available. Empty-search-result text is fixed text rather than interpolated HTML.

Regression checks:

```powershell
.\env\Scripts\python.exe manage.py test main.tests.ExperienceJsonTest main.tests.MainTest
node tests/experience-search.test.cjs "$env:TEMP\experience-xss-tests\node_modules\jsdom"
node tests/experience-xss.test.cjs "$env:TEMP\experience-xss-tests\node_modules\jsdom"
```

The Node tests use the jsdom dependency installed as described in
`docs/experience-xss.md`. They verify debounce request counts, query encoding,
clear/submit behavior, out-of-order responses, stale failures, current failures,
empty results and safe rendering.
