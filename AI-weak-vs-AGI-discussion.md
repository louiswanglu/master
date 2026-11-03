# Weak AI vs. AGI: Multimodal AI in Healthcare

**Course discussion post — domain: Healthcare**

---

## English version (main post, ~330 words)

Weak AI, or narrow AI, is engineered to excel inside a bounded problem space: it optimises a defined objective using statistical patterns learned from large datasets, but it cannot transfer its competence to a genuinely new domain, set its own goals, or reason about why it is doing what it does. AlphaFold predicting protein structure, a spam filter, or a radiology classifier are all weak AI — near-human or superhuman on their task, and helpless one step outside it. AGI, by contrast, is defined by generality: a single system that can acquire any cognitive skill a human can, transfer learning across unrelated domains, and operate autonomously in unfamiliar situations. Crucially, AGI is not a bigger version of weak AI; it requires capacities that current architectures only approximate — persistent memory, self-directed goal formation, causal world models, and reliable calibration about its own uncertainty. Multimodal systems sit on an interesting middle ground: they widen the input space dramatically, which feels like generality, yet they remain narrow because each capability is still trained and evaluated on a fixed task distribution.

Healthcare makes the distinction concrete, because medicine rewards narrow excellence and punishes unjustified generality.

**Case 1 — Radiology triage.** Convolutional and vision-transformer models read chest X-rays and mammograms and flag suspected pneumothorax or malignant lesions for prioritisation. This is weak AI par excellence: a closed task, a fixed label set, and a human radiologist retaining final authority. Adding text (the referral note) and prior imaging improves specificity, but the model still cannot decide that a patient needs a different exam entirely.

**Case 2 — Ambient clinical documentation.** Systems such as Microsoft/Nuance DAX Copilot and Abridge listen to the consultation, transcribe it, and draft the clinical note in the EHR. Here audio plus text genuinely changes professional practice: clinicians report substantial reductions in after-hours documentation ("pajama time") and more eye contact with patients. The system is still narrow — it summarises a conversation, it does not reason about the differential diagnosis.

**Case 3 — Multimodal second opinion / triage support.** Research systems combine image, text and lab values to draft impressions or suggest next steps, with results approaching or matching clinician performance on benchmark questions. Deployment remains assistive and supervised, precisely because benchmark competence is not generality.

The pattern across all three is the same: multimodal weak AI is already reshaping professional practice by removing administrative and perceptual load, which frees expert attention for judgement, communication and ethics. AGI would change the profession differently — by taking over the reasoning itself. That day has not arrived, and treating today's narrow tools as if it had is the real clinical risk.

---

## 中文版（备用 / 330 字左右，可直接作为中文回帖）

弱人工智能（Weak AI / Narrow AI）是在有限问题空间内被专门优化的系统：它依靠大规模数据学到的统计规律去逼近某个既定目标，但无法把能力迁移到全新领域，无法自行设定目标，也无法解释自己为何这样做。AlphaFold 预测蛋白质结构、垃圾邮件过滤器、影像分类模型都属于弱 AI——在其任务上可能超越人类，但跨出一步就无能为力。通用人工智能（AGI）的关键在于通用性：同一个系统能习得人类任何认知技能、跨不相关领域迁移学习，并在陌生情境中自主行动。它不是"更大的弱 AI"，而需要当前架构尚不擅长的能力：持久记忆、自主目标生成、因果世界模型、以及对自身不确定性的可靠校准。多模态系统处在有趣的中间地带：输入空间被极大拓宽，看起来像通用，但因每项能力仍固定在既定任务分布上训练与评估，本质上仍是窄的。

医疗领域最能说明这种区别，因为医学奖励窄而精的能力，却惩罚没有依据的"通用"。

**案例一：影像分诊。** 卷积网络与视觉 Transformer 阅读胸片与钼靶，标记疑似气胸或恶性病灶以供优先处理。这是典型的弱 AI：任务封闭、标签集固定、放射科医生保留最终决定权。加入文本（转诊单）与既往影像能提升特异度，但模型仍无法判断"这位患者其实需要换一种检查"。

**案例二：诊室环境记录。** DAX Copilot、Abridge 等系统旁听问诊，转写并自动生成病历草稿写入 EHR。音频加文本确实改变了专业实践：医生报告文书时间（"睡衣时间"）明显下降，与患者的目光交流增多。但它依然是窄的——它总结对话，不做鉴别诊断推理。

**案例三：多模态"第二意见"与分诊支持。** 研究系统结合图像、文本与检验值生成印象或建议下一步，在基准题上接近甚至达到临床医生水平。落地仍限定为辅助与受监督，正因为基准能力不等于通用性。

三个案例的共同规律是：多模态弱 AI 已经在通过卸下事务性与感知性负荷重塑专业实践，把专家的注意力释放给判断、沟通与伦理；而 AGI 会以另一种方式改变这个职业——接管推理本身。那一天尚未到来，把今天的窄工具当作它已经到来，才是真正的临床风险。
