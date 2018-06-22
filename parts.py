#!/usr/bin/env python3.6

import tweepy
import requests
import datetime
from api_keys import *

consumer_key = twitter_consumer_key
consumer_secret = twitter_consumer_secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

access_token = twitter_access_token
access_token_secret = twitter_access_token_secret

auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


def tweet(message):
    api.update_status(message)


def dm(user, message):
    api.send_direct_message(user, text=message)


def get_weather():
    lat = 40.0821290
    long = -74.2097014
    api_secret = darksky_api_secret
    api_url = f'https://api.darksky.net/forecast/{api_secret}/{lat},{long}'
    raw_data = requests.get(api_url)
    weather = raw_data.json()

    return weather


def today_weather():
    weather = get_weather()

    today = weather['daily']['data'][0]

    date = datetime.datetime.fromtimestamp(today['time'])
    date = date.strftime('%a, %b %d')

    precip = calculate_percip(today)

    temp_high = int(today['temperatureHigh'])
    temp_low = int(today['temperatureLow'])
    real_feel_high = int(today['apparentTemperatureHigh'])
    real_feel_low = int(today['apparentTemperatureLow'])
    summary = today['summary']

    message = (f'High: {temp_high}\n'
               f'Low:  {temp_low}\n'
               f'{precip}'
               f'Feels like:\n'
               f'High: {real_feel_high}\n'
               f'Low: {real_feel_low}')

    # Tries adding the summary to the message
    if len('Today ' + date + ' ' + summary + message) <= 140:
        message = 'Today ' + date + ' ' + summary.lower() + '\n' + message

    else:
        message = 'Today ' + date + message + '\n'

    return message


def weekly_forecast(days=7, keep_below_120c=True):
    weather = get_weather()

    def generate_forecast(count):
        weekly_weather = weather['daily']['data']

        message = f'\n{count} Day Forecast\n'

        for i in range(count):
            date = weekly_weather[i]['time']
            date = datetime.datetime.fromtimestamp(date)
            date = date.strftime('%a, %b %d')

            precip = calculate_percip(weekly_weather[i])

            temp_high = int(weekly_weather[i]['temperatureHigh'])
            temp_low = int(weekly_weather[i]['temperatureLow'])

            message = message + (f'\n{date}\n'
                                 f'{temp_high}/{temp_low}\n'
                                 f'{precip}')
        return message

    if keep_below_120c is True:
        to_long = True
        while to_long is True:
            message = generate_forecast(days)
            if len(message) <= 120:
                to_long = False
            else:
                days -= 1
    else:
        message = generate_forecast(days)
    return message


def hourly_forecast(hours=24, keep_below_120c=True, bi_hourly=True):
    """
    Returns the hourly forecast

    :param hours: Chose how many hours forecast you want the results to be
    :param keep_below_120c: If set to true, it will keep the character count of the
    return message under 120, even if it means less hours.
    :param bi_hourly: Set to true if forecast should bi bi-hourly. Set to false if it
    should be hourly.
    :return:
    """

    weather = get_weather()

    def generate_forecast(count):

        hourly_weather = weather['hourly']['data']

        message = f'\n{count} Hour Forecast\n'

        if bi_hourly is True:
            step = 2
        else:
            step = 1
        for i in range(0, count, step):
            time = datetime.datetime.fromtimestamp(hourly_weather[i]['time'])
            time = time.strftime('%I%p')
            # If the hour isn't 10 remove any extra 0
            if '10' not in time:
                time = time.strip('0')

            preip = calculate_percip(hourly_weather[i])

            temperature = int(hourly_weather[i]['temperature'])
            feels_like = int(hourly_weather[i]['apparentTemperature'])
            if feels_like == temperature:
                feels_like = ''
            else:
                feels_like = 'RF ' + str(feels_like) + '\n'

            message = message + (f'\n{time}\n'
                                 f'{temperature}\n'
                                 f'{feels_like}'
                                 f'{preip}')

        return message

    if keep_below_120c is True:
        to_long = True
        while to_long is True:
            message = generate_forecast(hours)
            if len(message) <= 120:
                to_long = False
            else:
                hours -= 1
    else:
        message = generate_forecast(hours)

    return message


def clean_up_weather_percent(percentage):
    percentage = str(percentage)
    percentage = percentage.replace('.', '')
    if percentage[:1] == '0':
        percentage = percentage[1:]
    return percentage + '%'


def calculate_percip(weather, sensitivity=0.20):
    """
    Takes the days weather and checks if there is a chance of rain.

    Calculates the chance of precipitation and the type, and returns it as a sentence
    if the percentage is over the set amount.
    :param weather:Accepts a dictionary of one segment of weather (day or hour)
    :param sensitivity:Accepts a float to determine how much chance of precipitation is
    needed to return the chance of precipitation.
    :return:The complete line of the chance and type of precipitation or nothing
    """
    precip = ''
    if 'precipType' in weather:
        precip_type = weather['precipType']
        precip_prob = clean_up_weather_percent(weather['precipProbability'])

        if weather['precipProbability'] > sensitivity:
            precip = f'{precip_type.title()}: {precip_prob}\n'
    return precip


if __name__ == '__main__':
    print(today_weather())
    print(hourly_forecast())
    print(weekly_forecast())


