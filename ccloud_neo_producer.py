
from confluent_kafka import Producer
import random
import os
import json
import time

conf = {'bootstrap.servers': os.getenv('BROKER_ENDPOINT'),
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': os.getenv('CLUSTER_API_KEY'),
        'sasl.password': os.getenv('CLUSTER_API_SECRET')}

producer = Producer(conf)

userlist = ['Rod', 'Jane', 'Freddie', 'Zippy', 'Bungle']
pagelist = ['ponies.org/shetland', 'harvard.edu/zuckerberg', 'zippy.com/rainbow', 'puppet.io/sooty',
            'bbc.co.uk/gloomy', 'aljazeera.com/gaza']


def pageview_generator():
    while True:
        record = {'user': random.choice(userlist), 'page': random.choice(pagelist)}
        yield json.dumps(record)


if __name__ == "__main__":
    pv_generator = pageview_generator()
    while True:
        pv = next(pv_generator)
        producer.produce('pageview', pv)
        producer.flush()
        time.sleep(2)
