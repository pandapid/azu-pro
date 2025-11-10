#!/data/data/com.termux/files/usr/bin/bash
while true; do
  if [ -d .git ]; then git pull --rebase || true; fi
  python main.py
  echo 'Bot stopped - restarting in 5s...'
  sleep 5
done
