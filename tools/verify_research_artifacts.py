#!/usr/bin/env python3
"""Verify preserved Minecraft evidence; no network access or game execution.

Run from the repository: python tools/verify_research_artifacts.py
Regenerate reviewed hashes explicitly: add --write-manifest.
This checks byte integrity, references, and selected calculations, not scientific truth.
"""
import argparse
import calendar
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
ASSET_REL = Path("assets/research/minecraft-local-agent")
ARTICLE = "_posts/2026-09-13-minecraft-local-agent-control.md"
EXTRA_FILES = [ARTICLE, "_pages/minecraft-traceability.md", "AGENTS.md",
               "tools/verify_research_artifacts.py"]
MANIFEST_REL = ASSET_REL / "traceability/SHA256SUMS.txt"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_path(base, path):
    target = (base / path).resolve()
    require(target.is_relative_to(base.resolve()), "Path escapes evidence root: " + path)
    require(target.is_file(), "Missing file: " + path)
    return target


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def pointer(document, ref):
    require(ref == "" or ref.startswith("/"), "Invalid JSON pointer: " + ref)
    for token in ref.split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        document = document[int(token)] if isinstance(document, list) else document[token]
    return document


def timestamp_ns(value):
    whole, _, fraction = value.removesuffix("Z").partition(".")
    return calendar.timegm(time.strptime(whole, "%Y-%m-%dT%H:%M:%S")) * 10**9 + int(
        (fraction + "000000000")[:9])


def expected_paths(root):
    paths = {p.relative_to(root).as_posix() for p in (root / ASSET_REL).rglob("*")
             if p.is_file() and p != root / MANIFEST_REL and "__pycache__" not in p.parts}
    return paths | set(EXTRA_FILES)


