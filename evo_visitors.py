import csv
import datetime
import random
import time

import pytz
import requests

# Seconds between fetching visitors (+/- up to 30s)
TIME_INTERVAL = 5 * 60
# How often to check for new locations
FETCH_LOCATIONS_EVERY = TIME_INTERVAL * 100

BASE_URL = "https://visits.evofitness.no/api/v1/locations"
LOCATIONS_URL = BASE_URL + "?operator=5336003e-0105-4402-809f-93bf6498af34"


def get(url, loc=None):
    try:
        response = requests.get(url)
    except:
        print(f"ERROR: Failed to get URL: {url} \t Location: {loc}")
        return None
    if response.status_code != 200:
        print(
            f"ERROR: Request to get data for location {loc} returned status code {response.status_code} \t URL: {url}"
        )
        return None
    return response.json()


locations = get(LOCATIONS_URL)
it = 0

while True:
    it += 1
    # Check whether we should update location list (in case of new locations)
    if not it % FETCH_LOCATIONS_EVERY:
        print("Updating location list...")
        locations = get(LOCATIONS_URL)

    # EVO is open from 0500 - 2400 every day
    # Go to sleep if EVO is closed
    current_datetime = datetime.datetime.now(tz=pytz.timezone("Europe/Oslo"))
    if current_datetime.hour < 5:
        sleep_time = (5 - current_datetime.hour) * 60 * 60
        print(f"EVO is closed, sleeping for {sleep_time} hours.")
        time.sleep(sleep_time)

    # Fetch visitor data for all locations
    print("Fetching visitor data..")
    last_visitor_data = []
    for loc in locations:
        print(f"Fetching data for {loc['name']}")
        data = get(BASE_URL + "/" + loc["id"] + "/current", loc=loc["name"])
        if data:
            last_visitor_data.append(data)

    # Append new visitor data to csv file
    with open("evo_visitor_data.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(
            [
                [current_datetime, loc["name"], loc["current"]]
                for loc in last_visitor_data
            ]
        )
    print(f"\n{current_datetime.time()} Data written to file")

    # Sleep for some time
    sleep_time = TIME_INTERVAL + random.randint(-30, 30)
    print(f"Sleeping for {sleep_time} seconds..\n")
    time.sleep(sleep_time)
