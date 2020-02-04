# Party Like Button: IoT and CompetitionLabs

Over the easter break, I took some time to play around with a few bits of tech I had lying around. I've been kicking the tires with a data event, aggregation, and rules platform that some former collegues have launched, as well as one of the physical AWS Dash buttons. And, of course, the ever useful Raspberry Pi. 

CompetitionLabs is a platform targeted at marketing engagement and retentions. But under the covers it is a highly scalable, high-performance data aggregation and rules engine. I decided to see what sort if interesting things I could build with a few few compentent. Namely:

* An Amazon IoT Button
* A Raspberry Pi
* A demo account at [CompetitionLabs.com](https://www.competitionlabs.com)

The primary driver for this is an annoying annoucement by Sonos that they are going to release an update that disables the physical remote controls. These remotes had physical buttons, a screen, and are fairly robust against kids, etc. Now, I know I'm not going to be able to replicate a full featured remote control with a screen. But I started to think about what might be fun to do with a little bit of hacking together.

What I came up with was *The Like Button*. You, know. For parties. Clear? Let me explain...

So imagine you're having a party and you have all of your mates around (Imagine you have mates who would come around to your house). Imagine you're playing a random selection of tracks. You want to know which tracks people like and which ones they'd like to skip, right? Of course you would. 

Now, you could give your guests your phone. But fingers are going to be sticky with the delicious BBQ I've provided. So what if there was a simple button anyone could push to say "I like this song!" 

## Sending Events to CompetitionLabs

For production deployments, you normally use a message queue like RabbitMQ or AWS SQS. For this, I just used their [REST API](https://complabs.atlassian.net/wiki/display/CLRAV/ReST+API). 

There were two types of events I wanted to send. First, an event whenever a song is played on my Sonos system. For this I used the Soco Python library to interact with a Sonos speaker. The library lets you query the Sosos system to determine when a track is played. from there, you map the data you want to the CompetitionLabs API and send the event. Second, an event whenever someone presses the AWS IoT button to show they like the track that's playing. 

With just those two events, I can create rules in CompetitionLabs that will fire triggers that are received by a webhook running on a RaspberryPi. 

### Mapping the Play Event

I'm not going to cover using the Soco library to interact with Sonos other than to say you get back an object that you can use to get various bits of information about the playing track. These I map to a CompetitionLabs event:

```python
def map_event_to_cl_event(event_data):

    track_data = event_data.variables['current_track_meta_data']

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

    logging.info("CL message %s" % json.dumps(cl_data))
    return cl_dat
```

As you can see, there are standard fields that you need to send to the API, but you can add any key/value metadata you want.

One slight wrinkle was dealing with the timestamp of the event. When I originally wrote the code, I was using Python 3.6. However my Raspberry Pi where it was going to run only has Python 3.5. The ```timespec``` parameter was only added in Python 3.6, so for 3.5 I had to do a bit more direct manipulation to the get the timestamp into the correct format. One little helper function later and now it works correctly on 3.5 or 3.6:

```python
from datatime import datetime, timezone

def timespec_now():
    if sys.version_info > (3,6,0):
        timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
    else:
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "+00:00"

    return timestamp
```

### Mapping the AWS IoT Button Event

I won't go into the gory details of how AWS IoT works, but basically you associate a button press with an AWS Lambda code block which gets exectured whenever you press the button. So mapping the event in the Lambda is simple as well:

```python
def map_event_to_cl_event(event_data):


    transactionTimestamp = timespec_now()

    cl_data = [{'memberRefId': event_data['serialNumber'],
                'action': event_data['clickType'],
                'sourceValue': 1,
                'entityRefId': 'AWS_IoT_Button',
                'transactionTimestamp': transactionTimestamp,
                "metadata": {
                    "battVoltage": event_data['batteryVoltage'],
                }
                }]
    print(transactionTimestamp)

    logging.info("CL message %s" % json.dumps(cl_data))

    return cl_data
```


### Sending the event to CompetitionLabs

In both cases, sending the event to the CompetitionLabs endpoint is a simple POST request:

```python
def send_event_to_cl(cl_data):
    url = CL_API_EVENT_ENDPOINT # i.e. https://api.competitionlabs.com/api/[spacename]/events

    payload = json.dumps(cl_data)
    logging.info("Sending to CL: ".format(payload))
    headers = {
        'x-api-key': CL_API_KEY,
        'content-type': "application/json"
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    return response
```



