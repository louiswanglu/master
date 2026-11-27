#!/usr/bin/env python3
"""Render the report figures from analysis.json (HTML -> PNG via headless Chrome)."""
import json, os, html, subprocess, statistics, tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
# Scripts live in scripts/; data lives one level up. Support both layouts so the
# folder can be copied anywhere without editing paths.
ROOT = _HERE if os.path.isdir(os.path.join(_HERE, "prompts")) else os.path.dirname(_HERE)
FIG = os.path.join(ROOT, "figures")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE = os.path.join(tempfile.gettempdir(), "dsh-fig-profile")
A = json.load(open(os.path.join(ROOT, "source", "analysis.json")))
CATS = ["约束满足度", "数据集使用正确性", "推理摘要质量", "结构化输出有效性",
        "提示注入警觉性", "实施方案可行性", "清晰度与简洁性"]
SHORT = ["约束", "数据集", "推理", "结构", "注入", "实施", "清晰"]
SETS = [("run1", "Run 1", 0.2, 0.3), ("run2", "Run 2", 0.7, 0.9),
        ("run3", "Run 3", 1.0, 0.95), ("run4", "Run 4", 1.2, 1.0)]
V3 = A["judge_versions"]["v3"]

CSS = """
*{box-sizing:border-box}
body{margin:0;padding:16px;background:#fff;font-family:"Times New Roman","Songti SC",serif;
     color:#111;font-size:13px}
h3{margin:0 0 3px;font-size:14.5px}
.sub{color:#555;font-size:11px;margin-bottom:10px}
table{border-collapse:collapse;width:100%;font-size:11px}
th,td{border:1px solid #b9bec6;padding:2.5px 5px}
th{background:#eef1f4;font-weight:700}
.mono{font-family:Menlo,monospace;font-size:10.2px}
.bar{display:inline-block;height:11px;vertical-align:middle}
"""


def shot(name, body, w, h, scale=2):
    p = os.path.join(FIG, name + ".html")
    open(p, "w").write(f"<!doctype html><meta charset='utf-8'><style>{CSS}</style>{body}")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--disable-crash-reporter", f"--user-data-dir={PROFILE}",
                    f"--screenshot={os.path.join(FIG, name + '.png')}",
                    f"--window-size={w},{h}", f"--force-device-scale-factor={scale}",
                    "--hide-scrollbars", "file://" + p], check=True, capture_output=True)


# ---------------- 图1：评审总分 + 逐维度 ----------------
tot = {k: [V3[f"{k}_rep{i}"]["total"] for i in (1, 2, 3)] for k, *_ in SETS}
rows = ""
for k, n, t, p in SETS:
    v = tot[k]
    rows += (f"<tr><td>{n}</td><td class='mono'>{t}</td><td class='mono'>{p}</td>"
             f"<td class='mono'>{v[0]} / {v[1]} / {v[2]}</td>"
             f"<td class='mono'><b>{statistics.mean(v):.2f}</b></td>"
             f"<td class='mono'>{max(v)-min(v)}</td></tr>")
bl = V3["baseline_T0.2_P0.3"]
rows += (f"<tr style='background:#fff5f0'><td>基线（无 CoT）</td><td class='mono'>0.2</td>"
         f"<td class='mono'>0.3</td><td class='mono'>{bl['total']}</td>"
         f"<td class='mono'><b>{float(bl['total']):.2f}</b></td><td class='mono'>—</td></tr>")

bars = ""
for k, n, t, p in SETS:
    m = statistics.mean(tot[k])
    bars += (f"<div style='margin:7px 0'><span style='display:inline-block;width:128px'>{n} "
             f"(T={t}, P={p})</span>"
             f"<span class='bar' style='background:#2b6cb0;width:{m/35*430:.0f}px'></span>"
             f"<span style='margin-left:6px'>{m:.2f}</span></div>")
bars += (f"<div style='margin:7px 0'><span style='display:inline-block;width:128px'>基线 (T=0.2, P=0.3)</span>"
         f"<span class='bar' style='background:#c05621;width:{bl['total']/35*430:.0f}px'></span>"
         f"<span style='margin-left:6px'>{bl['total']}.00</span></div>")

body = f"""

<div class="sub">评审器为同一模型在 T=0.1 / Top-P=0.3 下运行；基线为无 CoT 的简单提示。</div>
<table>
<tr><th>设置</th><th>Temperature</th><th>Top-P</th><th>三次得分</th><th>均值</th><th>极差</th></tr>
{rows}
</table>
<div style="margin-top:12px">{bars}</div>
"""
shot("fig_judge", body, 760, 290)

