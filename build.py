#!/usr/bin/env python3
"""《圣经主题分析》中译工程 —— 静态 HTML 生成器
用法：python3 build.py [--vocab-audit]
输入：data/grammar-points.json、data/NNN-*.json
输出：assets/grammar-registry.js、NNN-*.html、index.html
--vocab-audit：列出各词条正文（EN 原文）中尚未收入悬停词典的单词（过滤最常见基础词），
               供人工筛选四级以上词汇，避免漏收。
"""
import hashlib
import json
import re
import sys
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
BSB_PATH = ROOT.parent / "bsb" / "bsb.txt"

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'’-]*")

# 原书缩写 → BSB 书名（按需扩充）
BOOK_ABBREV = {
    "gen": "Genesis", "ex": "Exodus", "exod": "Exodus", "lev": "Leviticus",
    "num": "Numbers", "deut": "Deuteronomy", "josh": "Joshua", "judges": "Judges",
    "ruth": "Ruth", "sam": "Samuel", "kings": "Kings", "chron": "Chronicles",
    "ezra": "Ezra", "neh": "Nehemiah", "esther": "Esther", "job": "Job",
    "ps": "Psalm", "psa": "Psalm", "prov": "Proverbs", "eccles": "Ecclesiastes",
    "eccl": "Ecclesiastes", "cant": "Song of Solomon", "isa": "Isaiah",
    "jer": "Jeremiah", "lam": "Lamentations", "ezek": "Ezekiel", "dan": "Daniel",
    "hos": "Hosea", "hosea": "Hosea", "joel": "Joel", "amos": "Amos",
    "obad": "Obadiah", "jonah": "Jonah", "mic": "Micah", "micah": "Micah",
    "nahum": "Nahum", "nah": "Nahum", "hab": "Habakkuk", "zeph": "Zephaniah",
    "hag": "Haggai", "zech": "Zechariah", "mal": "Malachi",
    "matt": "Matthew", "mark": "Mark", "luke": "Luke", "john": "John",
    "acts": "Acts", "rom": "Romans", "cor": "Corinthians", "gal": "Galatians",
    "eph": "Ephesians", "phil": "Philippians", "col": "Colossians",
    "thes": "Thessalonians", "thess": "Thessalonians", "tim": "Timothy",
    "tit": "Titus", "philem": "Philemon", "heb": "Hebrews", "james": "James",
    "jas": "James", "pet": "Peter", "jude": "Jude", "rev": "Revelation",
}

# 经文块开头的引用，如 "Rom. 14:10, 12." / "1 Pet. 4:5." / "Ps. 119:75."
LEAD_REF_RE = re.compile(
    r"^((?:[1-3]\s+)?[A-Za-z]+)\.?\s+(\d+)\s*:\s*"
    r"(\d+(?:\s*[-–]\s*\d+)?(?:\s*,\s*\d+(?:\s*[-–]\s*\d+)?)*)"
)


def load_bsb():
    """读取 BSB 全文（公有领域），返回 {'Romans 14:12': '...'}。"""
    if not BSB_PATH.exists():
        print(f"[warn] 未找到 {BSB_PATH}，跳过现代英译（BSB）", file=sys.stderr)
        return {}
    verses = {}
    for line in BSB_PATH.read_text(encoding="utf-8-sig").splitlines():
        if "\t" not in line:
            continue
        ref, text = line.split("\t", 1)
        if ":" in ref and text.strip():
            verses[ref.strip()] = text.strip()
    return verses


