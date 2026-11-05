#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml>=6.0.3",
#     "rich>=15.0.0",
# ]
# ///

"""Validate every action in the repository (a top-level folder containing action.yaml).

Checks: required metadata, a README, third-party ``uses:`` pinned to a 40-character SHA with a ``# vX`` comment, and
any ``*_IMAGE`` value pinned as ``<image>:<tag>@sha256:<digest>``. Exits 1 on any problem.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml
from rich.console import Console

console = Console()
ROOT = Path(__file__).resolve().parents[1]
USES_RE = re.compile(r"^\s*(?:-\s+)?uses:\s*(?P<ref>\S+)(?P<rest>.*)$")
SHA_REF = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
IMAGE_RE = re.compile(r"^\s+\w*IMAGE:\s*(?P<value>\S+)\s*$")
IMAGE_PIN = re.compile(r"^[\w./-]+:[\w.-]+@sha256:[0-9a-f]{64}$")


def check(action_file: Path) -> list[str]:
    problems: list[str] = []
    folder = action_file.parent
    data = yaml.safe_load(action_file.read_text())
    for key in ("name", "description", "runs"):
        if not data.get(key):
            problems.append(f"missing '{key}'")
    if not (folder / "README.md").is_file():
        problems.append("missing README.md")
    for number, line in enumerate(action_file.read_text().splitlines(), start=1):
        uses = USES_RE.match(line)
        if uses and not uses["ref"].startswith(("./", "docker://")):
            if not SHA_REF.match(uses["ref"]) or not re.search(r"#\s*v\d", uses["rest"]):
                problems.append(f"line {number}: pin '{uses['ref']}' to a commit SHA with a '# vX.Y.Z' comment")
        image = IMAGE_RE.match(line)
        if image and not IMAGE_PIN.match(image["value"]):
            problems.append(f"line {number}: pin image '{image['value']}' as <image>:<tag>@sha256:<digest>")
    return problems


def main() -> None:
    actions = sorted(ROOT.glob("*/action.y*ml"))
    if not actions:
        console.print("[red]No actions found.[/]")
        sys.exit(1)
    failed = False
    for action in actions:
        problems = check(action)
        failed |= bool(problems)
        console.print(f"{'[red]FAIL[/]' if problems else '[green]ok[/]  '} {action.relative_to(ROOT)}")
        for problem in problems:
            console.print(f"       {problem}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
