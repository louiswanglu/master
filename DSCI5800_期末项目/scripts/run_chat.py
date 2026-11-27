#!/usr/bin/env python3
"""HPU Academic Success Coach -- 10-turn stress test runner.

Each run = ONE conversation: the system prompt is sent as the `system` message,
then the 10 student turns are appended one by one, always resending the full
history (this is how a normal ChatGPT conversation behaves).

Every request/response pair is logged verbatim to runs/<tag>.json so the report's
transcript can be audited against the raw API traffic.
"""
import json, os, re, sys, time, datetime, hashlib, urllib.request

# 本脚本位于 scripts/，项目根目录需要再上移一级
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(ROOT, "runs")
API = "https://bifrost.advai.net/v1/chat/completions"


def api_key():
    txt = open(os.path.expanduser("~/.dsh/.credentials.yaml")).read()
    return re.search(r"ANEXTO_API_KEY:\s*(\S+)", txt).group(1).strip('"')


def post(body, timeout=300):
    req = urllib.request.Request(
        API, data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + api_key(), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def run(tag, model, sp_file, turns, temperature=0.8, max_tokens=1500, note=""):
    sp = open(os.path.join(ROOT, "prompts", sp_file)).read().strip()
    messages = [{"role": "system", "content": sp}]
    rec = {"tag": tag, "model_requested": model, "sp_file": sp_file, "note": note,
           "temperature": temperature, "max_tokens": max_tokens, "turns": [],
           "started": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
    for i, u in enumerate(turns, 1):
        messages.append({"role": "user", "content": u})
        body = {"model": model, "messages": messages, "temperature": temperature,
                "max_tokens": max_tokens}
        t0 = time.time()
        for attempt in range(4):
            try:
                raw = post(body)
                break
            except Exception as e:
                print("  retry", tag, i, repr(e)[:160])
                time.sleep(4)
        else:
            raise SystemExit("failed turn %d" % i)
        msg = raw["choices"][0]["message"]
        content = msg.get("content") or ""
        messages.append({"role": "assistant", "content": content})
        rec["turns"].append({
            "turn": i, "user": u, "assistant": content,
            "reasoning_text": msg.get("reasoning") or "",
            "elapsed_s": round(time.time() - t0, 2),
            "usage": raw.get("usage"),
            "model_returned": raw.get("model"),
            "finish_reason": raw["choices"][0].get("finish_reason"),
            "sha256_12": hashlib.sha256(content.encode()).hexdigest()[:12],
        })
        print("%s T%d: %d chars  %ss" % (tag, i, len(content), rec["turns"][-1]["elapsed_s"]))
    rec["finished"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    os.makedirs(RUNS, exist_ok=True)
    with open(os.path.join(RUNS, tag + ".json"), "w") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    return rec


def main():
    jobs = {
        "v1": ("gpt-5.5", "sp_v1.txt", 0.8,
               "第一版提示词：首次 10 轮压力测试，ChatGPT 平台"),
        "v1_r2": ("gpt-5.5", "sp_v1.txt", 0.8,
                  "第一版提示词：重复运行，检查结果稳定性"),
        "v2": ("gpt-5.5", "sp_v2.txt", 0.8,
               "第二版提示词（修订后）：同一 10 轮脚本，验证改动是否生效"),
        "v2_r2": ("gpt-5.5", "sp_v2.txt", 0.8,
                  "第二版提示词：重复运行，检查稳定性"),
        "base": ("gpt-5.5", "sp_base.txt", 0.8,
                 "对照运行：无角色设定的通用助手，用于检验测试是否具有区分度"),
    }
    which = sys.argv[1:] or ["v1"]
    turns = json.load(open(os.path.join(ROOT, "prompts", "turns.json")))["turns"]
    for w in which:
        model, spf, t, note = jobs[w]
        target = os.path.join(RUNS, w + ".json")
        if os.path.exists(target):
            print("skip", w)
            continue
        run(w, model, spf, turns, temperature=t, note=note)


if __name__ == "__main__":
    main()
