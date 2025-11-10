# azu2-pro

Production-ready Telegram bot (vcf/xlsx/txt converter) - ready for Termux, Heroku, Docker.

## Quick start (Termux)
1. Upload this folder to Termux home (or clone GitHub)
2. Run `bash install.sh` and follow prompts (or edit config.py directly)
3. Check logs: `tmux attach -t bot`

## Deploy to Heroku
1. Create an app on Heroku
2. Set config vars (API_ID, API_HASH, BOT_TOKEN, CHAT_ID_NOTIFY)
3. `git push heroku main`

## Notes
- Bot will auto-restart on crash and attempt to clean logs if disk usage exceeds threshold.
- For Termux startup on boot, install Termux:Boot and place a startup script to call start_bot.sh
