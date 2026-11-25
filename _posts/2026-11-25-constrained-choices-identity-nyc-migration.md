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

.cc-chart{margin:1.2rem 0}
.cc-chart h4{margin:.2rem 0 .6rem;font-size:1rem}
.cc-row{display:flex;align-items:center;gap:.5rem;margin:.35rem 0}
.cc-lab{width:6.5rem;flex:none;text-align:right;font-size:.85rem}
.cc-track{flex:1;position:relative;height:1.35rem;background:#eee;border-radius:4px;overflow:hidden}
.cc-fill{position:absolute;top:0;bottom:0;border-radius:4px}
.cc-val{width:4.6rem;flex:none;font-size:.85rem;font-variant-numeric:tabular-nums}
.cc-note{font-size:.82rem;opacity:.8;margin-top:.4rem}
.cc-btn{padding:.25rem .8rem;border:1px solid #888;border-radius:999px;background:transparent;cursor:pointer;font-size:.85rem;margin-right:.4rem}
.cc-btn.active{background:#222;color:#fff;border-color:#222}
.cc-detail{border:1px solid #bbb;border-radius:8px;padding:.7rem 1rem;background:#fafafa;margin-top:.6rem;font-size:.92rem}
.cc-pep-row{cursor:pointer}
.cc-pep-row:hover .cc-track{outline:2px solid #222}
.cc-mid{position:absolute;top:0;bottom:0;left:50%;width:1px;background:#999}
.cc-ci{display:none;position:absolute;top:-2px;bottom:-2px;border-left:2px solid #222;border-right:2px solid #222}
.cc-ci::before{content:"";position:absolute;left:0;right:0;top:50%;border-top:2px solid #222}
.show-ci .cc-ci{display:block}
.cc-outcome{border:1px solid #bbb;border-radius:8px;padding:.7rem 1rem;background:#fafafa;margin-top:.6rem;font-size:.92rem}
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
  if (document.readyState==='loading') {
    document.addEventListener('DOMContentLoaded', function(){ setLang(initial()); });
  } else {
    setLang(initial());
  }
})();
</script>

<script>
(function(){
  function init(){
  document.querySelectorAll('.cc-pep-row').forEach(function(row){
    row.addEventListener('click', function(){
      var d=row.dataset;
      document.querySelectorAll('.cc-pep-detail').forEach(function(box){
        if(box.dataset.lang==='zh'){
          box.innerHTML='<b>'+d.year+'</b>：国内净迁移 '+d.dom+' 人，国际净迁移 +'+d.int+' 人，自然增长 +'+d.nat+' 人，总变化 '+d.total+' 人。三个分量加总与总变化不完全相等，PEP 估计中另有残差。';
        } else {
          box.innerHTML='<b>'+d.year+'</b>: net domestic '+d.dom+', net international +'+d.int+', natural increase +'+d.nat+', total change '+d.total+'. The three components do not sum exactly to the total; the PEP estimates include a residual.';
        }
      });
      document.querySelectorAll('.cc-pep-row').forEach(function(r){ r.style.opacity = (r===row) ? '1' : '.55'; });
    });
  });
  document.querySelectorAll('[data-cc-view]').forEach(function(btn){
    btn.addEventListener('click', function(){
      var chart=btn.closest('.cc-chart');
      chart.querySelectorAll('[data-cc-view]').forEach(function(b){ b.classList.toggle('active', b===btn); });
      chart.querySelectorAll('.cc-gross-flow').forEach(function(el){ el.hidden = (btn.dataset.ccView!=='flow'); });
      chart.querySelectorAll('.cc-gross-net').forEach(function(el){ el.hidden = (btn.dataset.ccView!=='net'); });
    });
  });
  document.querySelectorAll('[data-cc-ci]').forEach(function(btn){
    btn.addEventListener('click', function(){
      var chart=btn.closest('.cc-chart');
      chart.classList.toggle('show-ci');
      btn.classList.toggle('active');
      btn.textContent = chart.classList.contains('show-ci') ? btn.dataset.on : btn.dataset.off;
    });
  });
  document.querySelectorAll('[data-cc-choice]').forEach(function(btn){
    btn.addEventListener('click', function(){
      var chart=btn.closest('.cc-chart');
      chart.querySelectorAll('[data-cc-choice]').forEach(function(b){ b.classList.toggle('active', b===btn); });
      chart.querySelectorAll('.cc-outcome').forEach(function(box){
        if(box.dataset.lang==='zh'){
          box.innerHTML = btn.dataset.ccChoice==='keep'
            ? '<b>保留这顿饭：</b>花掉 50 美元，身份保住了——“我还是一个正常人”。钱少了，但生活没有坍缩成单纯的生存。'
            : '<b>砍掉这顿饭：</b>省下 50 美元，但感觉上不是省钱，而是承认“我在这里撑不下去了”。省下的钱是真实的，付出的代价也是真实的——只是不在账单上。';
        } else {
          box.innerHTML = btn.dataset.ccChoice==='keep'
            ? '<b>Keep the meal:</b> $50 spent, identity kept — “I am still a normal person.” The money is gone, but life has not collapsed into survival.'
            : '<b>Cut the meal:</b> $50 saved, but it feels less like saving and more like conceding “I can’t make it here.” The saving is real, and so is the cost — it just isn’t on the bill.';
        }
      });
    });
  });
  }
  if (document.readyState==='loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
</script>

<div class="lang-en" lang="en" markdown="1">

## 1. The question

Why does change feel out of reach in a big city, even when a person can name exactly what is wrong? And why does spending on ordinary pleasures — eating out, shopping — continue even while debt grows?

This note brings together three things that are usually discussed separately:

1. a high-school research guide, <a id="cite-en-ccguide-1" href="#ref-en-ccguide"><i>Constrained Choices</i></a>, which asks when everyday choices stop being real choices;
2. New York City migration data, which shows who actually leaves, who arrives, and who stays;
3. a hypothesis about identity: much of that spending is not a taste for luxury, but a way of remaining recognisable to oneself.

A note on method, before anything else. No individual or household is identified here, and no personal case is presented. The pattern in Section 5 is an anonymised, illustrative observation turned into a testable hypothesis — not a case study, and not evidence for the mechanism. The public data in Sections 2–4 establish the structure; the identity mechanism still needs its own evidence.

## 2. What *Constrained Choices* actually shows — and what it does not

<a id="cite-en-ccguide-2" href="#ref-en-ccguide"><i>Constrained Choices</i></a> is a Merit Point Academy guide for high-school social research: "Room for choice. The geography of everyday choices — when life offers choices, why can change still feel out of reach?" It contains 20 research topics, 6 public data sources, and 5 research lenses. Its value here is structural, not anecdotal: it makes the trap measurable instead of moral.

Its only fully worked example, HPS-01, uses the U.S. Household Pulse Survey 2024, Phase 4.2, Cycle 09 (20 August – 16 September 2024, 45,857 complete valid cases). It crosses financial hardship (difficulty paying expenses) with unmet transport need, against anxiety symptoms (GAD-2 ≥ 3):

| Group | Share with anxiety symptoms |
|---|---:|
| Neither hardship | 9.97% (95% interval 9.31–10.63) |
| Financial hardship only | 28.43% (26.93–29.92) |
| Transport need only | 17.97% (14.41–21.53) |
| Both hardships | 43.73% (39.55–47.91) |

Two hardships together are worse than either alone.

<div class="cc-chart" markdown="1">
<h4>Interactive: anxiety by hardship</h4>
<button type="button" class="cc-btn" data-cc-ci data-on="Hide 95% intervals" data-off="Show 95% intervals">Show 95% intervals</button>
<div class="cc-row"><span class="cc-lab">Neither</span><div class="cc-track"><div class="cc-fill" style="left:0;width:19.9%;background:#5dade2" title="9.97% (9.31–10.63)"></div><div class="cc-ci" style="left:18.6%;width:2.6%"></div></div><span class="cc-val">9.97%</span></div>
<div class="cc-row"><span class="cc-lab">Financial only</span><div class="cc-track"><div class="cc-fill" style="left:0;width:56.9%;background:#e67e22" title="28.43% (26.93–29.92)"></div><div class="cc-ci" style="left:53.9%;width:6.0%"></div></div><span class="cc-val">28.43%</span></div>
<div class="cc-row"><span class="cc-lab">Transport only</span><div class="cc-track"><div class="cc-fill" style="left:0;width:35.9%;background:#58d68d" title="17.97% (14.41–21.53)"></div><div class="cc-ci" style="left:28.8%;width:14.2%"></div></div><span class="cc-val">17.97%</span></div>
<div class="cc-row"><span class="cc-lab">Both</span><div class="cc-track"><div class="cc-fill" style="left:0;width:87.5%;background:#c0392b" title="43.73% (39.55–47.91)"></div><div class="cc-ci" style="left:79.1%;width:16.7%"></div></div><span class="cc-val">43.73%</span></div>
<p class="cc-note">Share with anxiety symptoms (GAD-2 ≥ 3), HPS 2024 Phase 4.2 Cycle 09, n = 45,857. Hover a bar for its 95% interval; use the button to show all intervals. Association, not causation.</p>
</div> That is an association in a cross-section, not proof that hardship causes anxiety, and not proof of entrapment — the guide says so itself.

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

<div class="cc-chart" markdown="1">
<h4>Interactive: the two-way flow</h4>
<button type="button" class="cc-btn active" data-cc-view="flow">Departures vs arrivals</button>
<button type="button" class="cc-btn" data-cc-view="net">Net domestic loss</button>
<div class="cc-gross-flow">
<div class="cc-row"><span class="cc-lab">2015 · left</span><div class="cc-track"><div class="cc-fill" style="left:0;width:59.4%;background:#c0392b" title="about 297,000 left"></div></div><span class="cc-val">~297,000</span></div>
<div class="cc-row"><span class="cc-lab">2015 · arrived</span><div class="cc-track"><div class="cc-fill" style="left:0;width:32.0%;background:#2471a3" title="about 160,000 arrived (derived)"></div></div><span class="cc-val">~160,000*</span></div>
<div class="cc-row"><span class="cc-lab">2021 · left</span><div class="cc-track"><div class="cc-fill" style="left:0;width:90.0%;background:#c0392b" title="about 450,000 left"></div></div><span class="cc-val">~450,000</span></div>
<div class="cc-row"><span class="cc-lab">2021 · arrived</span><div class="cc-track"><div class="cc-fill" style="left:0;width:36.8%;background:#2471a3" title="about 184,000 arrived (derived)"></div></div><span class="cc-val">~184,000*</span></div>
<div class="cc-row"><span class="cc-lab">2024 · left</span><div class="cc-track"><div class="cc-fill" style="left:0;width:59.2%;background:#c0392b" title="about 296,000 left"></div></div><span class="cc-val">~296,000</span></div>
<div class="cc-row"><span class="cc-lab">2024 · arrived</span><div class="cc-track"><div class="cc-fill" style="left:0;width:36.6%;background:#2471a3" title="about 183,000 arrived"></div></div><span class="cc-val">~183,000</span></div>
</div>
<div class="cc-gross-net" hidden>
<div class="cc-row"><span class="cc-lab">2015</span><div class="cc-track"><div class="cc-fill" style="left:0;width:27.4%;background:#c0392b" title="net domestic loss about 137,000"></div></div><span class="cc-val">−137,000</span></div>
<div class="cc-row"><span class="cc-lab">2021</span><div class="cc-track"><div class="cc-fill" style="left:0;width:53.2%;background:#c0392b" title="net domestic loss about 266,000"></div></div><span class="cc-val">−266,000</span></div>
<div class="cc-row"><span class="cc-lab">2024</span><div class="cc-track"><div class="cc-fill" style="left:0;width:22.6%;background:#c0392b" title="net domestic loss about 113,000 (±~25,000)"></div></div><span class="cc-val">−113,000</span></div>
</div>
<p class="cc-note">ACS, calendar year. *Arrivals for 2015 and 2021 are derived (departures minus net loss), not directly reported. The net view shows how small the pandemic spike looks against the ordinary two-way flow — and how large it was in 2021.</p>
</div>

### Net flows, PEP (July to July, Vintage 2025)

| Period | Net domestic | Net international | Natural increase | Total change |
|---|---:|---:|---:|---:|
| 2020–21 | −329,532 | +19,997 | +29,791 | −303,230 |
| 2021–22 | −212,791 | +83,564 | +33,718 | −85,293 |
| 2022–23 | −120,939 | +155,131 | +35,647 | +71,169 |
| 2023–24 | −93,867 | +219,578 | +36,906 | +162,991 |
| 2024–25 | −113,718 | +65,824 | +36,101 | −12,196 |

In 2024–25 the city was roughly flat:

<div class="cc-chart" markdown="1">
<h4>Interactive: what moved the population each year</h4>
<p class="cc-note" style="margin-top:0">Click a year to see its breakdown. Red (left) = net domestic migration; blue (right) = net international; green = natural increase. Total change is on the right.</p>
<div class="cc-row cc-pep-row" data-cc-year data-year="2020–21" data-dom="−329,532" data-int="19,997" data-nat="29,791" data-total="−303,230" title="Click for the breakdown / 点击查看分项"><span class="cc-lab">2020–21</span><div class="cc-track"><span class="cc-mid"></span><div class="cc-fill" style="right:50%;width:47.1%;background:#c0392b"></div><div class="cc-fill" style="left:50%;width:2.9%;background:#2471a3"></div><div class="cc-fill" style="left:calc(50% + 2.9%);width:4.3%;background:#229954"></div></div><span class="cc-val">−303,230</span></div><div class="cc-row cc-pep-row" data-cc-year data-year="2021–22" data-dom="−212,791" data-int="83,564" data-nat="33,718" data-total="−85,293" title="Click for the breakdown / 点击查看分项"><span class="cc-lab">2021–22</span><div class="cc-track"><span class="cc-mid"></span><div class="cc-fill" style="right:50%;width:30.4%;background:#c0392b"></div><div class="cc-fill" style="left:50%;width:11.9%;background:#2471a3"></div><div class="cc-fill" style="left:calc(50% + 11.9%);width:4.8%;background:#229954"></div></div><span class="cc-val">−85,293</span></div><div class="cc-row cc-pep-row" data-cc-year data-year="2022–23" data-dom="−120,939" data-int="155,131" data-nat="35,647" data-total="+71,169" title="Click for the breakdown / 点击查看分项"><span class="cc-lab">2022–23</span><div class="cc-track"><span class="cc-mid"></span><div class="cc-fill" style="right:50%;width:17.3%;background:#c0392b"></div><div class="cc-fill" style="left:50%;width:22.2%;background:#2471a3"></div><div class="cc-fill" style="left:calc(50% + 22.2%);width:5.1%;background:#229954"></div></div><span class="cc-val">+71,169</span></div><div class="cc-row cc-pep-row" data-cc-year data-year="2023–24" data-dom="−93,867" data-int="219,578" data-nat="36,906" data-total="+162,991" title="Click for the breakdown / 点击查看分项"><span class="cc-lab">2023–24</span><div class="cc-track"><span class="cc-mid"></span><div class="cc-fill" style="right:50%;width:13.4%;background:#c0392b"></div><div class="cc-fill" style="left:50%;width:31.4%;background:#2471a3"></div><div class="cc-fill" style="left:calc(50% + 31.4%);width:5.3%;background:#229954"></div></div><span class="cc-val">+162,991</span></div><div class="cc-row cc-pep-row" data-cc-year data-year="2024–25" data-dom="−113,718" data-int="65,824" data-nat="36,101" data-total="−12,196" title="Click for the breakdown / 点击查看分项"><span class="cc-lab">2024–25</span><div class="cc-track"><span class="cc-mid"></span><div class="cc-fill" style="right:50%;width:16.2%;background:#c0392b"></div><div class="cc-fill" style="left:50%;width:9.4%;background:#2471a3"></div><div class="cc-fill" style="left:calc(50% + 9.4%);width:5.2%;background:#229954"></div></div><span class="cc-val">−12,196</span></div>
<div class="cc-detail cc-pep-detail" data-lang="en">Click a year above — the 2023–24 surge was international migration (+219,578) doing the work, not a reversal of domestic outflow.</div>
<p class="cc-note">PEP, July to July, Vintage 2025. Scale: 350,000 people = half the bar. The three components do not sum exactly to the total; the PEP estimates include a residual.</p>
</div> population 8,585,000 in July 2025, essentially unchanged from July 2024 (whose estimate was revised up from 8,478,000 to 8,597,000, mainly because international inflows were re-estimated). International migration fell from its surge, domestic outflow widened slightly again, and births over deaths (+36,101) did the rest of the offsetting.

### Who comes, who leaves

Arrivals are young and credentialed: median age 27, 65% aged 18–34, 72% of adult arrivals holding a degree. Leavers are older (median 31), and after moving 45% live in owner-occupied housing, against 16% of arrivals; leavers live with children nearly twice as often. Children are the sharpest signal: in 2024 the net loss of people under 18 was about 29,000, and the city's under-18 population has fallen to its lowest level and share in decades.

The main destination is not Florida. It is the suburbs: about 35% of leavers, about 105,000 people, went to the metropolitan suburbs — northern New Jersey first, then Long Island, the Lower Hudson Valley, and southwestern Connecticut. Florida took about 22,000 (7%), California about 17,700, Pennsylvania about 14,400, Texas about 11,400. The suburbs sent about 47,000 people in and received about 105,000, so the net loss to the city's own suburbs is roughly as large as the net loss to all other states combined.

## 4. Why people consider leaving

The Census does not ask why people move. Reasons come from surveys, and they measure *considering* leaving, not the completed moves.

In the <a id="cite-en-cbc2025-1" href="#ref-en-cbc2025">Citizens Budget Commission's June 2025 resident survey</a>, among New Yorkers considering moving out, the top reasons were affordability (76%), safety (73%), and living space (60%). Only 34% rated the city's quality of life excellent or good, down from 51% in 2017, and 55% planned to remain in the city over the next five years. An <a id="cite-en-empire2026-1" href="#ref-en-empire2026">Empire Center poll</a> of New York State (not the city alone) ranked taxes first (30.4%) and cost of living second (26.1%), followed by politics and government (15.9%), housing affordability (6.7%), crime and safety (6.2%), and retirement and family (5.6%) — while noting that in New York City itself, cost of living ranked first.

Read together with Section 3, the picture is consistent:

<div class="cc-chart" markdown="1">
<h4>Interactive: why people consider leaving</h4>
<div class="cc-row"><span class="cc-lab">Affordability</span><div class="cc-track"><div class="cc-fill" style="left:0;width:76%;background:#c0392b" title="76% of those considering moving out"></div></div><span class="cc-val">76%</span></div>
<div class="cc-row"><span class="cc-lab">Safety</span><div class="cc-track"><div class="cc-fill" style="left:0;width:73%;background:#e67e22" title="73%"></div></div><span class="cc-val">73%</span></div>
<div class="cc-row"><span class="cc-lab">Living space</span><div class="cc-track"><div class="cc-fill" style="left:0;width:60%;background:#2471a3" title="60%"></div></div><span class="cc-val">60%</span></div>
<p class="cc-note">Citizens Budget Commission, June 2025 resident survey — share of New Yorkers <em>considering</em> moving out who named each reason. Hover a bar for the exact share. These are reasons for considering a move, not a census of why movers moved.</p>
</div> the push is not a single dramatic decision to go to Florida. It is rent, space, children, and remote work pushing households first to the suburbs — and the identity and cost of staying in the middle.

## 5. A hypothesis: much of the spending buys identity, not luxury

*Citations in this section link to the full references at the end of the note — click any author and year to jump there, and click &#8617; in a reference to jump back to where you were reading.*

The pattern to explain is familiar: a household under financial strain keeps spending on eating out and shopping, and treats those things as non-negotiable, even while debt grows. The hypothesis is that the spending is maintaining an identity — "I am still a normal person" — and that cutting it would feel like admitting defeat, not like saving money. The framework is identity economics: identity — a person's sense of self and the social categories they belong to — enters the utility function, so behaviour that looks wasteful on money alone can be rational once identity is counted (<a id="cite-en-akerlof2000-1" href="#ref-en-akerlof2000">Akerlof &amp; Kranton, 2000</a>; <a id="cite-en-oyserman2009-1" href="#ref-en-oyserman2009">Oyserman, 2009</a>).

Four layers, in increasing order of vulnerability:

1. **I am still me.** A meal out or a purchase is a small, repeatable proof that life has not collapsed into survival. Belk's argument is that possessions — and by extension, the experiences and objects consumption buys — are part of the self, so losing them diminishes the sense of self (<a id="cite-en-belk1988-1" href="#ref-en-belk1988">Belk, 1988</a>). The closest direct test: people whose self-esteem was threatened, and low-income people with bruised self-esteem, spent a larger share of income on status goods to repair self-worth, and an alternate way to restore self-worth removed the desire (<a id="cite-en-sivanathan2010-1" href="#ref-en-sivanathan2010">Sivanathan &amp; Pettit, 2010</a>).
2. **I can still decide something.** When income, housing, and work feel decided by others, a discretionary purchase is one of the few choices left that is entirely one's own. Experiments on powerlessness find the same pattern: feeling powerless raised willingness to pay, but only for status-related goods, not ordinary ones (<a id="cite-en-rucker2008-1" href="#ref-en-rucker2008">Rucker &amp; Galinsky, 2008</a>). And the active ingredient may be the choosing itself: making shopping choices — even hypothetical ones — reduced residual sadness by restoring a sense of personal control (<a id="cite-en-rick2014-1" href="#ref-en-rick2014">Rick, Pereira &amp; Burson, 2014</a>).
3. **I need an outlet.** Under sustained strain, spending is also coping: a break, a reward, a way to keep going. In field and diary studies, bad mood led people to buy themselves small treats as a deliberate mood-repair strategy, with lasting mood gains and no subsequent regret (<a id="cite-en-atalay2011-1" href="#ref-en-atalay2011">Atalay &amp; Meloy, 2011</a>). Scarcity itself narrows the bandwidth for planning and self-control (<a id="cite-en-mani2013-1" href="#ref-en-mani2013">Mani et al., 2013</a>; <a id="cite-en-mullainathan2013-1" href="#ref-en-mullainathan2013">Mullainathan &amp; Shafir, 2013</a>), which makes a quick, reliable outlet more attractive than a slow, effortful one.
4. **I do not want to be seen as poor, failed, or dependent.** Spending is partly performed for others — family, friends, children — as evidence that the household is still holding up. This is the oldest part of the argument: Veblen's conspicuous consumption, where failing to consume in due quantity and quality "becomes a mark of inferiority and demerit" (<a id="cite-en-veblen1899-1" href="#ref-en-veblen1899">Veblen, 1899</a>). Empirically, visible goods take a larger share of spending where status is at stake: Black and Hispanic households in the US spent about 25% more on visible goods than comparable White households after accounting for permanent income (<a id="cite-en-charles2009-1" href="#ref-en-charles2009">Charles, Hurst &amp; Roussanov, 2009</a>), and how visible an expenditure is predicts up to a third of the variation in income elasticities across goods (<a id="cite-en-heffetz2011-1" href="#ref-en-heffetz2011">Heffetz, 2011</a>). In interviews with 30 low-income UK families, ensuring children had the "right" brands was a strategy to avoid stigma and protect social identity (<a id="cite-en-hamilton2012-1" href="#ref-en-hamilton2012">Hamilton, 2012</a>). A recent field experiment in Abidjan finds the same logic from the other side: people invest in appearance and distort consumption to appear of higher rank, because being seen as very low rank means being sidelined from opportunities (<a id="cite-en-dupas2024-1" href="#ref-en-dupas2024">Dupas, Fafchamps &amp; Hernandez-Nunez, 2024</a>, NBER working paper).

Why does debt not stop it? Three mechanisms, each testable. First, credit defers the pain of paying, so the cost is abstract and future while the meal is concrete and today: willingness to pay rose by up to about 100% when people were told to pay by card rather than cash (<a id="cite-en-prelec2001-1" href="#ref-en-prelec2001">Prelec &amp; Simester, 2001</a>), and the theory is that payment carries its own immediate "pain", which credit decouples from consumption (<a id="cite-en-prelec1998-1" href="#ref-en-prelec1998">Prelec &amp; Loewenstein, 1998</a>). The link to identity is direct: under self-threat, people were willing to pay almost 30% more for status jeans and were over 60% more likely to intend to pay by credit (<a id="cite-en-pettit2011-1" href="#ref-en-pettit2011">Pettit &amp; Sivanathan, 2011</a>). Second, the amounts are mentally filed under "living" rather than "luxury", so each instance feels small: mental accounting assigns spending to non-fungible accounts and judges each instance in narrow isolation rather than summing them (<a id="cite-en-thaler1999-1" href="#ref-en-thaler1999">Thaler (1999)</a>). Third, loss is asymmetric — saving $50 is just saving, while cancelling a meal feels like conceding "I can't make it here": losses loom larger than equivalent gains (<a id="cite-en-kahneman1979-1" href="#ref-en-kahneman1979">Kahneman &amp; Tversky, 1979</a>), and giving up a valued good hurts more than receiving it pleases (<a id="cite-en-tversky1991-1" href="#ref-en-tversky1991">Tversky &amp; Kahneman, 1991</a>).

It helps to separate two kinds of identity spending. *Maintaining* identity is defensive: keeping the life one already has. *Upgrading* identity is offensive: becoming a manager, passing an interview in English, learning a system like eCW, negotiating a salary — a more dignified identity that costs time and effort rather than money. The first is fast and cheap per instance; the second is slow and expensive per step, but it is the one that changes the constraint. The closest formal model is the compensatory consumer behaviour model, whose five strategies include *direct resolution* — fixing the discrepancy itself, e.g. acquiring the skill — and *symbolic self-completion* and *fluid compensation* — using a product or experience to signal or substitute for the missing self (<a id="cite-en-mandel2017-1" href="#ref-en-mandel2017">Mandel et al., 2017</a>). The defensive/offensive labels are this note's own framing of that model, not the authors' terms. That poor households spend on more than subsistence is itself well documented: in household surveys across 13 countries, the extremely poor routinely spent a median 10% of their budget on festivals, weddings and funerals rather than extra food (<a id="cite-en-banerjee2007-1" href="#ref-en-banerjee2007">Banerjee &amp; Duflo, 2007</a>).

What would falsify this? If, when income recovers, the same spending falls away immediately and without resistance, it was probably coping or habit, not identity. If, when a household is offered the same dignity more cheaply — a free community meal that feels generous rather than charitable, a lower-cost version of the same outing — it switches happily, the mechanism is price, not identity. If it refuses the cheaper substitute even when the experience is equivalent, identity is doing real work. Those are the tests a follow-up study should run, rather than assuming the answer from one observation.

**What the literature does — and does not — show.** No published study tests the four-layer hypothesis as a whole, or eating out specifically, in a single design; the support above is component-wise, and applying it to a meal out is an interpretation, not a direct finding. Belk's extended self is about possessions, not meals. The "$50 saved versus meal cancelled" comparison is an application of loss aversion, not an experiment in Kahneman and Tversky. And the defensive/offensive distinction is this note's framing of Mandel et al.'s model, not their terminology. What the literature does establish is the mechanism's parts: identity enters economic decisions, threatened selves buy status, powerlessness is repaired by choosing, scarcity narrows bandwidth, visible spending signals rank, and credit decouples payment from pleasure.

<div class="cc-chart" markdown="1">
<h4>Try it: one $50 meal</h4>
<p class="cc-note" style="margin-top:0">An illustration of the mechanism, not data. A household under strain is deciding about one $50 meal out.</p>
<button type="button" class="cc-btn" data-cc-choice="keep">Keep the meal</button>
<button type="button" class="cc-btn" data-cc-choice="cut">Cut the meal</button>
<div class="cc-outcome" data-lang="en">Choose one — the point is that both options cost something, and only one of the costs shows up on a bill.</div>
</div>

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

- <span id="ref-en-ccguide"></span> Merit Point Academy, *Constrained Choices* — <https://courses.hopeembark.org/guides/constrained-choices/> <a href="#cite-en-ccguide-1" title="Back to the text">&#8617;1</a> <a href="#cite-en-ccguide-2" title="Back to the text">&#8617;2</a>
- <span id="ref-en-sparkydata"></span> SparkyData, "Who Moves to and Leaves New York City" (ACS 2015–2024 PUMS) — <https://sparkydata.dev/articles/who-is-leaving-and-who-is-arriving>
- <span id="ref-en-nycplanning2026"></span> NYC Department of City Planning, *New York City's Population Estimates and Trends*, March 2026 release (Vintage 2025) — <https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/population/population-estimates/new-york-city-population-estimates-and-trends-march-2026.pdf>
- <span id="ref-en-nycplanning2025"></span> NYC Department of City Planning, *New York City's Population Estimates and Trends*, May 2025 release (Vintage 2024) — <https://www.nyc.gov/assets/planning/downloads/pdf/our-work/reports/new-york-city-population-estimates-and-trends_may-2025.pdf>
- <span id="ref-en-comptroller2025"></span> NYC Comptroller, "NYC's Post-Pandemic Rebound", December 2025 Spotlight — <https://comptroller.nyc.gov/wp-content/uploads/2025/12/Dec-2025-Spotlight-NYC-Overview.pdf>
- <span id="ref-en-cbc2025"></span> Citizens Budget Commission, *Straight From New Yorkers 2025*, June 2025 — <https://cbcny.org/sites/default/files/media/files/CBCREPORT_Resident-Survey-2025_06042025.pdf> <a href="#cite-en-cbc2025-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-empire2026"></span> Empire Center, "Leaving New York" opinion poll, 2026 (New York State, not New York City alone) <a href="#cite-en-empire2026-1" title="Back to the text">&#8617;1</a>

### References for Section 5 — identity, status, and spending under strain

- <span id="ref-en-akerlof2000"></span> Akerlof, G. A., & Kranton, R. E. (2000). Economics and identity. *Quarterly Journal of Economics*, *115*(3), 715–753. <https://doi.org/10.1162/003355300554881> <a href="#cite-en-akerlof2000-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-akerlof2010"></span> Akerlof, G. A., & Kranton, R. E. (2010). *Identity Economics: How Our Identities Shape Our Work, Wages, and Well-Being*. Princeton University Press. ISBN 978-0-691-14648-5. <https://ideas.repec.org/a/eee/joepsy/v31y2010i6p1061-1063.html>
- <span id="ref-en-atalay2011"></span> Atalay, A. S., & Meloy, M. G. (2011). Retail therapy: A strategic effort to improve mood. *Psychology & Marketing*, *28*(6), 638–659. <https://doi.org/10.1002/mar.20404> <a href="#cite-en-atalay2011-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-banerjee2007"></span> Banerjee, A. V., & Duflo, E. (2007). The economic lives of the poor. *Journal of Economic Perspectives*, *21*(1), 141–168. <https://doi.org/10.1257/jep.21.1.141> <a href="#cite-en-banerjee2007-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-banerjee2011"></span> Banerjee, A. V., & Duflo, E. (2011). *Poor Economics*. PublicAffairs. ISBN 978-1-58648-798-0.
- <span id="ref-en-belk1988"></span> Belk, R. W. (1988). Possessions and the extended self. *Journal of Consumer Research*, *15*(2), 139–168. <https://doi.org/10.1086/209154> <a href="#cite-en-belk1988-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-case2008"></span> Case, A., Garrib, A., Menendez, A., & Olgiati, A. (2008). Paying the piper: The high cost of funerals in South Africa. NBER Working Paper No. 14456. <https://papers.ssrn.com/abstract=1294131> (working paper, not peer-reviewed)
- <span id="ref-en-charles2009"></span> Charles, K. K., Hurst, E., & Roussanov, N. (2009). Conspicuous consumption and race. *Quarterly Journal of Economics*, *124*(2), 425–467. <https://doi.org/10.1162/qjec.2009.124.2.425> <a href="#cite-en-charles2009-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-dupas2024"></span> Dupas, P., Fafchamps, M., & Hernandez-Nunez, L. (2024; rev. Dec 2025). Keeping up appearances: An experimental investigation of socioeconomic status signaling to avoid discrimination. NBER Working Paper No. 32491. <https://doi.org/10.3386/w32491> (working paper, not peer-reviewed) <a href="#cite-en-dupas2024-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-hamilton2012"></span> Hamilton, K. (2012). Low-income families and coping through brands: Inclusion or stigma? *Sociology*, *46*(1), 74–90. <https://doi.org/10.1177/0038038511416146> <a href="#cite-en-hamilton2012-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-heffetz2011"></span> Heffetz, O. (2011). A test of conspicuous consumption: Visibility and income elasticities. *Review of Economics and Statistics*, *93*(4), 1101–1117. <https://doi.org/10.1162/REST_a_00116> <a href="#cite-en-heffetz2011-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-kahneman1979"></span> Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, *47*(2), 263–291. <https://doi.org/10.2307/1914185> <a href="#cite-en-kahneman1979-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-landis2017"></span> Landis, B., & Gladstone, J. J. (2017). Personality, income, and compensatory consumption: Low-income extraverts spend more on status. *Psychological Science*, *28*(10), 1518–1520. <https://doi.org/10.1177/0956797617714811>
- <span id="ref-en-mandel2017"></span> Mandel, N., Rucker, D. D., Levav, J., & Galinsky, A. D. (2017). The compensatory consumer behavior model: How self-discrepancies drive consumer behavior. *Journal of Consumer Psychology*, *27*(1), 133–146. <https://doi.org/10.1016/j.jcps.2016.05.003> <a href="#cite-en-mandel2017-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-mani2013"></span> Mani, A., Mullainathan, S., Shafir, E., & Zhao, J. (2013). Poverty impedes cognitive function. *Science*, *341*(6149), 976–980. <https://doi.org/10.1126/science.1238041> <a href="#cite-en-mani2013-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-moav2012"></span> Moav, O., & Neeman, Z. (2012). Saving rates and poverty: The role of conspicuous consumption and human capital. *Economic Journal*, *122*(563), 933–956. <https://doi.org/10.1111/j.1468-0297.2012.02516.x>
- <span id="ref-en-mullainathan2013"></span> Mullainathan, S., & Shafir, E. (2013). *Scarcity: Why Having Too Little Means So Much*. Times Books. ISBN 978-0-8050-9264-6. <https://www.hks.harvard.edu/centers/cid/publications/books/scarcity-why-having-too-little-means-so-much> <a href="#cite-en-mullainathan2013-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-oyserman2009"></span> Oyserman, D. (2009). Identity-based motivation: Implications for action-readiness, procedural-readiness, and consumer behavior. *Journal of Consumer Psychology*, *19*(3), 250–260. <https://doi.org/10.1016/j.jcps.2009.05.008> <a href="#cite-en-oyserman2009-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-pettit2011"></span> Pettit, N. C., & Sivanathan, N. (2011). The plastic trap: Self-threat drives credit usage and status consumption. *Social Psychological and Personality Science*, *2*(2), 146–153. <https://doi.org/10.1177/1948550610385138> <a href="#cite-en-pettit2011-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-prelec1998"></span> Prelec, D., & Loewenstein, G. (1998). The red and the black: Mental accounting of savings and debt. *Marketing Science*, *17*(1), 4–28. <https://doi.org/10.1287/mksc.17.1.4> <a href="#cite-en-prelec1998-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-prelec2001"></span> Prelec, D., & Simester, D. (2001). Always leave home without it: A further investigation of the credit-card effect on willingness to pay. *Marketing Letters*, *12*(1), 5–12. <https://doi.org/10.1023/A:1008196717017> <a href="#cite-en-prelec2001-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-rick2014"></span> Rick, S. I., Pereira, B., & Burson, K. A. (2014). The benefits of retail therapy: Making purchase decisions reduces residual sadness. *Journal of Consumer Psychology*, *24*(3), 373–380. <https://doi.org/10.1016/j.jcps.2013.12.004> <a href="#cite-en-rick2014-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-rucker2008"></span> Rucker, D. D., & Galinsky, A. D. (2008). Desire to acquire: Powerlessness and compensatory consumption. *Journal of Consumer Research*, *35*(2), 257–267. <https://doi.org/10.1086/588569> <a href="#cite-en-rucker2008-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-rucker2009"></span> Rucker, D. D., & Galinsky, A. D. (2009). Conspicuous consumption versus utilitarian ideals: How different levels of power shape consumer behavior. *Journal of Experimental Social Psychology*, *45*(3), 549–555. <https://doi.org/10.1016/j.jesp.2009.01.005>
- <span id="ref-en-sivanathan2010"></span> Sivanathan, N., & Pettit, N. C. (2010). Protecting the self through consumption: Status goods as affirmational commodities. *Journal of Experimental Social Psychology*, *46*(3), 564–570. <https://doi.org/10.1016/j.jesp.2010.01.006> <a href="#cite-en-sivanathan2010-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-thaler1999"></span> Thaler, R. H. (1999). Mental accounting matters. *Journal of Behavioral Decision Making*, *12*(3), 183–206. <https://doi.org/10.1002/(SICI)1099-0771(199909)12:3%3C183::AID-BDM318%3E3.0.CO;2-F> <a href="#cite-en-thaler1999-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-tversky1991"></span> Tversky, A., & Kahneman, D. (1991). Loss aversion in riskless choice: A reference-dependent model. *Quarterly Journal of Economics*, *106*(4), 1039–1061. <https://doi.org/10.2307/2937956> <a href="#cite-en-tversky1991-1" title="Back to the text">&#8617;1</a>
- <span id="ref-en-veblen1899"></span> Veblen, T. (1899). *The Theory of the Leisure Class*. Macmillan. Full text: <https://www.gutenberg.org/ebooks/833> <a href="#cite-en-veblen1899-1" title="Back to the text">&#8617;1</a>


*Published 25 November 2026. Figures are as cited from the sources above; PEP estimates are revised with each vintage, so check the latest release before reusing the totals.*

</div>
<div class="lang-zh" lang="zh-CN" markdown="1" hidden>

# 受限的选择：大城市里，人们为什么留下、为什么离开、又到底在为什么付钱

## 1. 问题

为什么在大城市里，改变明明看得见，却总觉得够不着？为什么一个家庭明明已经负债，外出吃饭、购物的开销却一分不少，而且在当事人心里，那些开销根本没得商量？

这篇笔记把三件平时分开讨论的事放在一起：

1. 高中社会研究指南<a id="cite-zh-ccguide-1" href="#ref-zh-ccguide">《Constrained Choices》（受限的选择）</a>，它问的是：日常选择在什么时候不再是真正的选择；
2. 纽约市的人口流动数据，它呈现的是谁真的离开、谁进来、谁留下；
3. 一个关于身份的假说：很多这类消费买的不是奢侈，而是一种“自己还是自己”的感觉。

先说方法。文中不指认任何个人或家庭，也不呈现任何个人案例。第 5 节的模式是一则经过匿名化处理的、 illustrative 的观察，被提炼成一个可检验的假说——不是案例研究，也不是该机制的证据。第 2–4 节的公开数据确立的是结构；身份机制本身，仍需要自己的证据。

## 2. 《Constrained Choices》到底说明了什么——以及没有说明什么

<a id="cite-zh-ccguide-2" href="#ref-zh-ccguide">《Constrained Choices》</a>是 Merit Point Academy 为高中社会研究编写的指南，副标题是：“Room for choice. The geography of everyday choices — when life offers choices, why can change still feel out of reach?”（有选择的余地。日常选择的地理学——当生活提供了选择，为什么改变仍然觉得遥不可及？）它包含 20 个研究主题、6 个公开数据源、5 个研究视角。它在这里的价值是结构性的，而不是轶事性的：它把“被困住”变成可以测量的东西，而不是道德评判。

它唯一完整算出结果的例子是 HPS-01，使用美国人口脉动调查（Household Pulse Survey）2024 年第 4.2 期第 09 周期（2024 年 8 月 20 日至 9 月 16 日，45,857 个完整有效样本）。它把经济困难（难以支付开支）与交通需求未被满足交叉，对照焦虑症状（GAD-2 ≥ 3）：

| 群体 | 有焦虑症状的比例 |
|---|---:|
| 两种困难都没有 | 9.97%（95% 区间 9.31–10.63） |
| 只有经济困难 | 28.43%（26.93–29.92） |
| 只有交通需求未满足 | 17.97%（14.41–21.53） |
| 两种困难都有 | 43.73%（39.55–47.91） |

两种困难叠加比任何一种单独出现都更糟。

<div class="cc-chart" markdown="1">
<h4>互动图：按困难类型看焦虑比例</h4>
<button type="button" class="cc-btn" data-cc-ci data-on="隐藏 95% 区间" data-off="显示 95% 区间">显示 95% 区间</button>
<div class="cc-row"><span class="cc-lab">都没有</span><div class="cc-track"><div class="cc-fill" style="left:0;width:19.9%;background:#5dade2" title="9.97%（9.31–10.63）"></div><div class="cc-ci" style="left:18.6%;width:2.6%"></div></div><span class="cc-val">9.97%</span></div>
<div class="cc-row"><span class="cc-lab">只有经济困难</span><div class="cc-track"><div class="cc-fill" style="left:0;width:56.9%;background:#e67e22" title="28.43%（26.93–29.92）"></div><div class="cc-ci" style="left:53.9%;width:6.0%"></div></div><span class="cc-val">28.43%</span></div>
<div class="cc-row"><span class="cc-lab">只有交通困难</span><div class="cc-track"><div class="cc-fill" style="left:0;width:35.9%;background:#58d68d" title="17.97%（14.41–21.53）"></div><div class="cc-ci" style="left:28.8%;width:14.2%"></div></div><span class="cc-val">17.97%</span></div>
<div class="cc-row"><span class="cc-lab">两种都有</span><div class="cc-track"><div class="cc-fill" style="left:0;width:87.5%;background:#c0392b" title="43.73%（39.55–47.91）"></div><div class="cc-ci" style="left:79.1%;width:16.7%"></div></div><span class="cc-val">43.73%</span></div>
<p class="cc-note">有焦虑症状的比例（GAD-2 ≥ 3），HPS 2024 年第 4.2 期第 09 周期，n = 45,857。把鼠标悬停在条形上可以看到 95% 区间，点按钮可以显示全部区间。这是关联，不是因果。</p>
</div>但这是截面数据里的关联，不是“困难导致焦虑”的证明，也不是“被困住”的证明——指南自己就是这么说的。

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

<div class="cc-chart" markdown="1">
<h4>互动图：双向流动</h4>
<button type="button" class="cc-btn active" data-cc-view="flow">离开 vs 迁入</button>
<button type="button" class="cc-btn" data-cc-view="net">国内净流失</button>
<div class="cc-gross-flow">
<div class="cc-row"><span class="cc-lab">2015 · 离开</span><div class="cc-track"><div class="cc-fill" style="left:0;width:59.4%;background:#c0392b" title="约 297,000 人离开"></div></div><span class="cc-val">约 297,000</span></div>
<div class="cc-row"><span class="cc-lab">2015 · 迁入</span><div class="cc-track"><div class="cc-fill" style="left:0;width:32.0%;background:#2471a3" title="约 160,000 人迁入（推算）"></div></div><span class="cc-val">约 160,000*</span></div>
<div class="cc-row"><span class="cc-lab">2021 · 离开</span><div class="cc-track"><div class="cc-fill" style="left:0;width:90.0%;background:#c0392b" title="约 450,000 人离开"></div></div><span class="cc-val">约 450,000</span></div>
<div class="cc-row"><span class="cc-lab">2021 · 迁入</span><div class="cc-track"><div class="cc-fill" style="left:0;width:36.8%;background:#2471a3" title="约 184,000 人迁入（推算）"></div></div><span class="cc-val">约 184,000*</span></div>
<div class="cc-row"><span class="cc-lab">2024 · 离开</span><div class="cc-track"><div class="cc-fill" style="left:0;width:59.2%;background:#c0392b" title="约 296,000 人离开"></div></div><span class="cc-val">约 296,000</span></div>
<div class="cc-row"><span class="cc-lab">2024 · 迁入</span><div class="cc-track"><div class="cc-fill" style="left:0;width:36.6%;background:#2471a3" title="约 183,000 人迁入"></div></div><span class="cc-val">约 183,000</span></div>
</div>
<div class="cc-gross-net" hidden>
<div class="cc-row"><span class="cc-lab">2015</span><div class="cc-track"><div class="cc-fill" style="left:0;width:27.4%;background:#c0392b" title="国内净流失约 137,000 人"></div></div><span class="cc-val">−137,000</span></div>
<div class="cc-row"><span class="cc-lab">2021</span><div class="cc-track"><div class="cc-fill" style="left:0;width:53.2%;background:#c0392b" title="国内净流失约 266,000 人"></div></div><span class="cc-val">−266,000</span></div>
<div class="cc-row"><span class="cc-lab">2024</span><div class="cc-track"><div class="cc-fill" style="left:0;width:22.6%;background:#c0392b" title="国内净流失约 113,000 人（误差约 ±25,000）"></div></div><span class="cc-val">−113,000</span></div>
</div>
<p class="cc-note">ACS，按日历年。*2015 年和 2021 年的迁入人数是推算值（离开人数减净流失），不是直接报告的数字。切换到净流失视图可以看到：疫情高峰放在日常双向流动里看并不算大——但 2021 年那一年确实很大。</p>
</div>

### 净流量，PEP（7 月到 7 月，Vintage 2025）

| 时期 | 国内净迁移 | 国际净迁移 | 自然增长 | 总变化 |
|---|---:|---:|---:|---:|
| 2020–21 年 | −329,532 | +19,997 | +29,791 | −303,230 |
| 2021–22 年 | −212,791 | +83,564 | +33,718 | −85,293 |
| 2022–23 年 | −120,939 | +155,131 | +35,647 | +71,169 |
| 2023–24 年 | −93,867 | +219,578 | +36,906 | +162,991 |
| 2024–25 年 | −113,718 | +65,824 | +36,101 | −12,196 |

2024–25 年，城市人口基本持平：

<div class="cc-chart" markdown="1">
<h4>互动图：每年人口变化由什么驱动</h4>
<p class="cc-note" style="margin-top:0">点击某一行查看分项。红色（左）= 国内净迁移；蓝色（右）= 国际净迁移；绿色 = 自然增长。右侧数字是总变化。</p>
<div class="cc-row cc-pep-row" data-cc-year data-year="2020–21 年" data-dom="−329,532" data-int="19,997" data-nat="29,791" data-total="−303,230" title="Click for the breakdown / 点击查看分项"><span class="cc-lab">2020–21 年</span><div class="cc-track"><span class="cc-mid"></span><div class="cc-fill" style="right:50%;width:47.1%;background:#c0392b"></div><div class="cc-fill" style="left:50%;width:2.9%;background:#2471a3"></div><div class="cc-fill" style="left:calc(50% + 2.9%);width:4.3%;background:#229954"></div></div><span class="cc-val">−303,230</span></div><div class="cc-row cc-pep-row" data-cc-year data-year="2021–22 年" data-dom="−212,791" data-int="83,564" data-nat="33,718" data-total="−85,293" title="Click for the breakdown / 点击查看分项"><span class="cc-lab">2021–22 年</span><div class="cc-track"><span class="cc-mid"></span><div class="cc-fill" style="right:50%;width:30.4%;background:#c0392b"></div><div class="cc-fill" style="left:50%;width:11.9%;background:#2471a3"></div><div class="cc-fill" style="left:calc(50% + 11.9%);width:4.8%;background:#229954"></div></div><span class="cc-val">−85,293</span></div><div class="cc-row cc-pep-row" data-cc-year data-year="2022–23 年" data-dom="−120,939" data-int="155,131" data-nat="35,647" data-total="+71,169" title="Click for the breakdown / 点击查看分项"><span class="cc-lab">2022–23 年</span><div class="cc-track"><span class="cc-mid"></span><div class="cc-fill" style="right:50%;width:17.3%;background:#c0392b"></div><div class="cc-fill" style="left:50%;width:22.2%;background:#2471a3"></div><div class="cc-fill" style="left:calc(50% + 22.2%);width:5.1%;background:#229954"></div></div><span class="cc-val">+71,169</span></div><div class="cc-row cc-pep-row" data-cc-year data-year="2023–24 年" data-dom="−93,867" data-int="219,578" data-nat="36,906" data-total="+162,991" title="Click for the breakdown / 点击查看分项"><span class="cc-lab">2023–24 年</span><div class="cc-track"><span class="cc-mid"></span><div class="cc-fill" style="right:50%;width:13.4%;background:#c0392b"></div><div class="cc-fill" style="left:50%;width:31.4%;background:#2471a3"></div><div class="cc-fill" style="left:calc(50% + 31.4%);width:5.3%;background:#229954"></div></div><span class="cc-val">+162,991</span></div><div class="cc-row cc-pep-row" data-cc-year data-year="2024–25 年" data-dom="−113,718" data-int="65,824" data-nat="36,101" data-total="−12,196" title="Click for the breakdown / 点击查看分项"><span class="cc-lab">2024–25 年</span><div class="cc-track"><span class="cc-mid"></span><div class="cc-fill" style="right:50%;width:16.2%;background:#c0392b"></div><div class="cc-fill" style="left:50%;width:9.4%;background:#2471a3"></div><div class="cc-fill" style="left:calc(50% + 9.4%);width:5.2%;background:#229954"></div></div><span class="cc-val">−12,196</span></div>
<div class="cc-detail cc-pep-detail" data-lang="zh">点击上面某一行——2023–24 年的增长靠的是国际移民（+219,578 人），而不是国内流出逆转。</div>
<p class="cc-note">PEP，7 月到 7 月，Vintage 2025。比例尺：350,000 人 = 半条。三个分量加总与总变化不完全相等，PEP 估计中另有残差。</p>
</div>2025 年 7 月人口为 8,585,000 人，与 2024 年 7 月基本相同（2024 年 7 月的估计值从 8,478,000 上修到 8,597,000，主要是因为国际流入被重新估计）。国际移民从高峰回落，国内流出略有扩大，出生减死亡（+36,101）抵消了其余部分。

### 谁进来，谁离开

进来的人年轻且学历高：中位年龄 27 岁，65% 在 18–34 岁之间，72% 的成年迁入者拥有学位。离开的人年龄更大（中位 31 岁），搬走后 45% 住在自有住房里，而迁入者只有 16%；离开的人与孩子同住的比例接近迁入者的两倍。孩子是最尖锐的信号：2024 年 18 岁以下人口净流失约 29,000 人，纽约市 18 岁以下人口已降至几十年来最低的水平和占比。

最主要的去向不是佛州，而是郊区：约 35% 的离开者、约 105,000 人去了大都会郊区——新泽西北部居首，其次是长岛、下哈德逊河谷和康州西南部。佛州约 22,000 人（7%），加州约 17,700 人，宾州约 14,400 人，得州约 11,400 人。郊区送进来约 47,000 人，收走约 105,000 人，所以城市对自家郊区的净流失，大致相当于对其他所有州净流失的总和。

## 4. 人们为什么考虑离开

人口普查不问人们为什么搬家。原因来自调查，而且调查测量的是*考虑*离开，而不是已经完成的搬迁。

在 <a id="cite-zh-cbc2025-1" href="#ref-zh-cbc2025">Citizens Budget Commission 2025 年 6 月的居民调查</a>中，在考虑搬出纽约市的人里，最主要的原因是负担不起（76%）、安全（73%）和居住空间（60%）。只有 34% 的人认为城市生活质量优秀或良好，低于 2017 年的 51%；55% 的人计划未来五年留在城里。<a id="cite-zh-empire2026-1" href="#ref-zh-empire2026">Empire Center 关于纽约州（不是单指纽约市）的民调</a>中，税收排第一（30.4%），生活成本第二（26.1%），其次是政治与政府（15.9%）、住房可负担性（6.7%）、犯罪与安全（6.2%）、退休与家庭（5.6%）——同时指出，在纽约市本身，生活成本排第一。

把第 3 节和第 4 节放在一起看，图景是一致的：

<div class="cc-chart" markdown="1">
<h4>互动图：人们为什么考虑离开</h4>
<div class="cc-row"><span class="cc-lab">负担不起</span><div class="cc-track"><div class="cc-fill" style="left:0;width:76%;background:#c0392b" title="在考虑搬出的人里占 76%"></div></div><span class="cc-val">76%</span></div>
<div class="cc-row"><span class="cc-lab">安全</span><div class="cc-track"><div class="cc-fill" style="left:0;width:73%;background:#e67e22" title="73%"></div></div><span class="cc-val">73%</span></div>
<div class="cc-row"><span class="cc-lab">居住空间</span><div class="cc-track"><div class="cc-fill" style="left:0;width:60%;background:#2471a3" title="60%"></div></div><span class="cc-val">60%</span></div>
<p class="cc-note">Citizens Budget Commission，2025 年 6 月居民调查——在<em>考虑</em>搬出纽约市的人里，提到各原因的比例。把鼠标悬停在条形上可以看到精确数字。这些是“考虑离开”的原因，不是搬迁者为什么搬走的人口普查。</p>
</div>推动力不是某一天突然决定去佛州，而是房租、空间、孩子和远程工作，先把家庭推向郊区——而身份与留下的成本，处在中间。

## 5. 一个假说：很多消费买的是身份，不是奢侈

*本节的引用可点击，点作者和年份会跳转到文末的完整参考文献；点参考文献里的 &#8617; 可以跳回刚才读的位置。*

需要解释的模式很常见：一个经济紧张的家庭继续在外出吃饭和购物上花钱，并且把这些事看作没得商量，哪怕债务在增长。假说是：这笔消费在维持一种身份——“我还是一个正常人”——而砍掉它，感觉上不是省钱，而是承认失败。理论框架来自身份经济学：身份——一个人对自己的认知和所属的社会类别——进入了效用函数，所以只看钱会觉得浪费的行为，一旦计入身份就可能是合理的（<a id="cite-zh-akerlof2000-1" href="#ref-zh-akerlof2000">Akerlof &amp; Kranton, 2000</a>；<a id="cite-zh-oyserman2009-1" href="#ref-zh-oyserman2009">Oyserman, 2009</a>）。

按脆弱程度递进，有四个层面：

1. **我还是我。**一次外出吃饭或一次购买，是一个小而可重复的证明：生活还没有坍缩成单纯的生存。Belk 的论点是，物品——进而消费所购买的体验和东西——是自我的一部分，失去它们会削弱自我感（<a id="cite-zh-belk1988-1" href="#ref-zh-belk1988">Belk, 1988</a>）。最直接的检验是：自尊受到威胁的人，以及自尊受损的低收入者，会把更大比例的收入花在地位商品上以修复自我价值，而给他们另一条恢复自尊的路，这种欲望就消失了（<a id="cite-zh-sivanathan2010-1" href="#ref-zh-sivanathan2010">Sivanathan &amp; Pettit, 2010</a>）。
2. **我还能决定点什么。**当收入、住房和工作都像是别人决定的，一笔自主的消费是少数完全属于自己的选择。关于无力感的实验发现了同样的模式：感到无力会提高支付意愿，但只针对与地位有关的商品，普通商品则不会（<a id="cite-zh-rucker2008-1" href="#ref-zh-rucker2008">Rucker &amp; Galinsky, 2008</a>）。而且起作用的可能正是“选择”本身：做出购物的选择——哪怕只是假设性的——能通过恢复对环境的掌控感来缓解残留的悲伤（<a id="cite-zh-rick2014-1" href="#ref-zh-rick2014">Rick, Pereira &amp; Burson, 2014</a>）。
3. **我需要一个出口。**在持续的压力下，消费也是一种应对：休息、奖励、继续撑下去的方式。在商场实地研究和日记研究中，心情不好会让人给自己买小奖励，这是一种有意的情绪修复策略，效果持久，事后也没有后悔或内疚（<a id="cite-zh-atalay2011-1" href="#ref-zh-atalay2011">Atalay &amp; Meloy, 2011</a>）。稀缺本身会收窄用于规划和自控的认知带宽（<a id="cite-zh-mani2013-1" href="#ref-zh-mani2013">Mani et al., 2013</a>；<a id="cite-zh-mullainathan2013-1" href="#ref-zh-mullainathan2013">Mullainathan &amp; Shafir, 2013</a>），这让快速、可靠的出口比缓慢、费力的出口更有吸引力。
4. **我不想被看作穷人、失败者或依赖者。**消费部分是做给别人看的——家人、朋友、孩子——证明这个家庭还撑得住。这是这套论证里最古老的部分：Veblen 的炫耀性消费——未能按应有的数量和质量消费，“就成了低人一等和有过失的标志”（<a id="cite-zh-veblen1899-1" href="#ref-zh-veblen1899">Veblen, 1899</a>）。实证上，在地位受到威胁的地方，可见商品占支出的比重更大：美国黑人和西班牙裔家庭在可见商品上的支出比条件相当的白人家庭高约 25%（已计入永久收入）（<a id="cite-zh-charles2009-1" href="#ref-zh-charles2009">Charles, Hurst &amp; Roussanov, 2009</a>），而一项支出对别人有多可见，可以解释不同商品收入弹性差异的至多三分之一（<a id="cite-zh-heffetz2011-1" href="#ref-zh-heffetz2011">Heffetz, 2011</a>）。在对 30 个英国低收入家庭的访谈中，确保孩子拥有“对的”品牌是一种避免污名、保护社会身份的策略（<a id="cite-zh-hamilton2012-1" href="#ref-zh-hamilton2012">Hamilton, 2012</a>）。阿比让最近的一项实地实验从反面证实了同样的逻辑：人们会投资外表、扭曲消费以显得地位更高，因为被看作地位很低意味着在机会面前被边缘化（<a id="cite-zh-dupas2024-1" href="#ref-zh-dupas2024">Dupas, Fafchamps &amp; Hernandez-Nunez, 2024</a>，NBER 工作论文）。

为什么债务拦不住它？三个机制，每一个都可以检验。第一，信用卡把付款的痛苦推迟了，成本是抽象的、未来的，而一顿饭是具体的、今天的：当被告知用信用卡而不是现金支付时，支付意愿上升了至多约 100%（<a id="cite-zh-prelec2001-1" href="#ref-zh-prelec2001">Prelec &amp; Simester, 2001</a>），理论解释是付款本身带来即时的“痛苦”，而信用卡把这种痛苦与消费解耦了（<a id="cite-zh-prelec1998-1" href="#ref-zh-prelec1998">Prelec &amp; Loewenstein, 1998</a>）。与身份的联系是直接的：在自我受到威胁时，人们愿意为地位牛仔裤多付近 30%，而且更可能打算用信用卡支付的比例高出 60% 以上（<a id="cite-zh-pettit2011-1" href="#ref-zh-pettit2011">Pettit &amp; Sivanathan, 2011</a>）。第二，这些钱在心里被归入“生活”而不是“奢侈”，所以每一笔看起来都很小：心理账户把支出分到互不通用的账户里，并且以狭窄的视角逐笔评判，而不是加总起来看（<a id="cite-zh-thaler1999-1" href="#ref-zh-thaler1999">Thaler (1999)</a>）。第三，损失是不对称的——省下 50 美元只是省钱，而取消一顿饭却像是在承认“我在这里撑不下去了”：损失比同等收益的分量更重（<a id="cite-zh-kahneman1979-1" href="#ref-zh-kahneman1979">Kahneman &amp; Tversky, 1979</a>），放弃一件有价值的东西带来的痛苦，大于得到它带来的愉悦（<a id="cite-zh-tversky1991-1" href="#ref-zh-tversky1991">Tversky &amp; Kahneman, 1991</a>）。

区分两种身份消费会有帮助。*维持*身份是防御性的：保住已经拥有的生活。*提升*身份是进攻性的：成为一名经理、用英语通过面试、学会 eCW 这样的系统、谈成更高的薪水——一种更有尊严的身份，花的不是钱，而是时间和努力。前者每次都快而便宜；后者每一步都慢而昂贵，但只有它能改变约束本身。最接近的正式模型是补偿性消费行为模型，其五种策略包括*直接解决*——直接修复差距本身，例如获得技能——以及*象征性自我完成*和*流动补偿*——用某个产品或体验来标示或替代缺失的自我（<a id="cite-zh-mandel2017-1" href="#ref-zh-mandel2017">Mandel et al., 2017</a>）。“防御 / 进攻”这对标签是这篇笔记借用该模型做的表述，不是原作者的用语。贫困家庭在基本生存之外的花钱本身已有充分记录：在 13 个国家的家庭调查中，极端贫困家庭通常会把中位数 10% 的预算花在节日、婚礼和葬礼上，而不是多买食物（<a id="cite-zh-banerjee2007-1" href="#ref-zh-banerjee2007">Banerjee &amp; Duflo, 2007</a>）。

什么可以证伪这个假说？如果收入恢复后，同样的消费立刻、毫无阻力地消失，那它很可能只是应对或习惯，而不是身份。如果给一个家庭提供同样有尊严、但更便宜的替代品——一顿让人感觉慷慨而不是施舍的社区餐、一次成本更低的同样出游——它愉快地接受了，那起作用的就是价格，而不是身份。如果它在体验相当的情况下仍然拒绝更便宜的替代品，身份就确实在起作用。这些是后续研究应该做的检验，而不是从一次观察就假定答案。

**文献能证明什么、不能证明什么。**目前没有已发表的研究在单一设计中检验整个四层假说，也没有针对外出吃饭的研究；上面的支撑是按组成部分给出的，把它用到一顿饭上是一种解读，而不是直接发现。Belk 的扩展自我说的是物品，不是饭。 “省 50 美元 vs 取消一顿饭”的对比是对损失厌恶的应用，不是 Kahneman 和 Tversky 的实验。“防御 / 进攻”的区分是这篇笔记对 Mandel 等人模型的表述，不是他们的术语。文献确实确立的是机制的各个部分：身份进入经济决策，受到威胁的自我会购买地位，无力感通过选择得到修复，稀缺收窄带宽，可见消费传递地位，信用卡把付款与愉悦解耦。

<div class="cc-chart" markdown="1">
<h4>试一下：一顿 50 美元的饭</h4>
<p class="cc-note" style="margin-top:0">这是对机制的示意，不是数据。一个经济紧张的家庭正在决定，要不要花 50 美元出去吃一顿饭。</p>
<button type="button" class="cc-btn" data-cc-choice="keep">保留这顿饭</button>
<button type="button" class="cc-btn" data-cc-choice="cut">砍掉这顿饭</button>
<div class="cc-outcome" data-lang="zh">选一个——关键在于，两个选项都有代价，而且只有一个代价会出现在账单上。</div>
</div>

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

- <span id="ref-zh-ccguide"></span> Merit Point Academy，《Constrained Choices》——<https://courses.hopeembark.org/guides/constrained-choices/> <a href="#cite-zh-ccguide-1" title="回到正文">&#8617;1</a> <a href="#cite-zh-ccguide-2" title="回到正文">&#8617;2</a>
- <span id="ref-zh-sparkydata"></span> SparkyData，"Who Moves to and Leaves New York City"（ACS 2015–2024 PUMS）——<https://sparkydata.dev/articles/who-is-leaving-and-who-is-arriving>
- <span id="ref-zh-nycplanning2026"></span> 纽约市城市规划局，《New York City's Population Estimates and Trends》，2026 年 3 月发布（Vintage 2025）——<https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/population/population-estimates/new-york-city-population-estimates-and-trends-march-2026.pdf>
- <span id="ref-zh-nycplanning2025"></span> 纽约市城市规划局，《New York City's Population Estimates and Trends》，2025 年 5 月发布（Vintage 2024）——<https://www.nyc.gov/assets/planning/downloads/pdf/our-work/reports/new-york-city-population-estimates-and-trends_may-2025.pdf>
- <span id="ref-zh-comptroller2025"></span> 纽约市主计长，"NYC's Post-Pandemic Rebound"，2025 年 12 月 Spotlight——<https://comptroller.nyc.gov/wp-content/uploads/2025/12/Dec-2025-Spotlight-NYC-Overview.pdf>
- <span id="ref-zh-cbc2025"></span> Citizens Budget Commission，《Straight From New Yorkers 2025》，2025 年 6 月——<https://cbcny.org/sites/default/files/media/files/CBCREPORT_Resident-Survey-2025_06042025.pdf> <a href="#cite-zh-cbc2025-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-empire2026"></span> Empire Center，"Leaving New York" 民调，2026 年（纽约州，不是单指纽约市） <a href="#cite-zh-empire2026-1" title="回到正文">&#8617;1</a>

### 第 5 节参考文献——身份、地位与压力下的消费

- <span id="ref-zh-akerlof2000"></span> Akerlof, G. A., & Kranton, R. E. (2000). Economics and identity. *Quarterly Journal of Economics*, *115*(3), 715–753. <https://doi.org/10.1162/003355300554881> <a href="#cite-zh-akerlof2000-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-akerlof2010"></span> Akerlof, G. A., & Kranton, R. E. (2010). *Identity Economics: How Our Identities Shape Our Work, Wages, and Well-Being*. Princeton University Press. ISBN 978-0-691-14648-5. <https://ideas.repec.org/a/eee/joepsy/v31y2010i6p1061-1063.html>
- <span id="ref-zh-atalay2011"></span> Atalay, A. S., & Meloy, M. G. (2011). Retail therapy: A strategic effort to improve mood. *Psychology & Marketing*, *28*(6), 638–659. <https://doi.org/10.1002/mar.20404> <a href="#cite-zh-atalay2011-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-banerjee2007"></span> Banerjee, A. V., & Duflo, E. (2007). The economic lives of the poor. *Journal of Economic Perspectives*, *21*(1), 141–168. <https://doi.org/10.1257/jep.21.1.141> <a href="#cite-zh-banerjee2007-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-banerjee2011"></span> Banerjee, A. V., & Duflo, E. (2011). *Poor Economics*. PublicAffairs. ISBN 978-1-58648-798-0.
- <span id="ref-zh-belk1988"></span> Belk, R. W. (1988). Possessions and the extended self. *Journal of Consumer Research*, *15*(2), 139–168. <https://doi.org/10.1086/209154> <a href="#cite-zh-belk1988-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-case2008"></span> Case, A., Garrib, A., Menendez, A., & Olgiati, A. (2008). Paying the piper: The high cost of funerals in South Africa. NBER Working Paper No. 14456. <https://papers.ssrn.com/abstract=1294131>（工作论文，未经同行评审）
- <span id="ref-zh-charles2009"></span> Charles, K. K., Hurst, E., & Roussanov, N. (2009). Conspicuous consumption and race. *Quarterly Journal of Economics*, *124*(2), 425–467. <https://doi.org/10.1162/qjec.2009.124.2.425> <a href="#cite-zh-charles2009-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-dupas2024"></span> Dupas, P., Fafchamps, M., & Hernandez-Nunez, L. (2024; rev. Dec 2025). Keeping up appearances: An experimental investigation of socioeconomic status signaling to avoid discrimination. NBER Working Paper No. 32491. <https://doi.org/10.3386/w32491>（工作论文，未经同行评审） <a href="#cite-zh-dupas2024-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-hamilton2012"></span> Hamilton, K. (2012). Low-income families and coping through brands: Inclusion or stigma? *Sociology*, *46*(1), 74–90. <https://doi.org/10.1177/0038038511416146> <a href="#cite-zh-hamilton2012-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-heffetz2011"></span> Heffetz, O. (2011). A test of conspicuous consumption: Visibility and income elasticities. *Review of Economics and Statistics*, *93*(4), 1101–1117. <https://doi.org/10.1162/REST_a_00116> <a href="#cite-zh-heffetz2011-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-kahneman1979"></span> Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, *47*(2), 263–291. <https://doi.org/10.2307/1914185> <a href="#cite-zh-kahneman1979-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-landis2017"></span> Landis, B., & Gladstone, J. J. (2017). Personality, income, and compensatory consumption: Low-income extraverts spend more on status. *Psychological Science*, *28*(10), 1518–1520. <https://doi.org/10.1177/0956797617714811>
- <span id="ref-zh-mandel2017"></span> Mandel, N., Rucker, D. D., Levav, J., & Galinsky, A. D. (2017). The compensatory consumer behavior model: How self-discrepancies drive consumer behavior. *Journal of Consumer Psychology*, *27*(1), 133–146. <https://doi.org/10.1016/j.jcps.2016.05.003> <a href="#cite-zh-mandel2017-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-mani2013"></span> Mani, A., Mullainathan, S., Shafir, E., & Zhao, J. (2013). Poverty impedes cognitive function. *Science*, *341*(6149), 976–980. <https://doi.org/10.1126/science.1238041> <a href="#cite-zh-mani2013-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-moav2012"></span> Moav, O., & Neeman, Z. (2012). Saving rates and poverty: The role of conspicuous consumption and human capital. *Economic Journal*, *122*(563), 933–956. <https://doi.org/10.1111/j.1468-0297.2012.02516.x>
- <span id="ref-zh-mullainathan2013"></span> Mullainathan, S., & Shafir, E. (2013). *Scarcity: Why Having Too Little Means So Much*. Times Books. ISBN 978-0-8050-9264-6. <https://www.hks.harvard.edu/centers/cid/publications/books/scarcity-why-having-too-little-means-so-much> <a href="#cite-zh-mullainathan2013-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-oyserman2009"></span> Oyserman, D. (2009). Identity-based motivation: Implications for action-readiness, procedural-readiness, and consumer behavior. *Journal of Consumer Psychology*, *19*(3), 250–260. <https://doi.org/10.1016/j.jcps.2009.05.008> <a href="#cite-zh-oyserman2009-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-pettit2011"></span> Pettit, N. C., & Sivanathan, N. (2011). The plastic trap: Self-threat drives credit usage and status consumption. *Social Psychological and Personality Science*, *2*(2), 146–153. <https://doi.org/10.1177/1948550610385138> <a href="#cite-zh-pettit2011-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-prelec1998"></span> Prelec, D., & Loewenstein, G. (1998). The red and the black: Mental accounting of savings and debt. *Marketing Science*, *17*(1), 4–28. <https://doi.org/10.1287/mksc.17.1.4> <a href="#cite-zh-prelec1998-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-prelec2001"></span> Prelec, D., & Simester, D. (2001). Always leave home without it: A further investigation of the credit-card effect on willingness to pay. *Marketing Letters*, *12*(1), 5–12. <https://doi.org/10.1023/A:1008196717017> <a href="#cite-zh-prelec2001-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-rick2014"></span> Rick, S. I., Pereira, B., & Burson, K. A. (2014). The benefits of retail therapy: Making purchase decisions reduces residual sadness. *Journal of Consumer Psychology*, *24*(3), 373–380. <https://doi.org/10.1016/j.jcps.2013.12.004> <a href="#cite-zh-rick2014-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-rucker2008"></span> Rucker, D. D., & Galinsky, A. D. (2008). Desire to acquire: Powerlessness and compensatory consumption. *Journal of Consumer Research*, *35*(2), 257–267. <https://doi.org/10.1086/588569> <a href="#cite-zh-rucker2008-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-rucker2009"></span> Rucker, D. D., & Galinsky, A. D. (2009). Conspicuous consumption versus utilitarian ideals: How different levels of power shape consumer behavior. *Journal of Experimental Social Psychology*, *45*(3), 549–555. <https://doi.org/10.1016/j.jesp.2009.01.005>
- <span id="ref-zh-sivanathan2010"></span> Sivanathan, N., & Pettit, N. C. (2010). Protecting the self through consumption: Status goods as affirmational commodities. *Journal of Experimental Social Psychology*, *46*(3), 564–570. <https://doi.org/10.1016/j.jesp.2010.01.006> <a href="#cite-zh-sivanathan2010-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-thaler1999"></span> Thaler, R. H. (1999). Mental accounting matters. *Journal of Behavioral Decision Making*, *12*(3), 183–206. <https://doi.org/10.1002/(SICI)1099-0771(199909)12:3%3C183::AID-BDM318%3E3.0.CO;2-F> <a href="#cite-zh-thaler1999-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-tversky1991"></span> Tversky, A., & Kahneman, D. (1991). Loss aversion in riskless choice: A reference-dependent model. *Quarterly Journal of Economics*, *106*(4), 1039–1061. <https://doi.org/10.2307/2937956> <a href="#cite-zh-tversky1991-1" title="回到正文">&#8617;1</a>
- <span id="ref-zh-veblen1899"></span> Veblen, T. (1899). *The Theory of the Leisure Class*. Macmillan. 全文：<https://www.gutenberg.org/ebooks/833> <a href="#cite-zh-veblen1899-1" title="回到正文">&#8617;1</a>


*2026 年 11 月 25 日发布。数字均引自上述来源；PEP 估计值随每次 vintage 修订，复用总数前请核对最新发布。*

</div>
