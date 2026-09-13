# Retrospective traceability supplement

This supplement connects eight main claims in the Minecraft research note to recorded fields, calculations and source files. It was assembled after the pilot from retained evidence. It is **not a continuous execution trace, a full ARA compilation, an ARA seal, an independent replication or a guarantee that every action was recorded**.

`claims.json` assigns IDs C01–C08. Evidence paths are relative to the parent artifact directory, `assets/research/minecraft-local-agent/`. JSON pointers use RFC 6901; source files instead have one-based `lineStart` anchors. Each entry distinguishes observation, calculation, source inspection, retrospective audit and illustrative scenario. `sourceHashRefs` resolve to logical source keys in `raw-source-audit.json`; an empty list means no original raw hash is asserted for that reference. Published files are additionally covered by package/source checksum manifests.

## What is preserved

- `evidence/wood-outcome.json`: mission baseline and settings; selected prior, stopped and later status fields; intermediate recovery trees; explicit inventory/health/timing arithmetic.
- `evidence/diagnostic.json`: 60 field-only diagnostic observations with original UTC timestamps, tick counters and source line numbers; derived counts and game-clock rate.
- `evidence/safety.json`: selected later safety snapshot fields, arrow/skeleton types and in-game positions, and the separately labeled distance calculation.
- `raw-source-audit.json`: original byte hashes, the current audit result, derivative extraction rules and the evidence gap below.
- `extract-evidence.py`: standard-library-only, offline allowlist extractor for readers who possess the original private evidence. It does not execute game code or inspect a running process.

These exports omit machine directories, player names, entity IDs, command/session identifiers, launch arguments and unnecessary debug fields. In-game coordinates and UTC evidence timestamps are retained. The original diagnostic stream and raw snapshots are not redistributed; their hashes identify the sources used. The existing published `metrics.json`, figures and post-pilot source snapshot remain unchanged.

## The overwritten snapshot is an explicit gap

The audit rechecked the 14 raw references recorded in the published metrics: **13 still matched, and one had been superseded**. The exception, `laterIdle`, was a mutable idle-status file. The historical audit recorded it at 19:20:12 UTC; the file now reflects a later idle snapshot. Its original expected digest and the newly observed digest are both retained. The old bytes are unavailable, and a checksum cannot reconstruct them. Nothing here silently replaces the frozen publication metrics or invents missing observations.

A separately identified run10 snapshot was added to this supplement to ground the earlier health value of 20. It is not counted among the original 14 references. It is checked against its own digest before extraction.

## Reproducing the sanitized exports

The seven original inputs are `mission`, `frozenOutcome`, `laterSameRun`, `priorRun10`, `diagnostic`, `safety` and `partialExport`. A holder of the raw records creates a **private** JSON object mapping those keys to the corresponding local files. Do not publish the map or put credentials into it. Run from this directory with Python 3.12 or a compatible release:

```sh
python extract-evidence.py --raw-map private-raw-map.json --output reproduced-evidence
```

The output directory must not already exist. The extractor verifies all seven original byte hashes first, projects only the reviewed fields and writes three JSON files. Comparing those outputs with `evidence/` verifies the documented sanitization and calculations. Source line numbers refer to the original JSONL row order. UTC timestamp arithmetic uses integer nanoseconds before converting differences to seconds.

Public readers can independently check claim pointers, package hashes, inventory arithmetic, diagnostic counts/time differences, skeleton distance and consistency with the figure inputs. Without the private original records, they cannot independently verify that no omitted raw field changes the interpretation or that the game execution itself was authentic. Hashes establish byte identity against recorded references; they do not establish truth, complete coverage or causal validity.

## Interpretation remains bounded

The retained evidence supports 39 net new logs and an interrupted return, a configured 50-ms scheduler, and sampled mining progress with mouse capture released. It does not support a numerical performance advantage over direct model control. The final source is post-pilot, and its later threat/return changes were not given another complete field trial. The animation reconstructs saved route order without measured travel timing. The architectural robotics lessons remain hypotheses for future controlled tests.

For future runs, record immutable observation/action events, controller build identity, timing and pause boundaries, interventions, tool/model usage, and separate resource-acquisition and successful-return outcomes as the experiment happens. This retrospective supplement makes the remaining evidence auditable; it does not manufacture that missing history.
