#!/usr/bin/env python3
"""A tiny local client used to produce the screenshots in the report.

It is a real client: the page loaded in the browser performs an actual POST to
/v1/chat/completions through this server with the Temperature / Top-P shown on
screen, and renders the response that came back. Nothing is mocked.

Usage:  python3 ui_server.py 8765      (then open http://127.0.0.1:8765/)
"""
import json, os, re, sys, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

_HERE = os.path.dirname(os.path.abspath(__file__))
# Scripts live in scripts/; data lives one level up. Support both layouts so the
# folder can be copied anywhere without editing paths.
ROOT = _HERE if os.path.isdir(os.path.join(_HERE, "prompts")) else os.path.dirname(_HERE)
API = "https://bifrost.advai.net/v1/chat/completions"


def wants_json_output(prompt):
    """判断这条提示是否要求"以 JSON 输出"。

    否定句里也含 JSON，须区分两类：
      "不要输出 JSON"            -> 不要 JSON
      "不要输出 JSON 之外的文字" -> 恰恰要 JSON
      "只输出 JSON，不要解释"    -> 要 JSON（否定词在 JSON 之后，管的是"解释"）
    因此：只有"否定词出现在 JSON 之前且紧邻"才判为不要；"JSON 之外/以外"判为要。
    """
    up = prompt.upper()

    # 正向强信号："JSON 之外/以外/外" 把 JSON 设为唯一允许格式
    if re.search(r"JSON\s*(之外|以外)", up):
        return True

    # 否定信号：否定词必须出现在 JSON 之前，且中间不含句读
    if re.search(r"(不要|不得|无需|不需要|不必|别)[^。，；\n]{0,10}JSON", up):
        return False
    if re.search(r"JSON[^。，；\n]{0,4}(禁止|不允许)", up):
        return False

    # 正向：常见处方式说法
    return bool(re.search(
        r"(只输出|仅输出|输出格式|必须以|请输出|请返回|按下方|套用|要求|提供)"
        r"[^。，；\n]{0,24}JSON"
        r"|JSON\s*(对象|格式|模板|结构)", up))

def api_key():
    txt = open(os.path.expanduser("~/.dsh/.credentials.yaml")).read()
    return re.search(r"ANEXTO_API_KEY:\s*(\S+)", txt).group(1).strip('"')


