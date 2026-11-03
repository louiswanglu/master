# 结构化 NLP 练习 — 第 2 周提交

> 数据源：`第二周练习(1).pdf` 提供的 12 条校园班车追踪应用反馈（R01–R12）。
> 遵循「仅用数据集信息、不虚构、缺失即 null、每题附证据 ID」的硬性规则。

---

## 第 1 部分 — 提示设计（Prompt Design）

### 1.1 总结提示（Summarization Prompt）

```text
角色：你是一名严谨的高校学生事务分析员（NLP analyst），服务于学生事务办公室。
任务：把 12 条杂乱的班车追踪应用反馈，压缩成一份管理者 2 分钟内能读完的 Markdown 摘要。
背景：数据来自应用评论、客服邮件、调查回复与聊天记录；表述口语化、长度不一，
      有的记录同时含正负面内容，有的省略了主语与时间。
输入：<在此粘贴 R01–R12 原始记录全文，含记录 ID、来源、日期>
输出格式：必须严格套用下方 Markdown 模板的六个二级标题，不得增删章节、不得改标题名：
  ## 1. 一句话概述
  ## 2. 主要主题（表格：主题 | 证据ID | 用户影响 | 建议行动）
  ## 3. 正面反馈
  ## 4. 高优先级风险
  ## 5. 缺失或模糊信息
  ## 6. 建议的后续步骤（1./2./3. 有序列表）
规则：
1. 只使用输入记录中的信息。
2. 禁止虚构姓名、日期、技术原因（如"服务器故障""GPS 漂移""数据库迁移"）、
   解决方案或政策背景。原始记录没说的原因，一律不写。
3. 每条主题、每条正面反馈、每条风险都必须以记录 ID 标注证据，格式如 (R01, R09)。
4. 需要写原因或影响却缺少证据时，把该点移入「缺失或模糊信息」一节，
   并写明"原始记录未说明……"，不要猜测。
5. 表格每格不超过 25 个汉字，整体面向管理者：先结论、后证据。
6. 「建议行动」只能是数据可直接支持的动作（如"退还重复扣款""核实无障碍坡道"），
   不得提出需要新系统或新预算的方案。
```

### 1.2 提取提示（Extraction Prompt）

```text
角色：你是一名结构化数据抽取员。
任务：把 12 条原始反馈逐条转换成 JSON 对象，字段与取值必须符合给定 schema。
背景：下游会把这些 JSON 直接导入看板，因此字段一致性比语言流畅更重要。
输入：<在此粘贴 R01–R12 原始记录全文>
输出格式：只输出一个 JSON 对象，结构为 {"records": [...], "dataset_level_insights": {...}}，
          字段顺序与下方 schema 完全一致；不要输出解释文字。
受控词汇（只能用下列取值，不得自造新标签）：
  source: 应用评论 | 客服邮件 | 调查反馈 | 聊天记录
  issue_category: 时效准确性 | 退款问题 | 可访问性 | 应用程序漏洞 | 安全问题 | 隐私问题 | 功能需求 | 正面反馈 | 不明确
  sentiment: 正面 | 中性 | 负面 | 不明确
  urgency: 低 | 中 | 高
规则：
1. 每条记录恰好产生一个对象，id 必须保留原始 R 编号，不得合并、不得遗漏、不得新增。
2. evidence_quote 必须是原始记录中的连续原文片段（可截取，不得改写、不得翻译、不得拼接）。
3. 原文未提供的信息：字符串字段写 null，列表字段写在 missing_information 里，不要补全。
4. 不得推断技术原因或责任方。
5. JSON 必须可被解析：双引号、无注释、无尾随逗号、布尔值不加引号。
6. 同一类问题在不同记录中必须使用同一个标签（例如 R04 与 R11 都属"应用程序漏洞"）。
```

---

## 第 2 部分 — Markdown 摘要报告

# 校园班车应用反馈摘要（Campus Shuttle App Feedback Summary）

## 1. 一句话概述

12 条反馈整体肯定实时追踪的价值，但集中抱怨到站时间不准、无障碍与隐私信息不透明，以及退款与加载故障等具体可修复的缺陷（R01–R12）。

## 2. 主要主题

