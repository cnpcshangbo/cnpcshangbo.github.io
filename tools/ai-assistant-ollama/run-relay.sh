#!/bin/sh
# Keeps the Ask-about-Bo relay running. Start it once with
#   setsid nohup ~/ask-about-bo/run-relay.sh >/dev/null 2>&1 < /dev/null &
# and, to start it after a reboot, add this line with `crontab -e`:
#   @reboot $HOME/ask-about-bo/run-relay.sh >/dev/null 2>&1
cd "$HOME/ask-about-bo/tools/ai-assistant-ollama" || exit 1
while true; do PORT=8787 MODEL=gemma4:26b-a4b-it-q8_0 /usr/bin/node server.mjs >> "$HOME/ask-about-bo/relay.log" 2>&1; sleep 5; done
