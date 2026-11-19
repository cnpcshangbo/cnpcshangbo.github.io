# "Ask about Bo" relay on the 5090 (Ollama)

Browser -> Tailscale Funnel (public HTTPS, port 8443) -> `server.mjs` on 127.0.0.1:8787 -> Ollama on 127.0.0.1:11434.
Only the relay is published; Ollama stays private.

## Run
    git clone -b ai-assistant https://github.com/cnpcshangbo/cnpcshangbo.github.io ~/ask-about-bo
    mkdir -p ~/.config/systemd/user
    cp ~/ask-about-bo/tools/ai-assistant-ollama/ask-about-bo.service ~/.config/systemd/user/
    systemctl --user daemon-reload && systemctl --user enable --now ask-about-bo
    tailscale funnel --bg --https=8443 http://127.0.0.1:8787

## Stop
    tailscale funnel --https=8443 off
    systemctl --user disable --now ask-about-bo

## Change model
Edit `MODEL=` in the service file (any name from `ollama list`), then `systemctl --user daemon-reload && systemctl --user restart ask-about-bo`.

Limits: 10 questions/minute and 100/day per visitor, 1500/day in total, 2 answers at a time.
Logs: `journalctl --user -u ask-about-bo -f`
