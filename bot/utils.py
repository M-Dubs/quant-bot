from loguru import logger
import os, time

def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logger.add("logs/quantbot.log", rotation="10 MB", retention="10 files", enqueue=True)

def heartbeat():
    with open("logs/heartbeat", "w") as f:
        f.write(str(int(time.time())))
1~from loguru import logger
import os, time

def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logger.add("logs/quantbot.log", rotation="10 MB", retention="10 files", enqueue=True)

def heartbeat():
    with open("logs/heartbeat", "w") as f:
        f.write(str(int(time.time())))
