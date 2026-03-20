# Katamari Damacy

`Katamari Damacy` is an OpenPeon sound pack built from clips from Katamari Damacy.

This repo now focuses on the deliverable pack itself:

- [`openpeon.json`](openpeon.json) manifest
- packaged notification audio in [`sounds/`](sounds)
- a local audition page in [`clip-preview.html`](clip-preview.html)
- a single rebuild script in [`scripts/build_pack.py`](scripts/build_pack.py)

## Build

Rebuild the shipped pack from the curated source clips with:

```bash
uv run python scripts/build_pack.py
```

That command:

- transcodes the selected `source_clips/curated/*.wav` keepers into `sounds/*.mp3`
- refreshes [`openpeon.json`](openpeon.json)
- regenerates [`clip-preview.html`](clip-preview.html)

The rebuild flow expects a local `source_clips/` tree that is intentionally not tracked in Git. If you only want to use or distribute the pack, the tracked deliverables are already present in this repository.

## Layout

- [`config/pack.json`](config/pack.json): pack metadata, curated selections, and category mapping
- [`scripts/build_pack.py`](scripts/build_pack.py): packaging script
- [`sounds/`](sounds): shipped pack assets
- `source_clips/`: local raw and curated source material, intentionally ignored by Git

## Notes

- The tracked deliverable is the OpenPeon pack, not the larger source library.
- Pack metadata is licensed as `CC-BY-NC-4.0`.
- Labels in the manifest are short descriptive names for the curated clips rather than full transcriptions.
