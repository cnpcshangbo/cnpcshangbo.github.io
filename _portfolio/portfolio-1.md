---
title: "Highway LiDAR + Camera Synchronization Pipeline"
excerpt: "End-to-end multi-sensor capture, temporal/spatial alignment, and CNN-based 3D detection for fixed roadside LiDAR + camera at NYC highway sites.<br/>**Stack:** Python · PyTorch · ROS · OpenCV · LiDAR SDKs · calibration toolchains"
collection: portfolio
---

## What it does

A production-direction pipeline for **fixed roadside LiDAR + camera** deployed at New York City highway sites. The system handles the full loop:

1. **Multi-sensor capture** of LiDAR sweeps and RGB camera streams.
2. **Temporal synchronization** between LiDAR and camera clocks (timestamp alignment, drift correction).
3. **Spatial calibration** of LiDAR ↔ camera extrinsics for 2D–3D fusion.
4. **Background subtraction + segmentation** on synchronized frames.
5. **CNN-based 3D detection** classifying vehicles, motorcycles, bicycles, and pedestrians (vulnerable road users).
6. **Multi-frame vehicle reconstruction** that stitches successive sweeps into per-vehicle point cloud models.

## Why synchronization is the hard part

If LiDAR and camera disagree by even tens of milliseconds, point projection drifts, multi-frame reconstruction smears, and downstream detector quality collapses. A lot of the engineering is the **unglamorous time-sync / calibration layer** that everything else relies on.

## Configuration portability

I built the pipeline so models trained on one site's sensor configuration can be redeployed on another — different beam counts, different mounting geometries, different frame rates — without rewriting the inference path.

## Outputs

- Two MobiSPC 2025 papers (sensing perspectives survey + LiDAR beam-count study for VRU detection).
- Field-deployed pipeline supporting NYC DOT collaboration through the AI & Mobility Research Lab at CCNY.

[← Back to portfolio](/portfolio/) · [Robotics SWE CV](/cv/robotics/) · [ML CV](/cv/ml/)
