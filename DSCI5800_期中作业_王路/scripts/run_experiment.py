#!/usr/bin/env python3
"""Runner for the CoT / parameter-tuning experiment.

Every API call is logged verbatim (request params + full response) to runs/*.json
so that the report can be audited. Nothing is post-edited.
"""
import json, os, re, sys, time, urllib.request, urllib.error, datetime, hashlib

_HERE = os.path.dirname(os.path.abspath(__file__))
# Scripts live in scripts/; data lives one level up. Support both layouts so the
# folder can be copied anywhere without editing paths.
ROOT = _HERE if os.path.isdir(os.path.join(_HERE, "prompts")) else os.path.dirname(_HERE)
RUNS = os.path.join(ROOT, "runs")
API = "https://bifrost.advai.net/v1/chat/completions"
MODEL = "deepseek-v4.1-flash"


def api_key():
    txt = open(os.path.expanduser("~/.dsh/.credentials.yaml")).read()
    return re.search(r"ANEXTO_API_KEY:\s*(\S+)", txt).group(1).strip('"')


def call(prompt, temperature, top_p, max_tokens=2600, seed=None):
    body = {
        "model": MODEL,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    # NOTE: no `seed` is sent. Each repetition must be an independent draw so that
    # run-to-run variance under a given Temperature/Top-P setting is observable.
    req = urllib.request.Request(
        API,
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + api_key(), "Content-Type": "application/json"},
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as r:
        raw = json.loads(r.read())
    return body, raw, round(time.time() - t0, 2)


def save(name, prompt_file, body, raw, elapsed, note=""):
    msg = raw["choices"][0]["message"]
    content = msg.get("content") or ""
    reasoning = msg.get("reasoning") or ""
    rec = {
        "id": name,
        "note": note,
        "prompt_file": prompt_file,
        "request": body,
        "response_meta": {
            "model_returned": raw.get("model"),
            "finish_reason": raw["choices"][0].get("finish_reason"),
            "usage": raw.get("usage"),
            "id": raw.get("id"),
        },
        "elapsed_s": elapsed,
        "content": content,
        "reasoning_text_len": len(reasoning),
        "reasoning_text": reasoning,
        "content_sha256_12": hashlib.sha256(content.encode()).hexdigest()[:12],
        "timestamp": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    with open(os.path.join(RUNS, name + ".json"), "w") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    return rec


def strip_fence(s):
    s = s.strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", s, re.S)
    return m.group(1) if m else s


def main():
    os.makedirs(RUNS, exist_ok=True)
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    p1 = open(os.path.join(ROOT, "prompts/p1_baseline.txt")).read()
    p2 = open(os.path.join(ROOT, "prompts/p2_cot.txt")).read()
    fetch = {
        "P1": (p1, "p1_baseline.txt"),
        "P2": (p2, "p2_cot.txt"),
    }

    jobs = []
    if which in ("all", "baseline"):
        jobs.append(("baseline_T0.2_P0.3", "P1", 0.2, 0.3, 1, "基线：简单提示，低创造性设置"))
    if which in ("all", "main"):
        settings = [
            ("run1", 0.2, 0.3),
            ("run2", 0.7, 0.9),
            ("run3", 1.0, 0.95),
            ("run4", 1.2, 1.0),
        ]
        for tag, t, p in settings:
            for rep in (1, 2, 3):
                jobs.append((f"{tag}_rep{rep}", "P2", t, p, rep,
                             f"主实验 {tag}（T={t}, P={p}）第 {rep} 次重复，用于观察一致性"))

    for name, key, t, p, seed, note in jobs:
        prompt, pfile = fetch[key]
        target = os.path.join(RUNS, name + ".json")
        if os.path.exists(target):
            print("skip", name)
            continue
        for attempt in range(3):
            try:
                body, raw, el = call(prompt, t, p, seed=seed)
                rec = save(name, pfile, body, raw, el, note)
                print(f"{name}: T={t} P={p} chars={len(rec['content'])} "
                      f"reasoning_len={rec['reasoning_text_len']} {el}s")
                break
            except Exception as e:
                print("retry", name, repr(e)[:200])
                time.sleep(5)
        else:
            print("FAILED", name)


if __name__ == "__main__":
    main()
