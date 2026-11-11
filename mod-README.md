# Example Mod

A World of Tanks mod that writes a line to game.log when a battle loads.

<!-- What it does in game, in two or three sentences. Say what it reads and what it changes, and that it reads no enemy information if that is true. -->

## Install

Copy `maksforge.example_mod_<version>.wotmod` into `World_of_Tanks/mods/<game version>/`. No other mods are needed.

## Settings

The mod writes `mods/configs/maksforge.example_mod/config.json` the first time the client starts:

| Key | Default | Meaning |
| --- | --- | --- |
| `enabled` | `true` | Turns the mod off without uninstalling it |

## Build

Needs `zip` and Python 2.7, the game's script runtime (`pyenv install 2.7.18`, or set `PYTHON27`).

```sh
./build.sh                                   # dist/maksforge.example_mod_<version>.wotmod
python2.7 -m unittest discover -s tests
```

## Release

Bump `<version>` in `src/meta.xml`, merge, then push a tag `v<version>`. CI builds the `.wotmod` and attaches it to a GitHub release.

## Support

Questions and bug reports: open an issue at https://github.com/maks-sredniawa/wot-example-mod/issues or write to wotmods.support@maksforge.com. For a bug, include your game version and `game.log` from the game folder.

This is a free fan-made mod by MaksForge. It is not affiliated with or endorsed by Wargaming.
