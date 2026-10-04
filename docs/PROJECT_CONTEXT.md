# Hiruna Clip — Project Context

> **Status:** Draft v1  
> **Purpose:** This document is the primary context/source of truth for AI agents working on Hiruna Clip.

---

## 1. Project Overview

**Hiruna Clip** is a personal AI-assisted video clipping and repackaging system.

The goal is to replace dependence on third-party clipping/downloader websites with a workflow that is controlled by the user, is extensible, avoids unnecessary platform limitations, and can use the user's own computing resources.

The initial target workflow is:

```
YouTube URL
    ↓
AI analysis
    ↓
Find valuable moments
    ↓
Determine exact clip boundaries
    ↓
Clip Manifest (JSON)
    ↓
PC renderer
    ↓
Vertical short-form MP4
```

The project is intentionally designed so that **AI reasoning and heavy video processing are separate concerns**.

---

## 2. Problem

Existing online tools can provide useful functions such as:

- social media downloaders
- story viewers
- YouTube download/conversion tools
- AI clipping tools
- captioning tools

However, third-party tools may impose limitations such as:

- advertisements
- premium-only features
- download quality limitations
- watermarks
- rate limits
- unavailable or unreliable processing
- lack of control over the workflow
- vendor lock-in

Hiruna Clip exists to build the user's own pipeline instead of depending on those services for the complete workflow.

---

## 3. Product Vision

The long-term vision is:

> Give the user a single input, such as a YouTube URL, and automatically produce a curated set of short-form clips that are actually worth watching and ready for platforms such as TikTok, Instagram Reels, and YouTube Shorts.

The system should eventually support more than clipping:

- caption styling
- vertical reframing
- hook generation
- title generation
- multiple clip variants
- platform-specific exports
- automated delivery through messaging
- additional media utility tools

The initial project must **not** attempt to build all of these at once.

---

## 4. Current V1 Philosophy

V1 should optimize for:

1. **Selection quality**
2. **Correct clip boundaries**
3. **Simple, reliable rendering**
4. **Low infrastructure complexity**
5. **Low unnecessary model/token usage**

V1 should avoid premature complexity.

### Explicitly out of scope for the first implementation

- advanced computer vision
- face detection/tracking
- speaker tracking
- game-specific recognition
- automatic zoom tracking
- sophisticated motion graphics
- full web application UI
- distributed rendering infrastructure
- cloud GPU rendering
- multi-model optimization/fallback logic
- fully autonomous publishing

These can be considered later after the core workflow proves reliable.

---

## 5. Core Architecture

### 5.1 Muse / AI Agent — Brain

Muse is the intelligent orchestration layer.

Responsibilities:

- receive or identify the source URL
- obtain metadata
- obtain transcript when available
- obtain/analyze audio signals when useful
- inspect transcript/content
- identify candidate moments
- assess whether a moment has short-form potential
- determine a complete clip window
- score and rank clips
- generate a human-readable title
- explain the reason for selection
- output a Clip Manifest

Muse should behave as a **Clip Director**, not as the rendering engine.

### 5.2 PC — Worker / Renderer

The user's PC is the heavy processing worker.

Responsibilities:

- consume Clip Manifest
- obtain the best available source quality
- download only the required media or otherwise minimize unnecessary transfer
- cut clips
- crop/reframe to 9:16
- generate/burn captions
- encode final MP4 files
- write outputs and render logs

The PC renderer should be as deterministic as possible.

It should not decide which moments are viral or semantically valuable. It executes the plan produced by Muse.

### 5.3 LLM / Model

The model is a component used by the agent; it is not the agent itself.

Possible model providers include Gemini, Claude, GPT, or another capable model.

9router may later be used to abstract providers and provide fallback or model switching.

The first implementation should prefer **one working provider/path** over premature multi-model orchestration.

---

## 6. Intelligence Pipeline

The initial discovery/analysis pipeline is:

```
Source URL
   ↓
Metadata
   ↓
Transcript
   ↓
Audio signals
   ↓
Candidate moments
   ↓
Context expansion
   ↓
Boundary selection
   ↓
Scoring/ranking
   ↓
Clip Manifest
```

### 6.1 Transcript

Transcript is the primary semantic signal.

It can reveal:

- statements
- punchlines
- surprising information
- rare facts
- arguments
- reactions
- numbers and prices
- story reveals
- humorous exchanges
- strong hooks

Transcript alone is not sufficient for all content types.

### 6.2 Audio

Audio is a secondary signal used to catch moments that text may not fully represent.

Potential signals:

- sudden volume spike
- scream
- laughter
- excited voice
- abrupt silence followed by reaction
- sustained high-energy section
- unusual audio transition

