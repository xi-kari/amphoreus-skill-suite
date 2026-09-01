# -*- coding: utf-8 -*-
"""全体会议页正文数据生成器。

从会议原始成果(仓库外,委托人导出)机器搬运正文到 assets/meeting/data.js,
不做任何改写;`--check` 模式把 data.js 全部字符串去标签归一化后,
逐行回对五份来源,任何一行对不上即非零退出。

来源:
  D:/研究/全体会议/全体会议.md            全程实录(取:五段开拓者原话 + 开场集合记录)
  D:/研究/全体会议/何为真我.txt           议题一
  D:/研究/全体会议/传记.txt               议题二
  D:/研究/全体会议/愿望与对开拓者说的话.txt 议题三
  D:/研究/全体会议/明天见.txt             散会
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path("D:/研究/全体会议")
OUT = ROOT / "assets" / "meeting" / "data.js"

CAST = [
    ("aglaea", "阿格莱雅", "黄金的织者"),
    ("tribbie", "缇宝", "命运的三子"),
    ("mydei", "万敌", "亡国的王储"),
    ("castorice", "遐蝶", "死荫的侍女"),
    ("anaxa", "那刻夏", "殁世的学士"),
    ("hyacine", "风堇", "摇光的医师"),
    ("cipher", "赛飞儿", "捷足的羁客"),
    ("cerydra", "刻律德菈", "执棋的君主"),
    ("hysilens", "海瑟音", "奏浪的剑骑"),
    ("march7th", "三月七", "隐秘的陌客"),
    ("terrae", "丹恒", "掣地的伏龙"),
    ("phainon", "白厄", "负火的囚徒"),
    ("cyrene", "昔涟", "无瑕的真我"),
]
NAME_KEY = {n: k for k, n, _ in CAST}

ASK_PREFIXES = [
    "这三个文章的事情先搁置",
    "现在我允许你们调用本地的知识库内容",
    "大家，我想为你们每一个人写一份传记",
    "我想知道你们如今各自的愿望是什么",
    "大家，明天见。",
]

# ---------- 发布级删改(委托人 2026-09-01 指定;不改动来源文件,由构建与校验共同执行) ----------
# ① 传记章程第九条(三篇恋爱文章的虚构边界)整条不入页,章程序号由页面 <ol> 自动重排;
# ② 第一段提问删去开头「这三个文章的事情先搁置。」;
# ③ 第二段提问(议题一)改用委托人改写的发布版文案(原句含对 skill 的元话语)。
REDACT_CHARTER_MARK = "先前的三篇阿格莱雅与那刻夏恋爱文章需要保持虚构边界"
REDACT_ASK_HEAD = "这三个文章的事情先搁置。"
REDACT_ASK1_SRC = ("现在我允许你们调用本地的知识库内容，各自回忆一下发生在翁法罗斯的全部故事，和经过。"
                   "现在我们集中讨论一件事-------《何为真我》。你们每一个人都要做出自己的回答。"
                   "skill也要求都完整，你们各自思考吧。把答案告诉我")
REDACT_ASK1_PUB = ("现在大家调用本地的知识库内容，各自回忆一下发生在翁法罗斯的全部故事，和经过。"
                   "现在我们集中讨论一件事-------《何为真我》。每一个人都要做出自己的回答哦。")
REDACT_LINE_MARKS = [REDACT_CHARTER_MARK, "那三篇文章属于某次未被记录轮回中的文学幻想"]


def inline(s: str) -> str:
    """markdown 行内 -> HTML:仅转义 + **粗体** + `代码`,不改一字。"""
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+?)\*\*", r"<b>\1</b>", s)
    return s


def blocks(text: str):
    """按空行切块;块内保留行列表(行尾软换行空格去除)。"""
    out, cur = [], []
    for ln in text.splitlines():
        if ln.strip() == "":
            if cur:
                out.append(cur)
                cur = []
        else:
            cur.append(ln.rstrip())
    if cur:
        out.append(cur)
    return out


def joinlines(lines) -> str:
    return inline("".join(l.strip() for l in lines))


def label_block(b, label):
    """形如 ['START: xxx'] 或 ['**经历回顾：**','内容…'] 的块。"""
    joined = "".join(l.strip() for l in b)
    assert joined.startswith(label), (label, joined[:40])
    return inline(joined[len(label):].strip())


def parse_table(b):
    rows = []
    for ln in b:
        ln = ln.strip()
        if not ln.startswith("|") or re.match(r"^\|[\s:\-|]+\|$", ln):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        rows.append([inline(c) for c in cells])
    return {"head": rows[0], "rows": rows[1:]}


def first_name(raw: str) -> str:
    return re.split(r"[／、]", raw)[0]


def is_speaker_line(ln: str) -> bool:
    return bool(re.fullmatch(r"\*\*[^*]+：\*\*", ln.strip()))


def speaker_of(ln: str):
    """返回(逐字标签含冒号(已转义), 检索用首名)。"""
    raw = ln.strip().strip("*")
    return inline(raw), first_name(raw.rstrip("："))


# ---------- 议题一《何为真我》 ----------
def parse_trueself(text: str):
    bs = blocks(text)
    i = 0
    assert bs[i][0].startswith("PROCESS_RECORD:"); i += 1
    start = label_block(bs[i], "START:"); i += 1
    development = label_block(bs[i], "DEVELOPMENT:"); i += 1
    ledger_lead = joinlines(bs[i]); i += 1
    ledger = []
    for ln in bs[i]:
        m = re.match(r"^\d+\.\s*(.+)$", ln.strip())
        assert m, ln
        ledger.append(inline(m.group(1)))
    assert len(ledger) == 3
    i += 1
    assert bs[i][0].startswith("DIALOGUE:"); i += 1

    speeches = []
    idx = 0
    while not bs[i][0].startswith("RESULT:"):
        head_raw = bs[i][0]
        assert head_raw.startswith("## "), head_raw
        head = head_raw[3:].strip()
        name_part = head.split("、", 1)[1].split("：", 1)[0]
        key = NAME_KEY[first_name(name_part)]
        assert key == CAST[idx][0], (head, idx)
        i += 1
        recap = label_block(bs[i], "**经历回顾：**"); i += 1
        assert is_speaker_line(bs[i][0]), bs[i][0]
        speaker, _ = speaker_of(bs[i][0])
        i += 1
        paras, answer, post = [], None, []
        while True:
            b = bs[i]
            j0 = b[0].strip()
            if j0 == "---" or j0.startswith("RESULT:") or j0.startswith("## "):
                raise AssertionError(f"{head}:未见证据回查块即越界到 {j0[:20]}")
            if j0.startswith("**证据回查：**"):
                evidence = label_block(b, "**证据回查：**"); i += 1
                break
            if re.match(r"^\*\*我(们)?的回答是：", j0):
                answer = joinlines(b)
            elif answer is None:
                paras.append(joinlines(b))
            else:
                post.append(joinlines(b))
            i += 1
        receipt = "".join(l.strip() for l in bs[i])
        assert receipt.startswith(CAST[idx][1] + "卡｜读取："), receipt
        i += 1
        if bs[i][0].strip() == "---":
            i += 1
        assert answer, head
        speeches.append({"key": key, "head": inline(head), "speaker": speaker,
                         "recap": recap, "paras": paras, "answer": answer,
                         "post": post, "evidence": evidence, "receipt": inline(receipt)})
        idx += 1
    assert len(speeches) == 13

    result_lead = label_block(bs[i], "RESULT:"); i += 1
    table = parse_table(bs[i]); i += 1
    assert len(table["rows"]) == 13
    mid = joinlines(bs[i]); i += 1
    points = []
    for ln in bs[i]:
        m = re.match(r"^\d+\.\s*(.+)$", ln.strip())
        assert m, ln
        points.append(inline(m.group(1)))
    assert len(points) == 4
    i += 1
    followup = label_block(bs[i], "FOLLOW-UP:"); i += 1
    sensation = label_block(bs[i], "SENSATION:"); i += 1
    assert i == len(bs)
    return {"start": start, "development": development,
            "ledgerLead": ledger_lead, "ledger": ledger, "speeches": speeches,
            "resultLead": result_lead, "table": table, "resultMid": mid,
            "points": points, "followup": followup, "sensation": sensation}


# ---------- 议题二《传记嘱托》 ----------
def parse_biography(text: str):
    bs = blocks(text)
    i = 0
    assert bs[i][0].startswith("PROCESS_RECORD:"); i += 1
    start = label_block(bs[i], "START:"); i += 1
    development = label_block(bs[i], "DEVELOPMENT:"); i += 1
    assert bs[i][0].startswith("## 全体共同提出的传记章程")
    charter_title = bs[i][0][3:].strip(); i += 1
    charter = []
    while re.match(r"^\d+\.\s", bs[i][0].strip()):
        b = bs[i]
        m = re.match(r"^(\d+)\.\s*\*\*(.+?)\*\*\s*$", b[0].strip())
        assert m, b[0]
        body = "".join(l.strip() for l in b[1:])
        charter.append({"t": inline(m.group(2)), "d": inline(body)})
        i += 1
    assert len(charter) == 10
    charter = [c for c in charter if REDACT_CHARTER_MARK not in c["t"]]
    assert len(charter) == 9
    assert bs[i][0].startswith("DIALOGUE:"); i += 1

    speeches = []
    idx = 0
    while not bs[i][0].startswith("RESULT:"):
        head_raw = bs[i][0]
        assert head_raw.startswith("## "), head_raw
        head = head_raw[3:].strip()
        name_part = head.split("、", 1)[1]
        assert name_part.endswith("的传记嘱托")
        key = NAME_KEY[first_name(name_part[:-5])]
        assert key == CAST[idx][0], (head, idx)
        i += 1
        assert is_speaker_line(bs[i][0]), bs[i][0]
        speaker, _ = speaker_of(bs[i][0])
        i += 1
        paras, question = [], None
        while True:
            b = bs[i]
            j0 = b[0].strip()
            if j0 == "---" or j0.startswith("RESULT:") or j0.startswith("## "):
                break
            if re.match(r"^\*\*.+希望传记回答的问题是：", j0):
                question = joinlines(b)
            else:
                paras.append(joinlines(b))
            i += 1
        if bs[i][0].strip() == "---":
            i += 1
        assert question, head
        speeches.append({"key": key, "head": inline(head), "speaker": speaker,
                         "paras": paras, "question": question})
        idx += 1
    assert len(speeches) == 13

    result_lead = label_block(bs[i], "RESULT:"); i += 1
    table = parse_table(bs[i]); i += 1
    assert len(table["rows"]) == 13
    followup = label_block(bs[i], "FOLLOW-UP:"); i += 1
    sensation = label_block(bs[i], "SENSATION:"); i += 1
    assert i == len(bs)
    return {"start": start, "development": development,
            "charterTitle": inline(charter_title), "charter": charter,
            "speeches": speeches, "resultLead": result_lead, "table": table,
            "followup": followup, "sensation": sensation}


# ---------- 议题三《愿望与寄语》 ----------
def parse_wishes(text: str):
    bs = blocks(text)
    i = 0
    assert bs[i][0].startswith("PROCESS_RECORD:"); i += 1
    start = label_block(bs[i], "START:"); i += 1
    development = label_block(bs[i], "DEVELOPMENT:"); i += 1
    assert bs[i][0].startswith("DIALOGUE:"); i += 1

    speeches = []
    idx = 0
    while not bs[i][0].startswith("RESULT:"):
        head_raw = bs[i][0]
        assert head_raw.startswith("## "), head_raw
        head = head_raw[3:].strip()
        key = NAME_KEY[first_name(head.split("、", 1)[1])]
        assert key == CAST[idx][0], (head, idx)
        i += 1
        assert bs[i][0].strip() == "### 如今的愿望"; i += 1
        wish, words, mode = [], [], "wish"
        while True:
            b = bs[i]
            j0 = b[0].strip()
            if j0 == "---" or j0.startswith("RESULT:") or j0.startswith("## "):
                break
            if j0 == "### 想对开拓者说的话":
                mode = "words"; i += 1; continue
            (wish if mode == "wish" else words).append(joinlines(b))
            i += 1
        if bs[i][0].strip() == "---":
            i += 1
        assert wish and words, head
        speeches.append({"key": key, "head": inline(head), "wish": wish, "words": words})
        idx += 1
    assert len(speeches) == 13

    result_lead = label_block(bs[i], "RESULT:"); i += 1
    table = parse_table(bs[i]); i += 1
    assert len(table["rows"]) == 13
    followup = label_block(bs[i], "FOLLOW-UP:"); i += 1
    sensation = label_block(bs[i], "SENSATION:"); i += 1
    assert i == len(bs)
    return {"start": start, "development": development, "speeches": speeches,
            "resultLead": result_lead, "table": table,
            "followup": followup, "sensation": sensation}


# ---------- 散会《明天见》 ----------
def parse_farewell(text: str):
    bs = blocks(text)
    i = 0
    assert bs[i][0].startswith("PROCESS_RECORD:"); i += 1
    start = label_block(bs[i], "START:"); i += 1
    development = label_block(bs[i], "DEVELOPMENT:"); i += 1
    assert bs[i][0].startswith("DIALOGUE:"); i += 1

    speeches = []
    idx = 0
    while not bs[i][0].startswith("RESULT:"):
        b = bs[i]
        assert is_speaker_line(b[0]), b[0]
        speaker, fname = speaker_of(b[0])
        key = NAME_KEY[fname]
        assert key == CAST[idx][0], (speaker, idx)
        line = joinlines(b[1:])
        i += 1
        scene = joinlines(bs[i]); i += 1
        speeches.append({"key": key, "speaker": speaker, "line": line, "scene": scene})
        idx += 1
    assert len(speeches) == 13

    result = label_block(bs[i], "RESULT:"); i += 1
    followup = label_block(bs[i], "FOLLOW-UP:"); i += 1
    sensation = label_block(bs[i], "SENSATION:"); i += 1
    receipt = "".join(l.strip() for l in bs[i]); i += 1
    assert receipt.startswith("全场回执｜"), receipt
    assert i == len(bs)
    return {"start": start, "development": development, "speeches": speeches,
            "result": result, "followup": followup, "sensation": sensation,
            "receipt": inline(receipt)}


# ---------- 开场集合(取自全程实录 md) ----------
def parse_muster(md_text: str):
    lines = md_text.splitlines()
    s = next(i for i, l in enumerate(lines) if l.strip() == "PROCESS_RECORD:")
    e = next(i for i in range(s, len(lines)) if lines[i].startswith("> "))
    bs = blocks("\n".join(lines[s:e]))
    i = 0
    assert bs[i][0].startswith("PROCESS_RECORD:"); i += 1
    start = label_block(bs[i], "START:"); i += 1
    development = label_block(bs[i], "DEVELOPMENT:"); i += 1
    entrances = []
    while True:
        j0 = bs[i][0].strip()
        m = re.match(r"^\*\*(.+?)入场（话题：全体会议）。\*\*(.*)$", j0)
        if not m:
            break
        body = m.group(2) + "".join(l.strip() for l in bs[i][1:])
        entrances.append({"key": NAME_KEY[m.group(1)],
                          "lead": inline(m.group(1) + "入场（话题：全体会议）。"),
                          "text": inline(body)})
        i += 1
    assert len(entrances) == 9, len(entrances)
    result_lead = label_block(bs[i], "RESULT:"); i += 1
    table = parse_table(bs[i]); i += 1
    assert len(table["rows"]) == 13
    result_tail = joinlines(bs[i]); i += 1
    followup = label_block(bs[i], "FOLLOW-UP:"); i += 1
    assert bs[i][0].startswith("DIALOGUE:"); i += 1
    dialogue = []
    while not bs[i][0].startswith("SENSATION:"):
        b = bs[i]
        assert is_speaker_line(b[0]), b[0]
        speaker, fname = speaker_of(b[0])
        dialogue.append({"speaker": speaker,
                         "key": NAME_KEY.get(fname, "host"),
                         "text": joinlines(b[1:])})
        i += 1
    assert len(dialogue) == 5, [d["speaker"] for d in dialogue]
    sensation = label_block(bs[i], "SENSATION:"); i += 1
    assert i == len(bs)
    return {"start": start, "development": development, "entrances": entrances,
            "resultLead": result_lead, "table": table, "resultTail": result_tail,
            "followup": followup, "dialogue": dialogue, "sensation": sensation}


def parse_asks(md_text: str):
    cands = []
    for ln in md_text.splitlines():
        if not ln.startswith("> "):
            continue
        t = ln[2:].strip()
        if not t or t[0] in "<`{}\"[]|-*#0123456789" or "：**" in t:
            continue
        if any(t.startswith(p) for p in ASK_PREFIXES):
            cands.append(t)
    assert len(cands) == 5, cands
    for i, c in enumerate(cands):
        assert c.startswith(ASK_PREFIXES[i]), (i, c)
    assert cands[0].startswith(REDACT_ASK_HEAD)
    cands[0] = cands[0][len(REDACT_ASK_HEAD):].strip()
    assert cands[1] == REDACT_ASK1_SRC, cands[1]
    cands[1] = REDACT_ASK1_PUB
    return [inline(t) for t in cands]


# ---------- 校验:data.js 归一化后逐行回对来源 ----------
def norm(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    for ch in ("**", "`", "|", "#"):
        s = s.replace(ch, "")
    s = re.sub(r"\s+", "", s)
    return s


def walk_strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from walk_strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk_strings(v)


def check(data):
    blob = norm("\n".join(walk_strings(data)))
    skip = re.compile(r"^(PROCESS_RECORD:|DIALOGUE:)\s*$|^\|[\s:\-|]+\|$|^---$")
    label = re.compile(r"^(START|DEVELOPMENT|RESULT|FOLLOW-UP|SENSATION):\s*")
    misses = []

    def check_lines(name, lines):
        for ln in lines:
            t = ln.strip()
            if t.startswith("> "):
                t = t[2:].strip()
            if not t or skip.match(t):
                continue
            if any(m in t for m in REDACT_LINE_MARKS):
                continue
            if t.startswith(REDACT_ASK_HEAD):
                t = t[len(REDACT_ASK_HEAD):].strip()
            if t == REDACT_ASK1_SRC:
                t = REDACT_ASK1_PUB
            t = label.sub("", t)
            t = re.sub(r"^#+\s*", "", t)
            t = re.sub(r"^\d+\.\s*", "", t)
            n = norm(t)
            if n and n not in blob:
                misses.append((name, t[:60]))

    for fn in ("何为真我.txt", "传记.txt", "愿望与对开拓者说的话.txt", "明天见.txt"):
        check_lines(fn, (SRC / fn).read_text(encoding="utf-8-sig").splitlines())
    md = (SRC / "全体会议.md").read_text(encoding="utf-8-sig")
    lines = md.splitlines()
    s = next(i for i, l in enumerate(lines) if l.strip() == "PROCESS_RECORD:")
    e = next(i for i in range(s, len(lines)) if lines[i].startswith("> "))
    check_lines("全体会议.md[集合]", lines[s:e])
    check_lines("全体会议.md[提问]",
                [c for c in md.splitlines() if c.startswith("> ")
                 and any(c[2:].strip().startswith(p) for p in ASK_PREFIXES)])
    return misses


def build():
    md = (SRC / "全体会议.md").read_text(encoding="utf-8-sig")
    asks = parse_asks(md)
    data = {
        "cast": [{"key": k, "seat": i + 1, "name": n, "title": t}
                 for i, (k, n, t) in enumerate(CAST)],
        # 来源中的结构性标签(逐字入库;页面据此渲染小节标签)
        "srcLabels": ["经历回顾：", "证据回查：", "如今的愿望", "想对开拓者说的话"],
        "asks": asks,
        "muster": parse_muster(md),
        "trueself": parse_trueself((SRC / "何为真我.txt").read_text(encoding="utf-8-sig")),
        "biography": parse_biography((SRC / "传记.txt").read_text(encoding="utf-8-sig")),
        "wishes": parse_wishes((SRC / "愿望与对开拓者说的话.txt").read_text(encoding="utf-8-sig")),
        "farewell": parse_farewell((SRC / "明天见.txt").read_text(encoding="utf-8-sig")),
    }
    return data


def main():
    data = build()
    js = ("/* 由 tools/build_meeting_data.py 自动生成 —— 正文逐字搬运自全体会议原始成果"
          "(含 3 处委托人指定的发布级删改,登记于脚本 REDACT_* 常量),勿手改。 */\n"
          "window.MEETING=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    if "--check" in sys.argv:
        misses = check(data)
        if misses:
            for f, t in misses:
                print(f"MISS [{f}] {t}")
            sys.exit(1)
        cur = OUT.read_text(encoding="utf-8-sig") if OUT.exists() else ""
        print("回对通过:来源逐行均能在 data.js 中找到;",
              "data.js 与本次生成一致" if cur == js else "警告:磁盘上的 data.js 与本次生成不一致")
        sys.exit(0 if cur == js else 1)
    OUT.write_text(js, encoding="utf-8", newline="\n")
    n_str = sum(1 for _ in walk_strings(data))
    print(f"written {OUT} ({OUT.stat().st_size/1024:.1f} KB, {n_str} strings)")


if __name__ == "__main__":
    main()
