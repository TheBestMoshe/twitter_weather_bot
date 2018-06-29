#!/usr/bin/env python3.6
import parts
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from api_keys import version
import time
import os
import sys
import requests

# Logging needs to be completely rewritten
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

handler = logging.FileHandler('logs.log')
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
        logging.info('Testing network connection')
        requests.get('https://google.com')
        network_connection = True
        logging.info(f'It took {connection_attempts/2} seconds to connect to network.')
    except Exception:
        logging.info('Not connected to the network')
        time.sleep(2)


# Create a scheduler
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


# Schedule jobs
scheduler.add_job(morning_report, trigger='cron', day_of_week='mon-fri, sun', hour=7)
scheduler.add_job(evening_report, trigger='cron', day_of_week='sun, wed', hour=20)
scheduler.add_job(evening_report, trigger='cron', day_of_week='fri', hour=15)


# Send me a DM letting me know that the bot instance has started
parts.dm('moshe_grunwald', f'{version} version of LkwdWeatherBot has been started')
logger.info('Starting scheduler')
scheduler.start()

# Once we started the scheduler, we will begin checking if the script has been changed
cwd = os.path.abspath(os.path.dirname(__file__)) + '/'
watched_files = [sys.argv[0], cwd + 'parts.py', cwd + 'api_keys.py']

watched_files_mtimes = [(f, os.path.getmtime(f)) for f in watched_files]

while True:
    for f, mtime in watched_files_mtimes:
        if os.path.getmtime(f) != mtime:
            logging.info('Found changes in the files. Restarting...')
            os.execv(sys.argv[0], sys.argv)

        else:
            time.sleep(1)
