#!/data/data/com.termux/files/usr/bin/bash
set -e
echo "Updating packages..."
pkg update -y && pkg upgrade -y
echo "Installing dependencies..."
pkg install -y python git clang libjpeg-turbo freetype tmux curl
pip install --upgrade pip
pip install -r requirements.txt
if [ ! -f config.py ]; then
    read -p "API_ID: " api_id
    read -p "API_HASH: " api_hash
    read -p "BOT_TOKEN: " bot_token
    read -p "CHAT_ID_NOTIFY (optional): " chat_id
    cat > config.py <<EOF
API_ID = $api_id
API_HASH = "$api_hash"
BOT_TOKEN = "$bot_token"
CHAT_ID_NOTIFY = $chat_id
EOF
fi
chmod +x start_bot.sh || true
# create a start helper that loops and restarts
cat > start_bot.sh <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
while true; do
  echo "Checking for updates..."
  if [ -d .git ]; then git pull --rebase || true; fi
  python main.py
  echo "Bot stopped — restarting in 5s..."
  sleep 5
done
EOF
chmod +x start_bot.sh
tmux new-session -d -s bot './start_bot.sh'
echo "Bot started in tmux session 'bot'. Use 'tmux attach -t bot' to see logs."
