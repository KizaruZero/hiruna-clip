# Workflow Specification

## 1. Purpose
V1 execution contract: YouTube URL -> Discovery -> Candidate Manifest -> Human Selection -> PC Rendering.

Core rule: AI decides. Deterministic code executes.

Muse is the Clip Director. The PC is the Worker/Renderer.

## 2. Input
Required: YouTube URL.

Discovery must obtain source title, duration, usable transcript, and audio.

## 3. Discovery

### 3.1 Metadata
Collect source URL, title, duration, transcript availability, and practical media information.

### 3.2 Transcript
Produce a cleaned, timestamp-preserving transcript artifact.

Rules:
- preserve cue timestamps;
- remove duplicated/overlapping auto-caption text;
- preserve semantic wording;
- never flatten into timestamp-less text;
- use HH:MM:SS timestamps, with optional milliseconds.

Contract: docs/schemas/transcript.schema.json.

### 3.3 Audio
Analyze audio from the beginning using deterministic signals such as:
- energy spikes;
- volume peaks;
- silence breaks;
- high-energy regions;
- low-energy regions.

Audio events are evidence, not decisions.

Contract: docs/schemas/audio-events.schema.json.

## 4. Candidate Detection
Muse combines transcript and audio evidence to identify potential moments.

Signals include hook, reveal, surprise, emotion, humor, conflict/tension, rarity, value, reaction, curiosity, and audio energy.

Keywords are clues only and must never be the sole basis for selection.

## 5. Context Expansion
A detected event is not automatically a final clip.

For each strong candidate, inspect surrounding context to find setup, event/reveal, and reaction/payoff.

Story completeness has priority over rigid duration targets.

## 6. Boundary Selection
Preferred duration: 20-60 seconds.
Allowed duration: 15-90 seconds.

These are guidance, not hard clipping rules. A shorter complete moment is preferred over padding; a longer clip is acceptable when required for setup/payoff.

## 7. Scoring
Each candidate receives:
- score: 0-100;
- confidence: 0-1;
- signal breakdown.

Required signals:
hook, surprise, emotion, humor, tension, rarity, value, reaction, audio_energy, self_contained.

Self-contained comprehension is especially important. A viewer who never saw the source should still understand why the clip matters.

Exact weighting may evolve during V1 evaluation and is not a public API contract.

## 8. Deduplication
Candidates representing substantially the same event must be grouped.

When windows overlap heavily and represent the same moment, retain the strongest candidate and avoid near-identical outputs.

## 9. Candidate Output Policy
Return candidates with score >= 70, maximum 15 clips.

Fewer than 15 is valid. Never manufacture candidates to fill the quota.

## 10. Clip Manifest
The Clip Manifest is the contract between Muse and the renderer.

Contract: docs/schemas/clip-manifest.schema.json.

It contains source metadata, clip IDs, timestamps, duration, title, score, confidence, signal breakdown, reason, setup/event/payoff story, and relevant audio events.

The manifest is an analysis artifact, not a render-command language. Muse must not generate FFmpeg commands, codec settings, shell commands, or renderer implementation details inside it.

## 11. Human Review Gate
Rendering is explicitly human-controlled:
1. Muse produces manifest.
2. User reviews candidates.
3. User selects clip IDs.
4. PC renderer processes only selected clips.

Muse must not automatically render all candidates in V1.

## 12. Media Acquisition
Analysis and final rendering are separate.

Discovery may use the lightest practical source needed for transcript/audio analysis. After selection, the PC renderer obtains the best practical source quality available.

V1 may download the source once locally before cutting selected ranges. Range/network optimization is deferred.

## 13. Rendering
The PC renderer owns source acquisition, cutting, 9:16 crop, caption preparation/burning, encoding, output naming, and validation.

The renderer converts human-readable timestamps internally.

The renderer must not ask an LLM to generate FFmpeg commands.

## 14. QA
Validate:
- manifest schema;
- timestamp ordering;
- duration consistency;
- selected range exists;
- output is decodable;
- output is vertical 9:16;
- captions remain in safe area when enabled.

Subject-aware crop is out of scope for V1; center crop is acceptable initially.

## 15. V1 Non-Goals
Advanced computer vision, face/speaker tracking, intelligent subject-aware crop, game/UI recognition, automatic publishing, distributed/cloud GPU rendering, complex motion graphics, automatic render approval, and full web UI.

## 16. Reference Flow
YouTube URL
 -> Muse metadata/transcript/audio
 -> candidate detection
 -> context expansion
 -> boundary selection
 -> scoring
 -> deduplication
 -> ranking
 -> Rich Clip Manifest
 -> HUMAN REVIEW
 -> selected clip IDs
 -> PC Renderer
 -> Final MP4