Audio analysis is especially useful for gaming, reaction, entertainment, and horror-like content.

### 6.3 Visual Analysis

Visual analysis is deliberately deferred.

It may become useful later for:

- face tracking
- speaker framing
- gameplay event recognition
- object detection
- scene-change analysis
- intelligent crop positioning

Do not add this complexity to V1 unless real testing shows transcript + audio is insufficient.

---

## 7. Candidate Moment vs Final Clip Boundary

The system must distinguish between:

**Candidate event** — the point that looks interesting.

and

**Final clip boundary** — the complete segment that should actually be exported.

For example:

```
Candidate event:
01:23:40

Useful context:
01:23:27 → 01:24:04
```

A good clip should generally contain:

```
setup → build-up → event → reaction/payoff
```

rather than starting exactly at the strongest reaction.

The AI should therefore inspect context around a candidate before finalizing boundaries.

---

## 8. Clip Selection Principles

Clip selection should prioritize short-form value, not merely random interesting sentences.

Useful signals include:

1. Strong hook
2. Surprise / unexpected information
3. Emotional intensity
4. Humor
5. Conflict or tension
6. Rarity
7. High monetary/value significance
8. Strong reaction
9. Self-contained story/payoff
10. Curiosity gap

A clip should preferably make sense without requiring the viewer to watch the entire source video.

The AI should avoid:

- long setup with no payoff
- repetitive conversation
- context-dependent fragments
- technically interesting but emotionally flat sections
- clips whose key point is cut off at the boundaries

---

## 9. Clip Manifest

The Clip Manifest is the contract between Muse and the PC renderer.

The production workflow should use **JSON instead of MP4 as Muse's main output**.

Muse may have an optional quick/prototype rendering mode, but the canonical output of the analysis stage is JSON.

Example:

```json
{
  "source": {
    "url": "https://youtube.com/...",
    "title": "Video title",
    "duration": "02:14:32"
  },
  "clips": [
    {
      "id": "clip_001",
      "start": "00:09:55",
      "end": "00:10:42",
      "duration": "00:00:47",
      "title": "Kartu 300jt - cuma 8 di dunia",
      "score": 94,
      "reason": "Extreme rarity + high monetary value"
    }
  ]
}
```

### Timestamp rule

Human-readable timestamps are preferred in manifests:

```
HH:MM:SS
```

Milliseconds may be added later when more precise synchronization is needed.

Raw frame numbers must not be used as the primary interface.

The renderer is responsible for converting timestamps into numeric seconds or FFmpeg-compatible values internally.

---

## 10. Token and Compute Strategy

A critical distinction:

- **LLM tokens** are mainly consumed by transcript/content passed to the model and by reasoning.
- **Video rendering does not consume LLM tokens.**
- Rendering primarily consumes CPU/GPU/RAM/storage/time.

Therefore:

### Muse should avoid

- echoing entire transcripts in final responses
- repeatedly sending the same transcript unnecessarily
- rendering full-quality final MP4s during normal analysis
- doing heavy encoding on the agent VM

### Muse should produce

- compact structured output
- selected timestamps
- concise titles
- concise reasons
- scores
- only the information the renderer needs

Long-form transcript processing can later be optimized with staged/chunked analysis.

---

## 11. Media Acquisition Strategy

The workflow should be split into two conceptual phases.

### Phase A — Discovery

Goal: understand the source and identify useful moments.

Preferred inputs:

- metadata
- transcript
- audio-derived signals
- lightweight source information

It should avoid downloading the highest-quality video source unless it is actually needed.

### Phase B — Production

After the clip boundaries are known:

- obtain the best practical source quality
- download only required media where feasible
- render the selected clips

A low-quality source used for analysis should **not** automatically become the final production source.

The final clips should be produced from the best available source that can reasonably be acquired.

---

## 12. Rendering Responsibilities

The initial renderer should support:

- timestamp-based cutting
- 9:16 vertical output
- simple center crop
- 720x1280 or comparable vertical output for early testing
- subtitle generation
- subtitle burn-in
- H.264 video
- AAC audio
- output file per clip

The existing proof-of-concept renderer established this basic approach with Python + FFmpeg.

### Important known prototype limitation

The current prototype's subtitle timing is approximate because subtitle events are distributed using text length instead of preserving the original VTT cue timings.

A production renderer should preserve the actual subtitle timestamps whenever possible.

### Crop limitation

The prototype uses a center crop.

This is acceptable for V1 but can later be replaced with intelligent reframing or face/speaker tracking.

---

## 13. Proof of Concept Findings

