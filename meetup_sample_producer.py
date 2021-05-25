#!/usr/bin/env python3
from confluent_kafka import Producer
import os
import json
import datetime

import requests

conf = {'bootstrap.servers': os.getenv('BROKER_ENDPOINT'),
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': os.getenv('CLUSTER_API_KEY'),
        'sasl.password': os.getenv('CLUSTER_API_SECRET')}

producer = Producer(conf)

end_time = datetime.datetime.now() + datetime.timedelta(seconds=300)

url = 'https://stream.meetup.com/2/rsvps'
with requests.get(url, stream=True) as r:
    for line in r.iter_lines():

        if datetime.datetime.now() >= end_time:
            break

        if line:
            meetup = json.loads(line)

            member_id = meetup.get('member').get('member_id')
            time = meetup.get('event').get('time')

            group_topics = meetup.get('group').get('group_topics')

            for group_topic in group_topics:
                group_topic_name = group_topic.get('topic_name')
                record = {'member_id': member_id, 'time': time, 'group_topic_name': group_topic_name}
                producer.produce('meetup-member-group-topic', json.dumps(record))
                producer.flush()
