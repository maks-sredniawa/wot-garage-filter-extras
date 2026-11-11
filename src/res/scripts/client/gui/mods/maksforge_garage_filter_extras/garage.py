import weakref

from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR

from gui.mods.maksforge_garage_filter_extras.rules import is_hidden

LOG_PREFIX = '[maksforge.garage_filter_extras]'
CREATE_VEHICLES = '_VehiclesFilterComponent__createVehiclesDict'

_settings = {}
_components = weakref.WeakSet()
_originals = []


def install(settings):
    from gui.impl.lobby.hangar.base.vehicles_filter_component import VehiclesFilterComponent
    from gui.impl.lobby.hangar.random.random_hangar import RandomHangar

    if _originals:
        return
    if CREATE_VEHICLES not in VehiclesFilterComponent.__dict__ or '__init__' not in RandomHangar.__dict__:
        LOG_ERROR(LOG_PREFIX, 'the garage carousel changed in this game version, the mod stays off')
        return
    _settings.clear()
    _settings.update(settings)
    _patch(VehiclesFilterComponent, CREATE_VEHICLES, _hiding_create)
    _patch(RandomHangar, '__init__', lambda original: _registering_init(original, VehiclesFilterComponent))


def uninstall():
    while _originals:
        owner, name, original = _originals.pop()
        setattr(owner, name, original)
    _components.clear()


def apply(settings):
    _settings.clear()
    _settings.update(settings)
    for component in list(_components):
        try:
            component._setCriteria(component.criteria)
        except Exception:
            LOG_CURRENT_EXCEPTION()


def _patch(owner, name, wrap):
    original = owner.__dict__[name]
    _originals.append((owner, name, original))
    setattr(owner, name, wrap(original))


def _hiding_create(original):

    def create(self, *args, **kwargs):
        original(self, *args, **kwargs)
        if self not in _components:
            return
        try:
            vehicles = self._vehicles
            for intCD in [intCD for intCD, vehicle in vehicles.items() if is_hidden(vehicle, _settings)]:
                del vehicles[intCD]
        except Exception:
            LOG_CURRENT_EXCEPTION()

    return create


def _registering_init(original, component_type):

    def __init__(self, *args, **kwargs):
        original(self, *args, **kwargs)
        try:
            for value in vars(self).values():
                if isinstance(value, component_type):
                    _components.add(value)
        except Exception:
            LOG_CURRENT_EXCEPTION()

    return __init__