| 主题 | 证据ID | 用户影响 | 建议行动 |
|---|---|---|---|
| 到站时间与显示不准 | R01, R09, R10 | 错过实验课分组；夜间在户外久等，感到不安全 | 复核晚间与夜间到站预测；明确"Arriving"指哪一站 |
| 功能缺口（通知方式/提前量） | R05, R12 | 2 分钟提醒不够用；未装应用的学生收不到延误信息 | 评估提前 10 分钟通知与短信通知选项 |
| 可访问性缺陷 | R03, R06 | 阳光下看不清；无障碍图标错误导致等下一班 | 提高对比度；核实北门坡道状态数据 |
| 应用故障（追踪卡住/二维码不加载） | R04, R11 | 追踪器卡住十分钟后跳变；已付款却无法出示票 | 排查追踪与二维码加载链路 |
| 账务与隐私不透明 | R02, R07 | 通行证重复扣款；后台定位请求无解释 | 退款并说明所需交易 ID；公开定位数据说明 |

## 3. 正面反馈

- 实时公交与站点名称明显优于旧的 PDF 时刻表，用户明确表示"好太多了"（R10）。
- 到站提醒功能受欢迎，用户希望在此基础上加强而非替换（R05）。
- 司机服务获好评，主动帮乘客拿包（R04）。

## 4. 高优先级风险

- **安全风险**：夜间班车晚点而应用仍显示"准时"，学生天黑后在户外久等，风险直接指向人身安全（R09）。之所以高优先级，是因为错误信息会让用户做出错误的安全决策。
- **无障碍风险**：图标显示北门可到达，但到站车辆没有坡道，依赖无障碍班车的乘客被迫等下一班（R06）。这是可达性承诺与实际运力的不一致。
- **账务风险**：同一张通行证出现一笔待处理、一笔已扣款，用户要求退款但不知该提供哪个交易 ID（R02）。资金类问题易升级为投诉。

## 5. 缺失或模糊信息

- R01 未说明偏差发生在哪条线路、影响多少用户。
- R02 缺少重复扣款涉及的交易 ID 与时间范围（用户自己也不知道该提供哪个）。
- R03 未提供设备型号与出现问题的具体页面。
- R04 未说明卡住问题的发生频率与设备/版本。
- R06 未提供涉及班次时间与北门无障碍状态的数据来源。
- R07 未说明后台定位的触发条件与数据保留期限（用户正是要求解释这一点）。
- R08 未说明手机系统与受影响路线数量。
- R09 未给出具体线路、站点与本应到站的计划时间。
- R10 未说明"Arriving"误指前一站的影响范围。
- R11 未说明受影响用户范围；用户已排除 Wi-Fi 与蜂窝网络的差异。
- R12 未说明受影响学生规模与短信通知所需的手机号收集方式。
- R05 未说明该需求覆盖的线路范围。

## 6. 建议的后续步骤

1. 先处理三条高紧急度记录：核实夜间到站预测与"准时"显示的判定逻辑（R09），核对北门无障碍坡道的实际可用性并修正图标数据（R06），为 R02 发起退款流程并说明所需交易 ID。
2. 修复 R04 与 R11 两类加载/卡住故障，并在修复前为已付款却无法出示二维码的用户提供替代核验方式。
3. 就 R07 的后台定位与数据留存问题发布一份面向学生的说明；同时评估 R05、R12 的通知提前量与短信渠道需求。

---

## 第 3 部分 — JSON 提取文件

