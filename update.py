from logging import FileHandler, StreamHandler, INFO, basicConfig, error as log_error, info as log_info
from os import path as ospath, environ, remove
from platform import machine
from subprocess import run as srun
from requests import get as rget
from dotenv import load_dotenv
from pymongo import MongoClient

if ospath.exists('log.txt'):
    with open('log.txt', 'r+') as f:
        f.truncate(0)

basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[FileHandler('log.txt'), StreamHandler()],
                    level=INFO)

load_dotenv('config.env', override=True)

try:
    if bool(environ.get('_____REMOVE_THIS_LINE_____')):
        log_error('The README.md file there to be read! Exiting now!')
        exit()
except:
    pass

BOT_TOKEN = environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
    log_error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

bot_id = int(BOT_TOKEN.split(':', 1)[0])

DB_URI = environ.get('DATABASE_URL', '')
if len(DB_URI) == 0:
    DB_URI = None

if DB_URI:
    conn = MongoClient(DB_URI)
    db = conn.mltb
    if config_dict := db.settings.config.find_one({'_id': bot_id}):  #retrun config dict (all env vars)
        environ['UPSTREAM_REPO'] = config_dict['UPSTREAM_REPO']
        environ['UPSTREAM_BRANCH'] = config_dict['UPSTREAM_BRANCH']
    conn.close()

load_dotenv('config.env', override=True)

UPSTREAM_REPO = environ.get('UPSTREAM_REPO', '')
if len(UPSTREAM_REPO) == 0:
    UPSTREAM_REPO = 'https://github.com/junedkh/jmdkh-mltb'

UPSTREAM_BRANCH = environ.get('UPSTREAM_BRANCH', '')
if len(UPSTREAM_BRANCH) == 0:
    UPSTREAM_BRANCH = 'master'

if ospath.exists('.git'):
    srun(["rm", "-rf", ".git"])

update = srun([f"git init -q \
                    && git config --global user.email kjuned007@gmail.com \
                    && git config --global user.name junedkh \
                    && git add . \
                    && git commit -sm update -q \
                    && git remote add origin {UPSTREAM_REPO} \
                    && git fetch origin -q \
                    && git reset --hard origin/{UPSTREAM_BRANCH} -q"], shell=True)

if update.returncode == 0:
    srun(["pip3","install","-r","requirements.txt"])
    log_info('Successfully updated with latest commit from UPSTREAM_REPO')
else:
    log_error('Something went wrong while updating, check UPSTREAM_REPO if valid or not!')

try:
    res = rget(f"https://github.com/junedkh/jmdkh-mltb/releases/latest/download/jmdkh_mtlb_{machine()}.zip")
    if res.status_code == 200:
        log_info("Downloading important files....")
        with open('jmdkh.zip', 'wb+') as f:
            f.write(res.content)
        log_info("Extracting important files....")
        srun(["unzip", "-q", "-o", "jmdkh.zip"])
        srun(["chmod", "-R", "777", "bot"])
        log_info("Ready to Start!")
        remove("jmdkh.zip")
    else:
        log_error(f"Failed to download jmdkh.zip, link got HTTP response: {res.status_code}")
except Exception as e:
    log_error(f"Release url : {e}")