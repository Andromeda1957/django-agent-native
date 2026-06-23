// Example client module. Client behavior lives in TypeScript under
// static/web/ts/ and is compiled to static/web/js/ by `npm run build:js`.
// CI's "generated assets are current" gate fails if the committed JS is stale.

function showLoadedAt(el: HTMLElement): void {
  const now = new Date();
  el.textContent = `Page loaded at ${now.toLocaleTimeString()}`;
}

const target = document.getElementById("loaded-at");
if (target) {
  showLoadedAt(target);
}
