#!/usr/bin/env python3
"""LLM-as-a-judge runner.

The judge prompt (p3_judge.txt) is kept verbatim; only the %%OUTPUT%% slot is filled
with the exact text produced by a candidate run. The judge itself is run at a fixed
low-creativity setting (T=0.1, P=0.3) so that judging variance does not confound the
comparison of the candidate runs.
"""
import json, os, re, sys, time, urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
# Scripts live in scripts/; data lives one level up. Support both layouts so the
# folder can be copied anywhere without editing paths.
ROOT = _HERE if os.path.isdir(os.path.join(_HERE, "prompts")) else os.path.dirname(_HERE)
RUNS = os.path.join(ROOT, "runs")
API = "https://bifrost.advai.net/v1/chat/completions"
MODEL = "deepseek-v4.1-flash"
JUDGE_T, JUDGE_P = 0.1, 0.3


def api_key():
    txt = open(os.path.expanduser("~/.dsh/.credentials.yaml")).read()
    return re.search(r"ANEXTO_API_KEY:\s*(\S+)", txt).group(1).strip('"')


def call(prompt, temperature, top_p, max_tokens=2000):
    body = {"model": MODEL, "temperature": temperature, "top_p": top_p,
            "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + api_key(),
                                          "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as r:
        raw = json.loads(r.read())
    return body, raw, round(time.time() - t0, 2)


def parse_v3(c):
    """Return (scores dict, per-dim checkpoints hit, flaws) from the v3 table."""
    out = {}
    for line in c.splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        p = [x.strip() for x in line.strip("|").split("|")]
        if len(p) < 5:
            continue
        if p[0] in ("类别",) or not re.fullmatch(r"[1-5]", p[3] if len(p) > 3 else ""):
            continue
        try:
            out[p[0]] = int(p[3])
        except Exception:
            pass
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tplfile = "p3_judge.txt"
    suffix = ""
    for a in sys.argv[1:]:
        if a.startswith("--template="):
            tplfile = a.split("=", 1)[1]
        if a.startswith("--suffix="):
            suffix = a.split("=", 1)[1]
    targets = args
    tpl = open(os.path.join(ROOT, "prompts", tplfile)).read()
    for name in targets:
        out_path = os.path.join(RUNS, "judge" + suffix + "_" + name + ".json")
        if os.path.exists(out_path):
            print("skip", name)
            continue
        cand = json.load(open(os.path.join(RUNS, name + ".json")))
        prompt = tpl.replace("%%OUTPUT%%", cand["content"])
        for attempt in range(3):
            try:
                body, raw, el = call(prompt, JUDGE_T, JUDGE_P)
                rec = {
                    "id": "judge" + suffix + "_" + name,
                    "judged_run": name,
                    "judged_run_params": {"temperature": cand["request"]["temperature"],
                                          "top_p": cand["request"]["top_p"]},
                    "judge_request": body,
                    "prompt_file": tplfile,
                    "response_meta": {"model_returned": raw.get("model"),
                                      "usage": raw.get("usage"),
                                      "finish_reason": raw["choices"][0].get("finish_reason")},
                    "elapsed_s": el,
                    "content": raw["choices"][0]["message"].get("content") or "",
                }
                json.dump(rec, open(out_path, "w"), ensure_ascii=False, indent=2)
                print("judged", name, len(rec["content"]), el)
                break
            except Exception as e:
                print("retry", name, repr(e)[:150]); time.sleep(4)


if __name__ == "__main__":
    main()