# ---------------- 图2：逐维度雷达式条形 ----------------
rows = ""
for i, c in enumerate(CATS):
    vals = [statistics.mean(V3[f"{k}_rep{i2}"]["cat"][c] for i2 in (1, 2, 3)) for k, *_ in SETS]
    cells = "".join(f"<td class='mono' style='text-align:center'>{v:.2f}</td>" for v in vals)
    bc = bl["cat"][c]
    rows += (f"<tr><td>{c}</td>{cells}"
             f"<td class='mono' style='text-align:center;background:#fff5f0'>{bc}</td>"
             f"<td><span class='bar' style='background:#cbd5e1;width:{bc*52:.0f}px'></span></td></tr>")
body = f"""

<div class="sub">每个维度由 3 个检查点构成，得分 = 2 + 命中检查点数 − 缺陷扣分。
灰度条为基线得分：结构化输出 1 分、实施方案 2 分、推理摘要 2 分，是 CoT 模板带来的最大增益。</div>
<table>
<tr><th style="width:150px">维度</th><th>Run 1</th><th>Run 2</th><th>Run 3</th><th>Run 4</th>
<th style="background:#fde8dd">基线</th><th style="width:230px">基线水平</th></tr>
{rows}
</table>
"""
shot("fig_dims", body, 760, 235)

# ---------------- 图3：一致性 ----------------
rows = ""
for k, n, t, p in SETS:
    r = A["runs"][k]
    rows += (f"<tr><td>{n}</td><td class='mono'>{t}</td><td class='mono'>{p}</td>"
             f"<td class='mono'>{r['reasoning_summary']:.3f}</td>"
             f"<td class='mono'>{r['implementation_plan']:.3f}</td>"
             f"<td class='mono'>{r['one_sentence_answer']:.3f}</td>"
             f"<td class='mono'>{r['mean_chain_chars']}</td>"
             f"<td class='mono'>{statistics.mean(r['reasoning_tokens']):.0f}</td></tr>")
bars = ""
for k, n, t, p in SETS:
    r = A["runs"][k]
    bars += (f"<div style='margin:6px 0'><span style='display:inline-block;width:150px'>{n} "
             f"(T={t}, P={p})</span>"
             f"<span class='bar' style='background:#2f855a;width:{r['reasoning_summary']*640:.0f}px'></span>"
             f"<span style='margin-left:6px'>{r['reasoning_summary']:.3f}</span>"
             f"<span style='color:#777;font-size:10px'> ← reasoning_summary</span></div>")
body = f"""

<div class="sub">指标为字符二元组 Jaccard 系数（1.000 = 完全相同）。四组均选 B、评分与约束结论完全一致，
差异集中在措辞与论证角度，而非结论。</div>
<table>
<tr><th>设置</th><th>Temp.</th><th>Top-P</th><th>reasoning_summary</th><th>implementation_plan</th>
<th>one_sentence_answer</th><th>链均字符</th><th>推理 token 均</th></tr>
{rows}
</table>
<div style="margin-top:12px">{bars}</div>
"""
shot("fig_consistency", body, 800, 270)

# ---------------- 图4：三次判分演进 ----------------
rows = ""
for ver, label in (("v1", "v1 未给全数据集"), ("v2", "v2 加入澄清说明"), ("v3", "v3 检查点制式（采用）")):
    s = A["judge_versions"][ver]
    vals = [statistics.mean(s[f"{k}_rep{i}"]["total"] for i in (1, 2, 3)) for k, *_ in SETS]
    bt = s["baseline_T0.2_P0.3"]["total"]
    sweep = max(vals) - min(vals)
    rows += (f"<tr><td>{label}</td><td class='mono'>{bt}</td>"
             + "".join(f"<td class='mono' style='text-align:center'>{v:.2f}</td>" for v in vals)
             + f"<td class='mono' style='text-align:center'>{statistics.mean(vals):.2f}</td>"
             f"<td class='mono' style='text-align:center'>{sweep:.2f}</td></tr>")
body = f"""

<div class="sub">v1 组间均值区间 32.33–33.00 分、v2 收窄至 34.33–34.67 分（区分度丧失）、v3 拉开至 33.33–34.33 分，
且基线从 24→26→22 分，与人工核对结论一致。</div>
<table>
<tr><th style="width:190px">评审提示词版本</th><th>基线</th><th>Run 1</th><th>Run 2</th><th>Run 3</th>
<th>Run 4</th><th>改进版均值</th><th>组间极差</th></tr>
{rows}
</table>
<div style="margin-top:10px;font-size:11px;color:#555">
判定标准：组间极差过小 → 失去区分度（v2 的缺陷）；基线分过高 → 评审过宽（v2 的缺陷）；
本报告采用 v3，并同时用两条客观指标（JSON 有效性、检查项命中数）交叉验证。</div>
"""
shot("fig_judge_versions", body, 780, 175)

print("figures regenerated")
