# World of Tanks mod template

A template for a MaksForge World of Tanks mod: the build, tests, CI and release setup that `wot-ping-distance` and `wot-autoloader-timer` share, around an example mod small enough to delete in a minute.

The example mod writes `[maksforge.example_mod] battle loaded` to `game.log` when a battle loads, and keeps a JSON config with one `enabled` key. It builds and passes its tests as it is.

## Start

```sh
gh repo create maks-sredniawa/wot-<slug-with-hyphens> --template maks-sredniawa/wot-mod-template --public --clone
cd wot-<slug-with-hyphens>
python3 bootstrap.py --slug <slug> --name "<Name>" --description "<One sentence.>"
python2.7 -m unittest discover -s tests && ./build.sh
git commit -am "Start <Name> from the mod template"
gh repo edit --add-topic world-of-tanks-mod,world-of-tanks --homepage https://maksforge.com/#wot-mods \
  --description "Free World of Tanks mod that <does what>."
```

For example, `--slug ping_distance --name "Ping Distance"` in the repo `wot-ping-distance` gives the id `maksforge.ping_distance` and the entry point `mod_maksforge_ping_distance.py`. The repo name must be `wot-` plus the slug with hyphens, because the README's issue link is built from it. Use `--dry-run` to see the changes first.

`bootstrap.py` renames `example_mod` everywhere: the mod id, the files, the package, the config folder, the log prefix and the issue link. It replaces this README with `mod-README.md`, then deletes itself. The repository's topics, description and homepage aren't copied from a template, so the last command sets them. `world-of-tanks-mod` is the topic the org page's mod list filters on.

Then replace the example with the real mod:

1. Write the mod in `mod_maksforge_<slug>.py` and its package `maksforge_<slug>/`. A one-file mod can drop the package and `config.py`, as `wot-ping-distance` does.
2. Replace `tests/test_mod.py` with tests for the real behaviour. Add the game modules the mod imports to `tests/game_stubs.py`.
3. Fill in the README: what the mod does, its settings table, and any mods it needs (for example GUIFlash).
4. List it on the home page and the org overview, with its icon at `assets/icons/wot-<slug-with-hyphens>.webp`.

## What's in it

| Path | What it does |
| --- | --- |
| `src/meta.xml` | The mod's id, version, name and description. `build.sh` and the release job read the id and version from here. |
| `src/res/scripts/client/gui/mods/mod_maksforge_<slug>.py` | Entry point. The game imports every `gui/mods/mod_*.pyc` and calls `init()` at start and `fini()` at exit. |
| `src/res/scripts/client/gui/mods/maksforge_<slug>/config.py` | Loads `mods/configs/maksforge.<slug>/config.json`, writes the defaults on first start, ignores unknown keys, and falls back to the defaults if the file is broken. |
| `build.sh` | Compiles the scripts with Python 2.7 and packs `dist/maksforge.<slug>_<version>.wotmod`, uncompressed, which is the only way the game reads it. |
| `tests/game_stubs.py` | Fake `debug_utils`, `PlayerEvents` and `gui.mods` packages, so the mod imports as it does in the game. |
| `.github/workflows/build.yml` | Runs the tests and the build on Python 2.7 for pushes to `main`, `v*` tags and pull requests. A `v<version>` tag also publishes a GitHub release with the `.wotmod`, and fails if the tag and `meta.xml` disagree. |

## Conventions

- **Names:** files, package and log prefix carry `maksforge_<slug>` / `maksforge.<slug>`. Every installed mod shares the `gui.mods` package, so a bare name like `timer` can clash with someone else's mod.
- **Python 2.7:** the client runs Python 2.7. Write code that compiles there; the tests also run on Python 3.
- **Never crash the client:** wrap every game hook in `try`/`except Exception: LOG_CURRENT_EXCEPTION()`, so a broken mod logs and stays out of the way.
- **Release:** bump `<version>` in `src/meta.xml`, merge, push the tag `v<version>`.
- **Support:** issues on the repo, or `wotmods.support@maksforge.com`. Every README ends with the line saying the mod isn't affiliated with Wargaming.

## Licence

MIT, the same as the mods. A mod made from the template keeps it.
