#!/usr/bin/env python3.6
from version_1 import parts
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from version_1.api_keys import version
import time
import os
import sys
import requests

# Logging needs to be completely rewritten
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

handler = logging.FileHandler(os.path.dirname(__file__) + '/logs.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# Wait until there is a network connection
network_connection = False
connection_attempts = 0
while not network_connection:
    try:
        connection_attempts += 1
        logger.info('Testing network connection')
        requests.get('https://google.com')
        network_connection = True
        if connection_attempts == 1:
            logger.info('Connected to network')
        else:
            logger.info(f'It took {connection_attempts/2} seconds to connect to network.')
    except Exception:
        logger.info('Not connected to the network')
        time.sleep(2)


# Create a scheduler
scheduler = BackgroundScheduler()


def morning_report():
    logger.info('Beginning morning routine')
    logger.info('Sending hourly forecast')

    try:
        parts.tweet(parts.hourly_forecast(scheduler=scheduler))
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
    logger.info('Sending weekly forecast')
    parts.tweet(parts.weekly_forecast())


# Schedule jobs
scheduler.add_job(morning_report, trigger='cron', day_of_week='mon-fri, sun', hour=7)
scheduler.add_job(evening_report, trigger='cron', day_of_week='sun, wed', hour=20)
scheduler.add_job(evening_report, trigger='cron', day_of_week='fri', hour=14)


# Send me a DM letting me know that the bot instance has started
logger.debug('Sending startup DM')
parts.dm('moshe_grunwald', f'{version} version of LkwdWeatherBot has been started')
logger.info('Sent startup DM')

logger.debug('Starting scheduler')
scheduler.start()
logger.info('Scheduler started')

# Once we started the scheduler, we will begin checking if the script has been changed
cwd = os.path.abspath(os.path.dirname(__file__)) + '/'
watched_files = [sys.argv[0], cwd + 'parts.py', cwd + 'api_keys.py']

watched_files_mtimes = [(f, os.path.getmtime(f)) for f in watched_files]

while True:
    for f, mtime in watched_files_mtimes:
        if os.path.getmtime(f) != mtime:
            logger.info(f'Found changes in {f}.\nRestarting...')
            # Added this sleep to make sure all the files have been writen to.
            # In the past the script would restart while the files were being overwritten
            # it would crash
            time.sleep(2)
            os.execv(sys.argv[0], sys.argv)
        else:
            time.sleep(2)

