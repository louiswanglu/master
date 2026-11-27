# -*- coding: utf-8 -*-
"""Minimal Markdown -> HTML converter.

Covers exactly the subset produced by the tested assistant: ATX headings, fenced
code blocks, pipe tables, blockquotes, unordered/ordered lists, bold, inline code.
Kept dependency-free so the report build has no network requirement.
"""
import html
import re


def _inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


def _table(lines):
    rows = []
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        rows.append(cells)
    if len(rows) >= 2 and re.fullmatch(r"[\s:\-|]+", lines[1].strip()):
        header, body = rows[0], rows[2:]
    else:
        header, body = rows[0], rows[1:]
    out = ['<table class="tr-table"><thead><tr>']
    out += ["<th>%s</th>" % _inline(c) for c in header]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>" + "".join("<td>%s</td>" % _inline(c) for c in r) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def convert(text):
    lines = text.replace("\r\n", "\n").split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()

        if s.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre class=\"code\">%s</pre>" % "\n".join(buf))
            continue

        if not s:
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            lvl = min(len(m.group(1)) + 2, 6)
            out.append("<h%d class=\"tr-h\">%s</h%d>" % (lvl, _inline(m.group(2)), lvl))
            i += 1
            continue

        if s.startswith("|") and i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                buf.append(lines[i])
                i += 1
            out.append(_table(buf))
            continue

        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(_inline(lines[i].strip().lstrip(">")))
                i += 1
            out.append("<blockquote>%s</blockquote>" % "<br>".join(buf))
            continue

        if re.match(r"^\s*([-*+]|\d+\.)\s+", s):
            ordered = bool(re.match(r"^\s*\d+\.\s+", s))
            tag = "ol" if ordered else "ul"
            start = 1
            if ordered:
                start = int(re.match(r"^\s*(\d+)\.", s).group(1))
            buf = []
            while i < len(lines):
                cur = lines[i]
                if re.match(r"^\s*([-*+]|\d+\.)\s+", cur):
                    indent = len(cur) - len(cur.lstrip())
                    item = re.sub(r"^\s*([-*+]|\d+\.)\s+", "", cur)
                    style = "" if indent < 2 else ' style="margin-left:%dpx"' % (indent * 6)
                    buf.append([style, [item]])
                    i += 1
                elif cur.strip() and buf and (len(cur) - len(cur.lstrip())) >= 2 \
                        and not cur.strip().startswith(("```", "|", ">")):
                    # indented continuation of the current list item
                    buf[-1][1].append(cur.strip())
                    i += 1
                else:
                    break
            items = "".join(
                "<li%s>%s</li>" % (style, "<br>".join(_inline(x) for x in texts))
                for style, texts in buf)
            attr = ' start="%d"' % start if ordered and start != 1 else ""
            out.append("<%s%s>%s</%s>" % (tag, attr, items, tag))
            continue

        buf = []
        while i < len(lines):
            s2 = lines[i].strip()
            if not s2 or s2.startswith(("```", "|", ">", "#")) or re.match(r"^([-*+]|\d+\.)\s+", s2):
                break
            buf.append(_inline(s2))
            i += 1
        out.append("<p>%s</p>" % "<br>".join(buf))

    return "\n".join(out)
