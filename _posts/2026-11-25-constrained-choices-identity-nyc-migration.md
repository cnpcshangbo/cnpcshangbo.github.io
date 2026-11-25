---
title: 'Constrained Choices in a Big City: Why People Stay, Why They Leave, and What They Are Really Paying For'
date: 2026-11-25
permalink: /posts/2026/11/constrained-choices-identity-nyc-migration/
excerpt: "When choice feels out of reach in a big city, spending is often not about luxury. It is about staying recognisable to yourself. Evidence from the Constrained Choices guide and New York City migration data, in English and Chinese."
tags:
  - urban life
  - constrained choices
  - migration
  - New York City
  - identity
  - household finance
toc: false
---

<style>
.lang-switch{margin:0 0 1rem;display:flex;gap:.5rem;flex-wrap:wrap}
.lang-switch button{padding:.35rem .9rem;border:1px solid #888;border-radius:999px;background:transparent;cursor:pointer;font-size:.9rem}
.lang-switch button.active{background:#222;color:#fff;border-color:#222}
.lang-note{font-size:.9rem;opacity:.85}
</style>

<div class="lang-switch" role="group" aria-label="Language / 语言">
  <button type="button" data-lang-btn="en" aria-pressed="true" class="active">English</button>
  <button type="button" data-lang-btn="zh" aria-pressed="false">中文</button>
</div>
<p class="lang-note">Default: English. The page follows your system language on first visit; you can switch any time. / 默认英语，首次访问会跟随系统语言，可随时切换。</p>

<script>
(function(){
  var KEY='cc-note-lang';
  function setLang(lang){
    document.querySelectorAll('.lang-en').forEach(function(el){ el.hidden = (lang!=='en'); });
    document.querySelectorAll('.lang-zh').forEach(function(el){ el.hidden = (lang!=='zh'); });
    document.querySelectorAll('[data-lang-btn]').forEach(function(b){
      var active=b.getAttribute('data-lang-btn')===lang;
      b.setAttribute('aria-pressed', active ? 'true' : 'false');
      b.classList.toggle('active', active);
    });
    document.documentElement.setAttribute('lang', lang==='zh' ? 'zh-CN' : 'en');
    try{ localStorage.setItem(KEY, lang); }catch(e){}
  }
  function initial(){
    try{
      var saved=localStorage.getItem(KEY);
      if(saved==='en'||saved==='zh') return saved;
    }catch(e){}
    var nav=(navigator.language||navigator.userLanguage||'en').toLowerCase();
    return nav.indexOf('zh')===0 ? 'zh' : 'en';
  }
  document.querySelectorAll('[data-lang-btn]').forEach(function(b){
    b.addEventListener('click', function(){ setLang(b.getAttribute('data-lang-btn')); });
  });
  setLang(initial());
})();
</script>

<div class="lang-en" lang="en" markdown="1">

## 1. The question

Why does change feel out of reach in a big city, even when a person can name exactly what is wrong? And why does spending on ordinary pleasures — eating out, shopping — continue even while debt grows?

This note brings together three things that are usually discussed separately:

1. a high-school research guide, *Constrained Choices*, which asks when everyday choices stop being real choices;
2. New York City migration data, which shows who actually leaves, who arrives, and who stays;
3. a hypothesis about identity: much of that spending is not a taste for luxury, but a way of remaining recognisable to oneself.

A note on method, before anything else. No individual or household is identified here, and no personal case is presented. The pattern in Section 5 is an anonymised, illustrative observation turned into a testable hypothesis — not a case study, and not evidence for the mechanism. The public data in Sections 2–4 establish the structure; the identity mechanism still needs its own evidence.

## 2. What *Constrained Choices* actually shows — and what it does not

*Constrained Choices* is a Merit Point Academy guide for high-school social research: "Room for choice. The geography of everyday choices — when life offers choices, why can change still feel out of reach?" It contains 20 research topics, 6 public data sources, and 5 research lenses. Its value here is structural, not anecdotal: it makes the trap measurable instead of moral.

Its only fully worked example, HPS-01, uses the U.S. Household Pulse Survey 2024, Phase 4.2, Cycle 09 (20 August – 16 September 2024, 45,857 complete valid cases). It crosses financial hardship (difficulty paying expenses) with unmet transport need, against anxiety symptoms (GAD-2 ≥ 3):

| Group | Share with anxiety symptoms |
|---|---:|
| Neither hardship | 9.97% (95% interval 9.31–10.63) |
| Financial hardship only | 28.43% (26.93–29.92) |
| Transport need only | 17.97% (14.41–21.53) |
| Both hardships | 43.73% (39.55–47.91) |

Two hardships together are worse than either alone. That is an association in a cross-section, not proof that hardship causes anxiety, and not proof of entrapment — the guide says so itself.

Its New York topics (ACS-01 to ACS-05) ask whether rent burden (≥30% of income, and ≥50% as a severe threshold) and long commutes (≥60 minutes one way) cluster in the same census tracts, using the 2019–2023 ACS 5-year data for the five counties. Its heat topics (NYC-01 to NYC-04) ask whether lower-income neighbourhoods are hotter. Its displacement topics carry the warning that matters most for this note: "A low displacement rate does not establish safety or entrapment. Studying people who are trapped requires direct measures of their desire and ability to move." Movement counts are not unique people, and movers do not represent those forced to remain.

So the guide supports the *structure* of the argument — fixed costs first, geography second, exit expensive — but it contains nothing on credit cards, eating out, shopping, or dignity spending. That mechanism needs a separate source.

## 3. New York City: a large two-way flow, not a one-way exodus

Two measurement systems must not be confused. The American Community Survey (ACS) asks where a person lived a year ago, so it gives gross in- and out-flows for a calendar year. The Census Bureau's Population Estimates Program (PEP) runs July to July, largely from IRS address changes and Medicare data, and gives net domestic and net international migration only. Their nets differ because the method and the period differ.

### Gross flows, ACS 2024

- Left New York City for elsewhere in the United States: about **296,000**
- Arrived from elsewhere in the United States: about **183,000**
- Net domestic loss: about **113,000** (±~25,000)
- Residents who had lived abroad a year earlier: about **98,000**

That is almost identical to 2015 (about 297,000 left, net domestic loss about 137,000). The pandemic was the exception: in 2021 departures rose about 50% to about 450,000, the net domestic loss reached about 266,000, and the share of prior-year residents leaving rose from 3.5% (2015 and 2024) to 5.2%. By 2024 departures were back to their 2015 level.

### Net flows, PEP (July to July, Vintage 2025)

| Period | Net domestic | Net international | Natural increase | Total change |
|---|---:|---:|---:|---:|
| 2020–21 | −329,532 | +19,997 | +29,791 | −303,230 |
| 2021–22 | −212,791 | +83,564 | +33,718 | −85,293 |
| 2022–23 | −120,939 | +155,131 | +35,647 | +71,169 |
| 2023–24 | −93,867 | +219,578 | +36,906 | +162,991 |
| 2024–25 | −113,718 | +65,824 | +36,101 | −12,196 |

In 2024–25 the city was roughly flat: population 8,585,000 in July 2025, essentially unchanged from July 2024 (whose estimate was revised up from 8,478,000 to 8,597,000, mainly because international inflows were re-estimated). International migration fell from its surge, domestic outflow widened slightly again, and births over deaths (+36,101) did the rest of the offsetting.

### Who comes, who leaves

Arrivals are young and credentialed: median age 27, 65% aged 18–34, 72% of adult arrivals holding a degree. Leavers are older (median 31), and after moving 45% live in owner-occupied housing, against 16% of arrivals; leavers live with children nearly twice as often. Children are the sharpest signal: in 2024 the net loss of people under 18 was about 29,000, and the city's under-18 population has fallen to its lowest level and share in decades.

The main destination is not Florida. It is the suburbs: about 35% of leavers, about 105,000 people, went to the metropolitan suburbs — northern New Jersey first, then Long Island, the Lower Hudson Valley, and southwestern Connecticut. Florida took about 22,000 (7%), California about 17,700, Pennsylvania about 14,400, Texas about 11,400. The suburbs sent about 47,000 people in and received about 105,000, so the net loss to the city's own suburbs is roughly as large as the net loss to all other states combined.

## 4. Why people consider leaving

The Census does not ask why people move. Reasons come from surveys, and they measure *considering* leaving, not the completed moves.

In the Citizens Budget Commission's June 2025 resident survey, among New Yorkers considering moving out, the top reasons were affordability (76%), safety (73%), and living space (60%). Only 34% rated the city's quality of life excellent or good, down from 51% in 2017, and 55% planned to remain in the city over the next five years. An Empire Center poll of New York State (not the city alone) ranked taxes first (30.4%) and cost of living second (26.1%), followed by politics and government (15.9%), housing affordability (6.7%), crime and safety (6.2%), and retirement and family (5.6%) — while noting that in New York City itself, cost of living ranked first.

Read together with Section 3, the picture is consistent: the push is not a single dramatic decision to go to Florida. It is rent, space, children, and remote work pushing households first to the suburbs — and the identity and cost of staying in the middle.

## 5. A hypothesis: much of the spending buys identity, not luxury

The pattern to explain is familiar: a household under financial strain keeps spending on eating out and shopping, and treats those things as non-negotiable, even while debt grows. The hypothesis is that the spending is maintaining an identity — "I am still a normal person" — and that cutting it would feel like admitting defeat, not like saving money.

Four layers, in increasing order of vulnerability:

1. **I am still me.** A meal out or a purchase is a small, repeatable proof that life has not collapsed into survival.
2. **I can still decide something.** When income, housing, and work feel decided by others, a discretionary purchase is one of the few choices left that is entirely one's own.
3. **I need an outlet.** Under sustained strain, spending is also coping: a break, a reward, a way to keep going.
4. **I do not want to be seen as poor, failed, or dependent.** Spending is partly performed for others — family, friends, children — as evidence that the household is still holding up.

Why does debt not stop it? Three mechanisms, each testable: credit defers the pain of paying, so the cost is abstract and future while the meal is concrete and today; the amounts are mentally filed under "living" rather than "luxury", so each instance feels small; and loss is asymmetric — saving $50 is just saving, while cancelling a meal feels like conceding "I can't make it here."

It helps to separate two kinds of identity spending. *Maintaining* identity is defensive: keeping the life one already has. *Upgrading* identity is offensive: becoming a manager, passing an interview in English, learning a system like eCW, negotiating a salary — a more dignified identity that costs time and effort rather than money. The first is fast and cheap per instance; the second is slow and expensive per step, but it is the one that changes the constraint.

What would falsify this? If, when income recovers, the same spending falls away immediately and without resistance, it was probably coping or habit, not identity. If, when a household is offered the same dignity more cheaply — a free community meal that feels generous rather than charitable, a lower-cost version of the same outing — it switches happily, the mechanism is price, not identity. If it refuses the cheaper substitute even when the experience is equivalent, identity is doing real work. Those are the tests a follow-up study should run, rather than assuming the answer from one observation.

## 6. What this does — and does not — imply about making money from it

If the hypothesis is right, there are two honest ways to serve the need, and one dishonest one.

**Sell soothing.** Small-ticket, high-frequency, low-guilt pleasures: a good cheap meal, a small treat, a brief escape that does not require a big decision. The product is relief, and the price must stay low enough that buying it does not create the next problem.

**Sell a way out.** Identity upgrades: manager skills, interview English, a certification, salary negotiation. Slower, higher value, and harder to sell, because the buyer has to believe the ladder is real. The middle form is non-depriving budgeting: protect a "joy budget" first, and cut elsewhere, rather than demanding that a household give up the spending that holds its identity together.

**Do not sell credit against the need.** Pushing instalments or credit to exploit identity spending is profitable in the short term and corrosive in the long term: it deepens the trap it claims to relieve, and it destroys the trust any durable business needs. The durable route is the opposite — give the same dignity more cheaply, or help the person move to an identity that no longer needs the spending to prove itself.

## 7. Limits and next steps

- The HPS double-hardship numbers are associations, not causes, and they are national, not New York-specific.
- ACS tract data cannot show that the same renter who is rent-burdened is also the one with the long commute.
- The migration reasons are survey responses from people considering leaving, not a census of why movers moved.
- The identity mechanism in Section 5 is a hypothesis. It needs: a survey that asks directly about "normal life" spending under strain; a comparison of households that keep it versus cut it; and an experiment offering a cheaper, dignity-preserving substitute.

The next step, if this becomes a longer study, is to run those three tests on the New York data that already exists — ACS, the Household Pulse Survey, and the CBC survey — before collecting anything new.

## Sources

- Merit Point Academy, *Constrained Choices* — <https://courses.hopeembark.org/guides/constrained-choices/>
- SparkyData, "Who Moves to and Leaves New York City" (ACS 2015–2024 PUMS) — <https://sparkydata.dev/articles/who-is-leaving-and-who-is-arriving>
- NYC Department of City Planning, *New York City's Population Estimates and Trends*, March 2026 release (Vintage 2025) — <https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/population/population-estimates/new-york-city-population-estimates-and-trends-march-2026.pdf>
- NYC Department of City Planning, *New York City's Population Estimates and Trends*, May 2025 release (Vintage 2024) — <https://www.nyc.gov/assets/planning/downloads/pdf/our-work/reports/new-york-city-population-estimates-and-trends_may-2025.pdf>
- NYC Comptroller, "NYC's Post-Pandemic Rebound", December 2025 Spotlight — <https://comptroller.nyc.gov/wp-content/uploads/2025/12/Dec-2025-Spotlight-NYC-Overview.pdf>
- Citizens Budget Commission, *Straight From New Yorkers 2025*, June 2025 — <https://cbcny.org/sites/default/files/media/files/CBCREPORT_Resident-Survey-2025_06042025.pdf>
- Empire Center, "Leaving New York" opinion poll, 2026 (New York State, not New York City alone)

*Published 25 November 2026. Figures are as cited from the sources above; PEP estimates are revised with each vintage, so check the latest release before reusing the totals.*

</div>
<div class="lang-zh" lang="zh-CN" markdown="1" hidden>

# 受限的选择：大城市里，人们为什么留下、为什么离开、又到底在为什么付钱

## 1. 问题

为什么在大城市里，改变明明看得见，却总觉得够不着？为什么一个家庭明明已经负债，外出吃饭、购物的开销却一分不少，而且在当事人心里，那些开销根本没得商量？

这篇笔记把三件平时分开讨论的事放在一起：

1. 高中社会研究指南《Constrained Choices》（受限的选择），它问的是：日常选择在什么时候不再是真正的选择；
2. 纽约市的人口流动数据，它呈现的是谁真的离开、谁进来、谁留下；
3. 一个关于身份的假说：很多这类消费买的不是奢侈，而是一种“自己还是自己”的感觉。

先说方法。文中不指认任何个人或家庭，也不呈现任何个人案例。第 5 节的模式是一则经过匿名化处理的、 illustrative 的观察，被提炼成一个可检验的假说——不是案例研究，也不是该机制的证据。第 2–4 节的公开数据确立的是结构；身份机制本身，仍需要自己的证据。

## 2. 《Constrained Choices》到底说明了什么——以及没有说明什么

《Constrained Choices》是 Merit Point Academy 为高中社会研究编写的指南，副标题是：“Room for choice. The geography of everyday choices — when life offers choices, why can change still feel out of reach?”（有选择的余地。日常选择的地理学——当生活提供了选择，为什么改变仍然觉得遥不可及？）它包含 20 个研究主题、6 个公开数据源、5 个研究视角。它在这里的价值是结构性的，而不是轶事性的：它把“被困住”变成可以测量的东西，而不是道德评判。

它唯一完整算出结果的例子是 HPS-01，使用美国人口脉动调查（Household Pulse Survey）2024 年第 4.2 期第 09 周期（2024 年 8 月 20 日至 9 月 16 日，45,857 个完整有效样本）。它把经济困难（难以支付开支）与交通需求未被满足交叉，对照焦虑症状（GAD-2 ≥ 3）：

| 群体 | 有焦虑症状的比例 |
|---|---:|
| 两种困难都没有 | 9.97%（95% 区间 9.31–10.63） |
| 只有经济困难 | 28.43%（26.93–29.92） |
| 只有交通需求未满足 | 17.97%（14.41–21.53） |
| 两种困难都有 | 43.73%（39.55–47.91） |

两种困难叠加比任何一种单独出现都更糟。但这是截面数据里的关联，不是“困难导致焦虑”的证明，也不是“被困住”的证明——指南自己就是这么说的。

它关于纽约的主题（ACS-01 至 ACS-05）问的是：租金负担（占收入 ≥30%，≥50% 为严重负担）与长通勤（单程 ≥60 分钟）是否集中在同一个人口普查区，使用 2019–2023 年 ACS 五年数据，覆盖五个县。关于高温的主题（NYC-01 至 NYC-04）问的是：低收入社区是否更热。关于流离失所的主题里，有一句对这篇笔记最重要的警告：“低流离率并不能证明安全或被困。研究被困住的人，需要直接测量他们想走的意愿和能走的能力。”流动人数不是不重复计算的人数，搬走的人也不能代表那些被迫留下的人。

所以，这份指南支撑的是论证的*结构*——固定成本先行、地理位置其次、退出成本高昂——但它完全没有涉及信用卡、外出吃饭、购物或尊严消费。那个机制，需要另外的来源。

## 3. 纽约市：大规模的双向流动，而不是单向出走

两套统计口径不能混用。美国社区调查（ACS）问的是“一年前住在哪里”，因此给出的是一个日历年里的毛流入和毛流出。人口普查局的人口估计项目（PEP）按 7 月到 7 月统计，主要依据国税局地址变更和医保数据，只给出国内净迁移和国际净迁移。两者的净数不同，是因为方法和统计期不同。

### 毛流量，ACS 2024 年

- 离开纽约市、去往美国其他地方：约 **296,000 人**
- 从美国其他地方搬进来：约 **183,000 人**
- 国内净流失：约 **113,000 人**（误差约 ±25,000）
- 一年前住在国外的居民：约 **98,000 人**

这与 2015 年几乎相同（约 297,000 人离开，国内净流失约 137,000 人）。疫情是例外：2021 年离开的人数上升约 50%，达到约 450,000 人，国内净流失达到约 266,000 人，离开的前一年居民比例从 3.5%（2015 年和 2024 年）上升到 5.2%。到 2024 年，离开人数已回到 2015 年的水平。

### 净流量，PEP（7 月到 7 月，Vintage 2025）

| 时期 | 国内净迁移 | 国际净迁移 | 自然增长 | 总变化 |
|---|---:|---:|---:|---:|
| 2020–21 年 | −329,532 | +19,997 | +29,791 | −303,230 |
| 2021–22 年 | −212,791 | +83,564 | +33,718 | −85,293 |
| 2022–23 年 | −120,939 | +155,131 | +35,647 | +71,169 |
| 2023–24 年 | −93,867 | +219,578 | +36,906 | +162,991 |
| 2024–25 年 | −113,718 | +65,824 | +36,101 | −12,196 |

2024–25 年，城市人口基本持平：2025 年 7 月人口为 8,585,000 人，与 2024 年 7 月基本相同（2024 年 7 月的估计值从 8,478,000 上修到 8,597,000，主要是因为国际流入被重新估计）。国际移民从高峰回落，国内流出略有扩大，出生减死亡（+36,101）抵消了其余部分。

### 谁进来，谁离开

进来的人年轻且学历高：中位年龄 27 岁，65% 在 18–34 岁之间，72% 的成年迁入者拥有学位。离开的人年龄更大（中位 31 岁），搬走后 45% 住在自有住房里，而迁入者只有 16%；离开的人与孩子同住的比例接近迁入者的两倍。孩子是最尖锐的信号：2024 年 18 岁以下人口净流失约 29,000 人，纽约市 18 岁以下人口已降至几十年来最低的水平和占比。

最主要的去向不是佛州，而是郊区：约 35% 的离开者、约 105,000 人去了大都会郊区——新泽西北部居首，其次是长岛、下哈德逊河谷和康州西南部。佛州约 22,000 人（7%），加州约 17,700 人，宾州约 14,400 人，得州约 11,400 人。郊区送进来约 47,000 人，收走约 105,000 人，所以城市对自家郊区的净流失，大致相当于对其他所有州净流失的总和。

## 4. 人们为什么考虑离开

人口普查不问人们为什么搬家。原因来自调查，而且调查测量的是*考虑*离开，而不是已经完成的搬迁。

在 Citizens Budget Commission 2025 年 6 月的居民调查中，在考虑搬出纽约市的人里，最主要的原因是负担不起（76%）、安全（73%）和居住空间（60%）。只有 34% 的人认为城市生活质量优秀或良好，低于 2017 年的 51%；55% 的人计划未来五年留在城里。Empire Center 关于纽约州（不是单指纽约市）的民调中，税收排第一（30.4%），生活成本第二（26.1%），其次是政治与政府（15.9%）、住房可负担性（6.7%）、犯罪与安全（6.2%）、退休与家庭（5.6%）——同时指出，在纽约市本身，生活成本排第一。

把第 3 节和第 4 节放在一起看，图景是一致的：推动力不是某一天突然决定去佛州，而是房租、空间、孩子和远程工作，先把家庭推向郊区——而身份与留下的成本，处在中间。

## 5. 一个假说：很多消费买的是身份，不是奢侈

需要解释的模式很常见：一个经济紧张的家庭继续在外出吃饭和购物上花钱，并且把这些事看作没得商量，哪怕债务在增长。假说是：这笔消费在维持一种身份——“我还是一个正常人”——而砍掉它，感觉上不是省钱，而是承认失败。

按脆弱程度递进，有四个层面：

1. **我还是我。**一次外出吃饭或一次购买，是一个小而可重复的证明：生活还没有坍缩成单纯的生存。
2. **我还能决定点什么。**当收入、住房和工作都像是别人决定的，一笔自主的消费是少数完全属于自己的选择。
3. **我需要一个出口。**在持续的压力下，消费也是一种应对：休息、奖励、继续撑下去的方式。
4. **我不想被看作穷人、失败者或依赖者。**消费部分是做给别人看的——家人、朋友、孩子——证明这个家庭还撑得住。

为什么债务拦不住它？三个机制，每一个都可以检验：信用卡把付款的痛苦推迟了，成本是抽象的、未来的，而一顿饭是具体的、今天的；这些钱在心里被归入“生活”而不是“奢侈”，所以每一笔看起来都很小；损失是不对称的——省下 50 美元只是省钱，而取消一顿饭却像是在承认“我在这里撑不下去了”。

区分两种身份消费会有帮助。*维持*身份是防御性的：保住已经拥有的生活。*提升*身份是进攻性的：成为一名经理、用英语通过面试、学会 eCW 这样的系统、谈成更高的薪水——一种更有尊严的身份，花的不是钱，而是时间和努力。前者每次都快而便宜；后者每一步都慢而昂贵，但只有它能改变约束本身。

什么可以证伪这个假说？如果收入恢复后，同样的消费立刻、毫无阻力地消失，那它很可能只是应对或习惯，而不是身份。如果给一个家庭提供同样有尊严、但更便宜的替代品——一顿让人感觉慷慨而不是施舍的社区餐、一次成本更低的同样出游——它愉快地接受了，那起作用的就是价格，而不是身份。如果它在体验相当的情况下仍然拒绝更便宜的替代品，身份就确实在起作用。这些是后续研究应该做的检验，而不是从一次观察就假定答案。

## 6. 这对“靠它赚钱”意味着什么——以及不意味着什么

如果假说成立，有两种诚实的方式可以服务于这种需求，还有一种不诚实的方式。

**卖安抚。**小额、高频、低负罪感的愉悦：一顿好吃又便宜的饭、一个小奖励、一次不需要重大决定的短暂逃离。产品是缓解，价格必须低到买它不会制造下一个问题。

**卖出路。**身份提升：管理技能、面试英语、一张证书、薪资谈判。更慢、价值更高、也更难卖，因为买家必须相信这条梯子是真的。中间形态是不剥夺式预算：先保住一笔“快乐预算”，再从别处省钱，而不是要求一个家庭放弃维系其身份的消费。

**不要靠这种需求卖信用。**用分期或信贷去利用身份消费，短期有利可图，长期具有腐蚀性：它加深了它声称要缓解的困境，也摧毁了任何长期生意都需要信任。持久的做法正好相反——用更便宜的方式给人同样的尊严，或者帮助一个人走向一种不再需要靠消费来证明自己的身份。

## 7. 局限与下一步

- HPS 的双重困难数字是关联，不是因果，而且是全国性的，不是纽约市特有的。
- ACS 的人口普查区数据无法证明：同一个租金负担重的租户，就是那个通勤时间长的人。
- 关于搬迁原因的数据，是考虑离开的人的调查回答，不是搬迁者为什么搬走的人口普查。
- 第 5 节的身份机制是一个假说。它需要：直接询问“正常生活”消费在压力下的调查；比较保留这类消费与砍掉它的家庭；以及提供更便宜、同时保住尊严的替代品的实验。

如果这成为一项更长的研究，下一步是在收集任何新数据之前，先用已有数据做这三项检验——ACS、人口脉动调查和 CBC 的调查。

## 资料来源

- Merit Point Academy，《Constrained Choices》——<https://courses.hopeembark.org/guides/constrained-choices/>
- SparkyData，"Who Moves to and Leaves New York City"（ACS 2015–2024 PUMS）——<https://sparkydata.dev/articles/who-is-leaving-and-who-is-arriving>
- 纽约市城市规划局，《New York City's Population Estimates and Trends》，2026 年 3 月发布（Vintage 2025）——<https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/population/population-estimates/new-york-city-population-estimates-and-trends-march-2026.pdf>
- 纽约市城市规划局，《New York City's Population Estimates and Trends》，2025 年 5 月发布（Vintage 2024）——<https://www.nyc.gov/assets/planning/downloads/pdf/our-work/reports/new-york-city-population-estimates-and-trends_may-2025.pdf>
- 纽约市主计长，"NYC's Post-Pandemic Rebound"，2025 年 12 月 Spotlight——<https://comptroller.nyc.gov/wp-content/uploads/2025/12/Dec-2025-Spotlight-NYC-Overview.pdf>
- Citizens Budget Commission，《Straight From New Yorkers 2025》，2025 年 6 月——<https://cbcny.org/sites/default/files/media/files/CBCREPORT_Resident-Survey-2025_06042025.pdf>
- Empire Center，"Leaving New York" 民调，2026 年（纽约州，不是单指纽约市）

*2026 年 11 月 25 日发布。数字均引自上述来源；PEP 估计值随每次 vintage 修订，复用总数前请核对最新发布。*

</div>
