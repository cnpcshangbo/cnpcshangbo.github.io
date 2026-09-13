---
title: "When Should a Language Model Hand Over the Controls? A Minecraft Agent Case Study"
date: 2026-09-13
permalink: /posts/2026/09/minecraft-local-agent-control/
excerpt: "39 new logs, an interrupted return, and what a local feedback controller changes—and does not prove—about LLM agent efficiency and robot design."
tags:
  - embodied AI
  - robotics
  - language model agents
  - Minecraft
  - evaluation methodology
toc: true
toc_sticky: true
comments: false
page_views: true
page_views_since: 2026-09-13
---

**Research note · Engineering case study · September 13, 2026**

I asked GPT-6 Astra, running in Codex, to collect resources in an already-running Minecraft world. We first used a screenshot-and-action workflow for a cobblestone task. I then asked a different question: could Astra build a local worker, let that worker control the game at a higher frequency, and supervise it occasionally?

The local worker eventually collected **39 additional logs** outside a **128-block protected radius** around home. It also failed to complete an uninterrupted return: a skeleton's arrow reduced health from 20 to 16, and the worker paused the singleplayer game. Both outcomes matter.

The useful conclusion is architectural, not a headline speedup. A reusable local feedback loop can remove remote model calls from repetitive control. This episode demonstrates that such a loop can do meaningful work, including mining with mouse capture released. It does **not** establish how much faster it is at the same task, whether its engineering cost has paid back, or whether it is reliably autonomous.

<div class="notice--info">
<strong>Evidence boundary.</strong> This is one evolving engineering episode with inspections, patches, restarts, and operator supervision—not independent trials of a frozen controller. The earlier direct-control task was cobblestone mining; the local-worker task was wood collection. The worker also received exact game state that the screenshot workflow did not. No controlled task-speedup ratio is reported. Astra identifies the assistant configuration in the session; the game telemetry does not independently record a model identifier.
</div>

## 1. The two control loops

In the first approach, Astra inspected screenshots, chose a short action, sent input through desktop or virtual-input tooling, and inspected the result. The model remained in the task-level feedback loop. A local input adapter could deliver a timed key or mouse action, but that did not by itself make the action adaptive while it was running.

In the second approach, Astra acted as an engineer and supervisor. It inspected the installed game interfaces, wrote a deterministic Java worker, compiled and attached it to the running client, examined status files, and revised the implementation when it failed. The worker performed navigation, aiming, mining, progress checks, and stopping locally.

**“Local agent” here means control software, not a second language model running on the PC.** There was no local neural-policy training and no LLM call inside the worker's per-tick execution loop. Astra and its coding assistants contributed to development and diagnosis; they were not additional Minecraft players.

<figure>
  <a href="/assets/research/minecraft-local-agent/control-architecture.svg"><img src="/assets/research/minecraft-local-agent/control-architecture.svg" alt="Comparison of a screenshot-mediated language-model control loop and an Astra-supervised local worker with structured game-state access." loading="lazy"></a>
  <figcaption>Figure 1. The architectural change also changed the observation and action interfaces. Exact block, collision, and inventory queries make this a whole-system comparison, not an isolated test of feedback frequency. Open the figure for a larger view.</figcaption>
</figure>

### What we actually tried

| Method | Role in this episode | What it established |
|---|---|---|
| Screenshot inspection plus external input | Used during the earlier cobblestone phase | The conversation records collection of 32 cobblestone; there is no preserved matched timing benchmark. |
| Custom timed-input adapter over existing virtual-input infrastructure | A local mechanism for keyboard/mouse actions, authored during the session | Improved the available input path; a timed burst still needed a fresh observation to become feedback control. |
| A separate protocol-connected bot | Investigated as an alternative | Not deployed in this experiment. Compatibility with the installed release was an obstacle; no second account or server-joining result is claimed. |
| Java worker attached to the current client | Built and field-tested for wood collection | Navigated, selected trees, mined, and retained 39 new logs; the return was interrupted. |
| Packaged post-pilot worker | Added launch/stop/status scripts, a watchdog, return-path loop removal, and a wider ranged-threat check | Compiled and checked; the final threat/return changes were not given another full field trial. |

