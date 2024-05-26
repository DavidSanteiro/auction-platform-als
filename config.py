# config.py
import json


def load_config():
    with open('instance/config.json') as config_file:
        return json.load(config_file)