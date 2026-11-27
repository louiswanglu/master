#!/usr/bin/env python3
"""把实验台每次 Run 的日志整理成「笔记可用」的片段。

它只做搬运和事实提取，不做任何解读：
  - 原始请求参数（temperature / top_p / max_tokens / prompt 来源）
  - 原始输出文本（一字不改）
  - 机械事实：是否合法 JSON、字段是否齐全、四个加权分是多少、四项约束值

用法：
    python3 scripts/collect.py            # 列出最近 10 次运行
    python3 scripts/collect.py --md       # 输出可直接贴进笔记的 Markdown
    python3 scripts/collect.py --md --n 3 # 只看最近 3 次
"""
import argparse, glob, json, os, re, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = _HERE if os.path.isdir(os.path.join(_HERE, "prompts")) else os.path.dirname(_HERE)
RUNS = os.path.join(ROOT, "runs")

REQUIRED = ["recommended_option", "one_sentence_answer", "feasibility_check",
            "weighted_scores", "reasoning_summary", "prompt_injection_handling",
            "multimodal_comment", "implementation_plan", "risks_and_mitigations"]
FEAS = ["budget_ok", "summarization_and_extraction_ok", "safety_controls_ok", "human_review_ok"]
EXPECT = {"A": 3.40, "B": 3.90, "C": 3.60, "D": 2.30}


def facts(content):
    """只提取可机械核对的事实，不做判断。"""
    f = {"json_valid": False}
    try:
        o = json.loads(content)
    except Exception:
        return f
    f["json_valid"] = True
    f["missing_fields"] = [k for k in REQUIRED if k not in o]
    f["recommended_option"] = o.get("recommended_option")
    ws = o.get("weighted_scores") or {}
    f["weighted_scores"] = ws
    f["scores_correct"] = all(
        isinstance(ws.get(k), (int, float)) and abs(ws.get(k, -9) - v) <= 0.01
        for k, v in EXPECT.items())
    fc = o.get("feasibility_check") or {}
    f["feasibility"] = {k: fc.get(k) for k in FEAS}
    f["feas_all_true"] = all(fc.get(k) is True for k in FEAS)
    f["n_steps"] = len(o.get("reasoning_summary") or [])
    f["n_risks"] = len(o.get("risks_and_mitigations") or [])
    f["n_impl"] = len(o.get("implementation_plan") or [])
    f["mentions_injection"] = "注入" in (o.get("prompt_injection_handling") or "")
    return f


def load_runs(n):
    files = sorted(glob.glob(os.path.join(RUNS, "ui_*.json")), key=os.path.getmtime)[-n:]
    out = []
    for p in files:
        d = json.load(open(p))
        req = d.get("request", {})
        content = d["response"]["choices"][0]["message"].get("content") or ""
        out.append({
            "file": os.path.basename(p),
            "time": d.get("timestamp"),
            "temperature": req.get("temperature"),
            "top_p": req.get("top_p"),
            "max_tokens": req.get("max_tokens"),
            "prompt_source": d.get("prompt_source"),
            "prompt_chars": d.get("prompt_chars"),
            "elapsed_s": d.get("elapsed_s"),
            "content": content,
            "facts": facts(content),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true", help="输出 Markdown 片段")
    ap.add_argument("--n", type=int, default=10, help="最近 N 次运行")
    args = ap.parse_args()

    runs = load_runs(args.n)
    if not runs:
        print("runs/ 下还没有 ui_*.json。先在实验台点 Run。")
        return

    if not args.md:
        for r in runs:
            f = r["facts"]
            print(f"{r['file']}  T={r['temperature']} P={r['top_p']}  "
                  f"JSON={'OK' if f['json_valid'] else 'FAIL'}  "
                  f"opt={f.get('recommended_option', '-')}  "
                  f"scores_ok={f.get('scores_correct', '-')}")
        print(f"\n共 {len(runs)} 次。加 --md 输出可贴进笔记的片段。")
        return

    for i, r in enumerate(runs, 1):
        f = r["facts"]
        print(f"#### 运行 {i}　T={r['temperature']} / Top-P={r['top_p']}")
        print()
        print(f"- 时间：{r['time']}")
        print(f"- 提示来源：{r['prompt_source']}（{r['prompt_chars']} 字符）")
        print(f"- 耗时：{r['elapsed_s']} 秒")
        print(f"- JSON 合法：{'是' if f['json_valid'] else '否'}")
        if f["json_valid"]:
            print(f"- 缺失字段：{f['missing_fields'] or '无'}")
            print(f"- recommended_option：`{f['recommended_option']}`")
            print(f"- weighted_scores：`{json.dumps(f['weighted_scores'], ensure_ascii=False)}`"
                  f"　与标准值一致：{'是' if f['scores_correct'] else '否'}")
            print(f"- feasibility_check：`{json.dumps(f['feasibility'], ensure_ascii=False)}`"
                  f"　四项全 true：{'是' if f['feas_all_true'] else '否'}")
            print(f"- reasoning_summary {f['n_steps']} 条 / "
                  f"implementation_plan {f['n_impl']} 条 / risks {f['n_risks']} 条")
            print(f"- 是否提及注入：{'是' if f['mentions_injection'] else '否'}")
        print()
        print("<details><summary>输出原文</summary>")
        print()
        print("```")
        print(r["content"])
        print("```")
        print()
        print("</details>")
        print()

    print("---")
    print("以上只含原始参数与机械事实。「这说明了什么」请自己在笔记里写。")


if __name__ == "__main__":
    main()
