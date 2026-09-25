#!/usr/bin/env python3
"""Remove expired sample routes from the currently served GitHub Pages tree."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "sample-site-lifecycle.json"
ROUTE_ID_RE = re.compile(r"^r_[a-f0-9]{20}$")
ARTICLE_RE = re.compile(r"<article\b[^>]*>.*?</article>", re.IGNORECASE | re.DOTALL)
ACTIVE_ROUTE_RE = re.compile(r'href="[^"]*/r/r_[a-f0-9]{20}/', re.IGNORECASE)
EXPIRED_PAGE = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive"><title>Muestras caducadas · Web By Elie</title>
<style>body{margin:0;background:#f7f4ed;color:#253c39;font:16px/1.6 system-ui}main{max-width:720px;margin:12vh auto;padding:24px}h1{font:normal clamp(32px,6vw,48px)/1.1 Georgia,serif}</style>
</head><body><main><p>WEB BY ELIE · CARTAS DE MUESTRA</p><h1>Estas muestras han caducado</h1><p>La carta final del restaurante, si está publicada, conserva su propio enlace.</p></main></body></html>
"""


def utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def safe_route(root: Path, resto_id: str) -> Path:
    if not ROUTE_ID_RE.fullmatch(resto_id):
        raise ValueError(f"invalid restoID in expiry manifest: {resto_id!r}")
    base = (root / "r").resolve()
    route = root / "r" / resto_id
    if route.resolve().parent != base:
        raise ValueError(f"route path escapes sample root: {resto_id!r}")
    if route.is_symlink():
        raise ValueError(f"refusing symlink sample route: {resto_id!r}")
    return route


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def clean_due(
    root: Path,
    manifest_path: Path,
    now: datetime,
    apply: bool,
) -> list[dict[str, Any]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    due = [
        sample for sample in manifest.get("samples", [])
        if sample.get("status") == "active" and utc(sample["expires_at"]) <= now
    ]
    if not due:
        print("no expired GitHub Pages sample routes")
        return []
    if not apply:
        for sample in due:
            print(f"would remove {sample['restoID']} at {sample['expires_at']}")
        return []

    removed: list[dict[str, Any]] = []
    for sample in due:
        route = safe_route(root, sample["restoID"])
        existed = route.exists()
        if existed:
            shutil.rmtree(route)
        sample["status"] = "expired"
        sample["cleanup_completed_at"] = now.isoformat().replace("+00:00", "Z")
        removed.append({"restoID": sample["restoID"], "route_removed": existed})

    indexes: dict[str, list[str]] = {}
    for sample in due:
        index = sample.get("overview_path")
        if index:
            indexes.setdefault(index, []).append(sample["restoID"])

    changed_indexes: list[str] = []
    for relative in sorted(indexes):
        if relative not in {"round-2/index.html", "round3/index.html"}:
            raise ValueError(f"unapproved overview path in expiry manifest: {relative!r}")
        index = (root / relative).resolve()
        if root.resolve() not in index.parents:
            raise ValueError(f"overview path escapes sample root: {relative!r}")
        if not index.is_file():
            continue
        content = index.read_text(encoding="utf-8")
        expired_ids = set(indexes[relative])
        updated = ARTICLE_RE.sub(
            lambda match: ""
            if any(f"/r/{resto_id}/" in match.group(0) for resto_id in expired_ids)
            else match.group(0),
            content,
        )
        if not ACTIVE_ROUTE_RE.search(updated):
            updated = EXPIRED_PAGE
        if updated != content:
            index.write_text(updated, encoding="utf-8")
            changed_indexes.append(relative)

    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    receipt = {
        "cleanup_completed_at": now.isoformat().replace("+00:00", "Z"),
        "removed_sites": removed,
        "updated_indexes": changed_indexes,
        "scope": "current GitHub Pages tree only",
        "git_history_rewritten": False,
    }
    receipt_path = root / "cleanup-receipts" / f"{stamp}.json"
    write_json(receipt_path, receipt)
    write_json(manifest_path, manifest)
    print(f"expired {len(removed)} GitHub Pages sample routes")
    return [receipt]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--now", help="UTC test time; dry-run only")
    parser.add_argument("--apply", action="store_true", help="remove due routes from the current tree")
    args = parser.parse_args()
    if args.apply and args.now:
        parser.error("--now is test-only and cannot be combined with --apply")
    now = utc(args.now) if args.now else datetime.now(timezone.utc)
    try:
        clean_due(args.root, args.manifest, now, args.apply)
    except (KeyError, ValueError, OSError, json.JSONDecodeError) as error:
        print(f"cleanup stopped safely: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
