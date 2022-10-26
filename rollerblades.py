#!/usr/bin/env python3

import logging
import os
import requests
import urllib3
import xml.etree.ElementTree as ET
from time import strftime, sleep

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # type: ignore  # noqa E501

# --- To be passed in to container ---
# Required Vars
HOST = os.getenv('HOST')
PORT = os.getenv('PORT', '32400')
TOKEN = os.getenv('TOKEN')
INTERVAL = int(os.getenv('INTERVAL', 3600))
DEBUG = int(os.getenv('DEBUG', 0))

# --- Globals ---
VER = '0.1'
USER_AGENT = f"rollerblades.py/{VER}"
KEY = 'CinemaTrailersPrerollID'

HOLIDAYS = {
    '0401': '/homevideos/preroll/april-fool.mp4',
    '1225': '/homevideos/preroll/christmas.mp4',
    '0214': '/homevideos/preroll/valentine.mp4',
    '1031': '/homevideos/preroll/halloween.mp4'
}

SPECIAL_MONTHS = {
    'June': '/homevideos/preroll/pride.mp4'
}

HEADERS = {
    "User-Agent": USER_AGENT
}

# Setup logger
logger = logging.getLogger()
ch = logging.StreamHandler()
if DEBUG:
    logger.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    ch.setLevel(logging.INFO)

formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s',
                              datefmt='[%d %b %Y %H:%M:%S %Z]')
ch.setFormatter(formatter)
logger.addHandler(ch)


def get_current_preroll(host: str, port: str, token: str) -> str:
    url = f"https://{host}:{port}/:/prefs?X-Plex-Token={token}"
    r = requests.get(url, headers=HEADERS, verify=False)
    if (DEBUG):
        logger.debug(f"HTTP status code: {r.status_code}.")
    root = ET.fromstring(r.content)
    return root.findall(".//*[@id='CinemaTrailersPrerollID']")[0].attrib['value']  # noqa E501


def update_preroll(host: str, port: str, token: str, key: str, preroll: str) -> int:  # noqa E501
    url = f"https://{host}:{port}/:/prefs?{key}={preroll}&X-Plex-Token={token}"
    r = requests.put(url, headers=HEADERS, verify=False)
    if (DEBUG):
        logger.debug(f"Update HTTP status code: {r.status_code}.")
    return r.status_code


def main() -> None:
    logger.info(f"Startup {USER_AGENT}.")
    while True:
        current_preroll = get_current_preroll(HOST, PORT, TOKEN)
        logger.info(f"Current preroll is: {current_preroll}.")
        current_month = strftime("%m")
        todays_date = strftime("%m%d")

        if current_month == "06":
            # If it's June use the pride month preroll
            new_preroll = SPECIAL_MONTHS['June']
        elif HOLIDAYS.get(todays_date) is not None:
            # If match on a holiday in the list of holidays, use that
            new_preroll = HOLIDAYS.get(todays_date)
        else:
            # otherwise use the day of the week
            new_preroll = f'/homevideos/preroll/rotation/{strftime("%A").lower()}.mp4'  # noqa E501

        # If there's a change from the current preroll, update Plex
        if new_preroll != current_preroll:
            logger.info(f"Change {current_preroll} to {new_preroll}.")
            update_preroll(HOST, PORT, TOKEN, KEY, new_preroll)

        # take a nap for an hour and do it again
        sleep(INTERVAL)


if __name__ == "__main__":
    main()
