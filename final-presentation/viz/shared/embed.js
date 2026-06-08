/* shared/embed.js — slide-embed mode for the visualizations.
 * Load with `?embed`  -> hides page chrome (header / footer nav / hints).
 *        with `?embed=fig` -> also hides the .controls sidebar (figure only).
 * The page handles its own URL so it works under file:// and GitHub Pages alike.
 * Adds the class to <html> (always present) so CSS applies before <body> exists.
 */
(function () {
  try {
    var p = new URLSearchParams(location.search);
    if (!p.has("embed")) return;
    var root = document.documentElement;
    root.classList.add("embed");
    if (p.get("embed") === "fig") root.classList.add("embed-fig");
    if (p.has("row")) root.classList.add("embed-row");   // lay .plots canvases side-by-side
    if (p.has("light")) root.classList.add("embed-light"); // white-background light theme
  } catch (e) { /* no-op */ }
})();
