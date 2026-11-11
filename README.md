# Garage Filter Extras

A World of Tanks mod that adds the garage filters the game is missing: hide rented tanks, and show only tanks that are not premium.

- **Hide rented tanks:** trial and event rentals leave the garage carousel. WoT Plus and Clan Wars tanks stay, the same as the game's own rented filter treats them. The game's new garage has no toggle for rented tanks, so they always show without this mod.
- **Only tanks that are not premium:** the opposite of the game's own *Premium* filter. Don't turn both on at once, or the carousel is empty.

The mod changes only which of your own tanks the main garage's carousel lists. It reads nothing in battle. Other garages (Onslaught, Frontline, events) are left as the game made them.

## Install

Copy `maksforge.garage_filter_extras_<version>.wotmod` into `World_of_Tanks/mods/<game version>/`. No other mods are needed: rented tanks are hidden from the first start.

To switch the filters in the garage, also install [ModsSettingsAPI](https://github.com/IzeBerg/modssettingsapi) and the ModsList API it needs. Most modpacks include both.

## Settings

With ModsSettingsAPI installed, open its window from the garage and use the **Garage Filter Extras** checkboxes: **Hide rented tanks** and **Non-premium only**. The carousel changes as soon as you apply.

The settings live in `mods/configs/maksforge.garage_filter_extras/config.json`, which the mod writes the first time the client starts and the window keeps up to date:

| Key | Default | Meaning |
| --- | --- | --- |
| `enabled` | `true` | Turns the mod off without uninstalling it |
| `hideRented` | `true` | Hides rented tanks |
| `onlyNonPremium` | `false` | Shows only tanks that are not premium |

Restart the client after editing the file by hand. The file wins over what the window showed before.

## Build

Needs `zip` and Python 2.7, the game's script runtime (`pyenv install 2.7.18`, or set `PYTHON27`).

```sh
./build.sh                                   # dist/maksforge.garage_filter_extras_<version>.wotmod
python2.7 -m unittest discover -s tests
```

## Release

Bump `<version>` in `src/meta.xml`, merge, then push a tag `v<version>`. CI builds the `.wotmod` and attaches it to a GitHub release.

## Support

Questions and bug reports: open an issue at https://github.com/maks-sredniawa/wot-garage-filter-extras/issues or write to wotmods.support@maksforge.com. For a bug, include your game version and `game.log` from the game folder.

This is a free fan-made mod by MaksForge. It is not affiliated with or endorsed by Wargaming.
