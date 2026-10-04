# Product Requirements Document

## Status

Draft — derived from the current project context.

## 1. Product

Hiruna Clip is an AI-assisted long-form video clipping pipeline. The initial product accepts a YouTube URL, discovers valuable moments, creates a structured clip plan, and delegates deterministic rendering to the user's PC.

## 2. Primary User Goal

Given a long-form video, the user should be able to obtain a small set of strong short-form clip candidates without manually watching the entire video.

The user should then be able to render those selected candidates locally at useful vertical-video quality.

## 3. V1 Goals

- Analyze long-form YouTube content.
- Extract or obtain a usable transcript when possible.
- Use transcript semantics to discover candidate moments.
- Use lightweight audio signals as a complementary signal.
- Expand candidate points into complete clip boundaries.
- Score and rank candidate clips.
- Produce a human-readable Clip Manifest in JSON.
- Allow the local PC renderer to consume the manifest.
- Download a suitable high-quality source for final rendering.
- Cut clips and produce 9:16 vertical output.
- Generate and burn simple captions.
- Produce one MP4 per selected clip.

## 4. V1 Non-Goals

- Advanced computer vision.
- Face or speaker tracking.
- Game-specific visual recognition.
- Fully automatic publishing to social networks.
- Cloud GPU rendering.
- A large web application.
- Distributed rendering.
- Complex motion graphics.
- Multi-model optimization and automatic provider routing beyond a simple working integration.

## 5. User Flow

1. User provides a YouTube URL.
2. Muse obtains source metadata.
3. Muse obtains transcript when available.
4. Muse gathers lightweight audio evidence when useful.
5. Muse identifies candidate moments.
6. Muse checks surrounding context and determines boundaries.
7. Muse ranks the candidates.
8. Muse outputs a Clip Manifest.
9. User reviews/selects clips.
10. PC renderer consumes the manifest.
11. Renderer obtains the best practical source.
12. Renderer cuts, crops, captions, and encodes.
13. Final MP4 clips are stored locally.

## 6. Functional Requirements

### FR-001 — Source Input

The system shall accept a valid YouTube URL as the initial source input.

### FR-002 — Metadata

The discovery stage shall obtain available source metadata including title and duration.

### FR-003 — Transcript Acquisition

The discovery stage shall attempt to obtain a usable transcript from available subtitles or speech-to-text tooling.

### FR-004 — Transcript Cleanup

Rolling or overlapping subtitle cues shall be normalized into usable text/timestamp data before semantic analysis.

### FR-005 — Candidate Discovery

The AI shall identify moments with strong short-form potential using signals such as hook strength, surprise, emotion, humor, conflict, rarity, value, reaction, and self-contained payoff.

### FR-006 — Context Expansion

The system shall inspect context before and after a candidate event to avoid clips that begin too late or end before the payoff.

### FR-007 — Clip Scoring

Each selected candidate shall receive a normalized score and a concise reason.

### FR-008 — Clip Manifest

The analysis stage shall output JSON containing source metadata and clip definitions.

Each clip shall include at minimum:

- id
- start
- end
- duration
- title
- score
- reason

Timestamps shall use human-readable HH:MM:SS format.

### FR-009 — Renderer Input

The PC renderer shall accept a Clip Manifest without requiring the AI agent to render the final video.

### FR-010 — Source Acquisition

The renderer shall obtain a suitable source quality for production rendering and should minimize unnecessary media transfer where practical.

### FR-011 — Clip Cutting

The renderer shall cut each requested interval accurately.

### FR-012 — Vertical Conversion

The renderer shall produce 9:16 output. A simple center crop is acceptable for V1.

### FR-013 — Captions

The renderer shall generate captions from available transcript data and burn them into the output using a readable style.

### FR-014 — Output

The renderer shall produce one MP4 file for each rendered clip.

### FR-015 — Validation

The renderer shall fail clearly when source media, manifest fields, timestamps, subtitle data, or encoding steps are invalid.

## 7. Non-Functional Requirements

### NFR-001 — Deterministic Rendering

Given the same source, manifest, renderer version, and configuration, rendering should be reproducible.

### NFR-002 — Resource Separation

Heavy media processing should occur on the user's PC rather than the agent VM.

### NFR-003 — Low Infrastructure Complexity

The first implementation should not require a dedicated GPU server.

### NFR-004 — Provider Independence

The agent layer should not be tightly coupled to one LLM provider.

### NFR-005 — Human Reviewability

The Clip Manifest must remain understandable and editable by a human.

### NFR-006 — Extensibility

The manifest and renderer interfaces should allow future additions without breaking the basic workflow.

## 8. Acceptance Criteria for V1

V1 is considered successful when:

1. A YouTube URL can be analyzed.
2. The system produces multiple candidate clips from a long-form video.
3. Selected clips have sensible boundaries that include the relevant setup and payoff.
4. The Clip Manifest is valid JSON and uses human-readable timestamps.
5. The PC renderer can consume the manifest without manual timestamp rewriting.
6. The renderer produces valid 9:16 MP4 files.
7. Captions are readable and approximately synchronized.
8. The workflow does not require the agent VM to perform final heavy rendering.

## 9. Quality Benchmark

The primary benchmark is not merely whether the pipeline runs.

The primary benchmark is:

> Do the selected clips consistently feel like moments a human would actually want to publish as short-form content?

Technical correctness is necessary, but selection quality is the core product metric for the first milestone.

## 10. Roadmap

V0: selection validation.

V1: deterministic local renderer.

V1.5: stronger audio signals.

V2: messaging automation, reusable styles, and workflow automation.

V3: advanced visual intelligence and intelligent reframing.
