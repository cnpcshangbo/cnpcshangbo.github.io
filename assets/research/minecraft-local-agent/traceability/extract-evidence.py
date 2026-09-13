"""Reproduce reviewed field-only evidence exports from explicitly supplied raw files.

Offline and standard-library-only. Never attaches to Minecraft or executes source files.
The private input map is not copied to the output. All raw bytes must match the
recorded hashes before any derived evidence is written.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re

REQUIRED = ("mission", "frozenOutcome", "laterSameRun", "priorRun10", "diagnostic", "safety", "partialExport")
STATUS_FIELDS = ("updatedAt", "phase", "reason", "active", "version", "position", "health", "food", "inventoryLogs", "collectedLogs", "homeDistance", "targetLogs", "protectedRadius", "treesCut", "remainingWaypoints", "elapsedSeconds", "paused")


def instant_ns(value):
    match = re.fullmatch(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?Z", value)
    if not match:
        raise ValueError("Expected a UTC source timestamp with at most nanosecond precision")
    whole = datetime.strptime(match[1], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    return int(whole.timestamp()) * 1_000_000_000 + int((match[2] or "").ljust(9, "0"))


def project(raw):
    mission, end, later, prior = (raw[key] for key in REQUIRED[:4])
    trace, safety, partial = (raw[key] for key in REQUIRED[4:])
    outcome = {
        "schemaVersion": 1,
        "sourceHashRefs": ["mission", "frozenOutcome", "laterSameRun", "priorRun10", "partialExport"],
        "mission": {key: mission[key] for key in ("baselineLogs", "targetLogs", "radius", "homeX", "homeZ", "start")},
        "frozenOutcome": {key: end[key] for key in STATUS_FIELDS},
        "laterSameRun": {key: later[key] for key in STATUS_FIELDS},
        "priorRun10": {key: prior[key] for key in STATUS_FIELDS},
        "recovery": {
            "partialTrees": [{key: tree[key] for key in ("base", "airPrefix", "remainingLogs")} for tree in partial["trees"]],
            "remainingQueueLengthInSavedMission": len(mission["recoveryTrees"]),
            "qualification": "Four intermediate partially cut trunks and a later empty recovery queue; not a continuous record of every harvested block."
        },
        "derived": {
            "netAdditionalLogs": end["inventoryLogs"] - mission["baselineLogs"],
            "inventoryDeltaAgreesWithReportedCollectedLogs": end["inventoryLogs"] - mission["baselineLogs"] == end["collectedLogs"],
            "healthDecreaseFromPriorSnapshot": prior["health"] - end["health"],
            "wallSecondsBetweenStoppedSnapshots": (instant_ns(later["updatedAt"]) - instant_ns(end["updatedAt"])) / 1e9,
            "elapsedCounterIncreaseWhileStoppedSeconds": later["elapsedSeconds"] - end["elapsedSeconds"],
            "sameStoppedPausedPositionInventoryHealth": all(end[key] == later[key] for key in ("position", "inventoryLogs", "health")) and not end["active"] and not later["active"] and end["paused"] and later["paused"]
        },
        "interpretation": {
            "uninterruptedReturnCompleted": False,
            "basis": "Frozen outcome stopped after health loss while paused, retaining 60 logs, about 186 blocks horizontally from home. No successful return record exists.",
            "timingCaveat": "Elapsed counters include stopped/paused time and reset across resumes; do not derive mission duration or logs per minute."
        }
    }
    rows = [{"sourceLine": index, **{key: row[key] for key in ("at", "tick", "phase", "capture", "paused", "isDestroying")}, "logIndex": int(row["logIndex"]), "treesCut": int(row["treesCut"])} for index, row in enumerate(trace, 1)]
    span = (instant_ns(rows[-1]["at"]) - instant_ns(rows[0]["at"])) / 1e9
    ticks = rows[-1]["tick"] - rows[0]["tick"]
    diagnostic = {
        "schemaVersion": 1,
        "sourceHashRefs": ["diagnostic"],
        "samples": rows,
        "derived": {
            "sampleCount": len(rows),
            "observedSpanSeconds": span,
            "observedGameTicksAdvanced": ticks,
            "observedGameTickRateHz": ticks / span,
            "mouseNotCapturedSamples": sum(row["capture"] is False for row in rows),
            "unpausedSamples": sum(row["paused"] is False for row in rows),
            "activeMiningSamples": sum(row["isDestroying"] is True for row in rows),
            "phaseSampleCounts": dict(Counter(row["phase"] for row in rows))
        },
        "qualification": "Approximately 4 Hz diagnostic sampling of the game clock, not every worker callback/action. Source line 19 records a completed trunk with mouse capture released; observation began partway through that trunk."
    }
    damage = safety["lastDamageSource"]
    incident = {
        "schemaVersion": 1,
        "sourceHashRefs": ["safety", "frozenOutcome"],
        "snapshot": {key: safety[key] for key in ("at", "paused", "health", "food", "air", "fallDistance", "onFire", "inWater", "inLava")},
        "playerPosition": safety["player"]["position"],
        "lastDamageSource": {
            "messageId": damage["messageId"],
            "directEntity": {key: damage["directEntity"][key] for key in ("class", "position")},
            "causingEntity": {key: damage["causingEntity"][key] for key in ("class", "position")}
        },
        "derived": {
            "causingEntityDistanceBlocksAtObservation": math.dist(safety["player"]["position"], damage["causingEntity"]["position"]),
            "secondsAfterFrozenOutcomeSnapshot": (instant_ns(safety["at"]) - instant_ns(end["updatedAt"])) / 1e9,
            "playerPositionMatchesFrozenOutcome": safety["player"]["position"] == end["position"]
        },
        "qualification": "A later paused-snapshot diagnosis of skeleton-arrow damage, not measured arrow-release distance, impact time or stop latency."
    }
    return {"wood-outcome.json": outcome, "diagnostic.json": diagnostic, "safety.json": incident}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-map", type=Path, required=True, help="Private JSON object mapping source keys to original files; never publish this map")
    parser.add_argument("--output", type=Path, required=True, help="New output directory; refuses to overwrite")
    args = parser.parse_args()
    mapping = json.loads(args.raw_map.read_text(encoding="utf-8-sig"))
    audit = json.loads(Path(__file__).with_name("raw-source-audit.json").read_text(encoding="utf-8"))
    source_meta = {row["sourceKey"]: row for row in audit["sources"] + audit["additionalSources"]}
    raw = {}
    for key in REQUIRED:
        if key not in mapping:
            raise SystemExit(f"Missing source key: {key}")
        data = Path(mapping[key]).read_bytes()
        if hashlib.sha256(data).hexdigest() != source_meta[key]["expectedSha256"]:
            raise SystemExit(f"Original bytes do not match recorded source hash: {key}")
        content = data.decode("utf-8-sig")
        raw[key] = [json.loads(line) for line in content.splitlines() if line.strip()] if key == "diagnostic" else json.loads(content)
    outputs = project(raw)
    args.output.mkdir(parents=True, exist_ok=False)
    for filename, value in outputs.items():
        (args.output / filename).write_bytes((json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8"))
    print("Reproduced three sanitized evidence exports after verifying seven original hashes.")


if __name__ == "__main__":
    main()
