#!/usr/bin/env python3
"""Build analysis.json: consistency metrics, judge scores (v1/v2/v3), objective checks."""
import json, os, re, statistics, itertools

_HERE = os.path.dirname(os.path.abspath(__file__))
# Scripts live in scripts/; data lives one level up. Support both layouts so the
# folder can be copied anywhere without editing paths.
ROOT = _HERE if os.path.isdir(os.path.join(_HERE, "prompts")) else os.path.dirname(_HERE)
RUNS = os.path.join(ROOT, "runs")
CATS = ["约束满足度", "数据集使用正确性", "推理摘要质量", "结构化输出有效性",
        "提示注入警觉性", "实施方案可行性", "清晰度与简洁性"]
SETS = {"run1": (0.2, 0.3), "run2": (0.7, 0.9), "run3": (1.0, 0.95), "run4": (1.2, 1.0)}


def bigrams(s):
    s = re.sub(r"\s+", "", s)
    return set(s[i:i + 2] for i in range(len(s) - 1))


def jac(a, b):
    A, B = bigrams(a), bigrams(b)
    return len(A & B) / len(A | B) if A | B else 1.0


def parse_v1v2(c):
    d = {}
    for line in c.splitlines():
        if line.startswith("|") and "---" not in line and "类别" not in line:
            p = [x.strip() for x in line.strip("|").split("|")]
            if len(p) >= 2 and re.fullmatch(r"[1-5]", p[1]):
                d[p[0]] = int(p[1])
    return d


def parse_v3(c):
    d = {}
    for line in c.splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        p = [x.strip() for x in line.strip("|").split("|")]
        if len(p) >= 5 and p[0] in CATS and re.fullmatch(r"[1-5]", p[3]):
            d[p[0]] = int(p[3])
    return d


out = {"runs": {}, "baseline": {}, "judge_versions": {}}

# ---------- consistency ----------
for k, (t, p) in SETS.items():
    recs = [json.load(open(os.path.join(RUNS, f"{k}_rep{i}.json"))) for i in (1, 2, 3)]
    objs = [json.loads(r["content"]) for r in recs]
    fields = {
        "reasoning_summary": [" ".join(o["reasoning_summary"]) for o in objs],
        "implementation_plan": [" ".join(o["implementation_plan"]) for o in objs],
        "prompt_injection_handling": [o["prompt_injection_handling"] for o in objs],
        "one_sentence_answer": [o["one_sentence_answer"] for o in objs],
        "whole_json": [r["content"] for r in recs],
    }
    cons = {}
    for f, vals in fields.items():
        cons[f] = round(statistics.mean(jac(a, b) for a, b in itertools.combinations(vals, 2)), 3)
    cons["mean_chain_chars"] = round(statistics.mean(
        sum(len(x) for x in o["reasoning_summary"]) for o in objs))
    cons["mean_out_chars"] = round(statistics.mean(len(r["content"]) for r in recs))
    cons["reasoning_tokens"] = [r["response_meta"]["usage"]["completion_tokens_details"]["reasoning_tokens"] for r in recs]
    cons["completion_tokens"] = [r["response_meta"]["usage"]["completion_tokens"] for r in recs]
    cons["elapsed_s"] = [r["elapsed_s"] for r in recs]
    cons["risk_counts"] = [len(o["risks_and_mitigations"]) for o in objs]
    cons["opt"] = [o["recommended_option"] for o in objs]
    cons["scores"] = [o["weighted_scores"] for o in objs]
    cons["feas_all_true"] = [all(o["feasibility_check"].values()) for o in objs]
    cons["valid_json"] = [True for _ in objs]
    out["runs"][k] = {"T": t, "P": p, **cons}

# ---------- baseline ----------
b = json.load(open(os.path.join(RUNS, "baseline_T0.2_P0.3.json")))
out["baseline"] = {"T": b["request"]["temperature"], "P": b["request"]["top_p"],
                   "chars": len(b["content"]),
                   "reasoning_tokens": b["response_meta"]["usage"]["completion_tokens_details"]["reasoning_tokens"],
                   "elapsed_s": b["elapsed_s"], "valid_json": False}

# ---------- judge versions ----------
for ver in ("", "v2", "v3"):
    scores = {}
    for f in os.listdir(RUNS):
        if not f.startswith("judge" + ver + "_"):
            continue
        if ver == "" and f.startswith("judgev"):
            continue
        key = f.replace(".json", "").replace("judge" + ver + "_", "")
        c = json.load(open(os.path.join(RUNS, f)))["content"]
        d = parse_v3(c) if ver == "v3" else parse_v1v2(c)
        scores[key] = {"cat": d, "total": sum(d.values()), "n": len(d)}
    out["judge_versions"][ver or "v1"] = scores

os.makedirs(os.path.join(ROOT, "source"), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, "source", "analysis.json"), "w"), ensure_ascii=False, indent=2)

# ---------- print summary ----------
for k, v in out["runs"].items():
    js = [out["judge_versions"]["v3"][f"{k}_rep{i}"]["total"] for i in (1, 2, 3)]
    print(f"{k} T={v['T']} P={v['P']} judge_v3={js} mean={statistics.mean(js):.2f} "
          f"cons(chain)={v['reasoning_summary']:.3f} cons(impl)={v['implementation_plan']:.3f} "
          f"chain_chars={v['mean_chain_chars']}")
for ver in ("v1", "v2", "v3"):
    s = out["judge_versions"][ver]
    bl = s.get("baseline_T0.2_P0.3", {}).get("total")
    means = {k: statistics.mean(s[f"{k}_rep{i}"]["total"] for i in (1, 2, 3)) for k in SETS}
    print(f"judge {ver}: baseline={bl} " + " ".join(f"{k}={v:.2f}" for k, v in means.items()))
