---
layout: archive
title: "CV — Machine Learning Engineer"
permalink: /cv/ml/
author_profile: true
redirect_from:
  - /ml-cv/
  - /cv/machine-learning-engineer/
---

{% include base_path %}

<p><a class="button" href="/assets/cv.pdf" download>Download Full PDF</a> &nbsp;|&nbsp; <a href="/resumes/">All resumes</a> &nbsp;|&nbsp; <a href="/cv/robotics/">Robotics SWE view</a></p>

> **TL;DR** — ML engineer with applied research depth in **computer vision, 3D point-cloud detection, and multimodal sensor fusion**. Trained and deployed CNN models on AWS for NYC infrastructure inspection and traffic monitoring; comfortable owning the full loop from raw multi-sensor data → labeled datasets → model → cloud / edge deployment.

## Core skills

**Models & methods**
2D & 3D CNNs (object detection, segmentation), contrastive learning, multimodal fusion (LiDAR + RGB + thermal / hyperspectral), background subtraction and tracking, classical computer vision (OpenCV), control-theoretic models (PID, fractional-order) for closed-loop CV systems.

**ML platforms & infrastructure**
PyTorch, TensorFlow, CUDA, **AWS** (S3 for data, EC2/SageMaker for training, model hosting), Docker, NVIDIA Jetson (Nano / TX2 / Xavier) for **edge inference**, WebODM-based deployment platform for end-user delivery.

**Data & pipelines**
End-to-end ingestion from real-world sensors (fixed LiDAR + camera, drone payloads, robotic platforms), dataset versioning, format conversion across sensor configurations, ROS / MCAP / Protobuf, labeling and quality workflows, training-on-A → inference-on-B portability.

**Languages**
Python (primary), C++, MATLAB, Fortran.

## Selected ML projects

### CNN-Based 3D Detection on Highway LiDAR · 2024–present
*AI & Mobility Research Lab, CCNY · NYC DOT collaboration*

- Evaluating and tuning CNN-based 3D object detectors on fixed-LiDAR highway data covering vehicles, motorcycles, bicycles, and pedestrians.
- Built a **configuration-portable pipeline**: train on one dataset, infer on another with different sensor parameters — handling beam count, mounting geometry, and timing differences.
- Multi-frame point cloud reconstruction to densify per-vehicle representations for downstream classification.
- Co-authored MobiSPC 2025 papers on (a) **how many LiDAR beams are enough** for vulnerable road user detection, and (b) a survey of sensing perspectives for VRU monitoring.

### Bridge Defect Detection & Cloud Deployment · 2022–present
*CCNY Robotics Lab*

- Trained CNNs for **crack / spalling / stain detection** on robot-collected imagery; pushed models to **AWS for scalable inspection**.
- Built a custom **WebODM-based platform** integrating automated segmentation, 3D reconstruction, interactive visualization, and crack measurement.
- Selected for IEEE IROS 2025 presentation (Feng, Shang, et al., *IEEE T-ASE*, 2025).

### Contrastive Learning for Robust Defect Mapping · 2024
- Contrastive learning approach for impact-echo defect mapping on concrete slabs, robust across acquisition conditions. (Hoxha, Feng, …, Shang, et al., 2024.)

### Vision-Based Robotic Control · 2015–2022
- **Drone visual servoing** with fractional-order controllers — closed-loop computer vision at the edge (Raspberry Pi / embedded Linux), demonstrating control under longer-than-typical sampling periods.
- **Girder detection on NVIDIA Jetson** as part of the BIRDS bridge-inspection drone.
- **SmartCaveDrone** — sense-and-avoid + GPS-denied navigation using onboard vision in unstructured environments.

### Earlier signal-processing and CV work · 2010–2014
- Visual reconnaissance path planning algorithms; object tracking quadrotor on ROS + AR.Drone; data/image transmission systems (patented).

## Education

- **PhD, Civil Engineering (Transportation)** — CCNY, NY, USA · 2025–present
- **PhD, Pattern Recognition and Intelligent Systems** — Northeastern University, China · 2013–2020
- **Exchange PhD** — UC Merced · 2015–2017
- **MEng, Pattern Recognition and Intelligent Systems** — Northeastern University, China · 2011–2013
- **BEng, Automation** — Northeastern University, China · 2007–2011

## Experience

- **2025–now** — Postdoctoral Scholar, AI & Mobility Research Lab, CUNY City College
- **Dec 2022–Dec 2024** — Postdoctoral Researcher, CCNY Robotics Lab
- **Jan 2020–Nov 2022** — Postdoctoral Fellow, Missouri University of Science and Technology
- **Jun–Aug 2024** — Instructor, Computer Engineering Summer Academy (AI module), Vaughn College
- **2023–2024** — Adjunct, Vaughn College (Principles of AI, Robotics Mechanics & Control)
- **2015–2017** — Lecturer / Junior Specialist, UC Merced

## Teaching (ML / AI relevant)

- *Principles of AI* (Vaughn College, SBC 012)
- *Principles of Research — AI* (Vaughn College, SBC 014A)
- *Robotics, Mechanics and Control* (Vaughn College, MCE 355)

## Selected publications

1. Bo Shang et al. *Sensing Perspectives on Vulnerable Road User Monitoring for Traffic Safety: A Survey.* MobiSPC 2025.
2. Bo Shang et al. *How Many Beams of LiDAR is Enough for Detecting Vulnerable Road Users?* MobiSPC 2025.
3. Jinglun Feng, Bo Shang et al. *Robotic Inspection and Data Analytics to Localize and Visualize the Structural Defects of Concrete Infrastructure.* IEEE T-ASE 2025. *Selected for IROS 2025.*
4. Hoxha, Feng, …, **Shang**, et al. *Contrastive Learning for Robust Defect Mapping in Concrete Slabs using Impact Echo.* 2024.
5. Zhang et al. *Code-specified early delamination detection and quantification in a RC bridge deck.* 2025.

Full list on the [Publications page](/publications/) and [Google Scholar](https://scholar.google.com/citations?user=TVIPpDMAAAAJ&hl=en).

## Reviewer service (ML / robotics venues)

IEEE T-CST, ICRA, IROS, ICUAS, IEEE MFI, J. of Intelligent & Robotic Systems, Mechatronics, Control Engineering Practice, Nonlinear Dynamics, ISA Transactions, IET Control Theory & Applications, IJARS.

## Why this role fits

I bring an **applied ML profile shaped by real sensor hardware**: I've trained the model, debugged the calibration that made the dataset trustworthy, deployed it to AWS or to a Jetson on a robot, and shipped the result to a city agency. If you want an ML engineer who is comfortable upstream and downstream of `model.fit()`, that's me.

---

*Looking for the [Robotics SWE view](/cv/robotics/), the [full academic CV](/cv/), or [all resumes](/resumes/)?*
