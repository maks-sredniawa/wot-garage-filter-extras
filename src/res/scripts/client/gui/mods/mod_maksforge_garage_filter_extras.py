from debug_utils import LOG_CURRENT_EXCEPTION

_settings = {}
_views = {'window': False, 'popup': False}


def init():
    try:
        from gui.mods.maksforge_garage_filter_extras import config, garage
        _settings.update(config.load())
        _views['window'] = _register_window()
        if _settings['enabled'] or _views['window']:
            garage.install(dict(_settings))
            _views['popup'] = _install_popup()
    except Exception:
        LOG_CURRENT_EXCEPTION()


def fini():
    try:
        from gui.mods.maksforge_garage_filter_extras import garage
        garage.uninstall()
    except Exception:
        LOG_CURRENT_EXCEPTION()
    _settings.clear()


def _register_window():
    try:
        from gui.mods.maksforge_garage_filter_extras import settings_window
        return settings_window.register(dict(_settings), _on_change)
    except Exception:
        LOG_CURRENT_EXCEPTION()
        return False


def _install_popup():
    try:
        from gui.mods.maksforge_garage_filter_extras import popup
        return popup.install(dict(_settings), _on_change)
    except Exception:
        LOG_CURRENT_EXCEPTION()
        return False


def _on_change(new_settings):
    if not _settings:
        return
    try:
        from gui.mods.maksforge_garage_filter_extras import config, garage
        if all(_settings.get(key) == value for key, value in new_settings.items()):
            return
        _settings.update(new_settings)
        config.save(dict(_settings))
        garage.apply(dict(_settings))
        _show_everywhere()
    except Exception:
        LOG_CURRENT_EXCEPTION()


def _show_everywhere():
    from gui.mods.maksforge_garage_filter_extras import popup, settings_window
    if _views['window']:
        settings_window.show(dict(_settings))
    if _views['popup']:
        popup.show(dict(_settings))
