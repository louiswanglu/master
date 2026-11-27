import os, subprocess, sys
from pypdf import PdfReader, PdfWriter
src = sys.argv[1]; outdir = sys.argv[2]
pages = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv)>3 else None
os.makedirs(outdir, exist_ok=True)
r = PdfReader(src); n = len(r.pages)
for i in range(n):
    if pages and (i+1) not in pages: continue
    w = PdfWriter(); w.add_page(r.pages[i])
    tmp = os.path.join(outdir, f"_p{i+1}.pdf")
    with open(tmp,"wb") as f: w.write(f)
    png = os.path.join(outdir, f"page{i+1:02d}.png")
    subprocess.run(["sips","-s","format","png","-Z","1600",tmp,"--out",png],
                   capture_output=True)
    os.remove(tmp)
print("done", n)
