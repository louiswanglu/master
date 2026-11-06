# Weak AI vs. AGI: Multimodal Systems in eKYC, Credit Bureaus and AI Collections

**Course discussion post — domain: eKYC, credit bureau and AI collections (Indonesia & Philippines)**
**Author's context:** eKYC, credit bureau and AI collection work across the Indonesian and Philippine markets.

---

## English version (main post, ~980 words)

Weak AI, or narrow AI, is built to excel inside a bounded problem space: it optimises a defined objective against patterns learned from data, but it cannot transfer its competence to a genuinely new domain, set its own goals, or explain itself in terms a regulator would accept. AGI is defined by generality — a single system that can acquire any cognitive skill a human can, transfer learning across unrelated domains, and act autonomously in unfamiliar situations. The gap is not one of scale but of capability: persistent memory, causal world models, and reliable calibration of its own uncertainty. Multimodal systems make this gap confusing, because they widen the input space — text, images, audio — and that breadth feels like generality. It is not. Each capability is still trained and evaluated on a fixed distribution, inside a workflow a human designed.

I work in eKYC and credit infrastructure, serving the Indonesian and Philippine markets, and this distinction is not academic there. What we ship decides whether a real person gets a loan, and how we approach her when she cannot pay it back.

**Case 1 — eKYC onboarding in Indonesia.** A typical application hands the system two modalities at once: an image of the applicant's e-KTP (the chipped national ID issued through Dukcapil, including the embedded photograph and signature), and typed text — name, NIK, address, sometimes a scanned salary slip or a family card. A decade ago a reviewer opened each e-KTP image, read it under whatever light the applicant had, and retyped the fields; the failure mode was fatigue and inconsistency. Now vision models OCR the card, extract the portrait and signature, and a text model drafts a case summary for the human. The professional practice has changed: the reviewer no longer transcribes, they adjudicate exceptions — a woman whose card predates her marriage certificate, a card photographed under glare or a screen, a name transliterated two ways, a signature that no longer matches the one on file. Narrow, and deliberately so.

**Case 2 — dispute operations at the credit bureau.** A dispute rarely arrives as a clean form. It arrives as a narrative typed in haste, plus a photographed payment receipt, a bank statement, or a screenshot of a wallet transfer — sometimes all three, sometimes nothing but the narrative. Document understanding reads the receipt, pulls amount, date and reference number, and checks them against the loan ledger; a text model reconciles the narrative with the record and drafts the analyst's working note on a file that will be read against SLIK data in Indonesia or CIC data in the Philippines. This is where weak AI earns its keep — volume, consistency, and a first draft an analyst can reject. It also shows the ceiling clearly: when the receipt is blurred, or the narrative contradicts the statement, nothing but a human opening the original settles it.

**Case 3 — AI collections.** This is the system my team builds. Delinquency in both markets is worked overwhelmingly over the phone, and the economics have always been brutal: an agent can place perhaps a hundred and fifty calls a day, most of them unanswered, and the ones that connect are short, repetitive and scripted. An AI collection system does not remove the human; it changes what the human does first. The system dials, identifies itself as an automated assistant, states the account, the amount and the due date, and either takes a promise to pay or pushes a payment link over WhatsApp and SMS — which, in Indonesia especially, is where people actually read things. What comes back is genuinely multimodal, and this is the only place in my work where all three inputs arrive at once: a spoken reply during the call, a typed "sudah saya bayar kemarin", or a photo of the transfer receipt that the vision model reads and matches against the ledger. Only then does a conversation become a structured record instead of an agent's memory.

The professional change is not the calling. It is that a collections officer used to spend the day dialling and now spends it on what the system escalates — hardship, disputes, complaints, and anyone who asks for a person. The failure that matters is equally specific, and it is why I would not call this AGI even on a good day. Speech recognition in Bahasa Indonesia and Taglish is weakest exactly on the code-switching and regional accents of lower-income borrowers, and a misheard date is not a neutral error. If the log records "promised to pay this Friday" when the borrower said next Friday, that false promise is what later reaches SLIK or CIC as days past due, and the borrower pays for it, not us. So the correct design is narrow in a verifiable way: transcribe what was actually said, surface what the model could not parse, and route those cases to a person rather than guessing. Under Indonesia's Personal Data Protection Law and the Philippines' Data Privacy Act, a recording is also personal data with consent attached, which is why the call script and the retention policy are part of the product rather than an afterthought.

The pattern across all three is identical: multimodal weak AI removes perceptual and clerical load, freeing expert attention for judgement, ethics and accountability. AGI would change the profession differently — it would take over the judgement itself. In credit that day has not arrived, and behaving as if it had is not a productivity risk but a compliance one. An unexplained decline, or a collection log recording a promise the borrower never made, is exactly what a regulator can oblige us to justify. The difference between the two kinds of AI is therefore not a technical curiosity. It is the line between a tool that makes my colleagues faster and a system whose reasoning we would have to defend, in court, to the person whose file we got wrong.

---

## 中文版（备用，约 1540 字）

