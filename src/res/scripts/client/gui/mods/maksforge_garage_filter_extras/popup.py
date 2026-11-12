import weakref

from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR

LOG_PREFIX = '[maksforge.garage_filter_extras]'
LAYOUT_PATH = ('mods', 'maksforge_garage_filter_extras', 'views', 'FilterToggleView')

_settings = {}
_on_change = []
_views = weakref.WeakSet()


def install(settings, on_change):
    try:
        import openwg_gameface
    except ImportError:
        return False
    layout_id = _layout_id()
    if layout_id < 0:
        LOG_ERROR(LOG_PREFIX, 'the game did not register the filter popup toggle, it stays off')
        return False
    from gui.mods.maksforge_garage_filter_extras import popup_view
    from gui.shared.system_factory import registerDynamicRandomHangarPresenters
    _settings.clear()
    _settings.update(settings)
    del _on_change[:]
    _on_change.append(on_change)
    registerDynamicRandomHangarPresenters(layout_id, lambda: popup_view.FilterToggleView(layout_id))
    return True


def show(settings):
    _settings.clear()
    _settings.update(settings)
    for view in list(_views):
        try:
            view.show(dict(_settings))
        except Exception:
            LOG_CURRENT_EXCEPTION()


def attach(view):
    _views.add(view)
    view.show(dict(_settings))


def detach(view):
    _views.discard(view)


def toggle_non_premium():
    if _on_change:
        _on_change[0]({'onlyNonPremium': not _settings.get('onlyNonPremium')})


def _layout_id():
    from gui.impl.gen import R
    node = getattr(R, LAYOUT_PATH[0], None)
    for key in LAYOUT_PATH[1:]:
        if node is None:
            return -1
        node = node.dyn(key)
    return node() if node is not None else -1
