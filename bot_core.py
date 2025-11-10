import os
import sys
import shutil
import time
import logging
from logging.handlers import RotatingFileHandler
from pyrogram import Client
import config

# Logging with rotation
logger = logging.getLogger('azu2')
logger.setLevel(logging.INFO)
fh = RotatingFileHandler('bot.log', maxBytes=2000000, backupCount=5, encoding='utf-8')
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(logging.StreamHandler(sys.stdout))

class Bot(Client):
    def __init__(self):
        super().__init__(
            'bot',
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            plugins=dict(root='plugins')
        )

    async def start(self):
        await super().start()
        logger.info('Bot started')
        # Notify admin if configured
        try:
            if getattr(config, 'CHAT_ID_NOTIFY', None):
                await self.send_message(int(config.CHAT_ID_NOTIFY), '✅ Bot berhasil dijalankan!')
        except Exception as e:
            logger.warning('Notify failed: %s', e)

    async def stop(self, *args, **kwargs):
        logger.info('Stopping...')
        await super().stop()

class BotRunner:
    """Runs the bot with an auto-restart loop, disk-check and optional auto-update."""
    def __init__(self):
        self.restart_delay = 5
        self.disk_threshold_percent = 90  # restart if used percent > threshold

    def _disk_full(self):
        try:
            total, used, free = shutil.disk_usage('/')
            percent_used = (used / total) * 100
            return percent_used >= self.disk_threshold_percent, percent_used
        except Exception as e:
            logger.warning('Disk check failed: %s', e)
            return False, 0

    def _cleanup_logs(self):
        # safe cleanup: remove large .log and tmp files in working dir
        try:
            for dirpath, dirnames, filenames in os.walk('.'):
                for f in filenames:
                    if f.endswith('.log') or f.endswith('.tmp') or f.endswith('.cache'):
                        fp = os.path.join(dirpath, f)
                        try:
                            os.remove(fp)
                            logger.info('Removed %s', fp)
                        except Exception:
                            pass
        except Exception as e:
            logger.warning('Cleanup failed: %s', e)

    def _git_pull(self):
        if os.path.isdir('.git'):
            try:
                os.system('git pull --rebase')
            except Exception as e:
                logger.warning('Git pull failed: %s', e)

    def run(self):
        while True:
            # Auto-update from GitHub (if present)
            self._git_pull()

            # Check disk usage and cleanup if needed
            full, percent_used = self._disk_full()
            if full:
                logger.warning('Disk usage high: %.1f%% - cleaning logs and restarting', percent_used)
                self._cleanup_logs()
                # after cleanup, re-evaluate
                full2, percent_used2 = self._disk_full()
                if full2:
                    logger.critical('Disk still full after cleanup - attempting restart anyway')

            try:
                app = Bot()
                app.run()  # blocking: pyrogram handles loop internally
            except KeyboardInterrupt:
                logger.info('KeyboardInterrupt received - exiting')
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)
            except Exception as e:
                logger.exception('Bot crashed: %s', e)
                logger.info('Restarting in %s seconds...', self.restart_delay)
                time.sleep(self.restart_delay)
