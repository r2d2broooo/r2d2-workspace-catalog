# Public release — 5 November 2026

The operator explicitly requested public visibility and detailed explanations for
the ten source groups already in the catalogue. The four deferred application
categories remain excluded. No live workspace or private runtime store is moved.

## Documentation

Each README explains the problem it addresses, concrete modules/features, basic
setup/use, dependencies, data boundaries and limitations. GitHub descriptions are
expanded within the platform's length limit. Catalogue-owned README templates
preserve these guides during later explicit exports. Public access does not
relicense unrelated third-party material; existing notices are retained.

## Privacy checks

The release review scans current export text and every reachable Git-history
snapshot for secret patterns, configured local secrets, literal network addresses,
private contact/chat identifiers, source-workstation paths and operator-supplied
private markers. Gitleaks additionally scans reachable committed history. Commit
identities are generic project identities. Document checks extract PDF text and
metadata and inspect PNG textual/EXIF metadata. Browser-generator version strings
are classified as versions, not network addresses.

No account screenshots, email attachments, personal investment notes, populated
watchlist, private correspondence, live books, credentials or provider/browser
sessions are part of the public source. The chart report omits attachment names,
capture fingerprints and email logistics. The trading repository uses only its
clean release history; superseded export objects are not copied to that public
repository. An earlier backup is retained privately rather than deleted.

Automated checks report finding types and locations, never matched secret values.
Their result is evidence about the reviewed files and history, not a guarantee
about future additions or arbitrary encoded data. Examples and required upstream
copyright notices are not private information about the operator.

## Publishing and verification

Visibility changes are a separate operator-authorized release action. Normal
publish.py updates never flip visibility; existing public targets additionally
require --allow-public-update. There are no automatic publishing jobs or hooks.

The release sequence is: inspect the diff and complete checks, commit guides and
privacy changes, push the reviewed commits, update GitHub descriptions, explicitly
change visibility, then verify public API/anonymous access and matching remote
commits. publication-verification.json records observed final GitHub state and
release hashes after verification. A GitHub rate-limit response is a pending
external action, not a successful publication; requests are spaced/backed off.

## Observed publication status

Nine repositories are public and their detailed READMEs were verified without
login. GitHub continues to reject creation of the clean trading replacement
after spaced retries. The latest trading guide/source are retained in a private
backup; superseded capture objects were not exposed publicly. Trading publication
remains pending, not complete. No retry job is installed. The machine-readable
status is publication-verification.json; the catalogue list links to the prepared
trading guide until its source repository can be created.
