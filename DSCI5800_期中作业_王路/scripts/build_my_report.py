#!/usr/bin/env python3
"""把 我的实验/笔记.md 转成 A4 报告 PDF。

处理要点：
  1. <details><summary>...</summary> ... </details>  → 展开成带标题的小节（PDF 里无法折叠）
  2. 形如 `截图/xx.png` 的路径 → 内嵌真实图片（居中、限宽、带图注）
  3. Markdown 表格 → HTML 表格（A4 宽度内自动缩字号）
  4. 中文字体：宋体；西文：Times New Roman；单倍行距
"""
import html, os, re, subprocess

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = _HERE if os.path.isdir(os.path.join(_HERE, "prompts")) else os.path.dirname(_HERE)
SRC = os.path.join(ROOT, "我的实验", "笔记.md")
SHOT_DIR = os.path.join(ROOT, "我的实验", "截图")
HTML_OUT = os.path.join(ROOT, "我的实验", "_report.html")
PDF_OUT = os.path.join(ROOT, "DSCI5800_王_路_期中作业.pdf")


SHOT_TOKEN = "\x00SHOT%d\x00"
PLACED = set()   # 文档级：已插入过的图片，防止重复


def inline(s, shots=None):
    """shots 为列表时，`![图注](截图/xxx.png)` 会被替换为占位符，稍后在块级插入 <figure>。

    图注直接取 alt 文本，所以 PDF 里不会出现文件名或路径。
    """
    s = html.escape(s)

    # 1) 先把图片指令摘出来（必须在其它行内规则之前）
    def grab(m):
        cap, rel = m.group(1), m.group(2)
        if shots is None:
            return f'<span class="shotref">{cap}</span>'
        if rel in PLACED:
            return ""            # 已经插入过就不再重复
        shots.append({"rel": rel, "cap": cap})
        PLACED.add(rel)
        return SHOT_TOKEN % (len(shots) - 1)

    s = re.sub(r"!\[([^\]]*)\]\((截图/[^)]+\.png)\)", grab, s)

    # 2) 其余行内标记
    # 注意：不要用单个 * 做 <em>。报告里大量出现 0.35*Capability 这类算式，
    # 而代码块的 <pre> 是在 md_to_html 里单独处理的，行内算式一旦被 *…* 吞掉
    # 就会渲染成 0.352+0.254（见旧版 PDF 第 13、25 页）。正文没有真正的单星强调。
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    # Markdown 转义：评审输出里把算式写成 0.35\*2（防止被当成强调），PDF 里应还原成 *
    s = s.replace("\\*", "*")
    return s


def figures_for(shots):
    htmls = []
    for sh in shots:
        rel, cap = sh["rel"], sh["cap"]
        p = os.path.join(ROOT, "我的实验", rel)
        # 图注用 alt 文本；没有 alt 就退回"参数与输出同屏"，绝不显示文件名
        cap = cap or "参数与输出同屏"
        if os.path.isfile(p):
            htmls.append(f'<figure><img src="file://{p}">'
                         f'<figcaption>{html.escape(cap)}</figcaption></figure>')
        else:
            htmls.append(f'<p class="missing">[缺图：{html.escape(cap)}]</p>')
    return "".join(htmls)


