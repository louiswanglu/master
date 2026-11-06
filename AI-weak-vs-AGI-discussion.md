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

## 中文版（备用，约 1800 字，大白话口语版）

所谓弱人工智能，说白了就是"只会干一件事"的 AI。它在一个划死的范围里把某件事做到极致——靠大量数据学出来的规律去逼近一个定好的目标，但它挪不到别的领域去，不会自己给自己定目标，也说不清自己为什么这么判。AlphaFold 算蛋白结构、垃圾邮件过滤器、读身份证的模型，都是这一类：在自己那摊活上可能比人强，往外走一步就废了。AGI 不一样，它讲的是"什么都能干"——一个系统把人类会的东西都学会，能从一个领域跳到毫不相干的另一个领域，到了没见过的情况还能自己应付。这中间差的不只是规模，是几种现在还没有的能力：记得住事、对世界有因果的理解、以及知道自己有多不确定。多模态之所以容易让人看错，是因为它一次能吃文字、图片、声音，看起来"什么都懂"。其实不是。每一项本事还是只在一个固定范围里训练、在固定范围里考试，整个流程还是人给它排好的。

我干的这行是 eKYC 加征信，做印尼和菲律宾市场。在这儿这个区别不是课堂上讨论的东西：我们上线的模型，决定一个真人能不能拿到贷款，也决定她还不上钱的时候我们怎么去找她。

**案例一：印尼的开户实名认证。** 一份申请交上来，主要是两样东西：一张 e-KTP 的照片（印尼的芯片身份证，Dukcapil 发的，卡上有人像和签名），加一堆手填的字——姓名、NIK、地址，有时候再附一张工资单或者家庭卡。十年前，审核员得一张一张点开身份证照片，申请人当时什么光线拍的就照着看，看完再一个字一个字敲进去。这么干最容易出的问题就是累了就糊弄，两个人看同一张卡能录出两个结果。现在好了，机器先把卡上的字认出来，把人像和签名抠出来，再让语言模型写一段情况说明，交给人复核。这个岗位的活儿就变了：审核员不用再敲字，改成判那些"不对劲"的案子——证件签发日期比结婚证还早的、反光或者对着屏幕拍糊的、名字有两种拼法对不上的、签名跟档案里那个明显不是一个人的。这活儿很窄，而且必须窄。

**案例二：信用局处理争议。** 来投诉的人很少给你交一张填好的表。多半是一段急匆匆打出来的话，配一张拍的还款凭证、一份银行流水，或者一张钱包转账的截图。有时候三样都有，有时候除了那段话什么都没有。机器先把凭证上的金额、日期、流水号读出来，跟贷款账上的数对一遍；再用语言模型把用户说的和账上记的对齐，替分析师先写一稿底稿。这份底稿最后还要拿去跟印尼 SLIK 或者菲律宾 CIC 的数据再核一遍。这就是弱 AI 真正顶用的地方：量太大、口径要统一，先给你一版草稿让你去否。但它能到哪儿也很清楚——凭证拍糊了，或者用户说的跟流水对不上，除了人把原件打开来看，没别的办法。

**案例三：AI 催收。** 这个系统是我们团队自己做的。印尼和菲律宾这两个市场，逾期催收基本全靠打电话，这笔账一直很难算：一个催收员一天撑死打一百五十通，大多数没人接，接起来的也短、来来回回就那么几句、照着话术念。AI 催收不是把这个人干掉，是把这个人的活换个顺序干。系统自己拨出去，一开口就说我是自动助理，把账户、欠多少钱、什么时候到期报一遍，然后要么让对方答应一个还款日，要么发条 WhatsApp 和短信过去，里面带个还款链接——印尼那边，人真正会点开看的其实是 WhatsApp。回来的东西就很杂了，也是我这份工作里唯一文字、图片、声音三样一起进来的地方：对方在电话里说一句、打字回一句"我昨天已经付了"（sudah saya bayar kemarin）、或者干脆拍一张转账凭证过来，机器把凭证认出来跟账上对一遍。到这一步，一通电话才算变成一条能查的记录，而不是催收员脑子里记得的那点东西。

真正变的不是"打电话"这件事。催收员以前一天到晚在拨号，现在把时间花在系统筛出来推给人处理的案子上——家里困难的、有争议的、来投诉的，以及任何说"我要跟真人说话"的人。这里最要命的那个错，恰恰也最具体，也正是我不敢管它叫 AGI 的原因。印尼话和 Taglish 的语音识别，最弱的地方正好就是那种一句话里混两种语言、带地方口音的说话方式——而这恰恰是低收入借款人说话的样子。日期听错这件事一点都不中性。系统里记成"答应这周五还"，人家说的是下周五，这条假的还款承诺以后就会变成逾期天数，进到 SLIK 或者 CIC 里去，最后为它付代价的是借款人，不是我们。所以正确的做法是"窄，而且窄得能查"：人家实际说了什么就照实转写，机器没听明白的地方明明白白标出来，交给人去看，别猜。另外，按印尼的《个人数据保护法》和菲律宾《数据隐私法》，通话录音本身就是个人信息，得先拿到人家同意——这就是为什么话术怎么念、录音存多久，都是产品本身要解决的事，不是回头再补的文档。

三个案例的理儿是一个：这种只会干一件事的多模态 AI，实际上是在把"看"和"抄"这些活从人身上卸下来，让专业的人把注意力放在判断、伦理和担责任上。AGI 会从另一个方向改这个行业——它接管的是判断本身。信贷这行，那天还没到；把今天当成那天来过，就不是效率问题了，是合规问题。一笔说不清理由的拒绝，或者一条催收日志上记着借款人根本没答应过的还款承诺，恰恰是监管会要我们解释的东西。所以这两类 AI 的区别不是什么技术趣闻，是那条线——线这边是让同事们干活快一点的工具，线那边是我们要上法庭、对着被我们搞错档案的那个人，替它的判断过程负责的系统。

---

## Notes before submitting

- 三个案例对应你真实业务的三块：eKYC 开户（文本 + 图像）、信用局争议（文本 + 图像）、AI 催收（文本 + 图像 + 语音）。语音只出现在案例三，也就是你们真正在做语音的那个产品。
- 我刻意没有写任何百分比或人效数字（如催收员日均拨打量、接通率、回收率提升），因为无法核实。案例三里"一天一百五十通"是行业常见量级，若有真实数字请替换——这一处替换会让整段立刻更像本人所写。
- 若课程要求只交英文版，删掉中文版即可；两版内容一致，不是机翻对照。
- 中文版是按口语重写的，不是英文版逐句直译；两版论点和案例一致，但语气不同，中文版更像你在群里跟同事讲这事。
- 字数：英文正文约 980 词，中文正文约 1800 字，均远超 200 字要求。
