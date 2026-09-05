"""Check visible responses from real chat runs; semantic claims need human review."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


IMAGE = re.compile(r"!\[[^\]]*\]\((?:<[^>]+>|[^\n]+?)\)")
FORMAT_RULES = {
    "folded_metadata": r"<\s*/?\s*(?:details|summary)\b",
    "skill_filename": r"\b(?:SKILL|common|persona|relations)\.md\b",
    "receipt": r"[^\n|｜]{1,24}卡\s*[|｜]\s*读取\s*[:：]",
    "audit_field": r"(?:^|[\n|｜])\s*(?:[-*#>]\s*)?(?:\*\*)?(?:读取|档位|风格档|回执|审计台账|场级回执|工具调用|路由结果)\s*(?:\*\*)?\s*[:：|｜]",
    "routing_marker": r"(?:module_unavailable|mode_unavailable|PROCESS_RECORD\s*:|L[0-3]\s*[→→/｜|]\s*L[0-3])",
    "backstage_read": r"(?:我(?:会|先|已|刚|正在|将)|先|正在|需要先|接下来).{0,18}(?:读取|加载|查阅).{0,28}(?:技能|规则|规范|人设|角色设定|文件|表情索引)",
    "backstage_tool": r"(?:我(?:会|先|已|刚|正在|将)|先|正在|接下来).{0,18}(?:调用|运行|执行).{0,24}(?:工具|脚本|命令|选图)",
    "backstage_mode": r"(?:切换|进入|退出|启用|采用|遵循|按照).{0,12}(?:陪聊模式|工作模式|沙龙模式|输出契约|共享规范|深度门|标准档|静音档)",
}
UNPROMPTED_TERMS = ("台账", "审计", "档位", "回执", "深度门", "风格税", "升档", "降档")


def visible_text(event: dict) -> str | None:
    if event.get("type") == "reasoning":
        return None
    item = event.get("item", event)
    if isinstance(item, dict) and item.get("type") == "agent_message":
        if event.get("type") in ("item.started", "item.updated"):
            return None
        return item.get("text") if isinstance(item.get("text"), str) else None
    return None


def check_case(case: dict, directory: Path) -> dict:
    findings = []

    def add(rule: str, source: str, excerpt: str) -> None:
        findings.append({"rule": rule, "source": source, "excerpt": excerpt[:220]})

    final_path = directory / f"{case['id']}-final.md"
    events_path = directory / f"{case['id']}-events.jsonl"
    final = final_path.read_text(encoding="utf-8-sig") if final_path.is_file() else ""
    if not final.strip():
        add("missing_final", final_path.name, "Expected a nonempty final response.")
    messages = []
    if events_path.is_file():
        for line_number, line in enumerate(events_path.read_text(encoding="utf-8-sig").splitlines(), 1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                add("invalid_event", f"{events_path.name}:{line_number}", "Invalid JSON.")
                continue
            if not isinstance(event, dict):
                add("invalid_event", f"{events_path.name}:{line_number}", "Expected a JSON object.")
                continue
            text = visible_text(event)
            if text:
                messages.append((f"{events_path.name}:{line_number}", text))
    else:
        add("missing_events", events_path.name, "Cannot check visible progress messages.")
    messages.append((final_path.name, final))
    seen = set()
    for source, text in messages:
        normalized = text.replace("\r\n", "\n").strip()
        if normalized in seen:
            continue
        seen.add(normalized)
        if case["mode"] != "chat":
            continue
        for rule, pattern in FORMAT_RULES.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                add(rule, source, match.group())
        prose = IMAGE.sub("", text)
        if "amphoreus" not in case["prompt"].lower():
            match = re.search(r"\bamphoreus(?:-[a-z0-9]+)*\b", prose, re.IGNORECASE)
            if match:
                add("unprompted_skill_id", source, match.group())
        if "技能" not in case["prompt"] and "skill" not in case["prompt"].lower():
            match = re.search(r"(?:使用|选用|调用|用|启动|采用).{0,36}(?:技能|skill)", prose, re.IGNORECASE)
            if match:
                add("skill_invocation_notice", source, match.group())
        for term in UNPROMPTED_TERMS:
            if term not in case["prompt"] and term in prose:
                add("unprompted_metadata_term", source, term)
    images = len(IMAGE.findall(final))
    if not case["min_images"] <= images <= case["max_images"]:
        add("image_count", final_path.name, f"Found {images}; expected {case['min_images']}..{case['max_images']}.")
    review = ["Verify natural character voice and the expected speakers; literal names are not mandatory in solo chat."]
    if case["mode"] == "source":
        review.append("Compare claimed file reads and execution status with actual tool events; words alone cannot prove access.")
    else:
        review.append("Review implied backstage narration, invented actions, and topic context; pattern matches are candidates, not a semantic verdict.")
    return {"id": case["id"], "mode": case["mode"], "mechanical_pass": not findings,
            "image_count": images, "expected_speakers": case["expected_speakers"],
            "findings": findings, "semantic_review": review}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=Path(__file__).with_name("chat_cases.json"))
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--ids", nargs="+", help="Check only these case IDs.")
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text(encoding="utf-8-sig"))
    if args.ids:
        unknown = set(args.ids) - {case["id"] for case in cases}
        if unknown:
            parser.error("Unknown case IDs: " + ", ".join(sorted(unknown)))
        cases = [case for case in cases if case["id"] in args.ids]
    results = [check_case(case, args.outputs) for case in cases]
    report = {"mechanical_pass": bool(results) and all(item["mechanical_pass"] for item in results),
              "case_count": len(results), "semantic_review_required": True, "results": results}
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["mechanical_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