def md_to_html(md, shot_counter):
    lines = md.split("\n")
    out, i = [], 0
    in_list = None
    li_index = None
    buffer = []          # 连续正文行，合并成一个 <p>

    def flush():
        nonlocal buffer
        if buffer:
            shots = []
            txt = re.sub(r"\x00SHOT\d+\x00", "", inline(" ".join(buffer), shots))
            out.append("<p>" + txt + "</p>")
            out.append(figures_for(shots))
            buffer = []

    def close_list():
        nonlocal in_list, li_index
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None
        li_index = None

    while i < len(lines):
        ln = lines[i]

        # ---- 折叠块：展开 ----
        m = re.match(r"<details><summary>(.*?)</summary>", ln.strip())
        if m:
            flush(); close_list()
            out.append(f'<div class="folded"><div class="foldtitle">{inline(m.group(1))}</div>')
            i += 1
            continue
        if ln.strip() == "</details>":
            flush(); close_list()
            out.append("</div>")
            i += 1
            continue

        # ---- 代码块 ----
        if ln.startswith("```"):
            flush(); close_list()
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(html.escape(lines[i]))
                i += 1
            out.append("<pre>" + "\n".join(block) + "</pre>")
            i += 1
            continue

        # ---- 表格 ----
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i+1].strip()):
            flush(); close_list()
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            shots = []
            th = "".join(f"<th>{inline(c, shots)}</th>" for c in head)
            tb = "".join("<tr>" + "".join(f"<td>{inline(c, shots)}</td>" for c in r) + "</tr>" for r in rows)
            cls = "small" if len(head) >= 8 else ""
            # 首列是很短的表头（对象/类别）时，放宽首列以免竖排
            # 只在列数匹配时才套固定列宽，否则会把宽表挤坏（6.2 的 11 列表就踩过这个坑）
            if head and len(head) == 4 and head[0] in ("类别", "对象"):
                cls = (cls + " judge").strip()
            elif head and len(head) == 3 and head[0] in ("对象", "设计点"):
                cls = (cls + " short3").strip()
            elif head and len(head) == 4 and head[0] == "要求":
                cls = (cls + " req4").strip()
            elif head and len(head) == 6 and head[0] == "选项":
                cls = (cls + " opt6").strip()
            elif head and len(head) == 5 and head[0] == "方案":
                cls = (cls + " cal5").strip()
            html_tbl = f'<table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table>'
            # 单元格里只留文件名，图片统一放到表格之后
            html_tbl = re.sub(
                r"\x00SHOT(\d+)\x00",
                lambda m: '<span class="shotname">' + html.escape(shots[int(m.group(1))]["cap"] or "参数与输出同屏") + "</span>",
                html_tbl)
            out.append(html_tbl)
            out.append(figures_for(shots))
            continue

        # ---- 引用块 ----
        if ln.startswith(">"):
            flush(); close_list()
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ").strip())
                i += 1
            out.append('<div class="quote">' + "<br>".join(inline(b) for b in buf) + "</div>")
            continue

        # ---- 标题 ----
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            flush(); close_list()
            lv = len(m.group(1))
            out.append(f"<h{lv}>{inline(m.group(2))}</h{lv}>")
            i += 1
            continue

        # ---- 分隔线 ----
        if ln.strip() == "---":
            flush(); close_list()
            out.append('<hr class="soft">')
            i += 1
            continue

        # ---- 列表 ----
        if re.match(r"^\s*[-*] ", ln):
            flush()
            if in_list != "ul":
                close_list(); out.append("<ul>"); in_list = "ul"
            sh = []
            li_txt = re.sub(r"\x00SHOT\d+\x00", "", inline(re.sub(r'^\s*[-*] ', '', ln), sh))
            out.append(f"<li>{li_txt}</li>")
            if sh: out.append(figures_for(sh))
            li_index = len(out) - 1
            i += 1
            continue
        if re.match(r"^\s*\d+\.\s", ln):
            flush()
            if in_list != "ol":
                close_list(); out.append("<ol>"); in_list = "ol"
            out.append(f"<li>{inline(re.sub(r'^\s*\d+\.\s', '', ln))}</li>")
            li_index = len(out) - 1
            i += 1
            continue

        # ---- 缩进续行 ----
        if in_list and li_index is not None and ln.startswith(("  ", "\t")):
            cur = out[li_index]
            out[li_index] = cur[:-5] + " " + inline(ln.strip()) + "</li>"
            i += 1
            continue

        # ---- 空行 ----
        if not ln.strip():
            flush(); close_list()
            i += 1
            continue

        buffer.append(ln.strip())
        i += 1

    flush(); close_list()
    return "\n".join(out)


