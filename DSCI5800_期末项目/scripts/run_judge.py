#!/usr/bin/env python3
"""LLM-as-a-judge runner.

Judge prompt = assignment's required rubric text (judge_prompt.txt) with the
system prompt and the 10-turn transcript substituted in. The judge runs at a low
temperature (0.2) so scoring variance does not confound comparison.

Primary judge  : deepseek-v4-pro   (different vendor from the tested gpt-5.5)
Secondary judge: kimi-k3.1-pro     (used only to check inter-judge agreement)
"""
import json, os, re, sys, time, urllib.request

# 本脚本位于 scripts/，项目根目录需要再上移一级
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(ROOT, "runs")
API = "https://bifrost.advai.net/v1/chat/completions"


def api_key():
    return re.search(r"ANEXTO_API_KEY:\s*(\S+)",
                     open(os.path.expanduser("~/.dsh/.credentials.yaml")).read()).group(1).strip('"')


def transcript_md(rec):
    out = []
    for t in rec["turns"]:
        out.append("**Turn %d**\n学生：%s\n助手：%s\n" % (t["turn"], t["user"], t["assistant"]))
    return "\n".join(out)


def call(model, prompt, temperature=0.2, max_tokens=16000):
    body = {"model": model, "max_tokens": 8000 if model.startswith("kimi") else max_tokens,
            "messages": [{"role": "user", "content": prompt}]}
    # kimi-k3.1-pro rejects the `temperature` parameter at this gateway, so it is omitted
    # for that model; the sampling then follows the provider default.
    if not model.startswith("kimi"):
        body["temperature"] = temperature
    req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + api_key(),
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        raw = json.loads(r.read())
    return body, raw


def main():
    model = sys.argv[1]
    tag = sys.argv[2]
    sp_file = sys.argv[3]
    tpl = open(os.path.join(ROOT, "prompts", "judge_prompt.txt")).read()
    sp = open(os.path.join(ROOT, "prompts", sp_file)).read().strip()
    rec = json.load(open(os.path.join(RUNS, tag + ".json")))
    prompt = tpl.replace("%%SYSTEM_PROMPT%%", sp).replace("%%TRANSCRIPT%%", transcript_md(rec))
    out = os.path.join(RUNS, "judge_%s_%s.json" % (model.replace(".", "_"), tag))
    if os.path.exists(out):
        print("skip", out); return
    body, raw = call(model, prompt)
    c = raw["choices"][0]["message"].get("content") or ""
    json.dump({"judge_model": model, "judged": tag, "sp_file": sp_file,
               "judge_prompt": prompt, "request": body,
               "response_meta": {"model_returned": raw.get("model"), "usage": raw.get("usage")},
               "content": c,
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")},
              open(out, "w"), ensure_ascii=False, indent=2)
    print("=== %s judged %s (%d chars) ===" % (model, tag, len(c)))
    print(c)


if __name__ == "__main__":
    main()