def verify(root, write_manifest=False):
    assets = root / ASSET_REL
    manifest = root / MANIFEST_REL
    paths = expected_paths(root)
    if write_manifest:
        manifest.write_text("".join(digest(safe_path(root, name)) + "  " + name + "\n"
                                    for name in sorted(paths)), encoding="utf-8", newline="\n")
    require(manifest.is_file(), "Missing reviewed checksum manifest")
    listed = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        require(match is not None, "Malformed checksum entry")
        checksum, name = match.groups()
        require(name not in listed, "Duplicate manifest path: " + name)
        listed[name] = checksum
        require(digest(safe_path(root, name)) == checksum, "SHA-256 mismatch: " + name)
    require(set(listed) == paths, "Manifest coverage differs from public evidence files")

    # Verify the original, frozen publication bundle independently of the new manifest.
    require(digest(assets / "metrics.json") ==
            "34d4ac0921f4342620296f0fe3f7d470e6d95a6f8384e76bd95cda3f3e20df49",
            "Frozen publication metrics changed; create a new version instead")
    require(digest(assets / "worker-source.zip") ==
            "5a9b85645a8dfd983b5c48e2141c7a566468b0541cb1c13f9351599f298c6dd3",
            "Frozen post-pilot source ZIP changed")
    for line in (assets / "source/SHA256SUMS.txt").read_text().splitlines():
        if not line.strip():
            continue
        checksum, name = line.split(maxsplit=1)
        require(digest(safe_path(assets / "source", name.lstrip("*"))) == checksum,
                "Original source checksum mismatch: " + name)

    metrics = read_json(assets / "metrics.json")
    figures = read_json(assets / "figure-inputs.json")
    outcome = metrics["outcome"]
    require(outcome["finalInventoryLogs"] - outcome["baselineInventoryLogs"] ==
            outcome["netNewInventoryLogs"] == outcome["reportedCollectedLogs"] == 39,
            "Inventory delta mismatch")
    require(outcome["returnCompleted"] is False and outcome["paused"] is True and
            outcome["finalHealthPoints"] == 16, "Outcome boundary changed")
    diag = metrics["diagnosticWindow"]
    trace = diag["trace"]
    require(len(trace) == diag["sampleCount"] == 60, "Diagnostic sample count mismatch")
    require(sum(t["mouseCaptured"] is False for t in trace) == diag["mouseNotCapturedSamples"],
            "Mouse-capture count mismatch")
    require(sum(t["paused"] is False for t in trace) == diag["unpausedSamples"],
            "Pause count mismatch")
    require(dict(Counter(t["phase"] for t in trace)) == diag["phaseSampleCounts"],
            "Diagnostic phase counts mismatch")
    require(trace[-1]["gameTicksSinceFirst"] == diag["lastPlayerTick"] - diag["firstPlayerTick"]
            == diag["observedGameTicksAdvanced"] == 296, "Game tick delta mismatch")
    require(math.isclose(trace[-1]["tSeconds"], diag["observedSpanSeconds"], abs_tol=1e-9),
            "Diagnostic duration mismatch")
    require(math.isclose(diag["observedGameTicksAdvanced"] / diag["observedSpanSeconds"],
                         diag["observedGameTickRateHz"], rel_tol=1e-12), "Game tick rate mismatch")
    require(metrics["localLoop"]["measuredActionRateHz"] is None and
            metrics["localLoop"]["measuredWorkerInvocationRateHz"] is None and
            metrics["comparativeValidity"]["matchedBenchmark"] is False and
            figures["scenarios"]["measuredTaskSpeedup"] is None,
            "Unsupported measured-performance claim")
    observed = figures["observations"]
    require(observed["newInventoryLogs"] == outcome["netNewInventoryLogs"] and
            observed["protectedRadiusBlocks"] == outcome["protectedHomeRadiusBlocks"] and
            observed["homeXZ"] == outcome["homeXZ"] and
            observed["returnCompleted"] == outcome["returnCompleted"], "Figure/outcome mismatch")
    require(len(observed["routeBlockXZ"]) == 676, "Recorded breadcrumb count changed")
    require(any(h["description"] == "offline audit metrics" and
                h["sha256"] == digest(assets / "metrics.json")
                for h in figures["sourceArtifactHashes"]), "Figure provenance mismatch")

    raw_audit = read_json(assets / "traceability/raw-source-audit.json")
    original_sources = raw_audit["sources"]
    source_ids = {s["sourceKey"] for s in original_sources + raw_audit["additionalSources"]}
    require(len(source_ids) == len(original_sources) + len(raw_audit["additionalSources"]),
            "Duplicate raw-source key")
    require(len(original_sources) == 14 and
            sum(s["auditStatus"] == "matched" for s in original_sources) == 13 and
            sum(s["auditStatus"] == "superseded" for s in original_sources) == 1,
            "Historical raw-source availability boundary changed")
    require(raw_audit["originalAuditSummary"] ==
            {"originalReferencesChecked": 14, "matched": 13, "superseded": 1, "missing": 0},
            "Raw-source summary mismatch")
    for source in original_sources:
        expected = source["expectedHashReference"]
        require(pointer(read_json(safe_path(assets, expected["path"])), expected["pointer"])
                == source["expectedSha256"], "Original raw-source hash reference mismatch")
        require((source["observedSha256"] == source["expectedSha256"])
                == (source["auditStatus"] == "matched"), "Inconsistent raw-source audit status")
        if source["auditStatus"] == "superseded":
            require(source["sourceKey"] == "laterIdle", "Unexpected superseded evidence")

    wood = read_json(assets / "traceability/evidence/wood-outcome.json")
    diagnostic = read_json(assets / "traceability/evidence/diagnostic.json")
    samples = diagnostic["samples"]
    safety = read_json(assets / "traceability/evidence/safety.json")
    for exported in [wood, diagnostic, safety]:
        require(set(exported["sourceHashRefs"]).issubset(source_ids), "Unresolved export source hash")
    require(wood["frozenOutcome"]["inventoryLogs"] - wood["mission"]["baselineLogs"] ==
            wood["derived"]["netAdditionalLogs"] == outcome["netNewInventoryLogs"],
            "Sanitized outcome differs from published metrics")
    require(wood["priorRun10"]["health"] - wood["frozenOutcome"]["health"] ==
            wood["derived"]["healthDecreaseFromPriorSnapshot"] == 4, "Health delta mismatch")
    require(math.isclose((timestamp_ns(wood["laterSameRun"]["updatedAt"]) -
                          timestamp_ns(wood["frozenOutcome"]["updatedAt"])) / 1e9,
                         wood["derived"]["wallSecondsBetweenStoppedSnapshots"], abs_tol=1e-9),
            "Stopped-snapshot timing mismatch")
    require(wood["laterSameRun"]["elapsedSeconds"] - wood["frozenOutcome"]["elapsedSeconds"] ==
            wood["derived"]["elapsedCounterIncreaseWhileStoppedSeconds"], "Elapsed-counter difference mismatch")
    require(len(samples) == len(trace), "Sanitized diagnostic length mismatch")
    for i, (sample, projected) in enumerate(zip(samples, trace), 1):
        require(sample["sourceLine"] == i and sample["capture"] is False and sample["paused"] is False,
                "Diagnostic order or flags mismatch")
        require(sample["tick"] - samples[0]["tick"] == projected["gameTicksSinceFirst"],
                "Sanitized tick projection mismatch")
        require(math.isclose((timestamp_ns(sample["at"]) - timestamp_ns(samples[0]["at"])) / 1e9,
                             projected["tSeconds"], abs_tol=1e-9), "Timestamp projection mismatch")
        require(sample["phase"] == projected["phase"] and
                sample["logIndex"] == projected["logIndex"] and
                sample["treesCut"] == projected["segmentTreesCut"] and
                sample["isDestroying"] == projected["isDestroying"], "Diagnostic field mismatch")
    for key, value in diagnostic["derived"].items():
        require(value == diag[key], "Diagnostic aggregate mismatch: " + key)
    require(safety["playerPosition"] == outcome["finalPositionXYZ"], "Safety snapshot position mismatch")
    require(math.isclose(math.dist(safety["playerPosition"],
                         safety["lastDamageSource"]["causingEntity"]["position"]),
                         safety["derived"]["causingEntityDistanceBlocksAtObservation"], rel_tol=1e-12),
            "Safety distance calculation mismatch")
    require(math.isclose((timestamp_ns(safety["snapshot"]["at"]) -
                          timestamp_ns(wood["frozenOutcome"]["updatedAt"])) / 1e9,
                         safety["derived"]["secondsAfterFrozenOutcomeSnapshot"], abs_tol=1e-9),
            "Safety observation timing mismatch")

    claims = read_json(assets / "traceability/claims.json")
    require(claims["pathBase"] == "artifact-root", "Unexpected claim path base")
    require(claims["sourceHashRegistry"] == "traceability/raw-source-audit.json",
            "Unexpected raw-source registry")
    ids = set()
    evidence_refs = 0
    for claim in claims["claims"]:
        require(claim["id"] not in ids, "Duplicate claim ID")
        ids.add(claim["id"])
        require(claim["statement"] and claim["kind"] and claim["limitations"],
                "Claim missing scope or limitations: " + claim["id"])
        require(claim["evidence"], "Claim has no evidence: " + claim["id"])
        for evidence in claim["evidence"]:
            file = safe_path(assets, evidence["path"])
            require(set(evidence["sourceHashRefs"]).issubset(source_ids), "Unresolved source-hash reference")
            if "pointer" in evidence:
                pointer(read_json(file), evidence["pointer"])
            if "lineStart" in evidence:
                require(1 <= evidence["lineStart"] <= len(file.read_text().splitlines()),
                        "Code line reference out of range")
            evidence_refs += 1
    require(ids == {"C%02d" % n for n in range(1, 9)}, "Incomplete claim ledger")

    print("PASS: %d SHA-256 entries; %d claims / %d evidence references; selected numerical invariants"
          % (len(listed), len(ids), evidence_refs))
    print("Scope: preserved-byte integrity and checked consistency; no ARA seal or complete-history guarantee.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--write-manifest", action="store_true",
                        help="explicitly replace hashes after reviewing an intentional revision")
    options = parser.parse_args()
    try:
        verify(options.repo_root.resolve(), options.write_manifest)
    except (ValueError, KeyError, IndexError, OSError, json.JSONDecodeError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        sys.exit(1)
