import codecs
import json
import os

from debug_utils import LOG_CURRENT_EXCEPTION

CONFIG_DIR = os.path.join('mods', 'configs', 'maksforge.example_mod')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')

DEFAULTS = {
    'enabled': True,
}


def _merged(defaults, loaded):
    result = dict(defaults)
    for key, value in loaded.items():
        if key in defaults and isinstance(defaults[key], dict) and isinstance(value, dict):
            result[key] = _merged(defaults[key], value)
        elif key in defaults:
            result[key] = value
    return result


def load():
    try:
        if os.path.isfile(CONFIG_PATH):
            with codecs.open(CONFIG_PATH, 'r', 'utf-8-sig') as f:
                return _merged(DEFAULTS, json.load(f))
        save(DEFAULTS)
    except Exception:
        LOG_CURRENT_EXCEPTION()
    return _merged(DEFAULTS, {})


def save(settings):
    try:
        if not os.path.isdir(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        with codecs.open(CONFIG_PATH, 'w', 'utf-8') as f:
            json.dump(settings, f, indent=4, sort_keys=True)
    except Exception:
        LOG_CURRENT_EXCEPTION()
