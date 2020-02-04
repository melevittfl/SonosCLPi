import pytz as pytz
import soco
from soco.discovery import by_name
from time import sleep
from datetime import datetime, timezone
import fcntl
import sys
import errno
import logging
import logging.config
import requests
import json
import sys


from config import *


from queue import Empty
from soco.events import event_listener

time = "00:01:00"
sum(x * int(t) for x, t in zip([3600, 60, 1], time.split(":")))


def timespec_now():
    if sys.version_info > (3,6,0):
        timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
    else:
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "+00:00"

    return timestamp

def map_event_to_cl_event(event_data):

    track_data = event_data.variables['current_track_meta_data']

    tz = pytz.UTC
    transactionTimestamp = timespec_now()

    cl_data = [{'memberRefId': "FrontRoom",
                'entityRefId': track_data.title,
                'action': event_data.transport_state.lower(),
                'sourceValue': 1,
                'transactionTimestamp': transactionTimestamp,
                "metadata": {
                    "track_length": event_data.current_track_duration,
                    "album": track_data.album,
                    "artist": track_data.creator,
                    "track_number_in_queue": event_data.current_track,
                    "number_of_tracks_in_queue": event_data.number_of_tracks
                }
                }]
    print(transactionTimestamp)

    logging.info("CL message %s" % json.dumps(cl_data))

    return cl_data


def send_event_to_cl(cl_data):
    url = "https://app.competitionlabs.com/api/marktest1/events"

    payload = json.dumps(cl_data)
    logging.info("Sending to CL: ".format(payload))
    headers = {
        'X-API-KEY': CL_API_KEY,
        'content-type': "application/json"
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    print("Response Code: {0} Response Data: {1}".format(response.status_code, response.text))


def main():
    device = by_name("Front Room")
    logging.debug(device)

    logging.debug("Subscribing to play events")
    sub = device.avTransport.subscribe()

    while True:
        try:
            event = sub.events.get(timeout=0.5)
            print("Event Variables")
            print("---------------")
            print(event.variables)
            print("----------------")
            track_data = event.variables['current_track_meta_data']

            print("Event Sequence number: {}".format(event.seq))
            print("Event Subscription id: {}".format(event.seq))
            if "PLAYING" == event.transport_state:
                print("Transport State: {}".format(event.transport_state))
                print("Title: {}".format(track_data.title))
                # print(f"Track Length: {event.current_track_duration}")
                # print(f"Album: {track_data.album}")
                # print(f"Artist: {track_data.creator}")
                # print(f"Track Number in Queue: {event.current_track}")
                # print(f"Number of Tracks in Queue: {event.number_of_tracks}")
                # print(f"Timestamp: {event.timestamp}")
                cl_event = map_event_to_cl_event(event)
                payload = json.dumps(cl_event)
                # print(f"Sending to CL: {payload}")
                send_event_to_cl(cl_event)







        except Empty:
            pass

        except KeyboardInterrupt:
            print("Unsubscribing from events")
            sub.unsubscribe()
            event_listener.stop()
            break


if __name__ == '__main__':
    logging.config.dictConfig(LOG_SETTINGS)
    logging.debug("Checking Sonos")

    f = open('.lock', 'w')
    try:
        fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError as e:
        if e.errno == errno.EAGAIN:
            logging.error("Another instance already running")
            sys.exit(-1)

    main()

