# -*- coding: utf-8 -*-
"""Add a centred page-number footer (Times New Roman 9pt) to the rendered PDF.

Chrome's headless print cannot number pages, so the numbers are stamped afterwards
with reportlab. The cover page is left unnumbered; body pages start at 1.
"""
import sys, io
import pypdf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

SRC, DST = sys.argv[1], sys.argv[2]
FONT = "/System/Library/Fonts/Supplemental/Times New Roman.ttf"
pdfmetrics.registerFont(TTFont("TNR", FONT))

reader = pypdf.PdfReader(SRC)
writer = pypdf.PdfWriter()
total = len(reader.pages) - 1

for i, page in enumerate(reader.pages):
    if i > 0:
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        c.setFont("TNR", 9)
        c.drawCentredString(letter[0] / 2.0, 40, "%d / %d" % (i, total))
        c.save()
        buf.seek(0)
        page.merge_page(pypdf.PdfReader(buf).pages[0])
    writer.add_page(page)

writer.add_metadata({
    "/Title": "DSCI5800 期末项目 — HPU 学业成功辅导员系统提示词设计与评估",
    "/Author": "王路",
    "/Subject": "Take-Home Final Project: Designing and Evaluating a System Prompt for the HPU Academic Success Coach",
    "/Keywords": "prompt engineering, LLM-as-a-judge, prompt injection, persona consistency",
})
with open(DST, "wb") as f:
    writer.write(f)
print("stamped", DST, total, "numbered pages")
