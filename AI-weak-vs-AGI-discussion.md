# Weak AI vs. AGI: Multimodal Systems in eKYC and Credit Infrastructure

**Course discussion post — domain: Financial identity and credit infrastructure (Indonesia & Philippines)**
**Author's context:** eKYC and credit bureau operations across the Indonesian and Philippine markets.

---

## English version (main post, ~790 words)

Weak AI, or narrow AI, is built to excel inside a bounded problem space: it optimises a defined objective against patterns learned from data, but it cannot transfer its competence to a genuinely new domain, set its own goals, or explain itself in terms a regulator would accept. AGI is defined by generality — a single system that can acquire any cognitive skill a human can, transfer learning across unrelated domains, and act autonomously in unfamiliar situations. The gap is not one of scale but of capability: persistent memory, causal world models, and reliable calibration of its own uncertainty. Multimodal systems make this gap confusing, because they widen the input space — text, images, audio — and that breadth feels like generality. It is not. Each capability is still trained and evaluated on a fixed distribution, inside a workflow a human designed.

I work in eKYC and credit infrastructure, serving the Indonesian and Philippine markets, and this distinction is not academic there. What we ship decides whether a real person gets a loan.

**Case 1 — eKYC onboarding in Indonesia.** A typical application hands the system three modalities at once: an image of the applicant's e-KTP (the chipped national ID issued through Dukcapil), a liveness-check video or selfie, and typed text — name, NIK, address, sometimes a salary slip. A decade ago a reviewer opened each e-KTP photo, read it under whatever light the applicant had, and retyped the fields; the failure mode was fatigue and inconsistency. Now vision models OCR the card, face-match the selfie against the ID photo, and a text model drafts a case summary for the human. The professional practice has changed: the reviewer no longer transcribes, they adjudicate exceptions — a woman whose card predates her marriage certificate, a card photographed under glare, a name transliterated two ways. Narrow, and deliberately so.

**Case 2 — dispute operations at the credit bureau.** Disputes arrive as genuinely mixed evidence: a recorded service call in Bahasa Indonesia or Taglish, a written narrative, a photographed payment receipt or bank statement. Speech-to-text plus document understanding can assemble a timeline and draft a triage note for an analyst working over SLIK data in Indonesia or CIC data in the Philippines. This is where weak AI earns its keep — volume, consistency, and a first draft an analyst can reject. It is also where it can quietly do harm: ASR degrades on code-switching and regional accents, which are precisely the voices of lower-income applicants.

**Case 3 — identity resolution inside the bureau.** A bureau's core asset is one file per person, but the same person arrives many ways: "Siti Nurhaliza" and "Siti Nur Haliza", a maiden name on one loan and a married name on another, a NIK with a transposed digit, a name transliterated between scripts, a 2015 e-KTP photo next to a 2024 selfie. Matching used to be deterministic — exact NIK, else nothing — with analysts eyeballing fuzzy-name reports for the remainder, and the effect was that real people carried fragmented histories. Today two modalities do the real work. Text embeddings cluster candidate records on name, address and phone; vision compares ID photographs, signatures and the portrait on a supporting document. Analysts have stopped scanning reports and started adjudicating the small set of genuinely uncertain pairs. What is missing is instructive as well: we hold recorded verification calls, and matching on voice would be the obvious third modality, but it is not built — the recording quality is too uneven, and "your voice does not match" is far harder to explain to an applicant than "your name and NIK disagree". The error costs are asymmetric in a way that forbids automation: a false merge puts a stranger's default on your file and is slow and painful to unwind, while a false split merely leaves you thin-filed. So the threshold is a human decision, per market — and the model is never asked to make it.

The pattern across all three is identical: multimodal weak AI removes perceptual and clerical load, freeing expert attention for judgement, ethics and accountability. AGI would change the profession differently — it would take over the judgement itself. In credit that day has not arrived, and behaving as if it had is not a productivity risk but a compliance one. An unexplained decline, or an unexplained merge that discloses one person's repayment history to another, is exactly what a regulator can oblige us to justify, whether under Indonesia's Personal Data Protection Law or the Philippines' Data Privacy Act. The difference between the two kinds of AI is therefore not a technical curiosity. It is the line between a tool that makes my colleagues faster and a system whose reasoning we would have to be able to defend, in court, to the person whose file we got wrong.

---

## 中文版（备用，约 1310 字）