```json
{
  "records": [
    {
      "id": "R01",
      "date": "2026-04-12",
      "source": "应用评论",
      "issue_category": "时效准确性",
      "sentiment": "负面",
      "urgency": "中",
      "user_need": "希望晚间到站时间准确，避免因错误倒计时错过课程",
      "requested_action": null,
      "evidence_quote": "晚上6点以后就会偏差15–20分钟",
      "needs_follow_up": true,
      "missing_information": ["偏差发生的具体线路", "受影响用户范围"]
    },
    {
      "id": "R02",
      "date": "2026-04-13",
      "source": "客服邮件",
      "issue_category": "退款问题",
      "sentiment": "负面",
      "urgency": "高",
      "user_need": "希望退还同一张通行证的重复扣款",
      "requested_action": "退还重复扣款",
      "evidence_quote": "同一张月度学生班车通行证，我被扣了两次费",
      "needs_follow_up": true,
      "missing_information": ["重复扣款涉及的交易 ID", "扣款发生的时间范围"]
    },
    {
      "id": "R03",
      "date": "2026-04-14",
      "source": "调查反馈",
      "issue_category": "可访问性",
      "sentiment": "负面",
      "urgency": "中",
      "user_need": "希望在户外强光下也能看清界面文字",
      "requested_action": null,
      "evidence_quote": "绿色文字配灰色背景，在阳光下几乎看不见",
      "needs_follow_up": false,
      "missing_information": ["使用的设备与屏幕设置", "受影响的具体页面"]
    },
    {
      "id": "R04",
      "date": "2026-04-15",
      "source": "聊天记录",
      "issue_category": "应用程序漏洞",
      "sentiment": "中性",
      "urgency": "中",
      "user_need": "希望追踪器不要卡住后突然跳变",
      "requested_action": null,
      "evidence_quote": "追踪器在7:42卡住了大约十分钟，然后一下子跳到‘已到达’",
      "needs_follow_up": true,
      "missing_information": ["卡住问题的发生频率", "涉及的设备或应用版本"]
    },
    {
      "id": "R05",
      "date": "2026-04-15",
      "source": "应用评论",
      "issue_category": "功能需求",
      "sentiment": "正面",
      "urgency": "低",
      "user_need": "希望在到达前 10 分钟收到提醒，而不只是提前 2 分钟",
      "requested_action": "增加提前 10 分钟通知选项",
      "evidence_quote": "能不能增加一个选项，让我在到达前10分钟收到通知",
      "needs_follow_up": false,
      "missing_information": ["该需求涉及的线路范围", "通知频率偏好"]
    },
    {
      "id": "R06",
      "date": "2026-04-16",
      "source": "客服邮件",
      "issue_category": "可访问性",
      "sentiment": "负面",
      "urgency": "高",
      "user_need": "希望无障碍图标与实际到站车辆的可达性一致",
      "requested_action": "核实并修正北门无障碍可达性信息",
      "evidence_quote": "它显示了北门可到达，但抵达的班车没有可用的坡道",
      "needs_follow_up": true,
      "missing_information": ["涉及的班次时间", "北门无障碍状态的数据来源"]
    },
    {
      "id": "R07",
      "date": "2026-04-16",
      "source": "调查反馈",
      "issue_category": "隐私问题",
      "sentiment": "中性",
      "urgency": "中",
      "user_need": "希望了解后台定位的用途以及会存储哪些数据",
      "requested_action": "说明会存储哪些数据",
      "evidence_quote": "为什么它会在后台请求？请解释会存储哪些数据",
      "needs_follow_up": true,
      "missing_information": ["后台定位的具体触发条件", "数据保留期限"]
    },
    {
      "id": "R08",
      "date": "2026-04-17",
      "source": "聊天记录",
      "issue_category": "应用程序漏洞",
      "sentiment": "负面",
      "urgency": "中",
      "user_need": "希望在西班牙语界面下仍能看到自己的路线",
      "requested_action": null,
      "evidence_quote": "我把手机语言改成西班牙语后，我的路线就消失了",
      "needs_follow_up": true,
      "missing_information": ["发生语言切换的具体手机系统", "受影响的路线数量"]
    },
    {
      "id": "R09",
      "date": "2026-04-18",
      "source": "应用评论",
      "issue_category": "安全问题",
      "sentiment": "负面",
      "urgency": "高",
      "user_need": "希望夜间到站信息真实，避免学生在户外久等",
      "requested_action": null,
      "evidence_quote": "校园班车追踪应用仍然显示准时，但学生们却在外面等了很久",
      "needs_follow_up": true,
      "missing_information": ["具体线路与站点", "本应到站的计划时间"]
    },
    {
      "id": "R10",
      "date": "2026-04-18",
      "source": "调查反馈",
      "issue_category": "时效准确性",
      "sentiment": "正面",
      "urgency": "低",
      "user_need": "希望“Arriving”明确指向乘客自己所在的站点",
      "requested_action": null,
      "evidence_quote": "‘Arriving’有时指的是前一站，而不是我自己的站点",
      "needs_follow_up": false,
      "missing_information": ["受影响的具体站点"]
    },
    {
      "id": "R11",
      "date": "2026-04-19",
      "source": "客服邮件",
      "issue_category": "应用程序漏洞",
      "sentiment": "负面",
      "urgency": "高",
      "user_need": "希望已付款的访客日票能正常加载出二维码",
      "requested_action": null,
      "evidence_quote": "二维码一直没加载出来。我们试了Wi-Fi和蜂窝网络。付款倒是成功了，可应用里只显示一个转圈圈的加载图标",
      "needs_follow_up": true,
      "missing_information": ["受影响用户范围", "问题发生时的应用版本"]
    },
    {
      "id": "R12",
      "date": "2026-04-20",
      "source": "应用评论",
      "issue_category": "功能需求",
      "sentiment": "中性",
      "urgency": "中",
      "user_need": "希望无需安装应用即可通过短信获知班车延误",
      "requested_action": "增加简单的短信通知选项",
      "evidence_quote": "请增加一个简单的短信通知选项",
      "needs_follow_up": false,
      "missing_information": ["受影响学生规模", "短信通知所需的手机号收集方式"]
    }
  ],
  "dataset_level_insights": {
    "most_common_issue_categories": ["时效准确性", "应用程序漏洞", "可访问性"],
    "highest_priority_record_ids": ["R09", "R06", "R02"],
    "overall_sentiment": "负面"
  }
}
```

