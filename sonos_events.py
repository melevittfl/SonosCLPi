import soco
from soco.discovery import by_name
from time import sleep
import datetime
import fcntl
import sys
import errno
import logging
import logging.config
import requests
import json
from config import *


from queue import Empty
from soco.events import event_listener

def main():
    device = by_name("Front Room")
    logging.debug(device)

    logging.debug("Subscribing to play events")
    sub = device.avTransport.subscribe()

    while True:
        try:
            event = sub.events.get(timeout=0.5)
            print(event.variables)
            track_data = event.variables['current_track_meta_data']
            print(track_data.title)
            print(track_data.album)
            print(track_data.item_id)
            print(track_data)
            print(event.timestamp)
            print(event.seq)

        except Empty:
            pass

        except KeyboardInterrupt:
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

