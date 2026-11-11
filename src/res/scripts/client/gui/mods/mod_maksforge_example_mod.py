from debug_utils import LOG_CURRENT_EXCEPTION, LOG_NOTE

LOG_PREFIX = '[maksforge.example_mod]'

_subscribed = False


def _on_avatar_ready():
    try:
        LOG_NOTE(LOG_PREFIX, 'battle loaded')
    except Exception:
        LOG_CURRENT_EXCEPTION()


def init():
    global _subscribed
    try:
        from gui.mods.maksforge_example_mod import config
        if not config.load()['enabled']:
            return
        from PlayerEvents import g_playerEvents
        g_playerEvents.onAvatarReady += _on_avatar_ready
        _subscribed = True
    except Exception:
        LOG_CURRENT_EXCEPTION()


def fini():
    global _subscribed
    if not _subscribed:
        return
    try:
        from PlayerEvents import g_playerEvents
        g_playerEvents.onAvatarReady -= _on_avatar_ready
    except Exception:
        LOG_CURRENT_EXCEPTION()
    _subscribed = False
