# Portable figure reproduction and provenance

This package reconstructs four research figures and an optional schematic video from the accompanying sanitized `figure-inputs.json`. It is self-contained: the original local game files are not required. It does not load a Minecraft client, attach to a game process, send input, contact a server or use a model API.

## Reproduce

Use Python 3.12 or a compatible release. The original exports used Python 3.12.14; direct dependency versions are pinned in `requirements.txt`.

```sh
python -m pip install -r requirements.txt
python figures.py --output rendered
```

For static figures without the optional video, add `--no-video`. Relative output paths are resolved from the current directory. The input is always read from `figure-inputs.json` beside the script, so execution from another working directory is supported. SVGs retain searchable DejaVu Sans text; PNGs export at 200 dpi. The optional MP4 is an H.264 1080 × 720 schematic, 16 seconds at 10 frames/s, plus a PNG poster. Fonts and dependency versions can affect exact rendering across environments.

Only the scenario values supplied in this publication input are intended for exact reproduction: fixed axis ranges, labels and layout were chosen for this case. The script is not a general-purpose benchmark or arbitrary-data plotting application.

## Sanitization and source

The input preserves the 676 recorded breadcrumb X/Z block coordinates, protected home reference and radius, four recovery-tree X/Z bases, the final continuous X/Z position, two outcome totals, and four aggregate values from the diagnostic trace. Height, player/account identifiers, run identifiers, host paths, launch arguments and per-observation timestamps are omitted. Minecraft coordinates describe an in-game world, not a real-world location.

The data were extracted from four frozen artifact types: a saved mission, a final outcome snapshot, a recovery-tree export and an offline audit. Their SHA-256 checksums are retained under `sourceArtifactHashes` to identify the evidence used, without exposing private path names. The hashes are provenance identifiers; the portable generator does not need those original artifacts. The data are from Minecraft 26.3-rc-2 in one sequential survival-mode development session, not a randomized or matched benchmark.

## Control architecture — article Figure 1

`01-control-architecture.svg` / `.png`. Conceptual comparison. Screenshot-driven LLM control interprets rendered pixels and issues bounded desktop input. In the local collector, Astra constructs and supervises a deterministic worker with a configured 50 ms scheduler; the worker reads structured client state and uses movement and vanilla survival-mining APIs. Commands and status/logs connect supervision to execution. The observation and action interfaces differ as well as nominal cadence, so the comparison does not isolate model speed. “Privileged” means access to game internals, not elevated operating-system permissions. Diagram geometry is schematic.

## Nominal cadence scenarios — article Figure 4

`02-nominal-cadence-scenarios.svg` / `.png`. Assumed LLM cycle intervals of 1, 5, 10 and 20 seconds divided by a configured 0.05-second local scheduling delay yield 20, 100, 200 and 400 nominal dispatch opportunities. These LLM intervals are assumptions, and these ratios are not measured task speedups. Game ticks, state transitions and safety checks gate actual actions. The diagnostic trace contains 60 observations spanning 14.7673622 seconds, with 296 advanced player ticks: 20.0442 game ticks/s. That aggregate measures the sampled game clock, not worker callbacks, action frequency or end-to-end task performance.

## Saved breadcrumbs and final stop — article Figure 3

`03-recorded-route.svg` / `.png`. Plan view of 676 saved entries, a 128-block protected disk around home X = −698, Z = 195, and four recovery-tree bases. The orange marker is the recorded final continuous position, X = −636.3621, Z = 371.4995. The final snapshot reports 39 newly collected logs and a stop after a health change, with a reported horizontal home distance of 186.3 blocks calculated from integer block coordinates. The return was incomplete. Breadcrumbs and tree bases are plotted at block centers (+0.5 in X and Z); home and final continuous position are unchanged. Height is omitted, and positive Z runs downward. The sequence has no timestamps and does not record the return leg: only the final return stop is shown. This is not a terrain map, and the four recovery bases are not a complete inventory of harvested trees.

## Illustrative amortization — article Figure 5

`04-illustrative-amortization.svg` / `.png`. Hypothetical break-even task counts equal ceiling(setup time / time saved per subsequent task). Both inputs are assumptions: setup times of 15, 60 and 180 minutes, and per-task savings of 5, 15, 60 and 300 seconds. Positive constant savings are assumed, and maintenance is excluded. Neither quantity was established in this case; this is not an empirical break-even claim.

## Optional video

`05-breadcrumb-reconstruction.mp4` and `05-breadcrumb-reconstruction-poster.png`. A reveal of saved breadcrumb order with uniform illustrative step timing. It is explicitly a reconstruction, not gameplay footage, recorded travel timing or a performance demonstration. No return motion is animated because the return leg was not recorded. The final stop is a separate fixed marker.
