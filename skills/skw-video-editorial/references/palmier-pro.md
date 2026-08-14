# Palmier Pro workflow

Use the connected Palmier Pro MCP for media inspection, timeline construction, text, color, audio, and export.

## Operating order

1. Open or create the intended project.
2. Read the active timeline once and keep its returned state current after mutations.
3. Read media before referencing assets; inspect visual content rather than inferring from filenames.
4. Search source media for described actions, people, details, or spoken phrases.
5. Add selects by source seconds and place them by timeline frames.
6. Use layout operations for compositing; use text operations for authored lettering.
7. Detect music beats before beat-synchronous montage decisions.
8. Apply color and effects only after the narrative assembly is legible.
9. Inspect the final timeline and export a review version.

## Editorial translation

- Beat map → timeline ranges or markers.
- Shot plan → media searches and source trims.
- Rhythm map → clip durations and cut points.
- Audio map → music, production sound, linked audio, SFX, and silence.
- Lettering map → authored text clips, not generated video text.
- QC → timeline readback plus visual review export.

## Guardrails

- Do not generate media unless requested and confirmed; generation costs money.
- Do not describe footage from filenames.
- Use raw sources when the brief requires re-editable, unbranded material.
- Alternate projects and clients deliberately in a range montage.
- Preserve linked audio when it carries useful sync sound.
- Keep the user-visible project as the source of truth.
- Report unavailable or offline media instead of silently substituting it.
