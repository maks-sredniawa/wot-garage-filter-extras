"""Loads the mod against stubbed game modules (Python 2.7 or 3)."""
import importlib
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import game_stubs
from game_stubs import RandomHangar, SelectVehicle, Vehicle, VehiclesFilterComponent

CONFIG_PATH = os.path.join('mods', 'configs', 'maksforge.garage_filter_extras', 'config.json')
LINKAGE = 'maksforge.garage_filter_extras'

OWN = Vehicle(1)
RENTED = Vehicle(2, isRented=True)
PREMIUM = Vehicle(3, isPremium=True)
RENTED_PREMIUM = Vehicle(4, isRented=True, isPremium=True)
WOT_PLUS = Vehicle(5, isRented=True, isPremium=True, isWotPlus=True)
CLAN_WARS = Vehicle(6, isRented=True, isOnlyForClanWarsBattles=True)
SHOP_PREMIUM = Vehicle(7, isPremium=True, inInventory=False)
ALL = (OWN, RENTED, PREMIUM, RENTED_PREMIUM, WOT_PLUS, CLAN_WARS, SHOP_PREMIUM)


class ModTest(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        self.tmp = tempfile.mkdtemp()
        os.chdir(self.tmp)
        self.log, self.cache = game_stubs.install()
        self.cache.items.add(*ALL)
        self.mod = importlib.import_module('gui.mods.mod_maksforge_garage_filter_extras')
        self.garage = importlib.import_module('gui.mods.maksforge_garage_filter_extras.garage')

    def tearDown(self):
        self.mod.fini()
        os.chdir(self.cwd)
        shutil.rmtree(self.tmp)

    def write_config(self, settings):
        if not os.path.isdir(os.path.dirname(CONFIG_PATH)):
            os.makedirs(os.path.dirname(CONFIG_PATH))
        with open(CONFIG_PATH, 'w') as f:
            json.dump(settings, f)

    def open_garage(self):
        hangar = RandomHangar()
        hangar._onLoading()
        return hangar.filters

    def shown(self, component):
        return sorted(component.vehicles)

    def test_first_start_writes_default_config(self):
        self.mod.init()
        with open(CONFIG_PATH) as f:
            self.assertEqual(json.load(f), {'enabled': True, 'hideRented': True, 'onlyNonPremium': False})

    def test_hides_rented_tanks_by_default(self):
        self.mod.init()
        every, inventory = self.open_garage()
        self.assertEqual(self.shown(every), [1, 3, 7])
        self.assertEqual(self.shown(inventory), [1, 3])
        self.assertEqual(self.log.exceptions, 0)

    def test_hides_wot_plus_and_clan_wars_rentals_the_game_always_shows(self):
        self.mod.init()
        every, _ = self.open_garage()
        self.assertNotIn(WOT_PLUS.intCD, every.vehicles)
        self.assertNotIn(CLAN_WARS.intCD, every.vehicles)

    def test_only_non_premium(self):
        self.write_config({'hideRented': False, 'onlyNonPremium': True})
        self.mod.init()
        every, inventory = self.open_garage()
        self.assertEqual(self.shown(every), [1, 2, 6])
        self.assertEqual(self.shown(inventory), [1, 2, 6])

    def test_both_filters(self):
        self.write_config({'hideRented': True, 'onlyNonPremium': True})
        self.mod.init()
        every, _ = self.open_garage()
        self.assertEqual(self.shown(every), [1])

    def test_keeps_the_games_collection_type(self):
        self.mod.init()
        every, _ = self.open_garage()
        self.assertIsInstance(every.vehicles, game_stubs.ItemsCollection)

    def test_leaves_other_screens_alone(self):
        self.mod.init()
        self.assertEqual(sorted(SelectVehicle().filter.vehicles), [1, 2, 3, 4, 5, 6, 7])

    def test_new_rental_stays_hidden_after_a_resync(self):
        self.mod.init()
        every, _ = self.open_garage()
        removed = []
        every.onDiff += removed.append
        self.cache.items.add(Vehicle(8, isRented=True))
        self.cache.onSyncCompleted({8})
        self.assertNotIn(8, every.vehicles)
        self.assertEqual(removed, [{8}])

    def test_apply_refreshes_an_open_garage(self):
        self.mod.init()
        every, _ = self.open_garage()
        diffs = []
        every.onDiff += diffs.append
        self.garage.apply({'hideRented': False, 'onlyNonPremium': False})
        self.assertEqual(self.shown(every), [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(diffs, [{2, 4, 5, 6}])

    def test_disabled_in_config_changes_nothing(self):
        self.write_config({'enabled': False})
        self.mod.init()
        every, _ = self.open_garage()
        self.assertEqual(self.shown(every), [1, 2, 3, 4, 5, 6, 7])

    def test_fini_restores_the_game(self):
        original = VehiclesFilterComponent.__dict__[self.garage.CREATE_VEHICLES]
        self.mod.init()
        self.mod.fini()
        self.assertIs(VehiclesFilterComponent.__dict__[self.garage.CREATE_VEHICLES], original)
        every, _ = self.open_garage()
        self.assertEqual(self.shown(every), [1, 2, 3, 4, 5, 6, 7])

    def test_init_twice_patches_once(self):
        self.mod.init()
        self.mod.init()
        self.mod.fini()
        every, _ = self.open_garage()
        self.assertEqual(self.shown(every), [1, 2, 3, 4, 5, 6, 7])

    def test_stays_off_when_the_game_changed(self):
        name = self.garage.CREATE_VEHICLES
        original = VehiclesFilterComponent.__dict__[name]
        delattr(VehiclesFilterComponent, name)
        try:
            self.mod.init()
            self.assertEqual(len(self.log.errors), 1)
            self.assertEqual(self.log.exceptions, 0)
        finally:
            setattr(VehiclesFilterComponent, name, original)

    def test_broken_config_falls_back_to_defaults(self):
        os.makedirs(os.path.dirname(CONFIG_PATH))
        with open(CONFIG_PATH, 'w') as f:
            f.write('{not json')
        self.mod.init()
        every, _ = self.open_garage()
        self.assertNotIn(RENTED.intCD, every.vehicles)
        self.assertEqual(self.log.exceptions, 1)

    def test_unknown_config_keys_are_ignored(self):
        self.write_config({'enabled': True, 'typo': 1})
        config = importlib.import_module('gui.mods.maksforge_garage_filter_extras.config')
        self.assertEqual(config.load(), {'enabled': True, 'hideRented': True, 'onlyNonPremium': False})


class SettingsWindowTest(ModTest):

    def setUp(self):
        super(SettingsWindowTest, self).setUp()
        self.api = game_stubs.install_mods_settings_api()

    def saved_config(self):
        with open(CONFIG_PATH) as f:
            return json.load(f)

    def click(self, **changes):
        settings = dict(self.api.settings[LINKAGE])
        settings.update(changes)
        self.api.updateModSettings(LINKAGE, settings)

    def test_window_shows_the_config_values(self):
        self.write_config({'hideRented': False, 'onlyNonPremium': True})
        self.mod.init()
        template = self.api.templates[LINKAGE]
        self.assertEqual(template['modDisplayName'], 'Garage Filter Extras')
        self.assertEqual([(c['varName'], c['text'], c['value']) for c in template['column1']],
                         [('hideRented', 'Hide rented tanks', False), ('onlyNonPremium', 'Non-premium only', True)])

    def test_ticking_a_box_refreshes_the_garage_and_saves_the_config(self):
        self.mod.init()
        every, _ = self.open_garage()
        self.click(hideRented=False, onlyNonPremium=True)
        self.assertEqual(self.shown(every), [1, 2, 6])
        self.assertEqual(self.saved_config(), {'enabled': True, 'hideRented': False, 'onlyNonPremium': True})
        self.assertEqual(self.log.exceptions, 0)

    def test_turning_the_mod_off_in_the_window_shows_everything(self):
        self.mod.init()
        every, _ = self.open_garage()
        self.click(enabled=False)
        self.assertEqual(self.shown(every), [1, 2, 3, 4, 5, 6, 7])
        self.assertFalse(self.saved_config()['enabled'])

    def test_off_in_config_can_be_turned_back_on_in_the_window(self):
        self.write_config({'enabled': False})
        self.mod.init()
        every, _ = self.open_garage()
        self.assertEqual(self.shown(every), [1, 2, 3, 4, 5, 6, 7])
        self.click(enabled=True)
        self.assertEqual(self.shown(every), [1, 3, 7])

    def test_edited_config_wins_over_the_windows_old_values(self):
        self.mod.init()
        self.click(hideRented=False)
        self.mod.fini()
        self.write_config({'hideRented': True})
        self.mod.init()
        every, _ = self.open_garage()
        self.assertNotIn(RENTED.intCD, every.vehicles)
        self.assertTrue(self.api.settings[LINKAGE]['hideRented'])

    def test_other_mods_changes_are_ignored(self):
        self.mod.init()
        self.api.updateModSettings('someone.else', {'hideRented': False})
        self.assertTrue(self.saved_config()['hideRented'])

    def test_a_broken_window_still_leaves_the_filters_working(self):
        def broken(*args, **kwargs):
            raise RuntimeError('broken')
        self.api.setModTemplate = broken
        self.mod.init()
        every, _ = self.open_garage()
        self.assertNotIn(RENTED.intCD, every.vehicles)
        self.assertEqual(self.log.exceptions, 1)


if __name__ == '__main__':
    unittest.main()
