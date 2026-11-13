import json,re,sys,unicodedata,fitz
from collections import Counter
p='/Users/wanglu/.dsh/attachments/v1/files/e3/e3883fd55558d7b7adca24b950fdc47fa1fb850bcf65642e6fd7e72ff67257af/第二周练习(1).pdf'
pdf=re.sub(r'\s+','',unicodedata.normalize('NFKC',fitz.open(p)[1].get_text()))
n=lambda s: re.sub(r'\s+','',unicodedata.normalize('NFKC',s))

raw=open(sys.argv[1]).read()
m=re.search(r'```json\n(.*?)\n```',raw,re.S)
body=m.group(1) if m else raw
print("有代码围栏:",bool(m))
try:
    d=json.loads(body); print("json.loads: ✅")
except Exception as e:
    print("json.loads: ❌",e); sys.exit(1)

print("顶层键:",list(d.keys()))
print("issues 条数:",len(d.get('issues',[])))
ids=[x['id'] for x in d['issues']]
print("ID 顺序正确:",ids==[f"R{i:02d}" for i in range(1,13)],ids)

FIELDS=['id','reported_date','source_channel','component','symptom','observed_behavior',
 'expected_behavior','platform','app_version','device','frequency','severity_for_engineering',
 'is_regression','evidence_quote','repro_inputs_needed','needs_follow_up']
badfields=[x['id'] for x in d['issues'] if list(x.keys())!=FIELDS]
print("字段名/顺序完全一致:",not badfields, badfields[:3])

SRC={"应用评论","客服邮件","调查反馈","聊天记录"}
COMP={"eta_prediction","live_tracking","payment_billing","ticketing_qr","notification","ui_accessibility","accessibility_data","location_permissions","localization"}
FREQ={"one_off","intermittent","recurring","reproducible","unknown"}
SEV={"critical","major","minor","enhancement"}
viol=[(x['id'],k,x[k]) for x in d['issues'] for k,S in
      [('source_channel',SRC),('component',COMP),('frequency',FREQ),('severity_for_engineering',SEV)]
      if x[k] not in S]
print("受控词汇违规:",viol or "无 ✅")

ev=[x['id'] for x in d['issues'] if n(x['evidence_quote']) not in pdf]
print("evidence_quote 严格子串失败:",ev or "无 ✅")

cnt=Counter(x['component'] for x in d['issues'])
claimed=d['backlog_hints']['cluster_by_component']
print("cluster_by_component 与实际统计一致:",dict(cnt)=={k:v for k,v in claimed.items()})
if dict(cnt)!={k:v for k,v in claimed.items()}:
    print("   模型:",claimed); print("   实际:",dict(cnt))

crit=[x['id'] for x in d['issues'] if x['severity_for_engineering']=='critical']
print("blockers == critical 记录:",set(d['backlog_hints']['blockers'])==set(crit))
print("   critical:",crit,"| blockers:",d['backlog_hints']['blockers'])

hf=[x['id'] for x in d['issues'] if x['severity_for_engineering'] in ('critical','major') and not x['needs_follow_up']]
print("critical/major 但 follow_up=false:",hf or "无")

nulls=sum(1 for x in d['issues'] if x['platform'] is None and x['app_version'] is None and x['device'] is None)
print("platform/app_version/device 全 null 的条数:",nulls)
print("expected_behavior 为 null 的条数:",sum(1 for x in d['issues'] if x['expected_behavior'] is None))
print("is_regression 非 null 的条数:",sum(1 for x in d['issues'] if x['is_regression'] is not None))
