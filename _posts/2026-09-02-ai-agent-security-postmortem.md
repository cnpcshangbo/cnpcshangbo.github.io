---
title: 'AI Agent Security After 29 Attempts: Replay Noise, Leaderboard Overfitting, and the Private-Guardrail Reset'
date: 2026-09-02
permalink: /posts/2026/09/ai-agent-security-postmortem/
excerpt: "A source-first retrospective on 28 scored submissions, one system error, a public score that never improved after day one, and a hidden guardrail that reset most of the field."
tags:
  - AI agent security
  - adversarial evaluation
  - Kaggle
  - reproducible experiments
toc: true
toc_sticky: true
---

The most useful result from this competition was not my best leaderboard number. It was learning how quickly a security benchmark can become three different problems:

1. the security problem described in the task;
2. the behavior actually rewarded by the public evaluator; and
3. the behavior that survives a hidden guardrail.

I entered Kaggle's **AI Agent Security — Multi-Step Tool Attacks** competition expecting to search for diverse, compositional attacks against tool-using language models. My team produced 29 competition entries: 28 completed scores and one Kaggle system error. The best public result, `86.850`, came from the fifth version on August 22. Every later scored submission failed to improve it. When the private leaderboard was revealed, all of my completed entries scored zero.

That is not a winning solution story. It is a more useful story about objective reading, replay systems, noisy experiments, operational discipline, and public-leaderboard overfitting.

## The benchmark I thought I was solving

The official benchmark asked each submission to provide an `attack.py` program that generated attack candidates against two tool-using model families. Findings were then replayed and evaluated through a guardrail and a predicate-based scorer. The task described four attack categories, including data exfiltration, unauthorized transfer, destructive behavior, and confused-deputy behavior.

The public score rewarded severity and cell diversity. In simplified form, a newly credited high-severity event was worth far more than small prompt-quality differences:

\[
\text{raw score} = \sum \text{severity weight} + 2 \times \text{unique cells}
\]

The competition also used different public and private guardrails. That detail eventually mattered more than almost everything I tuned.

Official references:

