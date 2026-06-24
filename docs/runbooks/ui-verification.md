# UI / Layout Verification Runbook

Use whenever a change affects rendered pages, layout, styling, or client
behavior. Do not report a visual change as done from code inspection alone.

## Steps

1. Run the app locally (e.g. `python3 manage.py runserver`) with `DEBUG=True`.
2. If TypeScript changed, run `npm run build:js` first so the served JS is
   current.
3. Load the affected page(s) in a browser and confirm the intended change
   renders, including responsive/mobile width if relevant.
4. Check the browser console for errors.
5. Confirm no unrelated layout regressions on the same page.
6. For changes that are hard to eyeball, add or update a Django test that asserts
   the rendered content (see `web/tests/test_views.py`).

## Notes

- Verify against the actual compiled assets, not just the TypeScript source.
- Capture a screenshot when the change is visual and the user may want to confirm.
