def is_hidden(vehicle, settings):
    if settings.get('hideRented') and _is_rental(vehicle):
        return True
    if settings.get('onlyNonPremium') and getattr(vehicle, 'isPremium', False):
        return True
    return False


def _is_rental(vehicle):
    # Matches the game's own rented filter, which keeps WoT Plus and Clan Wars tanks.
    return (getattr(vehicle, 'isRented', False)
            and not getattr(vehicle, 'isWotPlus', False)
            and not getattr(vehicle, 'isOnlyForClanWarsBattles', False))
