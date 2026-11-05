#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "rich>=15.0.0",
# ]
# ///

"""Pin each action's runtime image to its latest stable release, by tag and digest.

Dependabot cannot see an image named in an ``env`` value of a composite action, so this script rewrites every
``*_IMAGE: public.ecr.aws/<alias>/<repo>:<tag>[@sha256:<digest>]`` line in ``*/action.yaml``. Only public.ecr.aws
images are supported: they allow anonymous reads, so no credentials are needed.

    update_image_pins.py           rewrite the pins
    update_image_pins.py --check   report drift and exit 1 without writing
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()
ROOT = Path(__file__).resolve().parents[1]
REGISTRY = "public.ecr.aws"
PIN_RE = re.compile(
    rf"^(?P<head>[ \t]+\w*IMAGE:[ \t]+)(?P<repo>{re.escape(REGISTRY)}/[\w./-]+):(?P<tag>[\w.-]+)"
    r"(?:@(?P<digest>sha256:[0-9a-f]{64}))?[ \t]*$",
    re.MULTILINE,
)
STABLE_TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
ACCEPT = (
    "application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json, "
    "application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json"
)


def _token(repository: str) -> str:
    query = urllib.parse.urlencode({"service": REGISTRY, "scope": f"repository:{repository}:pull", "t": time.time_ns()})
    with urllib.request.urlopen(f"https://{REGISTRY}/token/?{query}", timeout=30) as response:
        return json.load(response)["token"]


def _get(url: str, token: str, accept: str = "application/json"):
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": accept})
    return urllib.request.urlopen(request, timeout=30)


def latest_stable_tag(repository: str, token: str) -> str:
    """Highest vX.Y.Z tag; pre-releases and floating tags (v0, v0.47, latest) never match."""
    tags: list[str] = []
    url: str | None = f"https://{REGISTRY}/v2/{repository}/tags/list?n=1000"
    while url:
        with _get(url, token) as response:
            tags += json.load(response).get("tags") or []
            link = response.headers.get("Link", "")
        match = re.search(r"<([^>]+)>;\s*rel=\"next\"", link)
        url = urllib.parse.urljoin(f"https://{REGISTRY}", match.group(1)) if match else None
    stable = [tag for tag in tags if STABLE_TAG.match(tag)]
    if not stable:
        raise SystemExit(f"No stable vX.Y.Z tag found for {REGISTRY}/{repository}")
    return max(stable, key=lambda tag: tuple(int(part) for part in STABLE_TAG.match(tag).groups()))


def manifest_digest(repository: str, tag: str, token: str) -> str:
    with _get(f"https://{REGISTRY}/v2/{repository}/manifests/{tag}", token, ACCEPT) as response:
        return "sha256:" + hashlib.sha256(response.read()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="report drift, exit 1, write nothing")
    args = parser.parse_args()

    resolved: dict[str, tuple[str, str]] = {}
    rows: list[tuple[str, str, str, str]] = []
    for path in sorted(ROOT.glob("*/action.yaml")):
        text = path.read_text()

        def replace(match: re.Match[str], path: Path = path) -> str:
            repository = match["repo"].removeprefix(f"{REGISTRY}/")
            if repository not in resolved:
                token = _token(repository)
                tag = latest_stable_tag(repository, token)
                resolved[repository] = (tag, manifest_digest(repository, tag, token))
            tag, digest = resolved[repository]
            old = f"{match['tag']}@{(match['digest'] or 'none')[:19]}"
            rows.append((str(path.relative_to(ROOT)), repository, old, f"{tag}@{digest[:19]}"))
            return f"{match['head']}{match['repo']}:{tag}@{digest}"

        updated = PIN_RE.sub(replace, text)
        if updated != text and not args.check:
            path.write_text(updated)

    changed = [row for row in rows if row[2] != row[3]]
    table = Table(title="Image pins")
    for column in ("File", "Image", "Current", "Latest"):
        table.add_column(column)
    for row in rows:
        table.add_row(*row, style=None if row in changed else "dim")
    console.print(table)
    if not rows:
        console.print("[yellow]No image pins found.[/]")
    if changed and args.check:
        console.print("[red]Image pins are out of date.[/]")
        sys.exit(1)
    console.print(f"[green]{len(changed)} pin(s) {'to update' if args.check else 'updated'}.[/]")


if __name__ == "__main__":
    main()