弱人工智能（Weak AI / Narrow AI）是在有限问题空间内被专门优化的系统：它依靠数据中的统计规律逼近某个既定目标，但无法把能力迁移到全新领域，无法自行设定目标，也无法用监管者能接受的方式解释自己的判断。通用人工智能（AGI）的关键在于通用性：同一个系统能习得人类任何认知技能、跨不相关领域迁移，并在陌生情境中自主行动。二者的差距不在规模，而在能力本身——持久记忆、因果世界模型，以及对自身不确定性的可靠校准。多模态系统把这个差距变得模糊：文本、图像、音频同时进入模型，输入空间的拓宽看起来像"通用"，但它并不通用——每项能力仍固定在既定分布上训练与评估，仍跑在人设计好的流程里。

我在 eKYC 与征信基础设施行业工作，服务印尼与菲律宾市场。在那里，这个区分不是学术问题：我们上线的模型决定一个真实的人能不能拿到贷款。

**案例一：印尼的 eKYC 开户。** 一次申请同时交来三种模态：申请人 e-KTP（Dukcapil 发放的带芯片身份证）的影像、活体检测视频或自拍、以及手填文本（姓名、NIK、地址，偶尔一张工资单）。十年前，审核员要逐张打开 e-KTP 照片，在申请人当时的灯光条件下辨认，再手工录入字段，失败模式是疲劳与不一致。现在视觉模型做 OCR、把自拍与证件照做人脸比对，文本模型起草一份案情摘要给人工复核。专业实践随之改变：审核员不再录入，而是裁决例外——证件签发早于结婚证、反光下拍糊的卡片、两种音译写法的姓名。它是窄的，而且必须窄。

**案例二：信用局的争议处理。** 争议材料天然是多模态的：一段印尼语或 Taglish 的客服通话录音、一段文字陈述、一张拍照的还款凭证或银行流水。语音转写加文档理解可以把时间线拼起来，并为分析师起草一份分流意见——印尼侧对应 SLIK 数据，菲律宾侧对应 CIC 数据。这是弱 AI 真正创造价值的地方：量大、口径一致、先给一版草稿供人否掉。也是它可能悄悄伤人的地方：语音识别在语码转换与地方口音上明显退化，而这些恰恰是低收入申请人的声音。

**案例三：信用局内部的身份归一。** 信用局的核心资产是"一人一档"，但同一个人会以很多种形态出现："Siti Nurhaliza" 与 "Siti Nur Haliza"，一笔贷款用婚前姓名、另一笔用婚后姓名，NIK 里有一位被写错顺序，姓名在不同文字系统间音译，2015 年的 e-KTP 照片和 2024 年的自拍并排放着。过去匹配是确定性的——NIK 精确命中，否则就空着——剩下的交给分析师人工翻看姓名模糊匹配报告，结果是真实的人背着碎片化的信用历史。今天真正在用的是两种模态：文本嵌入按姓名、地址、电话把候选记录聚类，视觉模型比对证件照、签名以及佐证材料上的头像。分析师不再逐份翻报告，而是裁决真正不确定的那小批配对。没有做的那部分同样说明问题：我们手上其实有核验通话录音，按声音匹配是显而易见的第三种模态，但它还没做——录音质量参差不齐，而且"你的声音与档案不符"远比"你的姓名与 NIK 对不上"更难对申请人解释清楚。这里的错误代价是不对称的，因此不允许自动化：错误合并会把陌生人的违约记录写到你名下，撤销缓慢且痛苦；错误拆分只是让你暂时停留在薄档案。所以阈值必须由人按市场来定——模型从不被要求做这个决定。

三个案例的规律完全一致：多模态弱 AI 卸下感知与事务性负荷，把专家的注意力释放给判断、伦理与问责。AGI 会以另一种方式改变这个职业——它会接管判断本身。在信贷行业，那一天尚未到来；把今天当那一天来用，不是效率风险，而是合规风险。一笔无法解释的拒绝，或一次无法解释的合并——把一个人的还款记录披露给了另一个人——恰恰是印尼《个人数据保护法》或菲律宾《数据隐私法》下监管可以要求我们解释的东西。所以这两类 AI 的区别不是技术趣闻，而是那条线——线的一边是让同事们更快的工具，另一边是我们要在法庭上、对被我们弄错档案的那个人，为其推理过程负责的系统。

---

## Notes before submitting

- 以下表述建议替换为你自己的真实口径（我无法核实内部数据，因此刻意没有写任何具体百分比或人效数字）：案例一、二、三中"十年前/现在"的流程对比若有更准确的说法（例如你们的实际复核比例、平均耗时），补一句具体的会更像你本人写的。
- 若课程要求只交英文版，删掉中文版即可；两版内容一致，不是机翻对照。
- 字数：英文正文约 790 词，中文正文约 1310 字，均远超 200 字要求。