The installed environment was **Minecraft Java 26.3-rc-2**, with its existing Java 25 runtime. The worker controlled the **current character in singleplayer**, rather than joining as a separate bot. It used ordinary survival mining methods and game inputs; it did not award inventory items, teleport the player, or rewrite the world save. Java's instrumentation/attach interface supplied the local loading mechanism. This is a version-specific engineering choice, not a recommendation to treat an internal game API as a stable robotics interface. [Java instrumentation documentation](https://docs.oracle.com/en/java/javase/25/docs/api/java.instrument/java/lang/instrument/package-summary.html).

<figure>
  <a href="/assets/research/minecraft-local-agent/initial-mine.png"><img src="/assets/research/minecraft-local-agent/initial-mine.png" alt="User-supplied Minecraft screenshot showing the player inside a dirt excavation before the earlier cobblestone task." loading="lazy"></a>
  <figcaption>Figure 2. The user-supplied starting scene for the earlier cobblestone phase. This is an actual game screenshot, not an image of the later 39-log result. The screenshot and the wood-worker trace represent different tasks.</figcaption>
</figure>

## 2. How the local worker was organized

The worker combined a finite-state controller with bounded path search and explicit completion conditions:

1. **Establish the mission:** record the inventory baseline, home coordinates, protected radius, starting position, and requested log count.
2. **Navigate:** find traversable cells, walk or jump short segments, and later support slow ice travel and surface swimming. Record a return trail.
3. **Select and approach a tree:** check natural logs, soil, canopy, protected distance, and nearby constructed blocks. The implemented repertoire focused on straight trunks of three to six logs.
4. **Harvest and collect:** aim at visible points on a block, progress ordinary mining, move beneath the upper trunk, clear eligible obstructing leaves when necessary, and pick up drops.
5. **Return or stop:** distinguish reaching the inventory target from returning to the starting area. Stop on menu opening, health loss, selected threats, invalid movement, or supervision expiry.

A daemon scheduler requested work every **50 ms**, queued it on the Minecraft client thread, and avoided duplicate execution within the same player tick. This is a **nominal 20 Hz schedule**, not a hard real-time guarantee. Path search, state inspection, file writes, or other game-thread work can delay a callback. Holding a key across several ticks also does not mean a new independent action was chosen on every tick.

The supervisor read structured status rather than requiring a screenshot for each movement. Commands had identifiers; a lease bounded how long the worker could run without supervision. The packaged launcher supplied a separate local watchdog. Those mechanisms are useful operational controls, but a two-minute simulation lease is not an acceptable substitute for a robot's immediate safety layer.

### Failures that changed the design

| Failure observed during development | Change made | General lesson |
|---|---|---|
| A route search could leave the mine but not make useful outward progress | Search reachable terrain rather than assume distant candidate cells are accessible | Goal selection must account for reachability. |
| Home was on a small island; excluding ice did not solve the intervening open water | Add ice handling and surface swimming | A navigation abstraction is only useful within its supported terrain repertoire. |
| Mining stopped when mouse capture was released | Temporarily mediate ordinary mining calls so progress no longer requires mouse capture | Input semantics are part of the control problem. |
| A ray toward a bottom log could intersect another log or nearby leaves | Check multiple aiming points and better approach positions | Intended targets and actual contact/raycast targets must agree. |
| Diagonal approaches left partially cut trunks | Save unfinished work, approach from a clear side, and trim eligible leaves before finishing | A subtask needs a completion contract and a recovery path. |
| An arrow arrived from beyond the original hostile query, which expanded the player's bounding box by seven blocks | Pause on damage; later add a 24-block visible ranged-attacker check | A local loop can execute a bad hazard model quickly. |

