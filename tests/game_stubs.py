"""Stand-ins for the game modules a mod imports, so tests run outside the client (Python 2.7 or 3)."""
import contextlib
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


class ModsSettingsApi(object):
    """Keeps the real API's rule: a template that differs from the stored one resets the saved settings to its values."""

    def __init__(self):
        self.templates = {}
        self.settings = {}
        self.callbacks = []

    def setModTemplate(self, linkage, template, callback, buttonHandler=None):
        if self.templates.get(linkage) != template:
            self.templates[linkage] = template
            values = dict((c['varName'], c['value']) for column in ('column1', 'column2') for c in template.get(column, []))
            values['enabled'] = template['enabled']
            self.settings[linkage] = values
        self.callbacks.append(callback)
        return dict(self.settings[linkage])

    def updateModSettings(self, linkage, newSettings):
        self.settings[linkage] = newSettings
        for callback in list(self.callbacks):
            callback(linkage, newSettings)


def create_checkbox(text, varName, value, tooltip=None, tooltipIcon=None, button=None):
    return {'type': 'CheckBox', 'text': text, 'varName': varName, 'value': value, 'tooltip': tooltip}


def install_mods_settings_api():
    api = ModsSettingsApi()
    templates = module('gui.modsSettingsApi.templates', createCheckbox=create_checkbox)
    module('gui.modsSettingsApi', g_modsSettingsApi=api, templates=templates)
    return api


class ViewModel(object):

    def __init__(self, properties=0, commands=0):
        self.properties = {}
        self.order = []
        self._initialize()

    def _initialize(self):
        pass

    def _addBoolProperty(self, name, value):
        self.order.append(name)
        self.properties[name] = value

    def _getBool(self, index):
        return self.properties[self.order[index]]

    def _setBool(self, index, value):
        self.properties[self.order[index]] = value

    def _addCommand(self, name):
        return Event()

    def _addViewModelProperty(self, name, model):
        self.properties[name] = model

    @contextlib.contextmanager
    def transaction(self):
        yield self


class ViewComponent(object):

    def __init__(self, layoutID=0, model=ViewModel):
        self.layoutID = layoutID
        self.__model = model()

    def getViewModel(self):
        return self.__model

    def load(self):
        """Stands in for the garage loading this child: the game calls _onLoading, then subscribes _getEvents."""
        self._onLoading()
        for event, handler in self._getEvents():
            event += handler

    def destroy(self):
        self._finalize()

    def _onLoading(self, *args, **kwargs):
        pass

    def _finalize(self):
        pass

    def _getEvents(self):
        return ()


class ResNode(object):
    """Mirrors R.<a>.dyn(<b>)...(): calling a node gives its resource id, or -1 when the game has none."""

    def __init__(self, ids, path):
        self.ids = ids
        self.path = path

    def dyn(self, key):
        return ResNode(self.ids, self.path + (key,))

    def __call__(self):
        return self.ids.get(self.path, -1)


FILTER_TOGGLE_LAYOUT = ('mods', 'maksforge_garage_filter_extras', 'views', 'FilterToggleView')
FILTER_TOGGLE_LAYOUT_ID = 90210


def gf_mod_inject(model, name, styles=None, scripts=None, modules=None):
    model._addViewModelProperty('ModInjectModel', {'name': name, 'styles': styles or [], 'scripts': scripts or [],
                                                   'modules': modules or []})


class ToolTipMgr(object):

    def __init__(self):
        self.shown = []
        self.hidden = 0
        self.released = []

    def onCreateComplexTooltip(self, tooltipId, state):
        self.shown.append((tooltipId, state))

    def hide(self):
        self.hidden += 1

    def onHideTooltip(self, tooltipId):
        self.released.append(tooltipId)


class App(object):

    def __init__(self):
        self.toolTipMgr = ToolTipMgr()

    def getToolTipMgr(self):
        return self.toolTipMgr


class AppLoader(object):

    def __init__(self):
        self.app = App()

    def getApp(self):
        return self.app


def make_tooltip(header=None, body=None, note=None, attention=None):
    return '{HEADER}%s{/HEADER}{BODY}%s{/BODY}' % (header, body)


def tooltip_manager():
    return sys.modules['helpers'].dependency.instance(AppLoader).getApp().getToolTipMgr()


def install_openwg_gameface():
    sys.modules['gui.impl.gen'].R.mods.ids[FILTER_TOGGLE_LAYOUT] = FILTER_TOGGLE_LAYOUT_ID
    module('openwg_gameface', gf_mod_inject=gf_mod_inject)


def module(name, **attrs):
    mod = types.ModuleType(name)
    mod.__path__ = []
    mod.__dict__.update(attrs)
    sys.modules[name] = mod
    return mod


def install():
    """Replaces the game modules with fresh stubs and forgets every loaded mod module."""
    global ITEMS_CACHE
    for name in [name for name in sys.modules
                 if name in ('gui', 'openwg_gameface', 'frameworks', 'helpers', 'skeletons')
                 or name.startswith(('gui.', 'frameworks.', 'helpers.', 'skeletons.'))]:
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
    module('frameworks')
    module('frameworks.wulf', ViewModel=ViewModel)
    module('gui.impl.pub')
    module('gui.impl.pub.view_component', ViewComponent=ViewComponent)
    resources = types.ModuleType('R')
    resources.mods = ResNode({}, ('mods',))
    module('gui.impl.gen', R=resources)
    presenters = {}
    module('gui.shared')
    module('gui.shared.system_factory', registerDynamicRandomHangarPresenters=presenters.__setitem__)
    module('gui.shared.utils')
    module('gui.shared.utils.functions', makeTooltip=make_tooltip)
    app_loader = AppLoader()
    module('skeletons')
    module('skeletons.gui')
    module('skeletons.gui.app_loader', IAppLoader=AppLoader)
    module('helpers', dependency=module('helpers.dependency', instance={AppLoader: app_loader}.__getitem__))
    return log, ITEMS_CACHE, presenters