弱人工智能（Weak AI / Narrow AI）是在有限问题空间内被专门优化的系统：它依靠数据中的统计规律逼近某个既定目标，但无法把能力迁移到全新领域，无法自行设定目标，也无法用监管者能接受的方式解释自己的判断。通用人工智能（AGI）的关键在于通用性：同一个系统能习得人类任何认知技能、跨不相关领域迁移，并在陌生情境中自主行动。二者的差距不在规模，而在能力本身——持久记忆、因果世界模型，以及对自身不确定性的可靠校准。多模态系统把这个差距变得模糊：文本、图像、音频同时进入模型，输入空间的拓宽看起来像"通用"，但它并不通用——每项能力仍固定在既定分布上训练与评估，仍跑在人设计好的流程里。

我在 eKYC 与征信基础设施行业工作，服务印尼与菲律宾市场。在那里，这个区分不是学术问题：我们上线的模型决定一个真实的人能不能拿到贷款，也决定她还不上时我们怎么去找她。

**案例一：印尼的 eKYC 开户。** 一次申请同时交来两种模态：申请人 e-KTP（Dukcapil 发放的带芯片身份证，含卡内人像与签名）的影像，以及手填文本（姓名、NIK、地址，偶尔一份扫描的工资单或家庭卡）。十年前，审核员要逐张打开 e-KTP 图像，在申请人当时的灯光条件下辨认，再手工录入字段，失败模式是疲劳与不一致。现在视觉模型做 OCR，提取人像与签名，文本模型起草一份案情摘要给人工复核。专业实践随之改变：审核员不再录入，而是裁决例外——证件签发早于结婚证、反光下或对着屏幕拍糊的卡片、两种音译写法的姓名、与档案不一致的签名。它是窄的，而且必须窄。

**案例二：信用局的争议处理。** 争议很少以工整的表格到来。它是一段匆匆打出的文字陈述，加一张拍照的还款凭证、一份银行流水或一张钱包转账截图——有时三样都有，有时除了一段陈述什么都没有。文档理解读出凭证上的金额、日期与流水号，与贷款台账核对；文本模型把陈述与记录对齐，为分析师起草工作底稿，这份底稿最终会对照印尼 SLIK 或菲律宾 CIC 的数据被再次阅读。这是弱 AI 真正创造价值的地方：量大、口径一致、先给一版草稿供人否掉。它也很清楚地暴露了天花板：凭证拍糊了，或者陈述与流水互相矛盾，除了人打开原件来看，没有别的办法。

**案例三：AI 催收系统。** 这是我所在团队研发的系统。两个市场的逾期催收压倒性地靠电话完成，而经济账一直很难看：一名催收员一天大概能拨一百五十通电话，大部分没人接，接通的那些也短、重复、照脚本念。AI 催收系统不是把这个人拿掉，而是改变这个人先做什么。系统外呼，自报是自动助理，说明账户、欠款金额与到期日，要么拿到还款承诺，要么通过 WhatsApp 与短信推送还款链接——在印尼，人们真正会看的其实是 WhatsApp。回来的东西是真正的多模态，也是我这份工作里唯一三种输入同时到达的地方：通话中的语音回复、打字的"sudah saya bayar kemarin"（我昨天已经付了），或者一张转账凭证照片，由视觉模型读出并与台账比对。到这一步，一段对话才变成一条结构化记录，而不是催收员脑子里的记忆。

专业实践的改变不在"打电话"这件事上。催收员过去整天在拨号，现在把时间花在系统升级上来的案子——困难户、争议、投诉，以及任何要求跟真人说话的人。真正要命的失败点同样具体，也正是我不敢把它叫作 AGI 的原因。印尼语与 Taglish 的语音识别，恰恰在语码转换和低收入借款人的地方口音上表现最差，而"日期听错"不是中性错误。如果系统记为"承诺本周五还款"，而借款人说的是下周五，这条假的还款承诺以后会以逾期天数的形式进入 SLIK 或 CIC，为此买单的是借款人，不是我们。所以正确的设计是"可验证地窄"：如实转写实际说了什么，把模型没解析出来的部分显式暴露出来，交给人工处理，而不是猜。在印尼《个人数据保护法》与菲律宾《数据隐私法》下，通话录音还属于带同意前提的个人数据——这就是为什么话术脚本与留存策略是产品的一部分，而不是事后补的文档。

三个案例的规律完全一致：多模态弱 AI 卸下感知与事务性负荷，把专家的注意力释放给判断、伦理与问责。AGI 会以另一种方式改变这个职业——它会接管判断本身。在信贷行业，那一天尚未到来；把今天当那一天来用，不是效率风险，而是合规风险。一笔无法解释的拒绝，或一条记着借款人从未做过的还款承诺的催收日志，恰恰是监管可以要求我们解释的东西。所以这两类 AI 的区别不是技术趣闻，而是那条线——线的一边是让同事们更快的工具，另一边是我们要在法庭上、对被我们弄错档案的那个人，为其推理过程负责的系统。

---

## Notes before submitting

- 三个案例对应你真实业务的三块：eKYC 开户（文本 + 图像）、信用局争议（文本 + 图像）、AI 催收（文本 + 图像 + 语音）。语音只出现在案例三，也就是你们真正在做语音的那个产品。
- 我刻意没有写任何百分比或人效数字（如催收员日均拨打量、接通率、回收率提升），因为无法核实。案例三里"一天一百五十通"是行业常见量级，若有真实数字请替换——这一处替换会让整段立刻更像本人所写。
- 若课程要求只交英文版，删掉中文版即可；两版内容一致，不是机翻对照。
- 字数：英文正文约 980 词，中文正文约 1540 字，均远超 200 字要求。
