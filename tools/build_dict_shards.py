#!/usr/bin/env python3
"""从 ECDICT（开源英汉词典数据库）裁剪生成兜底词典分片。
用法：python3 tools/build_dict_shards.py
输入：../dict-source/stardict.db（ECDICT sqlite 发行包）
输出：assets/dict/dict-{a..z,misc}.js（window.ECDICT_LOAD 分片）

收录规则：
- 单词：有中文释义，且（带 cet4/cet6/ky/toefl/ielts/gre 标签，或牛津3000词，
        或 BNC/当代词频前 20000）
- 短语（有中文释义，2-4 个纯小写英文词），满足其一：
  a) 有任一词频/标签/柯林斯星级/牛津信号；
  b) 动词＋小品词型（give up / according to），首词须为已收录的基本形；
  c) 介词框架型（in spite of / as compared with）。
- 屈折变形（过去式/复数/-ing 等）作为别名键指向原型词条
"""
import json
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # 译文/
DB = ROOT.parent / "dict-source" / "stardict.db"
OUT = ROOT / "assets" / "dict"

WORD_RE = re.compile(r"^[a-z][a-z'-]*$")
PHRASE_RE = re.compile(r"^[a-z][a-z'-]*(?: [a-z][a-z'-]*){1,3}$")
TAG_MAP = {"zk": "中考", "gk": "高考", "cet4": "四级", "cet6": "六级",
           "ky": "考研", "toefl": "托福", "ielts": "雅思", "gre": "GRE"}
PARTICLES = set("up down out off over in on away back about around through with for at "
                "into upon onto by to of after against forward aside".split())
FUNC_WORDS = set("a an the of to in on at by for with from into unto upon as under over out".split())


def clean_trans(t):
    t = t.replace("\\n", "；").replace("\n", "；").replace("\r", "")
    t = re.sub(r"；+", "；", t).strip("； ")
    return t[:160] + ("…" if len(t) > 160 else "")


def tags_of(tag):
    return "/".join(TAG_MAP[t] for t in (tag or "").split() if t in TAG_MAP)


def shard_key(word):
    c = word[0]
    return c if "a" <= c <= "z" else "misc"


def main():
    if not DB.exists():
        sys.exit(f"找不到 {DB}，请先下载 ecdict-sqlite-28.zip 并解压到 dict-source/")
    db = sqlite3.connect(DB)
    cur = db.cursor()

    entries = {}   # word -> [phonetic, translation, tags]
    aliases = {}   # inflected -> base word
    exchanges = {}

    # ---- 单词层 ----
    q = """select word, phonetic, translation, tag, exchange from stardict
           where translation is not null and translation != '' and (
             tag like '%cet4%' or tag like '%cet6%' or tag like '%ky%'
             or tag like '%toefl%' or tag like '%ielts%' or tag like '%gre%'
             or oxford = 1 or (frq > 0 and frq <= 20000) or (bnc > 0 and bnc <= 20000))"""
    for word, ph, trans, tag, exch in cur.execute(q):
        w = word.lower()
        if not WORD_RE.match(w) or len(w) > 40:
            continue
        entries[w] = [ph or "", clean_trans(trans), tags_of(tag)]
        if exch:
            exchanges[w] = exch

    # ---- 屈折变形别名（exchange 字段: p:过去式/d:过去分词/i:现在分词/3:三单/s:复数/r:比较级/t:最高级）----
    for base, exch in exchanges.items():
        for item in exch.split("/"):
            if ":" not in item:
                continue
            k, v = item.split(":", 1)
            v = v.lower().strip()
            if k in "pdi3srt" and WORD_RE.match(v) and v not in entries and v not in aliases:
                aliases[v] = base

    # ---- 短语层 ----
    q2 = """select word, phonetic, translation, tag, collins, oxford, frq, bnc from stardict
            where word like '% %' and translation is not null and translation != ''
            and length(word) <= 40"""
    n_phrase = 0
    for word, ph, trans, tag, collins, oxford, frq, bnc in cur.execute(q2):
        w = word.lower()
        if not PHRASE_RE.match(w):
            continue
        parts = w.split()
        has_signal = bool((tag or "").strip()) or (collins or 0) > 0 or (oxford or 0) > 0 \
            or (frq or 0) > 0 or (bnc or 0) > 0
        verb_particle = (len(parts) == 2 and parts[1] in PARTICLES
                         and parts[0] in entries and parts[0] not in FUNC_WORDS
                         and parts[0] not in aliases and len(parts[0]) > 1)
        prep_frame = (len(parts) == 3 and parts[0] in FUNC_WORDS and parts[2] in FUNC_WORDS)
        if not (has_signal or verb_particle or prep_frame):
            continue
        entries[w] = [ph or "", clean_trans(trans), tags_of(tag)]
        n_phrase += 1

    # ---- 分片输出 ----
    OUT.mkdir(parents=True, exist_ok=True)
    shards = defaultdict(dict)
    for w, e in entries.items():
        shards[shard_key(w)][w] = e
    for w, base in aliases.items():
        shards[shard_key(w)][w] = base   # 字符串值 = 别名

    total_bytes = 0
    for key, data in sorted(shards.items()):
        js = "window.ECDICT_LOAD(%s, %s);\n" % (
            json.dumps(key), json.dumps(data, ensure_ascii=False, separators=(",", ":")))
        p = OUT / f"dict-{key}.js"
        p.write_text(js, encoding="utf-8")
        total_bytes += p.stat().st_size
    print(f"单词 {len(entries) - n_phrase}，短语 {n_phrase}，变形别名 {len(aliases)}，"
          f"共 {len(entries) + len(aliases)} 键")
    print(f"输出 {len(shards)} 个分片到 assets/dict/，总大小 {total_bytes / 1048576:.1f} MB")


if __name__ == "__main__":
    main()
