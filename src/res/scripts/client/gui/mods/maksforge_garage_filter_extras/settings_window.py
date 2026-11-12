LINKAGE = 'maksforge.garage_filter_extras'
KEYS = ('enabled', 'hideRented', 'onlyNonPremium')

_shown = {}


def register(settings, on_change):
    try:
        from gui.modsSettingsApi import g_modsSettingsApi, templates
    except ImportError:
        return False

    def callback(linkage, new_settings):
        if linkage == LINKAGE:
            on_change(dict((key, new_settings[key]) for key in KEYS if key in new_settings))

    shown = g_modsSettingsApi.setModTemplate(LINKAGE, _template(templates, settings), callback) or {}
    _shown.clear()
    _shown.update(shown)
    # The API keeps its saved values while the template is unchanged, so a config edited back to the
    # template's values would otherwise lose to them.
    if any(shown.get(key) != settings[key] for key in KEYS):
        show(settings)
    return True


def show(settings):
    from gui.modsSettingsApi import g_modsSettingsApi
    _shown.update((key, settings[key]) for key in KEYS)
    g_modsSettingsApi.updateModSettings(LINKAGE, dict(_shown))


def _template(templates, settings):
    return {
        'modDisplayName': 'Garage Filter Extras',
        'enabled': settings['enabled'],
        'column1': [
            templates.createCheckbox(
                'Hide rented tanks', 'hideRented', settings['hideRented'],
                tooltip='{HEADER}Hide rented tanks{/HEADER}{BODY}Every rented tank leaves the garage carousel, '
                        'WoT Plus and Clan Wars tanks too.{/BODY}'),
            templates.createCheckbox(
                'Non-premium only', 'onlyNonPremium', settings['onlyNonPremium'],
                tooltip="{HEADER}Non-premium only{/HEADER}{BODY}Shows only tanks that are not premium. "
                        "The opposite of the game's Premium filter, so don't turn both on.{/BODY}"),
        ],
        'column2': [],
    }
