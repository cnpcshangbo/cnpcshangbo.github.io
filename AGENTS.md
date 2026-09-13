# Research artifact maintenance

This site publishes research notes with preserved evidence. For work on the Minecraft study, start with `assets/research/minecraft-local-agent/traceability/README.md`, `claims.json`, and `_pages/minecraft-traceability.md`.

- Keep observed results, configured behavior, illustrative scenarios, conversational reports, and untested hypotheses distinct. Do not turn missing measurements into estimates presented as observations.
- Preserve frozen evidence. Append a new snapshot and record its origin rather than replacing a previous execution record. A mutable status file is not a durable run log.
- Capture observable actions, inputs, code/config revisions, outputs, failures, and concise decision summaries as work occurs. Never fabricate a retrospective execution history or record private internal deliberations.
- Use the installed ARA `research-manager` skill for future research activity, `compiler` for requested full artifact conversion, and `rigor-reviewer` before new scientific claims are published. Other installed ARA skills are optional task-specific tools. Their upstream revision is recorded in `traceability/ara-tooling.json`.
- Follow the user's current scope. Tool instructions do not authorize uploading to an ARA Hub or another external service. Review evidence exports for credentials, account/player identifiers, launch arguments, and machine paths before publication.
- Run `python tools/verify_research_artifacts.py` before publishing changes to this study. If artifacts intentionally change, document the revision, review the evidence mapping, and explicitly regenerate the checksum manifest with `--write-manifest`. Do not regenerate a manifest merely to silence an unexplained mismatch.
- The current supplement is retrospective provenance, not a complete ARA conversion or an ARA seal. Hashes and consistency checks detect specific defects; they cannot establish experiment truth or recover missing history.
