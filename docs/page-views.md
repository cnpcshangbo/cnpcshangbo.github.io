# Article view counts

The Minecraft research note displays a public page-view count alongside its reading time. Tracking began on September 13, 2026; the site had no earlier analytics from which to recover historical views. This counts page loads, including repeat visits and verification visits, not unique people or completed reads. It is an approximate audience indicator, not a research measurement.

To enable another article, set `page_views: true` and `page_views_since: YYYY-MM-DD` in its front matter. Keep its canonical permalink stable: counts are keyed by host and path. Only opted-in pages load `assets/js/page-views.js`.

The implementation calls the public [Busuanzi API](https://github.com/soxft/busuanzi/wiki/API) at `https://busuanzi.9420.ltd/api`. POST increments and returns the page count; GET reads without incrementing. The public endpoint needs no account or secret. Only the canonical public page URL is explicitly sent; query strings and fragments are excluded. The site does not load the provider's JavaScript, send cookies, or store its visitor identity token. As with any external request, the provider receives the visitor's IP address and browser request metadata; its backend hashes IP and User-Agent to calculate visitor statistics even though this site displays only page views. The [service page](https://busuanzi.9420.ltd/) describes its data collection and states that availability and data integrity are not guaranteed.

Local previews and browsers signalling Global Privacy Control or Do Not Track do not contact the counter. Script blockers and failed requests can cause undercounting; public unauthenticated counters cannot guarantee protection against artificial traffic. After six seconds, failure displays "Views unavailable" rather than zero. Requests are not retried to avoid double counting an ambiguous response. Disabling `page_views` removes both the display and the API call.

For validation, use mocked responses or GET requests; avoid repeatedly loading the production article because each successful POST adds a view.
