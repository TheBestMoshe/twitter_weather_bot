#!/usr/bin/env python3.6
import parts
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from api_keys import version
import time
import os
import sys

# Logging needs to be completely rewritten
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

handler = logging.FileHandler('logs.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info('Starting 20 second wait...')
time.sleep(20)
logger.info('Wait is complete')

scheduler = BackgroundScheduler()


def morning_report():
    logger.info('Beginning morning routine')
    logger.info('Sending hourly forecast')

    try:
        parts.tweet(parts.hourly_forecast())
    except NameError as e:
        logger.error(f'Error!\n{e}')
    except Exception as e:
        logger.error('Failed to tweet hourly forecast',
                     f'Exception message:\n{e}')

    logger.info('Sending today\'s forecast')
    try:
        parts.tweet(parts.today_weather())
    except NameError as e:
        logger.error(f'Error!\n{e}')
    except Exception as e:
        logger.error('Failed to tweet today weather forecast'
                     f'Exception message:\n{e}')


def evening_report():
    logger.info('sending weekly forecast')
    parts.tweet(parts.weekly_forecast())


scheduler.add_job(morning_report, trigger='cron', day_of_week='mon-fri, sun', hour=7)

# Send me a DM letting me know that the bot instance has started
parts.dm('moshe_grunwald', f'{version} version of LkwdWeatherBot has been started')
logger.info('Starting scheduler')
scheduler.start()

# Once we started the scheduler, we will begin checking if the script has been changed
cwd = os.getcwd() + '/'
watched_files = [__file__, cwd+'parts.py', cwd+'api_keys.py']

watched_files_mtimes = [(f, os.path.getmtime(f)) for f in watched_files]

while True:
    for f, mtime in watched_files_mtimes:
        if os.path.getmtime(f) != mtime:
            os.execv(__file__, sys.argv)

        else:
            time.sleep(1)
