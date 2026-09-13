/* Public page views via https://github.com/soxft/busuanzi/wiki/API.
 * A page view is a page load, not a unique reader or a completed read.
 */
(function () {
  "use strict";

  var counter = document.getElementById("page-views");
  if (!counter) return;

  var label = counter.querySelector("[data-view-count]");
  var pageUrl = new URL(counter.dataset.pageUrl);

  // Never count local previews or send campaign/query parameters to the service.
  if (location.origin !== pageUrl.origin || location.pathname !== pageUrl.pathname) return;
  if (navigator.globalPrivacyControl || navigator.doNotTrack === "1") return;

  label.textContent = "Loading views\u2026";
  var controller = new AbortController();
  var timeout = setTimeout(function () { controller.abort(); }, 6000);

  // No remote script, cookies, client-side identity storage, or secret API keys.
  // Do not retry POST: the service may have counted a request even if it timed out.
  fetch("https://busuanzi.9420.ltd/api", {
    method: "POST",
    headers: { "x-bsz-referer": pageUrl.origin + pageUrl.pathname },
    credentials: "omit",
    referrerPolicy: "no-referrer",
    cache: "no-store",
    signal: controller.signal
  }).then(function (response) {
    if (!response.ok) throw new Error("View counter unavailable");
    return response.json();
  }).then(function (result) {
    var count = result.data && result.data.page_pv;
    if (!result.success || !Number.isSafeInteger(count) || count < 0) {
      throw new Error("Invalid view count");
    }
    label.textContent = count.toLocaleString("en-US") + (count === 1 ? " view" : " views");
  }).catch(function () {
    label.textContent = "Views unavailable";
  }).finally(function () {
    clearTimeout(timeout);
  });
}());
