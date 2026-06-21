# Project 04: Kubernetes Resource Management for ML Inference

## Overview

This project demonstrates best practices for running ML inference workloads on Kubernetes, focusing on proper resource management, fairness, and predictability.

## Key Topics Covered
- ResourceQuotas for CPU, memory, and GPUs
- LimitRanges for default and boundary enforcement
- Quality of Service (QoS) classes for inference pods
- Right-sizing inference pods using measurement
- Vertical Pod Autoscaler (VPA) recommendations
- Pod Disruption Budgets

## Why It Matters
Inference workloads have unique characteristics (bursty CPU, predictable memory, slow startup). Proper configuration prevents OOM kills, ensures fairness, and improves reliability.

## Author
Sudipto Saha — AI Platform Engineering Portfolio