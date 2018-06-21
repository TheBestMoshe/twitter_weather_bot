#!/usr/bin/env python3.6
import parts
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
from api_keys import version
import time

time.sleep(20)

# Logging needs to be completely rewritten
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

handler = logging.FileHandler('logs.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='sun,mon,tue,wed,thu,fri', hour=8)
def morning_report():
    logger.info('Beginning morning routine')
    logger.info('Sending hourly forecast')
    parts.tweet(parts.hourly_forecast())
    logger.info('Sending today\'s forecast')
    parts.tweet(parts.today_weather())


@sched.scheduled_job('cron', day_of_week='sat,mon,thu', hour=20)
def evening_report():
    logger.info('sending weekly forecast')
    parts.tweet(parts.weekly_forecast())


# @sched.scheduled_job('interval', minutes=1)
# def minutely_report():
#     parts.tweet(parts.hourly_forecast(1))
#     print('hourly_forecast ran')

parts.dm('moshe_grunwald', f'{version} version of lkweatherbot has been started')
logger.info('Starting scheduler')
sched.start()