# R2D2 workspace catalogue

Start here to find the source repositories, their purpose, setup instructions and
manual update process. The full list is [REPOSITORIES.md](REPOSITORIES.md).

## What was saved

Ten grouped source repositories: trading/investing, agent workflow and memory,
browser research, knowledge tools, agent skills, Wi-Fi, Linux maintenance,
indicator research, productivity connectors, and this catalogue. Each has a simple
README, source manifest and read-only checks. Unfinished game, sound, wellness and
business-web projects were explicitly deferred and are not uploaded.

## Boundaries

The trading dashboard and bot runtime stay together because they are one integrated
application. Agent, browser and knowledge repos expose independently usable helpers.
Trading keeps integration copies of shared helpers to make its snapshot complete;
SOURCE_MANIFEST.json maps those copies back to their source. Use separate Python
environments. Optional external providers, accounts, hardware, browsers and data
feeds still require configuration; passing offline tests does not authenticate them.

The original local workspaces remain authoritative working copies. These repositories
are sanitized exports, not renamed/moved live applications and not a full machine image.
Generated market caches, private memory/chat, live paper books, account credentials,
cookies, models, environments, game saves and proprietary binaries stay local.
Private-history notes, account screenshots and rendered reports are excluded.

## Privacy and future public release

Initial visibility is private. Sanitization removes literal IP addresses, personal
contact details, chat identifiers and source-host paths; settings use configurable
workspace paths and hostnames. Upstream license notices remain intact. Source and
privacy checks are stored with the creation report. No original Git history is
uploaded: each export starts with a clean sanitized history and generic commit identity.
GitHub's account/repository URLs are intentional public identifiers, not credentials.

Do not switch visibility automatically. Before any later public release, review the
then-current staged diff and third-party licenses and rerun the privacy checks.

## On-demand updates only

Nothing runs automatically. There are no sync timers, commit hooks, scheduled GitHub
workflows or automatic pushes. See [UPDATE_ON_DEMAND.md](UPDATE_ON_DEMAND.md).
The export command does not contact GitHub. Publishing requires a separate explicit
--publish flag and repo selection; it refuses public targets.

## Contents

- repos.json: active groups and deferred categories.
- REPOSITORIES.md: full linked list and purpose.
- CREATION_REPORT.md: when/how each repo was created and what was verified.
- SOURCE_MANIFEST.json in each source repo: file provenance and exported hashes.
- export.py / sanitize.py: explicit source export and cleanup.
- secret_scan.py / privacy_scan.py: checks that print locations, never private values.
- publish.py: manual private creation/update and uploaded-commit verification.
