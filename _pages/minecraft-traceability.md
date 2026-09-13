---
layout: single
title: "Minecraft study: evidence and traceability"
permalink: /research-notes/minecraft-traceability/
author_profile: true
---

This record accompanies [the Minecraft local-agent case study](/posts/2026/09/minecraft-local-agent-control/). It was assembled retrospectively on September 13, 2026 from the surviving artifacts. It distinguishes recorded observations, source-code settings, derived calculations, illustrative scenarios, and statements available only in the conversation.

## Inspect the evidence

- [Claim-to-evidence ledger](/assets/research/minecraft-local-agent/traceability/claims.json): evidence references and limitations for the main conclusions.
- [Evidence guide and extraction rules](/assets/research/minecraft-local-agent/traceability/README.md): reviewed extracts, original source hashes, and instructions for reproducing them from privately retained inputs.
- [Raw-source availability audit](/assets/research/minecraft-local-agent/traceability/raw-source-audit.json): what could still be matched to the publication's source hashes.
- [SHA-256 manifest](/assets/research/minecraft-local-agent/traceability/SHA256SUMS.txt): byte-level identities of the public article, evidence, figures, source bundle, and traceability records.
- [Verification script](https://github.com/cnpcshangbo/cnpcshangbo.github.io/blob/master/tools/verify_research_artifacts.py): checks hashes and references and recomputes selected numerical relationships. GitHub Actions runs it before building the site.

## What remains unverified

The published figures, metrics, and source bundle are preserved. The local audit matched 13 of the 14 previously recorded raw-source hashes. One later idle-status file had been overwritten; its old hash remains recorded, and its original contents are unavailable. This gap does not replace or erase the separate frozen wood-collection outcome.

The record does not establish a measured speedup over direct language-model control. The earlier cobblestone result is conversation-reported, the diagnostic game-clock rate is not a worker action rate, and the published worker includes changes made after the pilot. No complete action log or continuous gameplay recording was saved. The ledger carries these boundaries alongside the evidence.

Checksums can detect a file changing relative to a reviewed manifest. Reference and arithmetic checks can detect broken links and inconsistent calculations. They cannot prove that a log is authentic, recover missing events, or guarantee a scientific conclusion. Use Git history to identify the exact manifest revision being checked.

## ARA tooling and future records

The seven core skills from [Agent-Native Research Artifact](https://github.com/ARA-Labs/Agent-Native-Research-Artifact) were installed for Codex from commit `e52a925e9d03b4ada3008653e72f99b04116fca2`. The [tooling record](/assets/research/minecraft-local-agent/traceability/ara-tooling.json) identifies that revision and the verified upstream file hashes.

This supplement applies claim/evidence bindings and explicit provenance boundaries. It is not a complete ARA conversion, an ARA validation seal, or a reconstruction of unsaved execution history. Future experiments should preserve immutable run records as they happen, with code/config revisions, timestamps, raw outputs, failures, and links from claims to supporting evidence.
