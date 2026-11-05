# Repository backup and publishing contract

- These repositories are private source snapshots. Live workspaces stay in place.
- Updates and pushes happen only when the operator explicitly asks. No timer,
  Git hook, background sync, scheduled workflow or automatic push is installed.
- Export the requested group, run its checks and the secret scan, inspect changes,
  commit locally with `Codex: <change>` (or actual identity), then push only when
  that request includes uploading/updating GitHub.
- Never export credentials, account/cookie databases, private conversations, live
  paper books, saves, virtual environments, models, caches or proprietary binaries.
- Source ownership and shared integration copies are recorded in repos.json and
  each SOURCE_MANIFEST.json. An updated shared source may affect several groups.
- Third-party tools remain upstream dependencies with attribution. Do not claim
  them as our work or silently change their licenses.
