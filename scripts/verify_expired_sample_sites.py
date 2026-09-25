#!/usr/bin/env python3
"""Verify that expired sample URLs no longer respond with a live page."""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
import expire_sample_sites

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "sample-site-lifecycle.json"
URL_PREFIX = "https://ec92009.github.io/menu-previews/r/"


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def verify_route_gone(
    url: str,
    *,
    open_url: Callable[..., Any] = urllib.request.urlopen,
    attempts: int = 12,
    interval_seconds: int = 5,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, int]:
    last_status: int | None = None
    for attempt in range(attempts):
        request = urllib.request.Request(
            url,
            method="GET",
            headers={"Accept": "text/html", "Range": "bytes=0-0"},
        )
        try:
            with open_url(request, timeout=15) as response:
                last_status = response.status
                if last_status in {404, 410}:
                    return {"http_status": last_status, "attempts": attempt + 1}
        except urllib.error.HTTPError as error:
            last_status = error.code
            error.close()
            if last_status in {404, 410}:
                return {"http_status": last_status, "attempts": attempt + 1}
            if last_status not in {429, 500, 502, 503, 504}:
                raise RuntimeError(f"sample URL verification returned HTTP {last_status}") from error
        except (TimeoutError, OSError) as error:
            if attempt == attempts - 1:
                raise RuntimeError("sample URL verification could not complete") from error
        if attempt < attempts - 1:
            sleep(interval_seconds)
    raise RuntimeError(f"sample URL still responds with HTTP {last_status}")


def verify_expired(
    manifest_path: Path,
    now: datetime,
    checker: Callable[[str], dict[str, int]] = verify_route_gone,
    root: Path = ROOT,
) -> tuple[int, dict[str, Any] | None]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    pending = [
        row for row in manifest.get("samples", [])
        if row.get("status") == "expired" and not row.get("public_url_verified_at")
    ]
    if not pending:
        print("no expired sample URLs pending verification")
        return 0, None

    urls: dict[str, str] = {}
    for row in pending:
        route_id = row["restoID"]
        expire_sample_sites.safe_route(root, route_id)
        urls[route_id] = f"{URL_PREFIX}{route_id}/"

    verified: list[dict[str, Any]] = []
    unresolved: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        jobs = {pool.submit(checker, url): route_id for route_id, url in urls.items()}
        for future in as_completed(jobs):
            route_id = jobs[future]
            try:
                result = future.result()
                row = next(item for item in pending if item["restoID"] == route_id)
                verified_at = now.isoformat().replace("+00:00", "Z")
                row["public_url_verified_at"] = verified_at
                row["public_url_http_status"] = result["http_status"]
                verified.append({"restoID": route_id, "url": urls[route_id], **result})
            except Exception as error:  # retain the failure evidence and retry on the next scheduled run
                unresolved.append({"restoID": route_id, "error": str(error)})

    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    receipt = {
        "verification_attempted_at": now.isoformat().replace("+00:00", "Z"),
        "verified_removed": verified,
        "unresolved": unresolved,
        "scope": "public GitHub Pages routes only",
    }
    atomic_json(manifest_path, manifest)
    atomic_json(root / "cleanup-receipts" / f"verification-{stamp}.json", receipt)
    print(f"verified removed: {len(verified)}; unresolved: {len(unresolved)}")
    return (1 if unresolved else 0), receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--now", help="UTC test time; not used for network access")
    args = parser.parse_args()
    now = expire_sample_sites.utc(args.now) if args.now else datetime.now(timezone.utc)
    try:
        code, _receipt = verify_expired(args.manifest, now)
        return code
    except (KeyError, ValueError, OSError, json.JSONDecodeError) as error:
        print(f"verification stopped safely: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
