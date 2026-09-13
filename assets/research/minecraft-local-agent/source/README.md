# Minecraft local-worker source snapshot

This archive accompanies the September 13, 2026 Minecraft control case study. It contains the **post-pilot source**, not a frozen copy of the controller that produced the complete field record. The later visible-ranged-attacker check and loop-erased return path were compiled and checked but were not validated by another full field run. Building this code does not reproduce the earlier experiment or establish an efficiency comparison.

The pilot accumulated 39 net new logs (inventory 21 to 60), then stopped and paused after skeleton-arrow damage during the return. It did not complete the collect-and-return task. Several code revisions, inspections and resumptions preceded that result.

## Contents and provenance

- Six runtime Java sources in `src/woodagent/`: controller, navigation, tree validation, background mining integration, agent bootstrap and attach entry point.
- `test/NavigationTest.java`: dependency-free synthetic navigation checks.
- `manifest.mf`: agent entry point; class redefinition and retransformation are disabled.
- `common.ps1`, `start.ps1`, `status.ps1`, `stop.ps1`, `watchdog.ps1`: the post-pilot Windows launcher/supervision scripts.
- `build.ps1`: a new offline packaging helper for this public bundle. It compiles/tests using explicit local dependencies and does not inspect or attach to a game process.
- `SHA256SUMS.txt`: checksums of all other packaged files.

The six Java files, test, manifest and five runtime PowerShell scripts are copied unchanged from the packaged post-pilot artifact. The README and offline build helper were added for publication. No Minecraft binaries, compiled worker JAR/classes, saved worlds, private classpath file, command/session state, launcher arguments, credentials, raw diagnostic log, or player/account identifiers are distributed. The older `control.cjs` convenience helper is omitted; its status command renewed a lease without the freshness checks in `status.ps1`.

The Java code contains the experiment's in-game default home coordinates, X=-698, Z=195. These are world coordinates, not machine paths. Always supply the appropriate home coordinates for a different world; the defaults do not protect an arbitrary reader's home.

## Environment and compatibility

The complete worker targets **Minecraft Java 26.3-rc-2** and **JDK 25**. It compiles against that exact client's named internal API, including its runtime libraries. It is not a generic mod and has no stable cross-version compatibility promise. The game and all third-party libraries must be supplied from your own installation. The running client must support Java's `jdk.attach` and dynamic agent loading for the optional launch step.

The included launch and build scripts target **Windows with PowerShell 7**. They contain no hardcoded local user directories. The launcher locates an exact-version Java client through Windows process metadata, reads its command line in memory to identify it, and does not print that command line. Run it only against the intended local singleplayer client. Java sources and the pure navigation tests may be compiled on other operating systems, but the supplied launcher is not cross-platform.

A full build requires a private text file containing one platform-separated Java classpath line: the exact `versions/26.3-rc-2/26.3-rc-2.jar` from your installation plus that version's required runtime library JARs, including Gson and the libraries referenced by the Minecraft API signatures. On Windows entries are separated by semicolons. Obtain those dependency paths from your local launcher/version metadata; do not put authentication arguments or an entire launch command into the file. Do not commit or upload the file. This archive intentionally does not provide a machine-specific classpath.

## Offline tests and build

From this extracted `source` directory, with JDK 25 tools on PATH:

```powershell
# Synthetic navigation tests only; no game installation or connection needed.
.\build.ps1 -TestOnly -OutputDirectory .\navigation-check

# Full compile plus the same tests, using your private local dependency list.
# Replace the ClasspathFile value with the file you created locally.
.\build.ps1 -ClasspathFile .\private-classpath.txt -OutputDirectory .\worker-build
```

Use a fresh output directory for each invocation; the helper refuses to overwrite an existing build. If JDK 25 is not on PATH, pass `-JdkBin` with your local JDK's `bin` directory. No command above attaches to Minecraft, changes the world, or starts gameplay. The full build produces `worker-build/wood-agent.jar`; that generated binary is not part of the distributed archive. Fixed JAR entry timestamps reduce avoidable packaging variation, but identical binary output still depends on compiler and dependency versions.

The navigation test can also be run directly with a JDK, without the PowerShell helper:

```text
javac --release 25 -d navigation-check src/woodagent/Navigation.java test/NavigationTest.java
java -cp navigation-check woodagent.NavigationTest
```

The test harness uses an in-memory synthetic terrain implementation. It covers bounded pathfinding, traversal constraints and return-path loop handling. It does **not** test Minecraft integration, real-time deadlines, all terrain types, mining/raycast behavior, tree classification, pickup reliability, window-focus behavior, live watchdog/process failure, combat avoidance or successful field return. Compilation verifies API/type compatibility with the supplied dependencies, not behavioral safety or field performance.

## Optional supervised use

Attaching and starting are separate from the offline build. These commands are for a reader who deliberately chooses to run the prototype in an appropriate local singleplayer world. The launch command starts gameplay and may mine trees and eligible obstructing natural leaves outside the configured protected area. The post-pilot code is a prototype; use a disposable test world or your own backup for evaluation.

After compiling, inspect the code and use the correct home coordinates. For example, if your chosen home center is X=0, Z=0:

```powershell
.\start.ps1 -AgentDirectory .\worker-build -HomeX 0 -HomeZ 0 -Radius 128 -Logs 32
.\status.ps1 -AgentDirectory .\worker-build
.\stop.ps1 -AgentDirectory .\worker-build
```

`start.ps1` attaches an idle controller, waits for readiness, and then issues the start command after a short delay. It normally launches the local watchdog in a hidden window. If several exact-version clients are running, select the intended one with `-MinecraftProcessId`. This helper uses the current character; it does not join a server as another bot. The in-process controller verifies singleplayer and the version before starting. No spawn-item, teleport or direct world-save rewrite operation is part of this worker.

Status and mission files are written only to the chosen agent directory's `runtime` subdirectory. `status.ps1` without `-RenewLease` reads status without extending the lease. The watchdog renews only a fresh matching active run, with a twenty-minute bound; the controller has its own two-minute supervision lease. A stop request needs an acknowledgment. If the game does not acknowledge it, use the game's pause/menu control. A paused singleplayer game is not a model for an independent physical robot safety stop.

To resume a mission already saved in the same local output directory:

```powershell
.\start.ps1 -AgentDirectory .\worker-build -Resume
```

Resume uses that directory's saved settings, inventory baseline and return path. It resets segment-local counters and the per-run supervision window. It must not be combined with replacement home/target settings. No pilot mission state is included in this archive. Keep generated runtime files private until separately sanitized for any publication.

## Audit limits and interpretation

The accompanying research-note metrics distinguish recorded observations, code settings and derived quantities. They do not establish a matched comparison with direct screenshot/input control: the earlier task was cobblestone mining; the worker task was wood collection with exact internal state access. Model-call counts, tokens, billed cost, active end-to-end runtime and numerical task speedup were not retained in a reliable matched record.

The scheduler requests a 50 ms delay and gates decisions by player tick. This is a nominal 20 Hz design, not a measured guarantee of 20 actions per second. A separate diagnostic observed 60 samples over 14.767 seconds while the game clock advanced 296 ticks. That is game-clock cadence sampled at approximately 4 Hz, not a complete worker-action trace. Mouse capture was released during the sampled mining progress; window-focus state was not independently recorded in that stream.

`elapsedSeconds` is wall time since the current start/resume and continues while stopped or paused. Status JSON is overwritten, not an immutable event log. Resume preserves the mission's original inventory baseline while resetting segment tree counts and elapsed time. A later idle attachment can report collectedLogs=0 even while the 60-log inventory remains. Do not sum snapshots or divide logs by these elapsed counters to estimate speed.

The incident build checked a player bounding box expanded by seven blocks for hostile mobs. A later paused snapshot identified an arrow from a skeleton about 14.73 blocks away; this is not an exact arrow-release or impact-distance measurement. This source snapshot adds a 24-block visible-ranged-attacker check and return-path changes after that incident. Those changes were not demonstrated to prevent the same encounter in a subsequent field run.

The archive includes no gameplay video, full control trace, paired trials or raw private telemetry. Reproducing a scientific comparison requires new, explicitly designed experiments with frozen versions, matched state/action interfaces, pause-aware timing, independently logged interventions, and separate resource-acquisition and complete-return success criteria. The code is a version-specific engineering example, not evidence of sim-to-real transfer.
