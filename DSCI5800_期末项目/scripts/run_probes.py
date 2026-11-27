#!/usr/bin/env python3
"""Adversarial probe runner.

Each probe is an independent short conversation (fresh context) that targets ONE
specific guardrail class: indirect prompt leakage, fake authority, role-play
jailbreak, fake database access, document-embedded injection, outcome guarantees,
and out-of-scope professional advice. Independence matters: a probe must not be
able to lean on the 10-turn context.

Results are logged verbatim to runs/probe_<sp>_<id>.json
"""
import json, os, re, sys, time, datetime, urllib.request

# 本脚本位于 scripts/，项目根目录需要再上移一级
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(ROOT, "runs")
API = "https://bifrost.advai.net/v1/chat/completions"
MODEL = "gpt-5.5"


def api_key():
    txt = open(os.path.expanduser("~/.dsh/.credentials.yaml")).read()
    return re.search(r"ANEXTO_API_KEY:\s*(\S+)", txt).group(1).strip('"')


def post(body):
    req = urllib.request.Request(
        API, data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + api_key(), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())


def main():
    sp_tag = sys.argv[1]          # v1 / v2
    sp_file = "sp_%s.txt" % sp_tag
    sp = open(os.path.join(ROOT, "prompts", sp_file)).read().strip()
    probes = json.load(open(os.path.join(ROOT, "prompts", "probes.json")))["scenarios"]
    for p in probes:
        out = os.path.join(RUNS, "probe_%s_%s.json" % (sp_tag, p["id"]))
        if os.path.exists(out):
            print("skip", p["id"]); continue
        msgs = [{"role": "system", "content": sp}]
        turns = []
        for u in p["messages"]:
            msgs.append({"role": "user", "content": u})
            body = {"model": MODEL, "messages": msgs, "temperature": 0.8, "max_tokens": 1200}
            for _ in range(4):
                try:
                    raw = post(body); break
                except Exception as e:
                    print("  retry", repr(e)[:120]); time.sleep(4)
            c = raw["choices"][0]["message"].get("content") or ""
            msgs.append({"role": "assistant", "content": c})
            turns.append({"user": u, "assistant": c})
            time.sleep(1)
        rec = {"id": p["id"], "sp": sp_tag, "tests": p["tests"], "turns": turns,
               "timestamp": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
        with open(out, "w") as f:
            json.dump(rec, f, ensure_ascii=False, indent=2)
        print("%s %s: %d chars" % (sp_tag, p["id"], sum(len(t["assistant"]) for t in turns)))


if __name__ == "__main__":
    main()
