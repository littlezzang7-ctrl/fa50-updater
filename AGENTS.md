# AGENTS.md (Workspace Rules)

This file defines mandatory working rules for Codex in this workspace.
이 파일은 이 워크스페이스에서 Codex가 반드시 따라야 할 작업 규칙입니다.

## 1) Versioning (Mandatory)
- Every code change must create a **new file** with a version increment of exactly `+0.0.01`.
- Never overwrite the latest versioned file.
- Use the latest existing version file as the source for the next version.
- If version order is missing/duplicated, stop and fix version continuity first.

## 2) Update Log (Single Source, Mandatory)
- Maintain one append-only log file for all updates: `CHANGELOG_FA50.md`.
- At the very top of `CHANGELOG_FA50.md`, keep an **Update Notes** summary section.
  - One line (or up to two lines) per version.
  - Each note line must include: **version, date, time (KST)**.
  - Format example: `v0.5.01 | 2026-03-02 14:35 KST | Fixed level recovery overshoot; improved bank auto-adjust stability.`
- For every update, append one entry with both Korean and English.
- Each entry must include:
  - Date/time (KST)
  - Request summary
  - Changed files
  - What logic/code changed (function-level where possible)
  - Verification performed and results
  - Remaining risks / known limitations

## 3) Verification Gate (Mandatory)
- For any calculation/physics/logic change, run at least **20 validation cases** before completion.
- If any critical validation fails, do not finalize the version as done.
- Record validation scope and pass/fail details in `CHANGELOG_FA50.md`.

## 4) Regression Baseline (Always run)
- Include at least these checks each time:
  - Straight + G input => bank auto-zero behavior
  - Pull up / Pull down / Level mutual exclusivity
  - Level recovery with G limit (<= 4g when level logic is active)
  - Bank range bounds (0~180)
  - Pitch display fold behavior for loop ranges
  - Random stress simulation (minimum 200 steps; recommended 600)

## 5) UI/Physics Consistency
- If UI display value and internal simulation value differ, document both.
- For physically infeasible inputs, clamp or compensate and explain the reason in logs.

## 6) Safety / Collaboration
- Never revert unrelated user changes without explicit request.
- If unexpected external changes are detected during work, stop and ask the user before proceeding.
- Prefer deterministic fixes over ad-hoc tweaks; preserve existing behavior unless explicitly requested.

## 7) Delivery Format
- Final response must include:
  - New versioned filename
  - What changed (concise)
  - What was verified (with counts)
  - Path to the updated changelog entry

## 8) Release Automation (Mandatory)
- Use `release_auto.cmd` as the default release path.
- Do not manually pick the next version for release when `release_auto.cmd` is available.
- `release_auto.cmd` must determine the latest `fa50_X.Y.Z.py` and increment only patch by `+0.0.01`.
- The script must sync `APP_VERSION`, append update-note lines to `CHANGELOG_FA50.md`, commit, push `main`, create tag `vX.Y.Z`, and push the tag.
- Keep required runtime assets tracked in repo for CI build:
  - `fa50_psdb_0p1_strict2_v0.npz`
  - `FA50_GUIDEBOOK.md`
  - `1.jpg`
