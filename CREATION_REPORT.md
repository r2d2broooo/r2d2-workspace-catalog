# Creation report — 5 November 2026

The operator requested grouped GitHub backups of the working system, with manual
updates only. The final scope is ten private repositories. Game-server tools,
sound studio, wellness prototype and the business website/artwork were deferred;
none of those folders was uploaded.

## How the repos were prepared

The original live workspaces were left in place. New export folders were built
from current source, preserving the coupled trading dashboard/runtime layout.
Reusable agent, browser and knowledge tools were exported separately, with
minimal export-only path/optional-integration adaptations and source manifests.
Each group received a simple README, feature list, setup/usage notes and checks.

The machine was authenticated to the operator's GitHub account with the GitHub
CLI device flow. No passwords, OAuth tokens or browser cookies were copied into
these repos. Fresh sanitized Git histories were used rather than uploading the
old histories. Commit identity is a generic project identity, not a private email.
Repositories were created private and each main branch was uploaded explicitly.
The publisher compares each local HEAD to the remote main commit and records
GitHub creation timestamps and privacy state in github-verification.json.

## Privacy exclusions

Credentials, cookies, private conversations/memory, live paper books, personal
investment wiki notes, caches, trained model blobs, virtual environments,
proprietary executables, private-history notes, screenshots and rendered reports
are excluded. Literal addresses, personal contacts/chat IDs and source-host paths
were removed from export text. Required upstream licenses/attribution stay intact.
The GitHub repository/account URLs are intentional identifiers for the requested
repo catalogue; they are not account credentials or private contact information.

## When and what each repo is for

See REPOSITORIES.md for the full linked list, repos.json for grouping, and
 github-verification.json for actual server-side creation times. See VERIFICATION.md
for test coverage and its limits, and UPDATE_ON_DEMAND.md for future changes.

No running application folder was moved or pointed at these exports. No automatic
sync, publishing timer, Git hook or scheduled upload workflow was added. The
original private state and four deferred project groups remain local.

## Public release — 5 November 2026

A later explicit operator request authorized public visibility and expanded documentation for the same ten groups. The public release has a separate text/history/metadata review, described in PUBLIC_RELEASE.md. The trading repository was recreated from its clean release history so superseded export objects are outside the public repository. Initial private-backup creation times in earlier records describe the earlier snapshot stage, not a public-release approval.
