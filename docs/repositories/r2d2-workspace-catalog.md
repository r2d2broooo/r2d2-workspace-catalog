# R2D2 Workspace Catalogue

The starting point for the public R2D2 source repositories: what each one does, how the parts relate, how they were prepared and how to update them deliberately. This repository contains documentation and maintenance scripts, not a second copy of every application or a store of private runtime data.

See [REPOSITORIES.md](REPOSITORIES.md) for the complete linked list and [PUBLIC_RELEASE.md](PUBLIC_RELEASE.md) for release checks and visibility verification.

## Current publication status

Nine source repositories are public. The clean trading-source replacement is
pending GitHub's temporary repository-creation block. Its detailed README is
available in docs/repositories/; the earlier export is retained privately. No
automatic retry or visibility change is scheduled. See publication-verification.json.

## Repository groups

| Group | Role |
|---|---|
| Trading system | Integrated market-data, dashboard, research, Strategy Lab and paper runtime |
| Agent workflow | Independent sessions, requested team discussion, memory, usage and provenance |
| Browser research | CDP automation, static extraction, captions and capture helpers |
| Knowledge tools | Document extraction, Markdown wiki bookkeeping and Python source graph |
| Agent skills | Locally used recipes, references and examples with mixed upstream provenance |
| Wi-Fi guard | NetworkManager watchdog and optional local interface/notifications |
| Linux system tools | Backup/checkpoint, workstation setup, inspection and launcher helpers |
| Indicator research | Standalone Pine prototype and technical study |
| Productivity connectors | Explicit SMTP and Google Tasks account actions |
| This catalogue | Source mapping, documentation, checks and manual release/update tools |

Four unfinished project categories were excluded at the operator's request. Their application folders are not part of this release.

## Architecture and source ownership

The trading dashboard and shared runtime are one integrated application, so their source stays together. Reusable helper repositories can be explored separately and document their own prerequisites. The trading integration retains compatible copies of some helpers; these are intentional integration snapshots, not automatically linked installations.

`repos.json` records the groups. Each source repo's `SOURCE_MANIFEST.json` records source/export file hashes and sanitized provenance. The original local workspaces remain the development sources. No running application was moved or pointed at the public exports.

## Manual updates

`export.py` requires an explicit repository selection and does not contact GitHub. `sanitize.py`, `secret_scan.py` and `privacy_scan.py` prepare/check export copies. `publish.py` requires an explicit publishing flag, checks the selected target and verifies the remote commit. It never changes repository visibility as a side effect of a normal update.

There are no scheduled publishing jobs, automatic pushes or sync hooks. Read [UPDATE_ON_DEMAND.md](UPDATE_ON_DEMAND.md) before updating an export; changes to a shared helper may require updating both its toolkit and its trading integration copy.

## Public release and privacy

The public source omits credentials, browser sessions, private conversations/memory, personal contacts, configured network addresses, live books, investment notes, watchlists, captures, caches, model blobs and proprietary application binaries. The provided watchlist is empty and examples use hostnames or configurable paths. Existing upstream copyright/license notices are retained; the GitHub owner/repository URLs are intentional public identifiers.

Release checks cover committed text/history, source metadata and selected offline behavior. They cannot authenticate your accounts or configure your hardware. Review any future diff and newly generated output before publishing an update.

## Further reading

- [CREATION_REPORT.md](CREATION_REPORT.md): initial grouping and backup preparation.
- [VERIFICATION.md](VERIFICATION.md): exercised checks and their limits.
- [DEPENDENCIES.md](DEPENDENCIES.md): software/services that remain external.
- [PUBLIC_RELEASE.md](PUBLIC_RELEASE.md): public visibility and pre-release review.
- [UPDATE_ON_DEMAND.md](UPDATE_ON_DEMAND.md): the explicit update process.
