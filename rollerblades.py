#!/usr/bin/env python3

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
INTERVAL = os.getenv('INTERVAL', 3600)

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


def get_current_preroll(host: str, port: str, token: str) -> str:
    url = f"https://{host}:{port}/:/prefs?X-Plex-Token={token}"
    r = requests.get(url, headers=HEADERS, verify=False)
    root = ET.fromstring(r.content)
    return root.findall(".//*[@id='CinemaTrailersPrerollID']")[0].attrib['value']  # noqa E501


def update_preroll(host: str, port: str, token: str, key: str, preroll: str) -> int:  # noqa E501
    url = f"https://{host}:{port}/:/prefs?{key}={preroll}&X-Plex-Token={token}"
    r = requests.put(url, headers=HEADERS, verify=False)
    return r.status_code


def main() -> None:
    while True:
        current_preroll = get_current_preroll(HOST, PORT, TOKEN)  # type: ignore  # noqa E501
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
            update_preroll(HOST, PORT, TOKEN, KEY, new_preroll)  # type: ignore

        # take a nap for an hour and do it again
        sleep(INTERVAL)  # type: ignore


if __name__ == "__main__":
    main()
