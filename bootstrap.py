#!/usr/bin/env python3
"""Turns the example mod into a new mod: renames its id, files and package, and swaps in the mod README."""
import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
SELF = Path(__file__).name
SLUG = "example_mod"
NAME = "Example Mod"
DESCRIPTION = "Writes a line to game.log when a battle loads."


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def tracked_files() -> list[Path]:
    return [ROOT / name for name in git("ls-files", "-z").split("\0") if name and name != SELF]


def lowercase_description(description: str) -> str:
    return description[0].lower() + description[1:]


def replacements(slug: str, name: str, description: str, xml: bool) -> list[tuple[str, str]]:
    text = escape if xml else str
    return [
        (DESCRIPTION, text(description)),
        (lowercase_description(DESCRIPTION), text(lowercase_description(description))),
        (SLUG, slug),
        (SLUG.replace("_", "-"), slug.replace("_", "-")),
        (NAME, text(name)),
    ]


def rewritten(path: Path, slug: str, name: str, description: str) -> Optional[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    new = text
    for old, replacement in replacements(slug, name, description, xml=path.suffix == ".xml"):
        new = new.replace(old, replacement)
    return new if new != text else None


def renamed(path: Path, slug: str) -> Path:
    return ROOT / str(path.relative_to(ROOT)).replace(SLUG, slug)


def remove_empty_dirs(sources: list[Path]) -> None:
    dirs = {parent for source in sources for parent in source.parents if ROOT in parent.parents}
    for path in sorted(dirs, key=lambda p: len(p.parts), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True, help="snake_case id, e.g. ping_distance. The mod id becomes maksforge.<slug>.")
    parser.add_argument("--name", required=True, help='Name shown in the README and release titles, e.g. "Ping Distance".')
    parser.add_argument("--description", required=True, help="One sentence for meta.xml and the README, ending with a full stop.")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Print what would change and stop.")
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z][a-z0-9_]*", args.slug):
        sys.exit("--slug must be lowercase letters, digits and underscores, starting with a letter")
    if args.slug == SLUG:
        sys.exit(f"--slug must differ from the template's {SLUG}")
    if not args.name.strip() or not args.description.strip():
        sys.exit("--name and --description must not be empty")
    if not (ROOT / "mod-README.md").is_file():
        sys.exit("mod-README.md is missing: this repository has already been bootstrapped")
    if git("status", "--porcelain", "--untracked-files=no"):
        sys.exit("commit or discard the changes to tracked files first")

    files = tracked_files()
    rewrites = [
        (path, text) for path in files
        if path != ROOT / "README.md" and (text := rewritten(path, args.slug, args.name, args.description))
    ]
    moves = [(path, renamed(path, args.slug)) for path in files if SLUG in str(path.relative_to(ROOT))]
    moves.append((ROOT / "mod-README.md", ROOT / "README.md"))
    taken = [target for _, target in moves[:-1] if target.exists()]
    if taken:
        sys.exit("already exists: " + ", ".join(str(target.relative_to(ROOT)) for target in taken))

    for path, _ in rewrites:
        print(f"rewrite {path.relative_to(ROOT)}")
    for source, target in moves:
        print(f"move    {source.relative_to(ROOT)} -> {target.relative_to(ROOT)}")
    print(f"remove  {SELF}")
    if args.dry_run:
        return 0

    for path, text in rewrites:
        path.write_text(text, encoding="utf-8")
    for source, target in moves:
        target.parent.mkdir(parents=True, exist_ok=True)
        git("mv", "-f", str(source), str(target))
    remove_empty_dirs([source for source, _ in moves])
    git("rm", "-q", SELF)
    print("\nDone. Next: python2.7 -m unittest discover -s tests && ./build.sh, then commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
