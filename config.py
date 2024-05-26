# config.py
import os
import json


def load_config():
    with open('instance/config.json') as config_file:
        config = json.load(config_file)
    config['REDISCLOUD_URL'] = os.getenv('REDISCLOUD_URL', 'redis://localhost:6379/0')
    return config
