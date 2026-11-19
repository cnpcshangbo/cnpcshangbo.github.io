# "Ask about Bo" relay on the 5090 (Ollama)

Browser -> Tailscale Funnel `https://enceldren047489.tailb06708.ts.net:8443/ask-about-bo` -> `server.mjs` on 127.0.0.1:8787 -> Ollama on 127.0.0.1:11434.
Only the relay is published (one path on the existing 8443 Funnel); Ollama stays private.

## Run (as installed on the 5090, user leichengadmin)
    git clone -b ai-assistant https://github.com/cnpcshangbo/cnpcshangbo.github.io ~/ask-about-bo
    cp ~/ask-about-bo/tools/ai-assistant-ollama/run-relay.sh ~/ask-about-bo/
    setsid nohup ~/ask-about-bo/run-relay.sh >/dev/null 2>&1 < /dev/null &
    tailscale funnel --bg --https=8443 --set-path=/ask-about-bo http://127.0.0.1:8787

Start after reboot (system unit, needs sudo once):

    sudo cp ~/ask-about-bo/tools/ai-assistant-ollama/ask-about-bo.service /etc/systemd/system/
    sudo systemctl daemon-reload && sudo systemctl enable --now ask-about-bo

Then use `sudo systemctl stop|restart ask-about-bo` instead of the loop script.

## Stop
    tailscale funnel --https=8443 --set-path=/ask-about-bo off
    pkill -f ask-about-bo/run-relay.sh; kill $(ss -ltnpH 'sport = :8787' | grep -o 'pid=[0-9]*' | cut -d= -f2)

## Change model
Edit `MODEL=` in run-relay.sh (any name from `ollama list`) and restart.

Limits: 10 questions/minute and 100/day per visitor, 1500/day in total, 2 answers at a time.
Log: `~/ask-about-bo/relay.log`
