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

    def clear(self):
        del self.handlers[:]


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


class Vehicle(object):

    def __init__(self, intCD, isRented=False, isPremium=False, isWotPlus=False, isOnlyForClanWarsBattles=False, inInventory=True):
        self.intCD = intCD
        self.isRented = isRented
        self.isPremium = isPremium
        self.isWotPlus = isWotPlus
        self.isOnlyForClanWarsBattles = isOnlyForClanWarsBattles
        self.inInventory = inInventory


class ItemsCollection(dict):
    pass


class Items(object):

    def __init__(self):
        self.vehicles = {}

    def add(self, *vehicles):
        for vehicle in vehicles:
            self.vehicles[vehicle.intCD] = vehicle

    def getVehicles(self, criteria):
        return ItemsCollection((intCD, v) for intCD, v in self.vehicles.items() if criteria(v))


class ItemsCache(object):

    def __init__(self):
        self.items = Items()
        self.onSyncCompleted = Event()


ITEMS_CACHE = ItemsCache()


class VehiclesFilterComponent(object):
    """Mirrors gui.impl.lobby.hangar.base.vehicles_filter_component, including its name-mangled private method."""

    def __init__(self, criteria):
        self.__criteria = criteria
        self.onDiff = Event()
        self._vehicles = {}

    @property
    def criteria(self):
        return self.__criteria

    @property
    def vehicles(self):
        return self._vehicles

    def initialize(self):
        self.__createVehiclesDict()
        ITEMS_CACHE.onSyncCompleted += self.__onCacheResync

    def destroy(self):
        ITEMS_CACHE.onSyncCompleted -= self.__onCacheResync
        self.onDiff.clear()

    def _setCriteria(self, criteria):
        oldVehiclesCDs = set(self._vehicles)
        self.__criteria = criteria
        self.__createVehiclesDict()
        self.onDiff(oldVehiclesCDs ^ set(self._vehicles))

    def __onCacheResync(self, changed):
        self.__createVehiclesDict()
        self.onDiff(changed)

    def __createVehiclesDict(self):
        self._vehicles = ITEMS_CACHE.items.getVehicles(self.__criteria)


def every_vehicle(vehicle):
    return True


def in_inventory(vehicle):
    return vehicle.inInventory


class RandomHangar(object):

    def __init__(self):
        self.__randomVehicleFilter = VehiclesFilterComponent(every_vehicle)
        self.__randomInvVehicleFilter = VehiclesFilterComponent(in_inventory)

    def _onLoading(self):
        self.__randomVehicleFilter.initialize()
        self.__randomInvVehicleFilter.initialize()

    @property
    def filters(self):
        return self.__randomVehicleFilter, self.__randomInvVehicleFilter


class SelectVehicle(object):

    def __init__(self):
        self.filter = VehiclesFilterComponent(every_vehicle)
        self.filter.initialize()


def module(name, **attrs):
    mod = types.ModuleType(name)
    mod.__path__ = []
    mod.__dict__.update(attrs)
    sys.modules[name] = mod
    return mod


def install():
    """Replaces the game modules with fresh stubs and forgets every loaded mod module."""
    global ITEMS_CACHE
    for name in [name for name in sys.modules if name == 'gui' or name.startswith('gui.')]:
        del sys.modules[name]
    log = Log()
    ITEMS_CACHE = ItemsCache()
    module('debug_utils', LOG_NOTE=log.note, LOG_ERROR=log.error, LOG_CURRENT_EXCEPTION=log.exception)
    gui = module('gui')
    gui.mods = module('gui.mods')
    gui.mods.__path__ = [MODS_DIR]
    for name in ('gui.impl', 'gui.impl.lobby', 'gui.impl.lobby.hangar', 'gui.impl.lobby.hangar.base', 'gui.impl.lobby.hangar.random'):
        module(name)
    module('gui.impl.lobby.hangar.base.vehicles_filter_component', VehiclesFilterComponent=VehiclesFilterComponent)
    module('gui.impl.lobby.hangar.random.random_hangar', RandomHangar=RandomHangar)
    return log, ITEMS_CACHE
