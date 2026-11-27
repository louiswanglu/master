"""Normalise Chinese quotation marks in report.html text nodes.

All “ ” and " inside text nodes are re-assigned alternately (open, close, open, ...)
in document order, so that every pair is consistent even when a quoted phrase spans
an inline tag. Text inside <pre> and <code> is left untouched.
"""
import re, sys

path = sys.argv[1] if len(sys.argv) > 1 else "report.html"
h = open(path).read()

body_start = h.index("<body>")
head, body = h[:body_start], h[body_start:]

# mask <pre>...</pre> and <code>...</code>
masked = []
def mask(m):
    masked.append(m.group(0))
    return f"\x00{len(masked)-1}\x00"
work = re.sub(r"<pre.*?</pre>|<code>.*?</code>", mask, body, flags=re.S)

out = []
in_tag = False
state = 0            # 0 -> expect opener
pending_ascii = False
for ch in work:
    if ch == "<":
        in_tag = True
        out.append(ch); continue
    if ch == ">":
        in_tag = False
        out.append(ch); continue
    if not in_tag and ch in '"“”':
        out.append("“" if state == 0 else "”")
        state = 1 - state
        continue
    out.append(ch)

work = "".join(out)
assert state == 0, "unbalanced quotation marks in text nodes"

work = re.sub(r"\x00(\d+)\x00", lambda m: masked[int(m.group(1))], work)
open(path, "w").write(head + work)

t = re.sub(r"(<pre.*?</pre>|<code>.*?</code>)", "", work, flags=re.S)
t = re.sub(r"<[^>]+>", "", t)
print("open:", t.count("“"), "close:", t.count("”"), "ascii:", t.count('"'))
