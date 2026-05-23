---
layout: archive
title: "CV — Robotics Software Engineer"
permalink: /cv/robotics/
author_profile: true
redirect_from:
  - /robotics-cv/
  - /cv/robotics-software-engineer/
---

{% include base_path %}

<p><a class="button" href="/assets/cv-robotics.pdf" download>Download Robotics SWE PDF</a> &nbsp;|&nbsp; <a href="/resumes/">All resumes</a> &nbsp;|&nbsp; <a href="/cv/ml/">ML Engineer view</a></p>

<p><small>PDF is built from a polished LaTeX source at <a href="https://github.com/cnpcshangbo/cnpcshangbo.github.io/blob/master/cv-tex/cv-robotics.tex"><code>cv-tex/cv-robotics.tex</code></a> (resume-style, distinct from this longer-form web page).</small></p>

> **TL;DR** — Robotics software engineer with deep field experience in **multi-sensor data pipelines, LiDAR + camera synchronization, and real-time perception systems**. Shipped fixed-LiDAR + camera pipelines for highway traffic monitoring with NYC agencies, built drone and climbing-robot inspection stacks on ROS / NVIDIA Jetson, and own the end-to-end loop from sensor calibration through ingestion, recording, and downstream ML.

## Core skills

**Sensors & perception**
LiDAR (mechanical and solid-state, multi-beam), multi-camera rigs, depth cameras, IMU, hyperspectral, infrared, underwater acoustic. **Temporal synchronization** (hardware triggers, PTP / NTP timestamp alignment, post-hoc time-correction), **spatial calibration** (intrinsic/extrinsic, LiDAR–camera cross-calibration, multi-camera rigs), **sensor fusion** for detection and tracking.

**Robotics stack**
ROS / ROS 2, ROS bag and **MCAP** recording, **Protobuf** for sensor message schemas, NVIDIA Jetson (Nano/TX2/Xavier) edge deployment, Raspberry Pi, Arduino, embedded Linux, **DepthAI / OAK** camera platforms (working knowledge), real-time control (PID, fractional-order, visual servoing).

**Software**
Python (primary), C++, MATLAB, Fortran. Linux/Ubuntu, Docker, AWS (S3, EC2, model serving), CUDA, OpenCV, PyTorch, TensorFlow. Git, CI/CD for research-to-production pipelines.

**Calibration & data systems**
Multi-camera + LiDAR extrinsic calibration workflows, time-sync diagnostics, high-throughput ingestion, MCAP/Protobuf-based recording, dataset format conversion across configurations, background subtraction and segmentation pipelines.

## Selected projects (synchronization & multi-sensor focus)

### Highway Traffic Monitoring — Fixed LiDAR + Camera Pipeline · 2024–present
*AI & Mobility Research Lab, CCNY · NYC DOT collaboration*

- Designed and deployed an **end-to-end multi-sensor capture pipeline** for fixed roadside LiDAR + camera at NYC highway sites, including **temporal alignment** of LiDAR frames with RGB streams and **spatial calibration** for downstream 2D-3D fusion.
- Built background subtraction, object segmentation, and CNN-based detection stages on top of synchronized frames; classified vehicles, motorcycles, bicycles, and pedestrians (vulnerable road users).
- Engineered **multi-frame vehicle reconstruction** that stitches successive sweeps into per-vehicle point cloud models — explicit dependency on tight time-sync between sensor and ego-clock.
- Built a configuration-portable training/inference loop so models trained on one site's sensor configuration can be retargeted to another with different beam counts, mounting geometry, and frame rates.
- Co-authored two MobiSPC 2025 papers on LiDAR beam-count requirements for VRU detection and a broader sensing-perspectives survey.

**Stack:** Python, PyTorch, ROS, LiDAR SDKs, OpenCV, calibration toolchains, NYC field deployments.

### Bridge Inspection Robot Deployment System (BIRDS) · 2020–2024
*Missouri S&T → CCNY Robotics Lab*

