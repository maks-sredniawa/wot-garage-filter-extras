def is_hidden(vehicle, settings):
    if not settings.get('enabled', True):
        return False
    if settings.get('hideRented') and _is_rental(vehicle):
        return True
    if settings.get('onlyNonPremium') and getattr(vehicle, 'isPremium', False):
        return True
    return False


def _is_rental(vehicle):
    return getattr(vehicle, 'isRented', False)
