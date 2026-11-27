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
    """shots 为列表时，截图路径会被替换为占位符，稍后在块级插入真正的 <figure>。"""
    s = html.escape(s)

    # 1) 先把 `截图/xxx.png` 摘出来（必须在 code 正则之前）
    def grab(m):
        rel = m.group(1)
        if shots is None:
            return f'<span class="shotref">{rel}</span>'
        if rel in shots or rel in PLACED:
            return ""            # 已经插入过就不再重复
        shots.append(rel)
        PLACED.add(rel)
        return SHOT_TOKEN % (len(shots) - 1)

    s = re.sub(r"`(截图/[^`]+\.png)`", grab, s)

    # 2) 其余行内标记
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    return s


def figures_for(shots):
    htmls = []
    for rel in shots:
        p = os.path.join(ROOT, "我的实验", rel)
        if os.path.isfile(p):
            htmls.append(f'<figure><img src="file://{p}">'
                         f'<figcaption>{os.path.basename(rel)}</figcaption></figure>')
        else:
            htmls.append(f'<p class="missing">[缺图：{rel}]</p>')
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
            html_tbl = f'<table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table>'
            # 单元格里只留文件名，图片统一放到表格之后
            html_tbl = re.sub(
                r"\x00SHOT(\d+)\x00",
                lambda m: '<span class="shotname">' + os.path.basename(shots[int(m.group(1))]) + "</span>",
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
@page { size: A4; margin: 22mm 18mm 18mm 18mm; }
body { font-family:"Songti SC","STSong","Times New Roman",serif; font-size:11pt;
       line-height:1.55; color:#111; text-align:justify; }
h1 { font-size:19pt; text-align:center; margin:0 0 4pt; border-bottom:1.5pt solid #222;
     padding-bottom:8pt; }
h2 { font-size:14pt; margin:22pt 0 8pt; padding:5pt 8pt; background:#2b3a4a; color:#fff;
     page-break-after:avoid; }
h3 { font-size:12pt; margin:15pt 0 6pt; color:#16324f; border-left:3pt solid #2b6cb0;
     padding-left:7pt; page-break-after:avoid; }
h4 { font-size:11pt; margin:11pt 0 5pt; page-break-after:avoid; }
p { margin:0 0 6pt; }
code { font-family:Menlo,monospace; font-size:9pt; background:#eef1f4; padding:0 3pt;
       border-radius:2pt; }
pre { font-family:Menlo,monospace; font-size:7.6pt; line-height:1.4; background:#f7f8fa;
      border:0.6pt solid #c3cad2; border-left:2.5pt solid #2b6cb0; padding:7pt 9pt;
      white-space:pre-wrap; word-break:break-word; margin:5pt 0 9pt; }
table { border-collapse:collapse; width:100%; margin:6pt 0 10pt; font-size:9pt; }
tr { page-break-inside:avoid; }
thead { display:table-header-group; }
table.small { font-size:7.8pt; }
th,td { border:0.6pt solid #8a939c; padding:3pt 4pt; vertical-align:top; }
th { background:#e3e8ee; font-weight:700; }
ul,ol { margin:3pt 0 8pt; padding-left:1.6em; }
li { margin:0 0 3pt; }
figure { margin:8pt 0 10pt; text-align:center; page-break-inside:avoid; }
figure img { max-width:100%; max-height:112mm; object-fit:contain;
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
