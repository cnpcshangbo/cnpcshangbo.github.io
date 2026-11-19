# "Ask about Bo" assistant: Cloudflare Worker

The chat bar at the bottom of the site (`_includes/ai-assistant.html`,
`assets/js/ai-assistant.js`, `assets/css/ai-assistant.css`) sends visitor
questions to this Worker. The Worker:

- keeps the Anthropic API key as a Worker secret, so it never reaches the browser;
- answers only from the public profile at `/llms-full.txt` (refreshed hourly);
- declines private questions and does not speak for Bo;
- only accepts requests from the site's own origin;
- limits each visitor IP to 10 questions a minute and caps message length.

Model: `claude-haiku-5-5` (set `MODEL` in `wrangler.toml` to change it).

## Deploy (one time)

1. Create an Anthropic Console account, add billing, and set a monthly spend
   limit (Settings, Limits). Create an API key there. Do not paste it anywhere
   except step 3.
2. Create a free Cloudflare account.
3. From this folder:

   ```sh
   npm install
   npx wrangler login
   npx wrangler secret put ANTHROPIC_API_KEY
   npx wrangler deploy
   ```

   `deploy` prints the Worker URL, such as
   `https://bo-ai-assistant.<account>.workers.dev`.
4. In `_config.yml`, set `ai_assistant.enabled: true` and
   `ai_assistant.endpoint` to that URL, then push.

## Local test

`npx wrangler dev` serves the Worker on `http://127.0.0.1:8787`. Put the key in
a `.dev.vars` file (`ANTHROPIC_API_KEY=...`, git-ignored) to test real answers.

## Turn it off

Set `ai_assistant.enabled: false` in `_config.yml` and push. The bar disappears
from every page; the Worker can stay or be deleted in the Cloudflare dashboard.
