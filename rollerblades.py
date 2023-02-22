#!/usr/bin/env python3

import logging
import os
import json
import requests
import urllib3
import xml.etree.ElementTree as ET
from time import strftime, sleep

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # noqa E501

# --- To be passed in to container ---
# Required Vars
SCHEME = os.getenv('SCHEME', 'https')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT', '32400')
TOKEN = os.getenv('TOKEN')
INTERVAL = int(os.getenv('INTERVAL', 3600))
PREROLLS = os.getenv('PREROLLS', '/config/prerolls.json')
USE_MONTHS = int(os.getenv('USE_MONTHS', 1))
DEBUG = int(os.getenv('DEBUG', 0))

# --- Globals ---
VER = '0.6.5'
USER_AGENT = f"rollerblades.py/{VER}"
KEY = 'CinemaTrailersPrerollID'

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


def load_prerolls(file: str) -> dict:
    with open(file, "r") as f:
        prerolls = json.load(f)
    return prerolls


def get_current_preroll(scheme: str, host: str, port: str, token: str) -> str:
    url = f"{scheme}://{host}:{port}/:/prefs?X-Plex-Token={token}"
    r = requests.get(url, headers=HEADERS, verify=False)
    if (DEBUG):
        logger.debug(f"HTTP status code: {r.status_code}.")
    root = ET.fromstring(r.content)
    return root.findall(".//*[@id='CinemaTrailersPrerollID']")[0].attrib['value']  # noqa E501


def is_directory_check(preroll_path):
    # Check if the preroll path defined in prerolls.json is a directory or file.
    # A list of files separated by ; makes it so Plex randomly selects a preroll in the list.
    if os.path.isdir(preroll_path):
        files_list = [os.path.join(preroll_path, file) for file in os.listdir(preroll_path) if file.endswith('.mp4')]
        preroll_list_string = ";".join(files_list)
        return preroll_list_string
    else:
        return preroll_path


def update_preroll(scheme: str, host: str, port: str, token: str, key: str, preroll: str) -> int:  # noqa E501
    url = f"{scheme}://{host}:{port}/:/prefs?{key}={preroll}&X-Plex-Token={token}"  # noqa E501
    r = requests.put(url, headers=HEADERS, verify=False)
    if (DEBUG):
        logger.debug(f"Update HTTP status code: {r.status_code}.")
    return r.status_code


def main() -> None:
    logger.info(f"Startup {USER_AGENT}.")
    my_prerolls = load_prerolls(PREROLLS)
    logger.info(f"Loaded in prerolls data from {PREROLLS}.")
    while True:
        current_preroll = get_current_preroll(SCHEME, HOST, PORT, TOKEN)
        logger.info(f"Current preroll is: {current_preroll}.")
        current_month = strftime("%m")
        todays_date = strftime("%m%d")

        if my_prerolls['HOLIDAYS'].get(todays_date) is not None:
            # If match on a holiday in the list of holidays, use that
            new_preroll = is_directory_check(my_prerolls['HOLIDAYS'].get(todays_date))
        elif USE_MONTHS == 1 and current_month in my_prerolls['MONTHS']:
            # If current_month exists in the MONTHS section, use that.
            new_preroll = is_directory_check(my_prerolls['MONTHS'][current_month])
        else:
            # otherwise use the day of the week
            if os.path.exists(f'{my_prerolls["DAILYPATH"]}/{strftime("%A").lower()}.mp4'):
                new_preroll = f'{my_prerolls["DAILYPATH"]}/{strftime("%A").lower()}.mp4'  # noqa E501
            else:
                new_preroll = is_directory_check(my_prerolls['DAILYPATH'])

        # If there's a change from the current preroll, update Plex
        if new_preroll != current_preroll:
            logger.info(f"Change {current_preroll} to {new_preroll}.")
            update_preroll(SCHEME, HOST, PORT, TOKEN, KEY, new_preroll)

        # take a nap for an hour and do it again
        sleep(INTERVAL)


if __name__ == "__main__":
    main()