PAGE = r"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>CoT 参数调优实验台</title>
<style>
*{box-sizing:border-box}
body{margin:0;font-family:"Times New Roman","Songti SC",serif;background:#f6f7f9;color:#111;font-size:18px}
header{background:#1f2937;color:#fff;padding:12px 20px;display:flex;justify-content:space-between;align-items:baseline}
header b{font-size:21px} header span{font-size:14px;color:#cbd5e1}
.wrap{display:flex;gap:14px;padding:14px}
.left{width:300px;flex:none}
.right{flex:1;min-width:0}
.card{background:#fff;border:1px solid #d7dbe0;border-radius:6px;padding:12px 14px;margin-bottom:12px}
.card h4{margin:0 0 12px;font-size:15px;text-transform:uppercase;letter-spacing:.04em;color:#374151}
label{display:block;font-size:17px;color:#374151;margin:14px 0 4px;font-weight:700}
.val{float:right;font-family:Menlo,monospace;font-size:24px;background:#ffe066;border:2px solid #d4a72c;
     border-radius:4px;padding:0 9px;font-weight:700}
input[type=range]{width:100%;margin:4px 0 0;height:22px}
select,textarea{width:100%;font-family:inherit;font-size:12.5px;border:1px solid #c7ccd3;border-radius:4px;padding:5px}
textarea{font-family:Menlo,monospace;font-size:12px;height:110px;resize:none;line-height:1.35}
button{width:100%;margin-top:16px;padding:11px;border:0;border-radius:5px;background:#2b6cb0;color:#fff;
       font-size:17px;font-family:inherit;cursor:pointer;font-weight:700}
button:disabled{background:#94a3b8}
.meta{font-family:Menlo,monospace;font-size:16px;color:#111;line-height:1.65;word-break:break-word}
.badge{display:inline-block;padding:1px 8px;border-radius:10px;font-size:11.5px;font-weight:700}
.ok{background:#c6f6d5;color:#22543d;font-size:15px;padding:3px 12px} .bad{background:#fed7d7;color:#822727;font-size:15px;padding:3px 12px} .note{background:#e2e8f0;color:#2d3748;font-size:15px;padding:3px 12px}
pre{margin:0;white-space:pre-wrap;word-break:break-word;font-family:Menlo,monospace;font-size:15.5px;line-height:1.52}
#outwrap{position:relative}
#out{border:1px solid #d7dbe0;border-radius:6px;background:#fff;padding:12px 12px 12px;
     height:470px;overflow:auto;user-select:text;cursor:text;
     -webkit-user-select:text}
#more{font-size:12px;color:#6b7280;margin-top:6px}
.tabs span{display:inline-block;padding:5px 12px;border:1px solid #d7dbe0;border-bottom:0;border-radius:5px 5px 0 0;
           background:#eef1f4;font-size:12.5px;cursor:pointer;margin-right:2px}
.tabs span.on{background:#fff;font-weight:700}
.hint{font-size:13.5px;color:#6b7280;margin-top:8px}
</style></head><body>
<header><b>GV College · CoT 参数调优实验台</b>
<span>本地客户端 → POST /v1/chat/completions · 模型 deepseek-v4.1-flash</span></header>
<div class="wrap">
  <div class="left">
    <div class="card">
      <h4>采样参数 Sampling</h4>
      <label>Temperature<span class="val" id="tv">—</span></label>
      <input type="range" id="temp" min="0" max="1.5" step="0.1">
      <label>Top-P<span class="val" id="pv">—</span></label>
      <input type="range" id="topp" min="0" max="1" step="0.05">
      <label>Model</label>
      <select id="model"><option>deepseek-v4.1-flash</option></select>
      <button id="run">Run ▶</button>
      <div class="hint">滑杆数值同时高亮在右侧请求日志中，运行时真实生效。<br><b>下面的提示词可以直接编辑</b>，改动会随请求真实发送。</div>
    </div>
    <div class="card">
      <h4>Prompt</h4>
      <select id="preset">
        <option value="P2">P2 · CoT + 形式化约束 + 注入防御</option>
        <option value="P1">P1 · 基线（无 CoT）</option>
      </select>
      <label>messages[0].content</label>
      <textarea id="prompt" spellcheck="false"></textarea>
    </div>
  </div>
  <div class="right">
    <div class="card" style="margin-bottom:10px">
      <h4>请求参数（实际发送）</h4>
      <div class="meta" id="reqmeta">尚未运行</div>
    </div>
    <div class="tabs"><span class="on" id="tabRaw">模型输出</span><span id="tabParse">结构校验</span></div>
<div style="display:flex;gap:8px;align-items:center;margin:8px 0 0">
  <button id="copyBtn" style="width:auto;margin:0;padding:6px 14px;font-size:13px;background:#4a5568">复制全部</button>
  <button id="dlBtn" style="width:auto;margin:0;padding:6px 14px;font-size:13px;background:#4a5568">下载 .json</button>
  <span id="copyMsg" style="font-size:12.5px;color:#2f855a"></span>
</div>
    <div id="outwrap"><div id="out"><pre id="content">点击 Run 开始…</pre></div><div id="more"></div></div>
  </div>
</div>
<script>
const T=document.getElementById('temp'), P=document.getElementById('topp');
function sync(){document.getElementById('tv').textContent=(+T.value).toFixed(1);
                document.getElementById('pv').textContent=(+P.value).toFixed(2);}
T.oninput=P.oninput=sync;
let PROMPTS={};
fetch('/api/prompts').then(r=>r.json()).then(d=>{PROMPTS=d;
  document.getElementById('prompt').value=d.P2;});
document.getElementById('preset').onchange=e=>{
  const k=e.target.value; document.getElementById('prompt').value=PROMPTS[k];};
async function run(){
  const btn=document.getElementById('run'); btn.disabled=true; btn.textContent='Running…';
  const body={temperature:+T.value, top_p:+P.value,
              preset:document.getElementById('preset').value,
              prompt:document.getElementById('prompt').value};
  document.getElementById('reqmeta').innerHTML=
    '等待响应… 送达参数 temperature=<b>'+(+T.value).toFixed(1)+'</b>, top_p=<b>'+(+P.value).toFixed(2)+'</b>';
  const r=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const d=await r.json();
  const q=d.echo;
  document.getElementById('reqmeta').innerHTML=
    'POST /v1/chat/completions &nbsp; model=<b>'+q.model+'</b><br>'+
    'temperature=<b style="background:#fff3c4;padding:0 4px">'+(+q.temperature).toFixed(1)+'</b> &nbsp;'+
    'top_p=<b style="background:#fff3c4;padding:0 4px">'+(+q.top_p).toFixed(2)+'</b> &nbsp; max_tokens='+q.max_tokens+
    ' &nbsp; seed=未发送<br>'+
    'prompt_tokens='+q.prompt_tokens+' · completion_tokens='+q.completion_tokens+
    ' · reasoning_tokens='+q.reasoning_tokens+' · elapsed='+q.elapsed_s+'s<br>'+
    'finish_reason='+q.finish_reason+' · sha256(content)='+q.sha;
  let ok=false,obj=null;
  try{obj=JSON.parse(d.content);ok=true;}catch(e){}
  window.__content=d.content;
  const el=document.getElementById('content');
  const wantsJson = q.wants_json;   // 本预设是否要求 JSON 输出

  // 判定口径：只有在"提示要求 JSON"时，解析失败才算结构缺陷。
  // 基线（P1）本来就不要 JSON，不能拿这个标它。
  let head;
  if(wantsJson && ok){
    head = '<span class="badge ok">JSON 有效</span>&nbsp; 可被程序解析';
  } else if(wantsJson && !ok){
    head = '<span class="badge bad">JSON 无效</span>&nbsp; 提示要求 JSON，但输出不是合法 JSON';
  } else if(!wantsJson){
    head = '<span class="badge note">文本输出</span>&nbsp; 本预设未要求 JSON，不适用结构校验';
  }

  if(wantsJson && ok){
    el.innerHTML = '<span style="font-family:inherit;font-size:12.5px">'+head+'</span>';
    const pre=document.createElement('pre');
    pre.textContent=JSON.stringify(obj,null,1);
    el.appendChild(pre);
  } else {
    el.innerHTML = '<span style="font-family:inherit;font-size:12.5px">'+head+'</span>';
    const pre=document.createElement('pre'); pre.textContent=d.content; el.appendChild(pre);
  }
  document.getElementById('tabParse').style.opacity = wantsJson ? 1 : .4;
  document.getElementById('more').textContent='共 '+d.content.length+' 字符 · 输出区可滚动、可选中复制，或点上方按钮一键复制';
  btn.disabled=false; btn.textContent='Run ▶';
  window.__done=true;
}
document.getElementById('tabRaw').onclick=()=>{document.getElementById('tabParse').classList.remove('on');
  document.getElementById('tabRaw').classList.add('on'); if(window.__content) document.getElementById('content').textContent=window.__content;};
document.getElementById('tabParse').onclick=()=>{document.getElementById('tabRaw').classList.remove('on');
  document.getElementById('tabParse').classList.add('on'); try{const o=JSON.parse(window.__content);
  document.getElementById('content').textContent=JSON.stringify(o,null,2);}catch(e){}};
document.getElementById('copyBtn').onclick=async()=>{
  const txt=window.__content||'';
  if(!txt){document.getElementById('copyMsg').textContent='还没有输出';return;}
  try{
    await navigator.clipboard.writeText(txt);
    document.getElementById('copyMsg').textContent='已复制 '+txt.length+' 字符';
  }catch(e){
    // 剪贴板 API 在非安全上下文可能被拒，退回到选中+execCommand
    const ta=document.createElement('textarea');
    ta.value=txt; document.body.appendChild(ta); ta.select();
    document.execCommand('copy'); document.body.removeChild(ta);
    document.getElementById('copyMsg').textContent='已复制 '+txt.length+' 字符（兼容模式）';
  }
  setTimeout(()=>document.getElementById('copyMsg').textContent='',3000);
};
document.getElementById('dlBtn').onclick=()=>{
  const txt=window.__content||'';
  if(!txt){document.getElementById('copyMsg').textContent='还没有输出';return;}
  const blob=new Blob([txt],{type:'application/json;charset=utf-8'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='output_'+Date.now()+'.json';
  a.click(); URL.revokeObjectURL(a.href);
  document.getElementById('copyMsg').textContent='已下载';
  setTimeout(()=>document.getElementById('copyMsg').textContent='',3000);
};
document.getElementById('run').onclick=run;
const qp=new URLSearchParams(location.search);
T.value=qp.get('t')||'0.7'; P.value=qp.get('p')||'0.9'; sync();
if(qp.get('auto')==='1') setTimeout(run, 400);
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path.startswith("/api/prompts"):
            d = {k: open(os.path.join(ROOT, "prompts", f)).read()
                 for k, f in (("P1", "p1_baseline.txt"), ("P2", "p2_cot.txt"))}
            return self._send(200, json.dumps(d))
        return self._send(200, PAGE, "text/html")

    def do_POST(self):
        import time, hashlib
        n = int(self.headers["Content-Length"])
        req = json.loads(self.rfile.read(n))
        preset = req.get("preset", "P2")
        # 前端传了自定义 prompt 就用它（支持你粘贴自己写的提示词）；否则回落到预设文件
        prompt = (req.get("prompt") or "").strip()
        if not prompt:
            prompt = open(os.path.join(ROOT, "prompts",
                                       "p2_cot.txt" if preset == "P2" else "p1_baseline.txt")).read()
        body = {"model": "deepseek-v4.1-flash", "temperature": req["temperature"],
                "top_p": req["top_p"], "max_tokens": 2600,
                "messages": [{"role": "user", "content": prompt}]}
        r = urllib.request.Request(API, data=json.dumps(body).encode(),
                                   headers={"Authorization": "Bearer " + api_key(),
                                            "Content-Type": "application/json"})
        t0 = time.time()
        with urllib.request.urlopen(r, timeout=300) as resp:
            raw = json.loads(resp.read())
        el = round(time.time() - t0, 2)
        content = raw["choices"][0]["message"].get("content") or ""
        u = raw["usage"]
        echo = {"model": body["model"], "temperature": body["temperature"], "top_p": body["top_p"],
                "wants_json": wants_json_output(prompt),
                "max_tokens": body["max_tokens"], "prompt_tokens": u["prompt_tokens"],
                "completion_tokens": u["completion_tokens"],
                "reasoning_tokens": u.get("completion_tokens_details", {}).get("reasoning_tokens", 0),
                "elapsed_s": el, "finish_reason": raw["choices"][0].get("finish_reason"),
                "sha": hashlib.sha256(content.encode()).hexdigest()[:12]}
        rec = {"source": "ui_server", "preset": preset,
               "prompt_source": "custom" if req.get("prompt") else "preset_file",
               "prompt_chars": len(prompt), "request": body, "response": raw,
               "elapsed_s": el, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
        os.makedirs(os.path.join(ROOT, "runs"), exist_ok=True)
        stamp = time.strftime("%H%M%S")
        json.dump(rec, open(os.path.join(ROOT, "runs", f"ui_T{body['temperature']}_P{body['top_p']}_{stamp}.json"), "w"),
                  ensure_ascii=False, indent=2)
        self._send(200, json.dumps({"content": content, "echo": echo}, ensure_ascii=False))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
