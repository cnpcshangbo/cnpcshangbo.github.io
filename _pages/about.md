---
permalink: /
title: ""
excerpt: "About me"
author_profile: true
redirect_from:
  - /about/
  - /about.html
---

# Bo Shang

**Robotics & AI Researcher**

My research asks how the infrastructure around us — highways, intersections, bridges — can perceive itself. I work across scales, from a single bridge component to a whole city, and the question is the same at each scale: what can be observed, and what does that observation make possible? The throughline is **resilient intelligent infrastructure**: fixed sensors and embodied robots that together give the built environment a working model of itself.

Since July 2026, I have been a Postdoctoral Associate in Civil and Environmental Engineering and the Maryland Transportation Institute at the University of Maryland, College Park, working under Professor Xianfeng Yang. I support hardware and software development, integration, testing, troubleshooting, data collection, technical documentation, and deliverables for two sponsored transportation research projects. My broader work brings together learning-based perception, ROS-based robotics, edge inference, and inspection workflows developed with public agencies. At UMD I am extending the macro scale to the city: I build and operate CERRA (Civil, Environmental, Road & Resource Analytics), a platform that turns real-world infrastructure data into actionable insight, including an LLM-driven traffic simulation and a quantum-safe evaluation of signal broadcast.

## Resume & CV

- **[Research Scientist Resume](/cv/research/)** · [PDF](/assets/cv-research-scientist.pdf) — selected research contributions, projects, publications, and technical skills in robotics and multimodal perception.
- **[Academic CV](/cv/)** · [PDF](/assets/cv.pdf) — the full record of appointments, publications, patents, teaching, and academic service.

## Research: intelligent infrastructure at three scales

- **Macro — highway mobility (InfraLiDAR-Eval).** Continuous traffic monitoring with fixed roadside LiDAR: an end-to-end pipeline from raw ingestion to sparse-to-dense registration, evaluated on a 61.9-hour dataset, with a failure analysis showing where current models break under continuous roadside observation.
- **Meso — urban intersections (PACO).** Cooperative observability: a 120° ADAS sees 0.39 of the intersection scene, a 360° AV 0.63, and roadside LiDAR (V2I) 1.00. Expanding the field of view alone cannot close the gap — the binding constraint is occlusion, not coverage — so infrastructure sensing is mathematically necessary.
- **Micro — structural health (embodied robotics).** UAVs and climbing robots that assess the physical integrity of structures where people cannot easily go: the BIRDS bridge-inspection flying robot and vision-based concrete defect detection, connecting perception results to engineering use.

The three scales feed one model: fixed sensors contribute macro-level intelligence, embodied robots contribute micro-level agility, and the synthesis is a unified, multi-scale picture of the built environment.

## Research notes

- **[AI Agent Security After 29 Attempts](/posts/2026/09/ai-agent-security-postmortem/)** — a source-first postmortem on replay noise, public-leaderboard overfitting, counterbalanced experiments, and the private-guardrail reset.

## Selected publications

Selected work in urban freight sensing, roadside LiDAR, vulnerable-road-user safety, and robotic infrastructure inspection.

{% include selected-pubs.html %}
