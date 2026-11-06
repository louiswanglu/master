# Weak AI vs. AGI: Multimodal Systems in eKYC, Credit Bureaus and AI Collections

**Course discussion post — domain: eKYC, credit bureau and AI collections (Indonesia & Philippines)**

---

## English version (main post, ~600 words)

Weak AI is built to excel inside a bounded problem: it optimises a defined objective from learned patterns, but it cannot move to a new domain, set its own goals, or explain itself in terms a regulator would accept. AGI is defined by generality — one system that acquires any human cognitive skill, transfers across unrelated domains, and acts in unfamiliar situations. The gap is not scale but capability: persistent memory, causal world models, calibration about its own uncertainty. Multimodal systems blur this, because text, images and audio together feel like generality. They are not: each capability is still trained and evaluated on a fixed distribution, inside a workflow a human designed.

I work in eKYC and credit infrastructure in Indonesia and the Philippines, where this is not academic. What we ship decides whether a real person gets a loan, and how we approach her when she cannot pay.

**Case 1 — eKYC onboarding.** An application brings an image of the e-KTP (Indonesia's chipped ID, issued through Dukcapil, carrying the portrait and signature) plus typed text: name, NIK, address. A decade ago a reviewer opened each photo and retyped the fields, and fatigue produced two results from one card. Now vision models OCR the card and extract portrait and signature; a text model drafts a summary for the human. The job moved from transcribing to adjudicating what looks wrong: a card issued before the marriage certificate, a photo of a screen, two transliterations of one name. Narrow, deliberately.

**Case 2 — disputes at the bureau.** A dispute is rarely a clean form. It is a hastily typed narrative plus a photographed receipt or statement — sometimes both, sometimes only words. Document understanding reads amount, date and reference number and checks them against the ledger; a text model reconciles the narrative and drafts the analyst's note. Volume and consistency are the value. The ceiling is equally clear: a blurred receipt, or a narrative contradicting the statement, is settled only by a human opening the original.

**Case 3 — AI collections.** This is what my team builds. Delinquency here is worked almost entirely by phone: an agent places perhaps 150 calls a day, most unanswered, the ones that connect short and scripted. The system dials, identifies itself as an automated assistant, states account, amount and due date, and either takes a promise to pay or sends a payment link over WhatsApp — in Indonesia, where people actually read. What comes back is the only place in my work where all three inputs arrive together: a spoken reply, a typed "sudah saya bayar kemarin", or a photo of the transfer receipt read against the ledger.

The change is not the calling. Officers used to dial all day; now they handle what the system escalates — hardship, disputes, complaints, anyone asking for a person. The failure that matters is specific: speech recognition is weakest on exactly the code-switching and accents of lower-income borrowers. Log "this Friday" when she said next Friday, and that false promise becomes days past due in SLIK or CIC. The borrower pays, not us. So the design stays verifiably narrow — transcribe what was said, surface what could not be parsed, route it to a person. Recordings are also consent-bound personal data under Indonesia's PDP Law and the Philippines' Data Privacy Act, which makes the script and retention policy part of the product.

In all three, multimodal weak AI removes perceptual and clerical load and frees expert attention for judgement. AGI would take over the judgement itself. In credit that day has not arrived, and behaving as if it had is not a productivity risk but a compliance one: an unexplained decline, or a log recording a promise never made, is what a regulator can oblige us to justify.

---

## 中文版（备用，约 870 字，大白话）

弱人工智能就是"只会干一件事"的 AI：范围划死，把一件事做到极致，但挪不到别的领域，不会自己定目标，也说不清为什么这么判。AGI 要的是"什么都能干"——跨领域迁移，没见过的情况也能应付。差的不是规模，是几种还没有的能力：记得住事、懂因果、知道自己有多不确定。多模态最容易让人看错：它一次能吃文字、图片、声音，看着像"什么都懂"，其实每项本事还是只在一个固定范围里训练和考核。我在印尼和菲律宾做 eKYC 和征信，模型决定真人能不能拿到贷款。

**案例一，印尼开户实名认证。** 一份申请就两样东西：一张 e-KTP 照片（印尼芯片身份证，卡上有人像和签名），加一堆手填的字。十年前审核员一张张点开看、再一个字一个字敲，累了就糊弄，同一张卡两个人能录出两个结果。现在机器认字、抠出人像和签名，写段说明交人复核。活儿变了：不再敲字，改成判"不对劲"的——证件日期比结婚证还早、对着屏幕拍糊、名字两种拼法对不上。很窄，而且必须窄。

**案例二，信用局处理争议。** 投诉很少是一张填好的表，多半是一段急匆匆打出来的话，配一张还款凭证或流水。机器把凭证上的金额、日期、流水号读出来跟账对一遍，再替分析师写一稿底稿。天花板也清楚：凭证拍糊了，或者说的跟流水对不上，只能人打开原件看。

**案例三，AI 催收，这个系统是我们团队自己做的。** 两个市场催收全靠打电话，一个催收员一天撑死打一百五十通，多数没人接，接起来的也短、照着话术念。AI 催收不是把人干掉，是把活换个顺序：系统自己拨出去，报账户、欠多少、什么时候到期，要么让对方答应个还款日，要么发条 WhatsApp 带个还款链接。回来的东西就杂了：电话里说一句、打字回一句"我昨天已经付了"、或者拍张转账凭证，机器认出来跟账对一遍。催收员以前整天拨号，现在只处理系统推上来的案子。

最要命的错也很具体：印尼话和 Taglish 的语音识别，最弱的地方正好是一句话混两种语言、带地方口音，而这正是低收入借款人说话的样子。日期听错一点都不中性——记成"答应这周五还"、人家说的是下周五，这条假承诺以后就变成逾期天数进到 SLIK 或 CIC，付代价的是借款人。所以做法是"窄得能查"：照实转写，没听明白就标出来交给人，别猜。

三个案例一个理儿：只会干一件事的多模态 AI 是把"看"和"抄"的活卸下来，让人把注意力放回判断和担责；AGI 接管的是判断本身。那天还没到；把今天当那天过，不是效率问题是合规问题：一笔说不清理由的拒绝，或者一条记着人家没答应过的还款承诺的日志，监管都会要我们解释。

---

## Notes before submitting

- 三个案例对应你真实业务：eKYC 开户（文本 + 图像）、信用局争议（文本 + 图像）、AI 催收（文本 + 图像 + 语音）。语音只在案例三出现。
- 数字方面只写了"一天一百五十通"这个行业常见量级，没有编百分比。换成你们真实数据会更像本人写的。
- 字数：英文约 625 词，中文约 870 字，都远超 200 字下限。