The mining implementation deserves particular care. Calling a convenient internal method was not enough: vanilla input handling could cancel destruction progress while the mouse was uncaptured. The final approach maintained ownership of a validated mining target while preserving ordinary mining progression and restoring the original game-mode instance when stopped. That is a concrete example of why “use the API” is not the end of integration work.

## 3. Results supported by the saved artifacts

The strongest outcome evidence is the inventory difference and the saved stop state. The full development history is not a clean event log: several status files were overwritten, some `elapsedSeconds` fields continued to increase while idle or paused, and counters were reset across reloads. Summing those fields would create a misleading runtime estimate.

| Quantity | Supported observation | Interpretation |
|---|---:|---|
| Initial log inventory | 21 | Baseline saved in mission state |
| Final log inventory | 60 | Inventory at the paused end of the pilot |
| Additional logs retained | **39** | 60 − 21; exceeds the requested resource target of 32 |
| Protected radius | **128 blocks** | Configured exclusion area around home |
| Known partially cut trunks subsequently finished | 4 | Recovery export and subsequent worker observations |
| End-of-pilot health | **16 / 20** | Eight hearts; down from 20 / 20 |
| Diagnosed attacker distance | **14.73 blocks** | Skeleton position in the subsequent paused diagnostic snapshot |
| Full collect-and-return outcome | **Interrupted** | Resource acquisition succeeded; uninterrupted return did not |
| End-to-end time, tokens, billed inference, measured task speedup | **Not established** | The available records do not support these totals or ratios |

The distance to the skeleton is a later diagnostic observation, not a measurement of the exact arrow-release distance. The saved damage-source record identifies an arrow as the source of the health loss. The game was paused, with the acquired wood still in inventory.

<figure>
  <a href="/assets/research/minecraft-local-agent/recorded-route.svg"><img src="/assets/research/minecraft-local-agent/recorded-route.svg" alt="Plan view of the recorded breadcrumb cells with the home reference, 128-block protected circle, recovered tree positions, and later return-stop position." loading="lazy"></a>
  <figcaption>Figure 3. A geometric reconstruction from recorded breadcrumb cells, not a terrain map or a time-stamped trajectory. The saved trail contains collection travel; the later return stop is marked separately. Repeated cells and detours reflect development and recovery, not independent evaluation trials.</figcaption>
</figure>

### What the short timing trace does—and does not—measure

A diagnostic observer saved **60 samples over 14.767 seconds**. The player-tick counter advanced by **296**, or approximately **20.04 game ticks/s**. All 60 samples recorded `mouseCaptured=false` and `paused=false`; they included active mining and a completed trunk.

This supports two narrow findings: the sampled game clock advanced at roughly its expected rate, and mining could progress without mouse capture. It does **not** show that every worker callback met a 50 ms deadline, measure observation-to-actuation latency, or prove a stable 20 Hz control rate over the full run. The observer itself sampled approximately every 250 ms, so treating its timestamps as action timestamps would be a measurement error.

<figure>
  <video controls preload="metadata" width="1080" height="720" style="width:100%;height:auto" poster="/assets/research/minecraft-local-agent/breadcrumb-reconstruction-poster.png" aria-label="Schematic reconstruction of saved route order, not gameplay or measured travel timing">
    <source src="/assets/research/minecraft-local-agent/breadcrumb-reconstruction.mp4" type="video/mp4">
    <a href="/assets/research/minecraft-local-agent/breadcrumb-reconstruction.mp4">Download the schematic route reconstruction</a>.
  </video>
  <figcaption>Video 1. A 16-second schematic reveal of the saved breadcrumb order, not gameplay footage. Animation timing is uniform and illustrative; the breadcrumbs have no timestamps. The unrecorded return leg is not animated, and its final stop is shown separately. This is not a demonstration of travel speed.</figcaption>
</figure>

## 4. How large could the efficiency benefit be?

There are at least four different efficiencies: feedback opportunity, remote inference consumption, task completion time, and total engineering cost. They should not share one “speedup” number.

