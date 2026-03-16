# AGENTS.md

## Tooling Preferences

- Prefer the `uv` toolchain whenever it is a reasonable fit.
- Use `uv`, `uv run`, and the broader `uv` command ecosystem as much as possible for Python execution, dependency management, and ad hoc scripts.
- If a task can be done either with plain `python`/`pip` or with `uv`, prefer `uv`.

## YouTube Downloading

- When using `yt-dlp` against YouTube in this repo, prefer browser cookies from Chrome's default profile.
- First choice: `yt-dlp --cookies-from-browser chrome:Default ...`
- Use that cookie source for both test downloads and real source acquisition unless there is a clear reason not to.
