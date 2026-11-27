#!/usr/bin/env python3
"""Render 手动完成指南.md to a printable PDF (A4, checklist boxes).

Markdown subset handled: # ## ### headings, tables, ``` fences, - [ ] checkboxes,
> blockquotes, --- rules, **bold**, `code`, nested list items.
"""
import html, os, re, subprocess, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = _HERE if os.path.isdir(os.path.join(_HERE, "prompts")) else os.path.dirname(_HERE)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC = os.path.join(ROOT, "手动完成指南.md")
HTML_OUT = os.path.join(ROOT, "guide.html")
PDF_OUT = os.path.join(ROOT, "DSCI5800_手动完成指南.pdf")


def inline(s):
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    return s


def md_to_html(md):
    lines = md.split("\n")
    out, i = [], 0
    in_list = None          # None | "ul" | "ol"
    li_index = None         # index in `out` of the currently open <li>, for续行拼接

    def close_list():
        nonlocal in_list, li_index
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None
        li_index = None

    def append_continuation(text):
        """A plain line right after a list item belongs to that item."""
        nonlocal li_index
        if li_index is not None:
            # out[li_index] looks like '<li ...>....</li>'
            cur = out[li_index]
            assert cur.endswith("</li>")
            out[li_index] = cur[: -len("</li>")] + " " + inline(text) + "</li>"
            return True
        return False

    while i < len(lines):
        ln = lines[i]

        if ln.startswith("```"):
            close_list()
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(html.escape(lines[i]))
                i += 1
            out.append("<pre>" + "\n".join(block) + "</pre>")
            i += 1
            continue

        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            close_list()
            header = [c.strip() for c in ln.strip().strip("|").split("|")]
            aligns = []
            for c in lines[i + 1].strip().strip("|").split("|"):
                c = c.strip()
                aligns.append("center" if c.startswith(":") and c.endswith(":") else
                              "right" if c.endswith(":") else "left")
            i += 2
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f'<th style="text-align:{aligns[k] if k < len(aligns) else "left"}">{inline(c)}</th>'
                         for k, c in enumerate(header))
            body = ""
            for r in rows:
                tds = "".join(f'<td style="text-align:{aligns[k] if k < len(aligns) else "left"}">{inline(c)}</td>'
                              for k, c in enumerate(r))
                body += f"<tr>{tds}</tr>"
            out.append(f"<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>")
            continue

        if re.match(r"^\s*- \[ \]", ln):
            if not in_list:
                out.append("<ul>")
                in_list = "ul"
            text = re.sub(r"^\s*- \[ \]\s*", "", ln)
            out.append(f'<li class="ck"><span class="box"></span>{inline(text)}</li>')
            li_index = len(out) - 1
            i += 1
            continue

        if re.match(r"^\s*[-*] ", ln):
            if not in_list:
                out.append("<ul>")
                in_list = "ul"
            text = re.sub(r"^\s*[-*] ", "", ln)
            out.append(f"<li>{inline(text)}</li>")
            li_index = len(out) - 1
            i += 1
            continue

        if re.match(r"^\s*\d+\.\s", ln):
            if not in_list:
                out.append("<ol>")
                in_list = "ol"
            out.append(f"<li>{inline(re.sub(r'^\s*\d+\.\s', '', ln))}</li>")
            li_index = len(out) - 1
            i += 1
            continue

        if ln.strip() == "---":
            close_list()
            out.append("<hr>")
            i += 1
            continue

        if ln.startswith(">"):
            close_list()
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> "))
                i += 1
            out.append('<div class="quote">' + "<br>".join(inline(b) for b in buf) + "</div>")
            continue

        # 续行：列表打开时，缩进 ≥2 空格 或 以破折号/但/且 开头的非空行
        if in_list and li_index is not None and ln.startswith(("  ", "\t")):
            append_continuation(ln.strip())
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            close_list()
            lv = len(m.group(1))
            out.append(f"<h{lv}>{inline(m.group(2))}</h{lv}>")
            i += 1
            continue

        if not ln.strip():
            close_list()
            i += 1
            continue

        close_list()
        out.append(f"<p>{inline(ln)}</p>")
        i += 1

    close_list()
    return "\n".join(out)


CSS = """
@page { size: A4; margin: 18mm 16mm 16mm 16mm; }
body { font-family:"Songti SC","STSong","Times New Roman",serif; font-size:10.5pt;
       line-height:1.55; color:#111; }
h1 { font-size:19pt; margin:0 0 14pt; padding-bottom:6pt; border-bottom:2pt solid #222; }
h2 { font-size:14pt; margin:22pt 0 8pt; padding:5pt 8pt; background:#2b3a4a; color:#fff;
     page-break-after:avoid; }
h3 { font-size:11.5pt; margin:14pt 0 6pt; color:#1a3a5c; border-left:3pt solid #2b6cb0;
     padding-left:7pt; page-break-after:avoid; }
h4 { font-size:11pt; margin:11pt 0 5pt; page-break-after:avoid; }
p { margin:0 0 6pt; }
code { font-family:Menlo,monospace; font-size:9pt; background:#eef1f4; padding:0 3pt;
       border-radius:2pt; }
pre { font-family:Menlo,monospace; font-size:8.6pt; line-height:1.45; background:#f7f8fa;
      border:0.7pt solid #c3cad2; border-left:3pt solid #2b6cb0; padding:8pt 10pt;
      white-space:pre-wrap; word-break:break-word; margin:5pt 0 9pt; page-break-inside:avoid; }
table { border-collapse:collapse; width:100%; margin:6pt 0 10pt; font-size:9.3pt;
        page-break-inside:avoid; }
th,td { border:0.7pt solid #8a939c; padding:3.5pt 5pt; vertical-align:top; }
th { background:#e3e8ee; font-weight:700; }
ul,ol { margin:3pt 0 8pt; padding-left:1.5em; }
li { margin:0 0 3pt; }
li.ck { list-style:none; margin-left:-1.2em; }
span.box { display:inline-block; width:9pt; height:9pt; border:1.1pt solid #333;
           margin-right:6pt; vertical-align:-1pt; background:#fff; }
.quote { background:#fffbe8; border:0.7pt solid #d9c377; border-left:3pt solid #c9a227;
         padding:7pt 10pt; margin:6pt 0 9pt; font-size:9.8pt; page-break-inside:avoid; }
hr { border:0; border-top:0.7pt dashed #aaa; margin:16pt 0 4pt; }
"""

md = open(SRC).read()
html_doc = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>DSCI5800 期中作业 · 手动完成指南</title><style>{CSS}</style></head>
<body>{md_to_html(md)}</body></html>"""
open(HTML_OUT, "w").write(html_doc)
print("guide.html", len(html_doc), "chars")

r = subprocess.run([
    "/Users/wanglu/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/node/bin/node",
    os.path.join(ROOT, "scripts", "print_pdf.js"), HTML_OUT, PDF_OUT],
    capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[:400])