def expand_verse_spec(spec):
    """'10, 12' / '14-16' / '2, 3, 16' → [10, 12] / [14, 15, 16] / [2, 3, 16]"""
    out = []
    for part in spec.split(","):
        part = part.strip()
        m = re.match(r"^(\d+)\s*[-–]\s*(\d+)$", part)
        if m:
            out.extend(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.isdigit():
            out.append(int(part))
    return out


def normalize_book(raw):
    """'Rom' / '1 Pet' / 'Hosea' → BSB 书名 'Romans' / '1 Peter' / 'Hosea'"""
    raw = raw.strip()
    m = re.match(r"^([1-3])\s+(.+)$", raw)
    prefix, name = (m.group(1) + " ", m.group(2)) if m else ("", raw)
    key = name.lower().rstrip(".")
    book = BOOK_ABBREV.get(key)
    if book is None:
        # 已是全称（如显式 bsb 字段里写 'Romans'）
        book = name if name[0].isupper() else None
    return (prefix + book) if book else None


def resolve_bsb_refs(block, entry_num, bsb):
    """确定块的 BSB 引用：显式 bsb 字段优先（false 表示不加）；否则从 en 开头自动解析。
    返回 [(display_ref, [(verse_no, text), ...]), ...]"""
    explicit = block.get("bsb")
    if explicit is False:
        return []
    refs = []
    if isinstance(explicit, str):
        for part in explicit.split(";"):
            m = re.match(r"^\s*((?:[1-3]\s+)?[A-Za-z][A-Za-z ]*?)\s+(\d+)\s*:\s*(.+)$", part)
            if not m:
                print(f"  [warn] 词条 {entry_num}：无法解析 bsb 字段 {part!r}", file=sys.stderr)
                continue
            refs.append((m.group(1), m.group(2), m.group(3)))
    else:
        m = LEAD_REF_RE.match(block["en"])
        if not m:
            return []
        refs.append((m.group(1), m.group(2), m.group(3)))

    out = []
    for raw_book, chap, spec in refs:
        book = normalize_book(raw_book)
        if not book:
            print(f"  [warn] 词条 {entry_num}：未知书卷缩写 {raw_book!r}", file=sys.stderr)
            continue
        verses = []
        for v in expand_verse_spec(spec):
            key = f"{book} {chap}:{v}"
            text = bsb.get(key)
            if text is None:
                print(f"  [warn] 词条 {entry_num}：BSB 中找不到 {key}", file=sys.stderr)
                continue
            verses.append((v, text))
        if verses:
            vs = ", ".join(str(v) for v, _ in verses)
            out.append((f"{book} {chap}:{vs}", verses))
    return out


def render_bsb(block, entry_num, bsb, vocab, used):
    parts = []
    for display_ref, verses in resolve_bsb_refs(block, entry_num, bsb):
        body = " ".join(
            ("<b>%d</b> " % v if len(verses) > 1 else "") + wrap_vocab(t, vocab, used)
            for v, t in verses
        )
        parts.append('<span class="ref">%s</span> %s' % (escape(display_ref), body))
    if not parts:
        return ""
    return '<p class="bsb"><span class="lbl">BSB</span>%s</p>' % "<br>".join(parts)

PAGE_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{num} {title_zh} | 圣经主题分析</title>
<link rel="stylesheet" href="assets/style.css">
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#2f7d46">
<link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
</head>
<body>
<div class="toolbar">
  <a class="home-link" href="index.html">← 目录</a>
  <button class="btn" id="btn-toc">☰ 本页</button>
  <span class="spacer"></span>
  <button class="btn" id="btn-en">隐藏全部英文</button>
  <button class="btn active" id="btn-bsb">现代英译：开</button>
  <button class="btn" id="btn-grammar">语法说明：关</button>
</div>
<nav id="side-toc" aria-label="本页目录">
<div class="toc-title">{num} {title_zh}</div>
{side_toc}
</nav>
<main>
<h1>{title_en} ｜ {title_zh}</h1>
<div class="source-note">
<p>📖 出处：J. Glentworth Butler, <em>Topical Analysis of the Bible</em>（《圣经主题分析》），1897 年出版，公有领域。{pages}</p>
<p>正文中的罗马数字引用（如 XI. 268）指向作者另一部著作 <em>The Bible Work</em> 的卷号与页码，保留原样。明显的 OCR 识别错误已修正。经文中文采用和合本通行译法。经文英文原文为 KJV/RV（1611/1885），其下 <b>BSB</b> 行是现代英语对照译文（Berean Standard Bible，公有领域）。{ocr_note}</p>
<p>💡 使用提示：鼠标悬停任意英文单词 1.5 秒（或点击）可查看音标与释义——<span class="w" data-k="__demo__">带下划线的</span>是本词条精编词汇，其余单词自动查通用词典（离线）；<b>划选任意单词或短语</b>（如 according to）也可查询并朗读；每节标题右侧按钮可隐藏该节英文；顶部按钮控制现代英译与语法说明。</p>
</div>
{sections}
{vocab_table}
</main>
<script type="application/json" id="vocab-data">{vocab_json}</script>
<script src="assets/grammar-registry.js"></script>
<script src="assets/app.js"></script>
<script>if ('serviceWorker' in navigator) navigator.serviceWorker.register('./sw.js');</script>
</body>
</html>
"""

INDEX_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>圣经主题分析 · 中英对照 · 目录</title>
<link rel="stylesheet" href="assets/style.css">
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#2f7d46">
<link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
</head>
<body>
<main>
<h1>《圣经主题分析》中英对照 · 目录</h1>
<div class="source-note">
<p>📖 J. Glentworth Butler, <em>Topical Analysis of the Bible</em>, 1897（公有领域）。按字母顺序的主题词条，每词条一个页面。</p>
<p>全书约 300 个词条，本目录随翻译进度更新。</p>
</div>
<div id="toc-search">
<input type="search" id="toc-q" placeholder="搜索词条：中文 / English / 编号 / 页码…" autocomplete="off" aria-label="搜索词条">
<button type="button" id="toc-clear" title="清除">✕</button>
<div id="toc-count"></div>
</div>
<ul class="toc">
{items}
</ul>
<p id="toc-empty" hidden>没有匹配的词条。换个关键词试试（可搜中文、英文、编号或原书页码）。</p>
</main>
<script>
(function () {{
  var q = document.getElementById('toc-q');
  var clear = document.getElementById('toc-clear');
  var count = document.getElementById('toc-count');
  var empty = document.getElementById('toc-empty');
  var rows = [].slice.call(document.querySelectorAll('ul.toc > li'));
  rows.forEach(function (li) {{ li.dataset.s = li.textContent.toLowerCase(); }});
  var total = rows.length;

  function run() {{
    var terms = q.value.toLowerCase().split(/\\s+/).filter(Boolean);
    var n = 0;
    rows.forEach(function (li) {{
      var hit = terms.every(function (t) {{ return li.dataset.s.indexOf(t) !== -1; }});
      li.hidden = !hit;
      if (hit) n++;
    }});
    clear.hidden = !q.value;
    empty.hidden = n !== 0;
    count.textContent = terms.length ? (n + ' / ' + total + ' 个词条') : (total + ' 个词条');
  }}

  q.addEventListener('input', run);
  clear.addEventListener('click', function () {{ q.value = ''; run(); q.focus(); }});
  document.addEventListener('keydown', function (e) {{
    if (e.key === '/' && document.activeElement !== q) {{ e.preventDefault(); q.focus(); }}
    if (e.key === 'Escape' && document.activeElement === q) {{ q.value = ''; run(); }}
  }});
  run();
}})();
</script>
<script>if ('serviceWorker' in navigator) navigator.serviceWorker.register('./sw.js');</script>
</body>
</html>
"""


def wrap_vocab(text, vocab, used):
    """所有单词都包成可查词节点：精编词典命中 → class="w"（虚线下划线）；
    其余 → class="w2"（无标记，悬停走 ECDICT 兜底词典）。"""
    out = []
    pos = 0
    for m in TOKEN_RE.finditer(text):
        out.append(escape(text[pos:m.start()]))
        tok = m.group(0)
        key = tok.lower()
        if key in vocab:
            used.add(key)
            cls = "w"
        else:
            cls = "w2"
        out.append('<span class="%s" data-k="%s">%s</span>' % (cls, escape(key, quote=True), escape(tok)))
        pos = m.end()
    out.append(escape(text[pos:]))
    return "".join(out)


def render_grammar(refs, entry_num, points, full_rendered):
    """渲染一个块的语法注解。首次出现（本词条 == first 且本页尚未详解过）给完整讲解，其余给可展开 chip。"""
    items = []
    for ref in refs:
        gid = ref.get("id")
        note = ref.get("note", "")
        if gid is None:
            # 无 id 的自由注解：仅针对本句的语法说明，不进入全局登记表
            items.append(
                '<div class="gitem gfree"><span class="gtag">语法</span>%s</div>'
                % escape(note)
            )
            continue
        g = points.get(gid)
        if g is None:
            print(f"  [warn] 词条 {entry_num}：语法点 {gid} 未登记", file=sys.stderr)
            continue
        is_first = g["first"] == entry_num and gid not in full_rendered
        if is_first:
            full_rendered.add(gid)
            items.append(
                '<div class="gitem gfull"><span class="gtag">语法</span>'
                '<span class="gtitle">%s</span>'
                '<div class="gbody">%s%s</div></div>'
                % (escape(g["title"]), escape(g["body"]),
                   ('<br><em>本句：</em>' + escape(note)) if note else "")
            )
        else:
            items.append(
                '<div class="gitem"><span class="gtag">语法</span>'
                '<span class="gchip" data-gid="%s">参：%s <span class="arrow">→ %s</span></span>'
                '%s</div>'
                % (escape(gid, quote=True), escape(g["title"]), escape(g["first"]),
                   (' <span class="gnote">' + escape(note) + '</span>') if note else "")
            )
    if not items:
        return ""
    return '<div class="grammar">%s</div>' % "".join(items)


def render_entry(entry, points, bsb, common_vocab):
    used = set()
    vocab = dict(common_vocab)
    vocab.update(entry.get("hover_vocab", {}))   # 词条自有释义优先
    full_rendered = set()
    sec_html = []
    toc_items = []
    for sec_idx, sec in enumerate(entry["sections"], 1):
        blocks = []
        for b in sec["blocks"]:
            en = wrap_vocab(b["en"], vocab, used)
            bsb_html = render_bsb(b, entry["num"], bsb, vocab, used)
            grammar = render_grammar(b.get("grammar", []), entry["num"], points, full_rendered)
            blocks.append(
                '<div class="block">'
                '<p class="en"><span class="lbl">EN</span>%s</p>'
                '%s%s'
                '<p class="zh"><span class="lbl">中</span>%s</p>'
                '</div>' % (en, bsb_html, grammar, escape(b["zh"]))
            )
        sec_html.append(
            '<section class="section" id="sec-%d">'
            '<div class="section-head"><h2>%s</h2>'
            '<button class="btn en-toggle">隐藏EN</button></div>'
            '%s</section>' % (sec_idx, wrap_vocab(sec["heading"], vocab, used), "".join(blocks))
        )
        label = sec["heading"].split(" / ")[0].split("【")[0].strip()
        toc_items.append('<a href="#sec-%d">%s</a>' % (sec_idx, escape(label)))

    rows = "".join(
        '<tr><td>%s<button class="speak" data-word="%s" title="朗读">🔊</button></td>'
        '<td class="ipa">%s</td><td>%s</td></tr>'
        % (escape(w["word"]), escape(w["word"], quote=True), escape(w["ipa"]), escape(w["def"]))
        for w in entry.get("vocab_table", [])
    )
    vocab_table = (
        '<section class="section" id="sec-vocab"><div class="section-head">'
        '<h2>词汇表（CET-4 及以上）</h2></div>'
        '<table class="vocab"><tr><th>单词</th><th>音标</th><th>词性与释义</th></tr>'
        '%s</table></section>' % rows
    ) if rows else ""
    if rows:
        toc_items.append('<a href="#sec-vocab">词汇表</a>')

    unused = set(entry.get("hover_vocab", {})) - used   # 共享常用词典不参与未命中警告
    if unused:
        print(f"  [warn] 词条 {entry['num']}：悬停词典中未在正文命中的键：{sorted(unused)}", file=sys.stderr)

    hover = dict(vocab)
    hover["__demo__"] = {"ipa": "/dɪˈmɒnstreɪʃn/", "def": "示例：这就是悬停查词的效果。"}

    ocr_note = entry.get("ocr_note", "")
    return PAGE_TMPL.format(
        num=entry["num"],
        title_en=escape(entry["title_en"]),
        title_zh=escape(entry["title_zh"]),
        pages=escape(entry.get("pages", "")),
        ocr_note=escape(ocr_note),
        side_toc="\n".join(toc_items),
        sections="".join(sec_html),
        vocab_table=vocab_table,
        vocab_json=json.dumps(hover, ensure_ascii=False),
    )


# 词汇审计用的基础词过滤表（初中级常用词、圣经专名缩写等，不视为四级+候选）
AUDIT_STOP = set("""
a an and the of to in on at by for with from into unto upon as but or nor not no yes
i you he she it we they me him her us them my your his its our their this that these those
who whom whose which what when where why how all any each every some both few more most other
another such only own same so than too very just also then once here there again further
is are was were be been am do does did have has had will would can could may might must
shall should about against between through during before after above below up down out off
over under go goes went gone come comes came get gets got make makes made see sees saw seen
say says said give gives given take takes took know known let lets stand stands stood
man men one two three new old good great long little way day days time life world
lord god christ jesus father son holy spirit heaven earth kingdom
rom cor pet thes tim matt heb eccles prov isa jer lam ezek dan hos hosea joel jonah mic
micah nahum nah hab zeph hag zech mal gen ex deut josh ps psa gal eph phil col tit philem
james jude rev luke john mark acts job ruth sam kings chron ezra neh esther illus etc
ver vol page see also and-so
ii iii iv v vi vii viii ix x xi xii
work works word words heart hearts hand hands eyes face name love loved fear
people children child things thing point points truth truths text texts
""".split())


def vocab_audit(entries, common_vocab):
    print("\n===== 词汇审计（正文中未收入悬停词典的候选词）=====")
    for entry in entries:
        vocab = set(entry.get("hover_vocab", {})) | set(common_vocab)
        seen = {}
        for sec in entry["sections"]:
            for b in sec["blocks"]:
                for m in TOKEN_RE.finditer(b["en"]):
                    key = m.group(0).lower()
                    if (len(key) >= 4 and key not in vocab
                            and key not in AUDIT_STOP and not key[0].isdigit()):
                        seen.setdefault(key, 0)
                        seen[key] += 1
        cands = sorted(seen)
        print(f"\n[{entry['num']} {entry['title_en']}] 候选 {len(cands)} 个：")
        print("  " + ", ".join(cands))


SW_TMPL = """// 自动生成，勿手改（build.py）
const CACHE = 'topical-cn-%(version)s';
const ASSETS = %(assets)s;
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request, {ignoreSearch: true}).then(hit => hit || fetch(e.request).then(resp => {
      if (resp.ok && new URL(e.request.url).origin === location.origin) {
        const copy = resp.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
      }
      return resp;
    }))
  );
});
"""


def write_service_worker(entries):
    """生成 sw.js：预缓存全站文件，版本号取自文件内容哈希（内容变则自动更新缓存）。"""
    files = ["index.html", "manifest.json",
             "assets/style.css", "assets/app.js", "assets/grammar-registry.js"]
    files += sorted(f"assets/dict/{p.name}" for p in (ASSETS / "dict").glob("*.js"))
    files += sorted(f"assets/icons/{p.name}" for p in (ASSETS / "icons").glob("*.png"))
    files += [e["html_name"] for e in entries]

    h = hashlib.md5()
    for f in files:
        p = ROOT / f
        if p.exists():
            h.update(p.read_bytes())
    version = h.hexdigest()[:10]

    urls = ["./" + quote(f) for f in files]
    sw = SW_TMPL % {"version": version, "assets": json.dumps(urls, ensure_ascii=False, indent=2)}
    (ROOT / "sw.js").write_text(sw, encoding="utf-8")
    print(f"生成 sw.js（预缓存 {len(urls)} 个文件，版本 {version}）")


def main():
    points = json.loads((DATA / "grammar-points.json").read_text(encoding="utf-8"))
    common_vocab = json.loads((DATA / "common-vocab.json").read_text(encoding="utf-8"))
    bsb = load_bsb()
    print(f"载入 BSB 经文 {len(bsb)} 节，共享常用词典 {len(common_vocab)} 词")

    registry_js = "window.GRAMMAR_REGISTRY = %s;\n" % json.dumps(points, ensure_ascii=False, indent=2)
    (ASSETS / "grammar-registry.js").write_text(registry_js, encoding="utf-8")
    print("生成 assets/grammar-registry.js（%d 个语法点）" % len(points))

    entries = []
    for f in sorted(DATA.glob("[0-9][0-9][0-9]-*.json")):
        entry = json.loads(f.read_text(encoding="utf-8"))
        html = render_entry(entry, points, bsb, common_vocab)
        out = ROOT / entry["html_name"]
        out.write_text(html, encoding="utf-8")
        entries.append(entry)
        print(f"生成 {entry['html_name']}")

    items = "".join(
        '<li><a href="%s">%s　%s ｜ %s</a><span class="meta">%s</span></li>\n'
        % (escape(e["html_name"], quote=True), e["num"], escape(e["title_en"]),
           escape(e["title_zh"]), escape(e.get("pages", "")))
        for e in entries
    )
    (ROOT / "index.html").write_text(INDEX_TMPL.format(items=items), encoding="utf-8")
    print(f"生成 index.html（{len(entries)} 个词条）")

    write_service_worker(entries)

    if "--vocab-audit" in sys.argv:
        vocab_audit(entries, common_vocab)


if __name__ == "__main__":
    main()