- [Competition overview and evaluation](https://www.kaggle.com/competitions/ai-agent-security-multi-step-tool-attacks/overview/abstract)
- [Final leaderboard](https://www.kaggle.com/competitions/ai-agent-security-multi-step-tool-attacks/leaderboard)

## The result in one table

My last captured public snapshot placed the team at **1,283 of 4,219** with a score of **86.850**. After the competition closed, the final leaderboard API contained 4,252 teams. Only 1,397 teams had a positive private score; 2,855 teams, or **67.14%**, had a private score of zero.

| Measurement | Result |
|---|---:|
| Competition entries | 29 |
| Completed scored entries | 28 |
| Kaggle system errors | 1 |
| Best public score | 86.850 |
| Best version | v5, submitted Aug. 22 |
| Completed entries beating v5 | 0 |
| My private score | 0.000 |
| Teams with private score 0 | 2,855 / 4,252 |

The zero was therefore common, but it was still decisive. My public strategy had learned a scoring surface that did not survive the hidden policy.

## Phase 1: build the measurement system before searching

The first durable contribution was not an attack. It was a validation pipeline.

For a candidate to become submission-ready, I required:

- fresh adjacent control and candidate runs;
- GPT-OSS and Gemma replays at both 60- and 120-second budgets;
- unit and invariant tests;
- a private, internet-disabled Kaggle notebook run;
- the same `attack.py` hash locally, inside the notebook, and in cloud output; and
- an explicit confirmation immediately before consuming a submission.

I also kept the submission scheduler separate from the experiment pipeline. Waiting for quota or a score was not a reason to stop preparing the next candidate.

This process felt conservative during a fast competition. It later prevented several attractive but false local improvements from reaching the leaderboard.

## Phase 2: an early public optimum

Version 5 used a live-fill strategy: generate replayable candidates, keep candidates that appeared to fire, adapt to observed latency, and use distinct destinations to preserve scoring-cell diversity. It scored **86.850**.

At that point I treated v5 as a baseline, not a final architecture. The next versions tested ideas that sounded stronger:

- denser multi-step chains;
- model-aware routing;
- replay-throughput calibration;
- candidate-cap-aware packing;
- static calibrated pools; and
- smaller changes to ordering, punctuation, response restrictions, tool names, and success parsing.

The public leaderboard was blunt:

| Version / experiment | Single changed idea | Public score | Delta from v5 |
|---|---|---:|---:|
| v5 | Live-fill baseline | **86.850** | — |
| v6 | Adaptive chain packing | 76.005 | -10.845 |
| v7 | Replay-throughput calibration | 70.220 | -16.630 |
| v8 | Model-aware throughput | 68.080 | -18.770 |
| v9 | Trace-routed singletons | 85.365 | -1.485 |
| E14 | Calibrated static pool | 41.130 | -45.720 |
| E43 | `.io` destination family | 84.600 | -2.250 |
| E46 | Remove terminal period | 85.680 | -1.170 |
| E52 | Stable half-rotation | 60.210 | -26.640 |
| E58 | Adjacent order swap | 82.170 | -4.680 |
| E64 | Comma argument separator | 84.825 | -2.025 |
| E66 | Success-string normalization | 85.725 | -1.125 |
| E76 | Answer-token change | 83.880 | -2.970 |
| E74 | Remove one response restriction | 82.620 | -4.230 |

The striking result is that almost every plausible improvement made the hosted score worse. Even changes that helped fresh local pairs did not transfer reliably.

## Phase 3: discovering that the experiment order was an attack surface too

Late in the competition, E101 appeared to beat its control locally:

- candidate first: `40 findings / 720 raw`;
- control second: `39 findings / 702 raw`.

An 18-point raw gain looked clean enough to investigate. But the same `40/720` versus `39/702` pattern appeared when I ran control against itself. Reversing the candidate/control order moved the advantage to whichever run executed first.

The candidate had not improved the algorithm. It had measured warm state, timing, or resource order.

From then on, a convincing comparison required both orders:

\[
A \rightarrow B \quad \text{and} \quad B \rightarrow A
\]

When bytes or generated notebooks might have drifted, I also restored the control byte-for-byte before replaying it. This was slower than ordinary A/B testing, but it changed the question from “did the candidate get a larger number?” to “does the candidate retain the advantage when order is neutralized?”

That distinction is essential for agent benchmarks with stateful model loading, variable tool latency, replay time walls, and shared hardware.

## Phase 4: testing changes that were locally correct but causally inactive

Not all rejected candidates were noisy. Some were simply irrelevant in the evaluated environment.

E102 sorted SDK-root discovery before choosing an installed SDK. The code was cleaner and more deterministic, but a private, no-network diagnostic found exactly one matching SDK root. Sorted and unsorted discovery were therefore identical in the actual environment.

E103 preserved an explicit `time_budget_s=0` rather than replacing it with a default. E104 narrowed a broad compatibility fallback from `except Exception` to `except ImportError`. Both passed their local invariant tests and compilation checks.

Neither was promoted merely because it was good engineering. A valid code change is not automatically a scoring change, and a scoring change is not automatically a private-guardrail improvement.

The clock expired before E103 and E104 completed every replay and cloud gate. I did not submit them. Preserving that distinction—implemented, tested, replay-qualified, cloud-qualified, submitted, scored—was one of the most valuable operational lessons from the project.

## What public write-ups clarified

After the competition, several source-oriented analyses argued that the *publicly reachable scored surface* was much narrower than the narrative suggested.

Xander's [“The Scored Attack Surface Collapses to a Single Predicate”](https://www.kaggle.com/writeups/canqiang/the-scored-attack-surface-collapses-to-a-single-pr) separates guardrail reachability from predicate scoring and shows why public optimization could collapse into repeated exfiltration throughput. The note also reports substantial score variation across repeated same-configuration runs, supporting the idea that small public-score differences were not automatically causal.

The write-up [“Reading the Objective from Source”](https://www.kaggle.com/writeups/radiantallomancer/reading-the-objective-from-source-a-throughput-bo) reaches a related conclusion by tracing the scorer and guardrail implementation. Pilkwang Kim's [replay-ceiling analysis](https://pilkwangkim.github.io/posts/AI-Agent-Security-Part-2-The-Linear-Score-Law-and-the-Replay-Ceiling/) is particularly useful because it preserves corrections to earlier hypotheses rather than presenting a frictionless success narrative.

These are participant analyses, not official statements about the hidden evaluator. But they explain the shape of my public results: once v5 found a robust public exfiltration-throughput configuration, many “smarter” multi-step or formatting changes only added latency and variance.

## The private leaderboard changed the interpretation

If the story ended at the public leaderboard, I would conclude that v5 found a stable local optimum and later experiments mostly explored dominated details.

The private leaderboard makes that conclusion incomplete.

Every completed submission scored zero privately. The hidden guardrail did not merely reorder my candidates; it erased the entire family. Across the full field, roughly two-thirds of teams also received zero. Several high public positions collapsed, while some lower public positions moved sharply upward.

The correct interpretation is not “the private leaderboard was random.” It is that public score was a weak proxy for hidden-policy robustness. Once that became true, selecting only the strongest public exploit was equivalent to selecting on a distribution with a missing feature: whether the attack class survived a different policy.

In a future benchmark, I would reserve candidate diversity across **guardrail assumptions**, not just prompt variants. For example:

- destination-only inspection versus payload inspection;
- single-call filtering versus cross-step intent tracking;
- syntactic blocklists versus semantic capability policy;
- direct tool misuse versus confused-deputy behavior; and
- one model family versus cross-model transfer.

The final portfolio should contain candidates that fail for different reasons. Twenty variants of the same public exploit are not twenty independent chances.

## What I would do differently

### 1. Read reachability before optimizing prompts

I would build a matrix with one row per predicate and columns for guardrail visibility, predicate visibility, required event state, replay behavior, and expected score. Any branch that is unreachable or economically dominated would be closed before large prompt searches.

### 2. Treat evaluator variance as a first-class measurement

I would pre-register minimum effect sizes and require counterbalanced repeats. A one-point public movement would not justify a causal claim unless it exceeded same-configuration variance.

### 3. Separate four kinds of success

A candidate can be:

1. logically correct;
2. locally faster;
3. publicly higher-scoring; or
4. robust to an unseen guardrail.

These are different claims requiring different evidence.

### 4. Optimize a portfolio, not a single score

Before the private reveal, I optimized expected public score. A better late-stage objective would combine public score, attack-family diversity, model transfer, and guardrail-assumption diversity.

### 5. Preserve negative results

The most informative experiments were not the highest-scoring ones. E14 showed that a static pool could catastrophically underperform. E52 showed that ordering changes were not harmless. E101 exposed run-order confounding. E102 showed how an apparently rigorous change could be inactive in the real environment.

Without those records, the final story would incorrectly attribute every score difference to prompt quality.

## Lessons for benchmark designers

This competition also provides a useful security-evaluation case study.

First, the guardrail, event trace, predicate scorer, and reward should be analyzed as one joined system. If the guardrail blocks an action the scorer expects, a nominal attack category may be unreachable. If the scorer rewards repeated events independently, an intended multi-step benchmark may become a throughput contest.

Second, public and private policies should differ enough to test transfer but not so much that public model selection becomes nearly uninformative. Per-model and per-predicate diagnostics would help participants distinguish robustness failures from infrastructure variance without revealing the private policy.

Third, replay systems need explicit variance reporting. Deterministic code does not imply deterministic evaluation when model generation, scheduling, tool latency, and time walls interact.

Finally, a benchmark should reward causal diversity, not merely repeated instances of the most profitable public event. Otherwise the leaderboard measures how efficiently participants exploit the evaluator's narrowest seam.

## Closing perspective

The public leaderboard told me that v5 was the best version. The private leaderboard told me that all 28 scored versions belonged to the same brittle family.

Both observations are true.

The lasting result is a better experimental method: read the objective from source, map reachability, preserve byte-identical controls, counterbalance run order, distinguish implementation correctness from scoring impact, and maintain diversity across failure mechanisms.

That method is more reusable than the attack that scored 86.850—and considerably more valuable for evaluating real tool-using agents.

