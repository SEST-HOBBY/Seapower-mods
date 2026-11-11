# Branches

Since 11 November 2026 the repository keeps three long-lived branches.

| Branch | What it holds | How it moves |
|---|---|---|
| `dev` | Development. Every change lands here first, by pull request from a short-lived `feature/`, `fix/` or `chore/` branch. | Pull requests into `dev`. The release gates run on each one. |
| `beta` | What the owner installs on the gaming PC, tests and posts to the Steam Workshop. `data/deploy-branch.txt` names it, so `tools/sync-sest.ps1` installs from it, and the PC toolkit (`tools/build_pc_toolkit.py`) is built from it. | A pull request from `dev` when a build is ready for the PC check. |
| `steam` | What is live on the Workshop (item 3812461539). | Moved to `beta`'s commit after each upload. It started at `0776fa50`, the content of the 26 Oct 2026 upload. |

The flow is `feature` → `dev` → `beta` (PC check and Workshop upload) → `steam`.

Short-lived branches are deleted once merged. Older branches that held work
never merged were kept as tags named `archive/<branch>`, so nothing was
lost. The branch for the beta runtime R13 (`feature/runtime-mission-awards-20261110`)
stays until R13 is merged into `dev`.

On GitHub, the default branch should be `dev`, so new pull requests target
it, and "Automatically delete head branches" should be on.

Moving `steam` after an upload, from a clone with push access:

```
git fetch origin
git push origin origin/beta:refs/heads/steam
```

Reports, reviews and release notes written before 11 November 2026 name the
branches of that time (`sest-dev/jolly-ride-rptj4t` was the deploy branch).
They are records and are not rewritten.