### Feedback opportunity: a transparent sensitivity calculation

Suppose an external model-mediated cycle takes $$L$$ seconds from one observation/action decision to the next. Its nominal cycle frequency is $$1/L$$. Comparing that with the worker's configured 20 Hz gives:

$$
R_{\mathrm{cadence}} = \frac{20}{1/L}=20L.
$$

| Assumed external cycle time | External cycles/s | Configured local cycles/s | Nominal cadence ratio |
|---:|---:|---:|---:|
| 1 s | 1.00 | 20 | 20× |
| 5 s | 0.20 | 20 | 100× |
| 10 s | 0.10 | 20 | 200× |
| 20 s | 0.05 | 20 | 400× |

**These are scenarios, not measured Astra latencies and not task-speedup results.** They express potential opportunities to react between remote decisions. A model can batch actions, issue longer skills, or operate asynchronously; a local callback may simply maintain an existing command. Walking speed, block-breaking time, path quality, perception errors, retries, and survival can dominate the time to finish a task.

<figure>
  <a href="/assets/research/minecraft-local-agent/cadence-scenarios.svg"><img src="/assets/research/minecraft-local-agent/cadence-scenarios.svg" alt="Sensitivity plot showing nominal feedback cadence ratios for assumed external cycle times, explicitly labeled as scenarios rather than measured task speedups." loading="lazy"></a>
  <figcaption>Figure 4. Illustrative cadence comparison against a configured 50 ms local schedule. Neither the assumed external latencies nor the resulting ratios were measured as task performance in this experiment.</figcaption>
</figure>

### Remote calls: reuse changes where inference is spent

The practical advantage is that Astra need not reconsider every repeated motion. It can spend model calls on setting objectives, diagnosing an exception, or revising a skill, while deterministic software handles routine feedback. A useful future accounting, with all terms converted to a common cost unit, is:

$$
C_{\mathrm{hybrid}} = C_{\mathrm{development}} + C_{\mathrm{supervision}} + C_{\mathrm{local\ execution}}.
$$

The direct workflow has its own setup and per-task inference costs. This session did not preserve a complete accounting of model calls, tokens, cost, or power for either condition. Claiming a percentage reduction would therefore be unsupported. There were no LLM calls in the local worker's execution code, but there were substantial model-assisted engineering and diagnosis efforts outside it.

### Task time and amortization: setup can reverse the conclusion

A prototype that takes longer to build than a single manual or direct-control task can still be valuable when reused. Conversely, a fast executor that repeatedly fails can be inefficient overall.

If additional setup costs $$B$$ minutes, and a **future measured** expected saving is $$\Delta T>0$$ minutes per comparable assigned mission, parity occurs at $$n=B/\Delta T$$ repetitions. This assumes comparable reliability and counts failures, timeouts, and rescue effort in the expected per-mission saving. For illustration only, 60 minutes of setup and five minutes saved per mission gives parity after 12 missions. Neither number is an estimate from this episode. Maintenance and hardware use would also belong in a full cost model.

<figure>
  <a href="/assets/research/minecraft-local-agent/illustrative-amortization.svg"><img src="/assets/research/minecraft-local-agent/illustrative-amortization.svg" alt="Illustrative number of repetitions needed to amortize assumed setup costs at different assumed per-mission time savings." loading="lazy"></a>
  <figcaption>Figure 5. An accounting scenario, not an estimate of this prototype's payback. The setup costs and per-mission savings are assumptions; measured reliability and failure costs could change or eliminate the benefit.</figcaption>
</figure>

**Is a local agent needed?** For this kind of sustained navigation and manipulation, a reusable local executor is a strong engineering candidate. For a one-off, slow, easily observed task, building one may cost more than it saves. The deeper requirement is a suitable fast feedback layer; it could be a conventional controller, a learned visual policy, an existing skill API, or generated code. It does not have to be a second LLM or a separately spawned player.

## 5. Why this is not a causal comparison yet

