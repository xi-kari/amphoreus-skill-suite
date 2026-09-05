#!/usr/bin/env python3
"""Resolve an installed Amphoreus sticker for the actual speaking character."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ASSETS = Path(__file__).resolve().parents[1] / "assets/stickers"


def image_result(assets: Path, speaker: dict, item: dict) -> dict | None:
    path = (assets / item["file"]).resolve()
    if not path.is_relative_to(assets.resolve()) or not path.is_file():
        return None
    label = speaker["name"]
    if item["label"] != label:
        label += "·" + item["label"]
    label = label.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
    destination = path.as_posix().replace("<", "%3C").replace(">", "%3E").replace("\n", "%0A").replace("\r", "%0D")
    return {
        "status": "ok", "reason": None, "speaker": speaker["key"],
        "key": item["key"], "path": path.as_posix(),
        "markdown": f"![{label}](<{destination}>)",
    }


def select(catalog: dict, assets: Path, name: str, *, key: str | None = None,
           mood: str | None = None, listing: bool = False) -> dict:
    speaker = next((row for row in catalog["speakers"] if name.strip().casefold() in
                    {value.casefold() for value in [row["key"], row["name"], *row["aliases"]]}), None)
    empty = {"status": "error", "reason": "unknown_speaker", "speaker": name,
             "key": None, "path": None, "markdown": ""}
    if not speaker:
        return empty
    empty["speaker"] = speaker["key"]
    own = [row for row in catalog["items"] if row["speaker"] == speaker["key"]]
    if listing:
        images = [result for row in own if (result := image_result(assets, speaker, row))]
        return {"status": "ok", "speaker": speaker["key"], "items": images}
    reason = None
    selected = None
    if key is not None:
        selected = next((row for row in catalog["items"] if row["key"] == key), None)
        if not selected:
            return {**empty, "reason": "unknown_key"}
        if selected["speaker"] != speaker["key"]:
            return {**empty, "reason": "speaker_mismatch"}
    elif mood is not None:
        selected = next((row for row in own if row["label"] == mood.strip()), None)
        if selected is None:
            reason = "unknown_mood"
    if selected:
        result = image_result(assets, speaker, selected)
        if result:
            return result
        reason = "missing_file"
    default = next((row for row in own if row["key"] == speaker["default"]), None)
    result = image_result(assets, speaker, default) if default else None
    if result:
        if reason:
            result.update(status="fallback", reason=reason)
        return result
    return {**empty, "status": "omitted", "reason": "missing_default"}


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--speaker", required=True, help="Actual speaker key or Chinese name")
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--key", help="Exact sticker key belonging to this speaker")
    choice.add_argument("--mood", help="Exact label from this speaker's catalog")
    choice.add_argument("--list", dest="listing", action="store_true", help="List this speaker's available images")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()
    try:
        catalog = json.loads((ASSETS / "manifest.json").read_text(encoding="utf-8"))
        if catalog.get("version") != 1:
            raise ValueError("Unsupported catalog version")
        result = select(catalog, ASSETS, args.speaker, key=args.key, mood=args.mood, listing=args.listing)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        result = {"status": "omitted", "reason": "catalog_unavailable", "speaker": args.speaker,
                  "key": None, "path": None, "markdown": ""}
        print(f"Sticker catalog unavailable: {exc}", file=sys.stderr)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False))
    elif "items" in result:
        for item in result["items"]:
            print(f"{item['key']}\t{item['markdown']}")
    elif result["markdown"]:
        print(result["markdown"])
    if result["status"] == "error":
        if args.format != "json":
            print(f"Sticker selection rejected: {result['reason']}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