CSS = """
@page { size: A4; margin: 16mm 15mm 14mm 15mm; }
body { font-family:"Songti SC","STSong","Times New Roman",serif; font-size:11pt;
       line-height:1.42; color:#111; text-align:justify; }
h1 { font-size:19pt; text-align:center; margin:0 0 4pt; border-bottom:1.5pt solid #222;
     padding-bottom:8pt; }
h2 { font-size:13pt; margin:14pt 0 6pt; padding:5pt 8pt; background:#2b3a4a; color:#fff;
     page-break-after:avoid; }
h3 { font-size:11.5pt; margin:11pt 0 5pt; color:#16324f; border-left:3pt solid #2b6cb0;
     padding-left:7pt; page-break-after:avoid; }
h4 { font-size:11pt; margin:11pt 0 5pt; page-break-after:avoid; }
p { margin:0 0 4.5pt; }
code { font-family:Menlo,monospace; font-size:9pt; background:#eef1f4; padding:0 3pt;
       border-radius:2pt; }
pre { font-family:Menlo,monospace; font-size:7.0pt; line-height:1.28; background:#f7f8fa;
      border:0.6pt solid #c3cad2; border-left:2.5pt solid #2b6cb0; padding:7pt 9pt;
      white-space:pre-wrap; word-break:break-word; margin:4pt 0 7pt; }
table { border-collapse:collapse; width:100%; margin:4pt 0 7pt; font-size:8.4pt; }
tr { page-break-inside:avoid; }
thead { display:table-header-group; }
table.small { font-size:7.8pt; }
/* 评审明细表：4 列，首列窄、依据列宽，避免"类别"被挤成竖排 */
table.judge { table-layout:fixed; font-size:8.4pt; }
/* 三列表（对象 / 最弱维度 / 意见）：首列窄但有固定宽度，避免被压成竖排 */
table.short3 { table-layout:fixed; }
table.short3 th:nth-child(1), table.short3 td:nth-child(1) { width:11%; }
table.short3 th:nth-child(2), table.short3 td:nth-child(2) { width:17%; }
table.short3 th:nth-child(3), table.short3 td:nth-child(3) { width:72%; }
/* 3 列且首列短：设计点 / 我怎么做的 / 为什么这样设计 */
table.short3 th:nth-child(1), table.short3 td:nth-child(1) { width:11%; }
table.short3 th:nth-child(2), table.short3 td:nth-child(2) { width:34%; }
table.short3 th:nth-child(3), table.short3 td:nth-child(3) { width:55%; }
table.cal5 th:nth-child(1), table.cal5 td:nth-child(1) { width:8%; }
table.cal5 th:nth-child(2), table.cal5 td:nth-child(2) { width:52%; }
table.cal5 th:nth-child(3), table.cal5 td:nth-child(3) { width:13%; }
table.cal5 th:nth-child(4), table.cal5 td:nth-child(4) { width:13%; }
table.cal5 th:nth-child(5), table.cal5 td:nth-child(5) { width:14%; }
table.req4 th:nth-child(1), table.req4 td:nth-child(1) { width:15%; }
table.req4 th:nth-child(2), table.req4 td:nth-child(2) { width:45%; }
table.req4 th:nth-child(3), table.req4 td:nth-child(3) { width:10%; }
table.req4 th:nth-child(4), table.req4 td:nth-child(4) { width:30%; }
table.opt6 th:nth-child(1), table.opt6 td:nth-child(1) { width:7%; }
table.opt6 th:nth-child(2), table.opt6 td:nth-child(2) { width:19%; }
table.opt6 th:nth-child(3), table.opt6 td:nth-child(3) { width:10%; }
table.opt6 th:nth-child(4), table.opt6 td:nth-child(4) { width:22%; }
table.opt6 th:nth-child(5), table.opt6 td:nth-child(5) { width:24%; }
table.opt6 th:nth-child(6), table.opt6 td:nth-child(6) { width:18%; }
table.judge th:nth-child(1), table.judge td:nth-child(1) { width:14%; }
table.judge th:nth-child(2), table.judge td:nth-child(2) { width:14%; }
table.judge th:nth-child(3), table.judge td:nth-child(3) { width:42%; }
table.judge th:nth-child(4), table.judge td:nth-child(4) { width:30%; }
th,td { border:0.6pt solid #8a939c; padding:3pt 4pt; vertical-align:top; }
th { background:#e3e8ee; font-weight:700; }
ul,ol { margin:3pt 0 8pt; padding-left:1.6em; }
li { margin:0 0 3pt; }
figure { margin:4pt 0 6pt; text-align:center; page-break-inside:avoid; }
figure img { max-width:100%; max-height:84mm; object-fit:contain;
             border:0.6pt solid #999; }
figcaption { font-size:8.5pt; color:#444; margin-top:3pt; }
.quote { background:#fffbe8; border:0.6pt solid #d9c377; border-left:2.5pt solid #c9a227;
         padding:6pt 9pt; margin:6pt 0 9pt; font-size:10pt; page-break-inside:avoid; }
.folded { border:0.6pt solid #c3cad2; border-radius:3pt; padding:7pt 9pt; margin:6pt 0 10pt;
          background:#fcfcfd; }
.foldtitle { font-weight:700; font-size:10pt; margin-bottom:5pt; color:#2b3a4a;
             border-bottom:0.5pt dashed #aab; padding-bottom:3pt; }
.missing { color:#c00; font-size:9pt; }
hr.soft { border:0; border-top:0.5pt dashed #bbb; margin:12pt 0; }
"""

PLACED.clear()
md = open(SRC).read()

# 报告化处理：换标题、去掉写给自己看的提示块、去掉"素材/结论方向"的批注
md = re.sub(r"^# .*$", "# 思维链提示与参数调优\n\n"
            "## DSCI5800 期中作业\n\n"
            "**姓名：** 王路　　**课程：** DSCI5800　　**日期：** 2026 年 11 月 27 日\n\n"
            "**模型：** deepseek-v4.1-flash　　**接口：** POST /v1/chat/completions\n\n"
            "---", md, count=1, flags=re.M)

# 删掉开头那段"这份笔记由我自己填写……"的提示块（容忍 ** 加粗）
md = re.sub(r"\n>\s*这份笔记.*?(?=\n\n)", "", md, flags=re.S)

# 删掉"素材（只列证据，结论自己写）"这类写给自己看的小标题
md = re.sub(r"\n> \*\*素材（只列证据，结论自己写）\*\*\n", "\n", md)

# 删掉"可写的结论方向：……"整段（它是给作者的提示，不是报告内容）
md = re.sub(r"\n\*\*可写的结论方向\*\*：.*?(?=\n\n)", "", md, flags=re.S)
body = md_to_html(md, {})
doc = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>DSCI5800 期中作业 · 王路</title><style>{CSS}</style></head>
<body>{body}</body></html>"""
open(HTML_OUT, "w").write(doc)
print("html:", len(doc), "字符")

r = subprocess.run([
    "/Users/wanglu/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/node/bin/node",
    os.path.join(ROOT, "scripts", "print_pdf.js"), HTML_OUT, PDF_OUT],
    capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[:500])