The local worker had privileged, structured access to loaded-world block identities, positions, collision shapes, inventory, and entities. It could also set orientation and invoke in-process controls precisely. The screenshot workflow had to infer much of the state visually and use an external input path. That changes perception difficulty, actuation precision, and feedback scheduling simultaneously.

Voyager makes the same comparison boundary explicit: its authors do not directly compare their high-level Mineflayer-based system with pixel-to-low-level-action agents as though the interfaces were equivalent. Its executable skill library is a close precedent for reuse, but its results are not a speedup estimate for this worker. [Voyager, especially §3.2](https://arxiv.org/html/2305.16291v2).

The evolving code is another confound. Fixing a failure and continuing from the same world is useful engineering, but the next segment benefits from knowledge acquired in the previous one. It is not a new independent test. The post-pilot wider threat check and loop-erased return path were compiled and checked; they were **not** demonstrated to solve the nighttime return in a new field run. In particular, navigation unit tests do not establish combat avoidance.

### A benchmark that could answer the question

Freeze the game build, controller versions, task rules, and success criteria before testing. Use held-out saved worlds, restore the same starting state for paired conditions, randomize condition order, and include failures and timeouts. Dynamic encounters can still diverge after actions diverge; record that rather than assume a seed makes the entire episode identical.

| Comparison | What must be matched | Question it can answer |
|---|---|---|
| Model-mediated vs local feedback using structured state | Same state fields, action adapter, rate cap, and emergency interventions | Does scheduling and local reuse help when the interface advantage is removed? |
| Model-mediated vs local feedback using images | Same camera channels, resolution, sampling rules, actuator, and observation limits | Does the advantage persist when both must solve visual state estimation? Subsequent frames can differ as trajectories diverge. This local visual condition has not been implemented here. |
| Best available practical system on each side | Explicitly disclose all interface differences | Which complete system is most useful, without attributing the result to hierarchy alone? |
| Local feedback vs timed open-loop action batches | Same primitives and action-duration budget | Is the benefit feedback, or merely fewer tool round trips? |

A concrete success contract could require at least 32 new logs from outside the protected area, all retained on return within two blocks of the start, alive and within a fixed time budget, with no protected blocks removed. Report resource acquisition separately from complete-and-return success.

Measure wall-clock and active simulation time, observation age, observation-to-command latency, p50/p95/p99 feedback intervals, missed deadlines, supervisor calls and tokens, CPU/GPU use, damage, deaths, stops, and human interventions. Include development time and post-freeze patches. Predeclare a primary efficiency endpoint and an acceptable complete-and-return success-rate degradation (a non-inferiority margin); an efficiency win should not silently trade away task reliability. Report paired differences and uncertainty intervals after selecting a sample size through a pilot or precision analysis. A single successful harvest cannot estimate reliability.

## 6. What real robot design can learn

The experiment does not demonstrate sim-to-real transfer. It exposes interface and control-design questions that are also important in robotics.

**Keep semantic planning and time-sensitive execution separately accountable.** SayCan combines language-based task relevance with skill affordances; Code as Policies generates programs over perception and control APIs. Both are useful precedents for connecting a high-level instruction to executable capabilities. The Minecraft worker is an iteratively engineered instance of that separation, not a new control principle. [SayCan](https://arxiv.org/abs/2204.01691), [Code as Policies](https://arxiv.org/abs/2209.07753).

**Do not confuse a simulator's state API with perception.** A robot needs time-stamped estimates with uncertainty, calibration, occlusion handling, and checks that an intended object or free-space region actually exists. Minecraft's exact block identities remove much of that burden. MineDojo's explicit observation specification and privileged-state distinctions show why the information interface belongs in a benchmark definition. [MineDojo](https://arxiv.org/html/2206.08853v2).

**Give skills explicit contracts.** “Harvest this tree” should include approach, contact/target confirmation, complete removal of the intended trunk, retained inventory, and a defined failure state. A robot's pick-and-place skill similarly needs evidence of grasp, transport, release, and placement—not just a sequence of plausible commands. The partially cut trunks were failures of subtask completion and recovery, not failures to understand the word “wood.”

**Make safety local, but recognize that locality is insufficient.** The worker stopped further play after detecting damage, yet its original neighborhood check omitted the ranged attacker. The saved record does not measure detection-to-pause latency. A faster loop cannot compensate for an incomplete hazard model. On hardware, an independent safety mechanism must bound motion and interaction even when generated task code is wrong or the supervisor is unreachable.

For a simplified robot stopping calculation, a design might start with:

$$
d_{\mathrm{reserve}} \geq vL + \frac{v^2}{2a} + m,
$$

where $$v$$ is speed toward a stationary obstacle, $$L$$ bounds total sensing/decision/actuation delay, $$a>0$$ is a conservatively guaranteed deceleration, and $$m$$ covers uncertainty. This is an illustrative one-dimensional constant-deceleration model, not a validated safety bound for a particular robot. A latency percentile or nominal peak braking value is not a deterministic bound. The model makes the relevant issue visible: timing, physical dynamics, and uncertainty determine a response envelope, not the mere presence of an “agent.”

**A paused game is not a stopped physical world.** Our recovery relied on pausing an integrated singleplayer simulation. A robot cannot freeze approaching people, falling objects, contact forces, or its own inertia. Emergency behavior, command expiry, collision/force limits, and communications-loss handling need an appropriate independent implementation. The required rates depend on the plant and task; 20 Hz in Minecraft is not a recommended robot servo rate.

**Keep alternative architectures in the comparison.** VPT supplies a Minecraft example of fast learned visual sensorimotor behavior. RT-2 shows that a large vision-language-action model can emit robot actions directly; these are discretized end-effector and gripper commands, not the elimination of underlying servo control. Its reported rates and computation limits are specific to its models and hardware. The lesson is not “LLMs can never control directly.” It is to match the model, controller, observations, and timing budget to the task. [VPT](https://arxiv.org/abs/2206.11795), [RT-2](https://arxiv.org/html/2307.15818v1).

## 7. Conclusion and reproducibility

This episode supports a limited but useful claim: **Astra can design and supervise a local deterministic worker that performs nontrivial Minecraft collection without requiring a fresh model decision for every movement.** The local worker retained 39 new logs and mined with mouse capture released. Its interrupted return also shows that a higher configured feedback cadence does not by itself establish robust autonomy.

The strongest next step is a matched-interface, frozen-controller evaluation with total-cost accounting. Until then, the cadence calculations are design scenarios, the inventory change is an observed result, and the robotics discussion is a set of testable engineering hypotheses.

### Evidence and artifacts

- [Sanitized measurements and provenance](/assets/research/minecraft-local-agent/metrics.json)
- [Source snapshot, navigation tests, and artifact guide](/assets/research/minecraft-local-agent/source/README.md)
- [Download the source bundle](/assets/research/minecraft-local-agent/worker-source.zip)
- [Figure-generation script](/assets/research/minecraft-local-agent/figures.py)
- [Sanitized figure inputs](/assets/research/minecraft-local-agent/figure-inputs.json) and [Python dependencies](/assets/research/minecraft-local-agent/requirements.txt)
- [Figure captions and reconstruction limitations](/assets/research/minecraft-local-agent/figure-provenance.md)

The source bundle is the **post-pilot** version, including the later ranged-threat and return-path changes. It is tied to Minecraft Java 26.3-rc-2; reproducing a performance comparison requires a controlled evaluation beyond compiling it. Game binaries, launcher arguments, credentials, and machine-specific classpaths are not included. The metrics file distinguishes saved artifacts, calculations, and statements available only in the conversation record. No full gameplay video or complete end-to-end performance trace was recorded.

*Experiment conducted by Bo Shang with GPT-6 Astra in Codex. The note and supporting analysis were prepared with AI assistance from the conversation and saved local artifacts. This is an engineering research note, not a peer-reviewed benchmark result.*
