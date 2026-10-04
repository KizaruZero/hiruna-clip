# Hiruna Clip

AI-assisted long-form video clipping and repackaging pipeline.

## Vision

Turn a long-form video source, initially YouTube, into a set of high-quality short-form clip plans and eventually rendered vertical videos.

The core design separates **intelligence** from **heavy media processing**:

- **Muse / AI Agent = Brain / Clip Director**
- **PC = Worker / Renderer**

Muse analyzes the content, finds promising moments, determines clip boundaries, scores candidates, and produces a machine-readable **Clip Manifest**.

The PC consumes that manifest and performs deterministic, resource-heavy work such as downloading the best source, cutting, cropping, captioning, and encoding.

## Current Stage

This repository starts as a **workflow and specification-first project**.

The first milestone is to validate that AI can reliably select good moments from long-form content using transcript + audio signals without requiring computer vision.

See `docs/PROJECT_CONTEXT.md` for the current source of truth.
