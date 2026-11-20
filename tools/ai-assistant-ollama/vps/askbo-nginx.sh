#!/bin/bash
# Adds (or with --remove, removes) a /ask-about-bo location on academic.hopeembark.org
# that forwards to the relay on the 5090 via Tailscale Funnel. Backs up the site file first
# and restores it if nginx -t fails.
set -euo pipefail
F=/etc/nginx/sites-enabled/academic-edge
ANCHOR='nginx-legacy-redirect.conf;'
BAK=/root/academic-edge.bak-askbo-$(date +%Y%m%d%H%M%S)
cp -p "$F" "$BAK"
echo "backup: $BAK"
if [ "${1:-}" = "--remove" ]; then
  python3 - "$F" <<'PY'
import sys,re
p=sys.argv[1]; s=open(p).read()
s=re.sub(r'\n[ \t]*# BEGIN ASK-ABOUT-BO.*?# END ASK-ABOUT-BO[^\n]*','',s,flags=re.S)
open(p,'w').write(s)
PY
else
  if grep -q 'BEGIN ASK-ABOUT-BO' "$F"; then echo "already present"; rm -f "$BAK"; exit 0; fi
  python3 - "$F" "$ANCHOR" <<'PY'
import sys
p,anchor=sys.argv[1],sys.argv[2]; s=open(p).read()
i=s.index(anchor)+len(anchor)
block='''
    # BEGIN ASK-ABOUT-BO (AI assistant on cnpcshangbo.github.io -> relay on the 5090)
    location = /ask-about-bo {
        proxy_pass https://enceldren047489.tailb06708.ts.net/ask-about-bo;
        proxy_http_version 1.1;
        proxy_ssl_server_name on;
        proxy_set_header Host enceldren047489.tailb06708.ts.net;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 5s;
        proxy_read_timeout 100s;
        client_max_body_size 64k;
    }
    # END ASK-ABOUT-BO'''
s=s[:i]+block+s[i:]
open(p,'w').write(s)
PY
fi
if nginx -t; then
  systemctl reload nginx
  echo "nginx reloaded"
else
  cp -p "$BAK" "$F"
  echo "nginx -t failed; restored $F"
  exit 1
fi
sleep 1
curl -s -m 20 -o /dev/null -w 'preflight %{http_code}\n' -X OPTIONS \
  -H 'Origin: https://cnpcshangbo.github.io' -H 'Access-Control-Request-Method: POST' \
  https://academic.hopeembark.org/ask-about-bo || true
