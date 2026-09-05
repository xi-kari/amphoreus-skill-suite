#!/usr/bin/env python3
"""Package the canonical sticker catalog and display files with the router skill."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = Path("skills/amphoreus")
ASSETS = SKILL / "assets/stickers"
INDEX = SKILL / "references/stickers.md"


def make_catalog(source: dict) -> dict:
    heroes = {row["key"]: row["name"] for row in source["heroes"]}
    bases = {row["key"]: row for row in source["items"] if row["kind"] == "base"}
    base_names = {row["label"]: key for key, row in bases.items()}
    speakers = {}
    items = []
    seen = set()
    for row in source["items"]:
        key, owner, note = row["key"], row["owner"], row.get("note", "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", key) or key in seen:
            raise ValueError(f"Invalid or duplicate sticker key: {key}")
        seen.add(key)
        if owner not in heroes:
            raise ValueError(f"Unknown owner for {key}: {owner}")
        if row["kind"] == "base":
            speaker, name = key, row["label"]
        elif row["kind"] == "companion":
            if key.startswith("chimera-"):
                speaker = key
            elif key.startswith("cyrene-young-"):
                speaker = "cyrene-young"
            elif key.startswith("mimi-"):
                speaker = "mimi"
            else:
                raise ValueError(f"Unmapped companion: {key}")
            if not note:
                raise ValueError(f"Missing companion identity: {key}")
            name = note
        elif row["kind"] == "mood":
            if note:
                if note not in base_names or bases[base_names[note]]["owner"] != owner:
                    raise ValueError(f"Unmapped speaker for {key}: {note}")
                speaker, name = base_names[note], note
            else:
                speaker, name = owner, heroes[owner]
        else:
            raise ValueError(f"Unknown sticker kind: {row['kind']}")
        if speaker not in speakers:
            default = speaker if speaker in bases else key
            if speaker == "mimi":
                default = "mimi-hug"
            speakers[speaker] = {
                "key": speaker, "name": name, "aliases": [], "default": default,
            }
        elif speakers[speaker]["name"] != name:
            raise ValueError(f"Conflicting speaker identity: {speaker}")
        items.append({
            "key": key, "speaker": speaker, "label": row["label"],
            "file": f"{key}.webp",
        })
    aliases = {
        "march7th-evernight": ["evernight"],
        "terrae": ["丹恒•腾荒", "丹恒·腾荒", "丹恒腾荒", "dan-heng"],
        "trailblazer-stelle": ["星", "开拓者女", "stelle"],
        "trailblazer-caelus": ["穹", "开拓者男", "caelus"],
    }
    for speaker, names in aliases.items():
        if speaker in speakers:
            speakers[speaker]["aliases"] = names
    by_key = {row["key"]: row for row in items}
    for speaker in speakers.values():
        default = by_key.get(speaker["default"])
        if not default or default["speaker"] != speaker["key"]:
            raise ValueError(f"Missing own default for {speaker['key']}")
    if source.get("count", len(items)) != len(items):
        raise ValueError("Source count does not match its items")
    return {"version": 1, "speakers": list(speakers.values()), "items": items}


def make_index(catalog: dict) -> str:
    lines = [
        "# 表情索引", "",
        "按当前实际发言者选图；所属角色组不代表图中人物。三月七与长夜月、缇宝与缇安／缇宁、昔涟与小昔涟分别选择，伙伴也有独立身份。是否显示及数量服从 [共享合同](common.md#对话表情)。", "",
        "缇宝卡的三声部教学标题表示受众层级，未让姐妹分别出场时，整卡收尾使用缇宝形象；若缇安或缇宁被明确点名出场、冠名发言，紧随该发言的图片只用她本人，不凭教学标题切换人物。", "",
        "从当前已加载的 `amphoreus` 目录运行 `scripts/stickers.py`；角色卡位于其同级目录。把脚本返回的完整 Markdown 放入回复，可获得经过文件存在检查的绝对路径。", "",
        "```text",
        'python "<amphoreus目录>/scripts/stickers.py" --speaker 昔涟 --mood 收到',
        'python "<amphoreus目录>/scripts/stickers.py" --speaker 长夜月 --key march7th-evernight-warning',
        'python "<amphoreus目录>/scripts/stickers.py" --speaker 缇安 --list --format json',
        "```", "",
        "`--speaker` 接受下列英文键、中文名或列出的别名。`--key` 必须是本人的精确键；`--mood` 按本人标签精确匹配；两者与 `--list` 互斥。不指定选择参数时用本人默认图，情绪无匹配或图片缺失时尝试本人默认图，默认图也缺失则省略。伙伴没有基础头像时使用表中本人的代表图。", "",
        "默认格式为 `markdown`；`json` 返回 `status`、`reason`、`speaker`、`key`、`path`、`markdown`。成功为 `ok`，回退为 `fallback`，资源缺失为 `omitted`，输入错误为 `error`；输入错误退出码为 2，其余为 0。`--list` 返回本人实际存在的图片列表，不自动展示整组图片。", "",
        "无法运行脚本时，可从本表精确键定位当前 `amphoreus/assets/stickers/<key>.webp`，用可用的文件工具确认存在并取得绝对路径，再写 `![角色·表情](<绝对路径>)`；无法核实就省略。客户端不支持本地图片时只保留文字，不使用开发机路径或猜测远程地址。", "",
    ]
    lines.extend(["| 实际发言者 | 英文键／别名 | 默认图精确键 | 其他表情：精确键 |", "|---|---|---|---|"])
    for speaker in catalog["speakers"]:
        names = "／".join([speaker["key"], *speaker["aliases"]])
        choices = "；".join(
            f"{row['label']}：{row['key']}" for row in catalog["items"]
            if row["speaker"] == speaker["key"] and row["key"] != speaker["default"]
        ) or "—"
        lines.append(f"| {speaker['name']} | {names} | {speaker['default']} | {choices} |")
    lines.append("")
    return "\n".join(lines)


def expected_files(root: Path) -> tuple[dict[Path, bytes], dict]:
    source_dir = root / "assets/stickers"
    source = json.loads((source_dir / "manifest.json").read_text(encoding="utf-8"))
    catalog = make_catalog(source)
    outputs = {
        ASSETS / "manifest.json": (json.dumps(catalog, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        INDEX: make_index(catalog).encode("utf-8"),
    }
    for row in catalog["items"]:
        outputs[ASSETS / row["file"]] = (source_dir / "w" / row["file"]).read_bytes()
    return outputs, catalog


def package(root: Path, check: bool = False) -> list[str]:
    root = root.resolve()
    outputs, _ = expected_files(root)
    differences = []
    for relative, data in outputs.items():
        target = root / relative
        if not target.is_file() or target.read_bytes() != data:
            differences.append(str(relative))
            if not check:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
    web = root / ASSETS
    for target in web.glob("*.webp"):
        if target.relative_to(root) not in outputs:
            differences.append(str(target.relative_to(root)))
            if not check:
                if target.resolve().parent != web.resolve():
                    raise ValueError(f"Refusing to remove a file outside {web}")
                target.unlink()
    return differences


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check packaged bytes and index without writing")
    args = parser.parse_args()
    try:
        differences = package(ROOT, check=args.check)
        if args.check and differences:
            print("Sticker package differs:\n" + "\n".join(differences))
            return 1
        catalog = json.loads((ROOT / ASSETS / "manifest.json").read_text(encoding="utf-8"))
        print(f"Sticker package {'verified' if args.check else 'ready'}: {len(catalog['items'])} images, {len(catalog['speakers'])} speakers")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Sticker package error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