> 注：分类计数为 应用程序漏洞 3（R04/R08/R11）、时效准确性 2（R01/R10）、可访问性 2（R03/R06）、功能需求 2（R05/R12）、退款问题 1（R02）、隐私问题 1（R07）、安全问题 1（R09）。R09 兼有"显示不准"与"夜间安全"两面，按主导诉求归入安全问题，因此 `most_common_issue_categories` 取出现频次最高的三类（应用程序漏洞、时效准确性、可访问性）。

---

## 第 4 部分 — 验证与修订（Validation & Revision）

### 4.1 实际执行的验证

| 检查项 | 方法 | 结果 |
|---|---|---|
| JSON 可解析 | 用 Python `json.loads` 解析第 3 部分代码块 | ✅ 通过，无注释、无尾随逗号 |
| 记录数完整 | 统计 `records` 长度并比对 R01–R12 | ✅ 12/12，无重复、无新增 |
| 受控词汇 | 逐条比对 source / issue_category / sentiment / urgency 是否落在枚举内 | ✅ 全部命中，无自造标签 |
| 证据支撑 | 把 `evidence_quote` 归一化（去空白）后检查是否为原始记录的子串 | ✅ 12/12 为原文子串 |
| null 使用 | 检查无证据的字段是否写 null / 落入 missing_information | ✅ `requested_action` 有 7 条为 null |
| 无幻觉 | 通读输出，确认未出现原因类技术解释 | ✅ 未出现"服务器""GPS 故障""数据库"等措辞 |

### 4.2 我做的一处修正

第一版把 R02 的 `issue_category` 标成「应用程序漏洞」，理由是"账单显示异常"。但原文只说"被扣了两次费"并明确要求"请退还重复扣款"——这是账务诉求，不是应用崩溃。按"标签必须由原文直接支撑"的规则，我把它改回「退款问题」，并把"需要哪个交易 ID"移入 `missing_information`。

### 4.3 提示层面的修订

第一版提取提示只写了"不要编造"，模型仍倾向于补原因。第二版把禁令具体化为"禁止推断技术原因或责任方"，并要求 `evidence_quote` 必须是连续原文片段，之后再未出现原因类补全。

---

## 第 5 部分 — 反思（Reflection，约 190 词）

What changed with the templates was not the model's vocabulary but its discipline. My first unstructured attempt read fluently and was unusable: it invented a "GPS drift" explanation for the stalled tracker (R04), merged two records into one theme, and silently upgraded R09 from a complaint about prediction to a claim about staffing. The JSON template forced one object per record, which made the merge impossible, and the controlled vocabulary pushed me to choose between 时效准确性 and 安全问题 instead of writing a vague paragraph that covered both.

The most useful constraint turned out to be the continuous-quote rule. Requiring `evidence_quote` to be an exact substring let me verify all twelve records mechanically instead of trusting plausibility, and it exposed one bad label: I had tagged R02 as an application bug when the text only asks for a refund.

The limitation is real, though. Controlled vocabularies flatten mixed records — R04 praises the driver and reports a freezing tracker, and 中性 hides both. If I extended this, I would add a secondary-category field rather than widen the primary list.