A real Muse experiment has already demonstrated that the basic approach is viable.

Observed workflow:

1. YouTube source acquired through `yt-dlp`
2. YouTube bot protection caused source-quality limitations
3. A lower-quality source was still sufficient for discovery
4. Indonesian YouTube auto-subtitles were available
5. Rolling/overlapping subtitles were cleaned and deduplicated
6. AI inspected the transcript and found a strong moment
7. The selected section was cut with FFmpeg
8. The video was cropped to 9:16
9. Captions were generated and burned in
10. A rendered frame was inspected for verification

The result was judged by the user to be **good and accurate enough to validate the workflow direction**.

This is strong evidence that the project should proceed from workflow validation into structured implementation rather than immediately adding advanced computer vision.

---

## 14. Example Proof-of-Concept Insight

One selected moment involved a card worth roughly 300 million with a claim that only 8 existed in the world.

The AI selected it because the combination of:

- high monetary value
- rarity
- surprising information

created strong short-form potential.

This illustrates the project's intended semantic selection behavior.

---

## 15. Infrastructure Philosophy

The project should avoid forcing heavy work onto the Muse VM.

Conceptually:

```
Muse VM
  = orchestration + reasoning + lightweight analysis

User PC
  = media worker + rendering
```

The system should remain usable even if the agent environment has modest CPU/RAM and no GPU.

The PC can be upgraded independently without redesigning the AI layer.

---

## 16. Desired End-to-End Workflow

The target V1 workflow is:

```
User
  │
  │ YouTube URL
  ▼
Muse / AI Agent
  │
  ├─ obtain metadata
  ├─ obtain transcript
  ├─ analyze audio signals
  ├─ identify candidate moments
  ├─ inspect context
  ├─ choose boundaries
  ├─ score/rank clips
  │
  ▼
Clip Manifest JSON
  │
  ▼
PC Renderer
  │
  ├─ download best source
  ├─ cut selected ranges
  ├─ crop 9:16
  ├─ generate subtitles
  ├─ burn captions
  └─ encode
  │
  ▼
Final MP4 Clips
```

---

## 17. Future QA Loop

A future version may introduce a feedback loop:

```
Muse generates manifest
        ↓
PC renders preview
        ↓
PC returns frame/preview
        ↓
Muse performs QA
        ↓
PC rerenders when necessary
```

Possible QA checks:

- caption readability
- caption timing
- crop correctness
- subject visibility
- awkward dead time
- incorrect boundary selection
- output duration
- encoding success

This is not required for V1.

---

## 18. Proposed Roadmap

### V0 — Selection Validation

Goal: prove that AI can consistently identify useful moments.

Output:

- top 5–10 candidate clips
- timestamps
- scores
- titles
- reasons

No final rendering required.

### V1 — Deterministic PC Renderer

Input:

- Clip Manifest

Output:

- MP4 clips

Features:

- best-source download
- cut
- 9:16 crop
- captions
- encode

### V1.5 — Better Signal Detection

Add:

- volume spikes
- scream detection
- laughter detection
- additional lightweight audio features

### V2 — Workflow Automation

Potential additions:

- Telegram integration
- WhatsApp integration
- automated manifest transfer
- status/progress notifications
- reusable caption styles

### V3 — Advanced Intelligence

Potential additions:

- visual analysis
- face/speaker tracking
- intelligent crop
- game-aware detection
- more sophisticated editing

---

## 19. Non-Negotiable Design Principles

1. **AI decides; deterministic code executes.**
2. **Do not use an LLM for deterministic tasks that code can perform reliably.**
3. **Do not render high-quality video on the agent VM unless there is a specific reason.**
4. **The Clip Manifest is the contract between analysis and rendering.**
5. **Use human-readable timestamps in the manifest.**
6. **Keep V1 simple enough to validate quickly.**
7. **Do not add computer vision until current signals are proven insufficient.**
8. **Prefer reusable local tools over dependence on third-party web tools.**
9. **Use the best available source for final rendering, even if discovery used a lower-quality source.**
10. **Every new feature should justify its complexity against measurable improvement in clip quality or workflow reliability.**

---

## 20. Current Decision

As of this context version, the project should proceed with:

> **Muse as the Clip Director + PC as the Renderer, connected through a structured Clip Manifest JSON.**

The immediate next design artifact should be:

```
PROJECT_CONTEXT.md
        ↓
WORKFLOW_SPEC.md
        ↓
PRD.md
        ↓
TECHNICAL_ARCHITECTURE.md
        ↓
AI_AGENT_INSTRUCTIONS.md
        ↓
Implementation
```

Do not start broad implementation before these contracts are sufficiently clear.
