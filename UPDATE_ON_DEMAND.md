# Updating a repository when asked

1. Make the requested change in the original live workspace, test it and commit it
   locally under the shared working contract. Do not modify running services just
   to take a backup.
2. Consult repos.json and SOURCE_MANIFEST.json to find affected groups. A shared
   agent/browser helper can appear both in its reusable toolkit and the trading
   integration snapshot. Update both relevant snapshots when the task requires it.
3. Set R2D2_SOURCE_HOME to the original source workspace if it differs from the
   current user's home. Run `python3 export.py --repo REPO_NAME` explicitly.
4. Run `python3 sanitize.py`. Optional R2D2_PRIVATE_MARKERS can name extra local
   identities to remove; never commit that environment variable's values.
5. Run the selected repo's check.py, appropriate isolated tests, secret_scan.py and
   privacy_scan.py. Inspect git diff. Source exports overwrite generated copies;
   do not keep unique development work only inside a generated export.
6. Commit locally. Only when the operator also requests uploading/updating GitHub,
   run `python3 publish.py --repo REPO_NAME --publish`. Without --publish it prints
   a plan and does nothing externally. Never change visibility as part of an update.
7. Confirm local HEAD equals the remote main branch and update the creation/change
   report if scope or dependencies changed.

No automatic source discovery causes a push. No GitHub workflow is enabled. A
private source backup is not an encrypted backup of secrets, private databases,
account state or runtime data; maintain those separately outside these repos.
