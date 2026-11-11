"""Stand-ins for the game modules a mod imports, so tests run outside the client (Python 2.7 or 3)."""
import os
import sys
import types

MODS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'res', 'scripts', 'client', 'gui', 'mods')


class Event(object):

    def __init__(self):
        self.handlers = []

    def __iadd__(self, handler):
        self.handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.handlers.remove(handler)
        return self

    def __call__(self, *args, **kwargs):
        for handler in list(self.handlers):
            handler(*args, **kwargs)


class PlayerEvents(object):

    def __init__(self):
        self.onAvatarReady = Event()


class Log(object):

    def __init__(self):
        self.notes = []
        self.errors = []
        self.exceptions = 0

    def note(self, *args):
        self.notes.append(' '.join(str(a) for a in args))

    def error(self, *args):
        self.errors.append(' '.join(str(a) for a in args))

    def exception(self):
        self.exceptions += 1


def module(name, **attrs):
    mod = types.ModuleType(name)
    mod.__dict__.update(attrs)
    sys.modules[name] = mod
    return mod


def install():
    """Replaces the game modules with fresh stubs and forgets every loaded mod module."""
    for name in [name for name in sys.modules if name == 'gui' or name.startswith('gui.')]:
        del sys.modules[name]
    log = Log()
    module('debug_utils', LOG_NOTE=log.note, LOG_ERROR=log.error, LOG_CURRENT_EXCEPTION=log.exception)
    player_events = PlayerEvents()
    module('PlayerEvents', g_playerEvents=player_events)
    gui = module('gui')
    gui.__path__ = []
    gui.mods = module('gui.mods')
    gui.mods.__path__ = [MODS_DIR]
    return log, player_events
