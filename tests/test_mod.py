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

CONFIG_PATH = os.path.join('mods', 'configs', 'maksforge.example_mod', 'config.json')


class ModTest(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        self.tmp = tempfile.mkdtemp()
        os.chdir(self.tmp)
        self.log, self.events = game_stubs.install()
        self.mod = importlib.import_module('gui.mods.mod_maksforge_example_mod')

    def tearDown(self):
        self.mod.fini()
        os.chdir(self.cwd)
        shutil.rmtree(self.tmp)

    def write_config(self, settings):
        os.makedirs(os.path.dirname(CONFIG_PATH))
        with open(CONFIG_PATH, 'w') as f:
            json.dump(settings, f)

    def test_first_start_writes_default_config(self):
        self.mod.init()
        with open(CONFIG_PATH) as f:
            self.assertEqual(json.load(f), {'enabled': True})

    def test_logs_when_battle_loads(self):
        self.mod.init()
        self.events.onAvatarReady()
        self.assertEqual(self.log.notes, ['[maksforge.example_mod] battle loaded'])
        self.assertEqual(self.log.exceptions, 0)

    def test_fini_unsubscribes(self):
        self.mod.init()
        self.mod.fini()
        self.assertEqual(self.events.onAvatarReady.handlers, [])

    def test_disabled_in_config_does_nothing(self):
        self.write_config({'enabled': False})
        self.mod.init()
        self.assertEqual(self.events.onAvatarReady.handlers, [])

    def test_broken_config_falls_back_to_defaults(self):
        os.makedirs(os.path.dirname(CONFIG_PATH))
        with open(CONFIG_PATH, 'w') as f:
            f.write('{not json')
        self.mod.init()
        self.assertEqual(len(self.events.onAvatarReady.handlers), 1)
        self.assertEqual(self.log.exceptions, 1)

    def test_unknown_config_keys_are_ignored(self):
        self.write_config({'enabled': True, 'typo': 1})
        config = importlib.import_module('gui.mods.maksforge_example_mod.config')
        self.assertEqual(config.load(), {'enabled': True})


if __name__ == '__main__':
    unittest.main()