- Engineered a **drone + robotic-arm clamping system** for autonomous bridge inspection — included **vision-based girder detection on NVIDIA Jetson**, PID and fractional-order controllers for the clamping mechanism, and an iOS app for human-in-the-loop control.
- Owned hardware-software integration across **multi-camera (visible / infrared / hyperspectral) UAS payloads**, including capture, time-tagging, and downstream signal processing.
- Built supporting underwater **robot-assisted acoustic imaging** rig for bridge scour evaluation on ROS + Arduino + embedded Linux.
- Patent: *Unmanned vehicle having flight configuration and surface traverse configuration* (US 12,296,994, granted 2025).

### Advanced Bridge Inspection Automation · 2022–present
*CCNY Robotics Lab*

- Trained and deployed CNNs for crack / spalling / stain detection from inspection imagery; pushed models to **AWS for scalable cloud inference**.
- Built a custom **WebODM-based platform** integrating segmentation, 3D reconstruction, interactive visualization, and crack measurement — sensor data in, structured defect output out.
- Selected for IEEE IROS 2025 presentation (Feng, Shang, et al., *IEEE T-ASE*, 2025).

### Earlier robotics work · 2010–2019
- 2015–2019: Drone visual servoing with fractional-order control (Raspberry Pi, embedded Linux).
- 2015–2017: SmartCaveDrone — sense-and-avoid + GPS-denied UAV navigation in cave environments.
- 2013–2014: ROS + AR.Drone object tracking quadrotor.
- 2012–2013: Indoor quadrotor UAV with LiDAR (early multi-sensor work).
- 2014 International Aerial Robotics Competition — **Best System Control** + **Best Mission Planning** awards (team lead).

## Education

- **PhD, Civil Engineering (Transportation)** — CCNY, NY, USA · 2025–present
- **PhD, Pattern Recognition and Intelligent Systems** — Northeastern University, China · 2013–2020
- **Exchange PhD** — UC Merced · 2015–2017 (Mechatronics Embedded Control Systems Lab)
- **MEng, Pattern Recognition and Intelligent Systems** — Northeastern University, China · 2011–2013
- **BEng, Automation** — Northeastern University, China · 2007–2011

## Experience

- **2025–now** — Postdoctoral Scholar, AI & Mobility Research Lab, CUNY City College
- **Dec 2022–Dec 2024** — Postdoctoral Researcher, CCNY Robotics Lab
- **Jan 2020–Nov 2022** — Postdoctoral Fellow, Missouri University of Science and Technology
- **2015–2017** — Lecturer / Junior Specialist, UC Merced — courses on Mechatronics and Unmanned Aerial Systems; co-designed UAS lab curriculum
- Multiple adjunct / instructor roles teaching Robotics, Mechanics and Control (Vaughn College), Mechatronics, UAS, and Electric Circuits (CUNY City)

## Patents

- Chen, Reven, **Shang**, et al. *Unmanned vehicle having flight configuration and surface traverse configuration.* US 12,296,994, granted May 2025.
- Wu, **Shang**, et al. *Data/image transmission device based on TCP/IP.* CN 102427464 B.
- Zhang, **Shang**, et al. *Internet-based interactive digital media terminal device.* CN 102306237 A.

## Certifications

- **FAA Part 107** — Remote Pilot Certificate for Small Unmanned Aircraft Systems (2016).

## Awards (selected)

- 2014 — *Best System Control* and *Best Mission Planning*, International Aerial Robotics Competition (AUVSI Foundation, USA). Team lead.
- 2010 — First Prize, Northeastern Region, National Smart Car Competition, Freescale.
- 2025–2030 — PhD Fellowship, CCNY Civil Engineering (Transportation).

## Why this role fits

I've been the engineer who actually deploys the LiDAR rig at the side of a NYC highway, runs the time-sync diagnostics when the camera and LiDAR disagree by 30 ms, recalibrates the extrinsics, and then trains the detector on whatever messy data the system produced. The **multi-camera ingestion + synchronization + calibration + recording + downstream model loop** is exactly where I've been living for the last several years — and what I want to keep building.

---

*Looking for the [Machine Learning Engineer view](/cv/ml/), the [full academic CV](/cv/), or [all resumes](/resumes/)?*
