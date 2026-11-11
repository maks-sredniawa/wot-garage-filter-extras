from debug_utils import LOG_CURRENT_EXCEPTION


def init():
    try:
        from gui.mods.maksforge_garage_filter_extras import config, garage
        settings = config.load()
        if settings['enabled']:
            garage.install(settings)
    except Exception:
        LOG_CURRENT_EXCEPTION()


def fini():
    try:
        from gui.mods.maksforge_garage_filter_extras import garage
        garage.uninstall()
    except Exception:
        LOG_CURRENT_EXCEPTION()
