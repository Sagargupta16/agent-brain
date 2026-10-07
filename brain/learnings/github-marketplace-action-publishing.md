---
name: github-marketplace-action-publishing
description: "Publishing a GitHub Action to the Marketplace is UI-only, the new-release page rejects an existing tag, and moving the major tag is normal"
type: reference
source: "observed 2026-09-25 publishing five composite Python actions to the GitHub Marketplace"
created: 2026-09-25
modified: 2026-10-07
status: active
visibility: public
---

- **Marketplace listing cannot be done through the API.** The "Publish this Action to the GitHub Marketplace" checkbox exists only in the release UI. A release created with `gh release create` is not listed until someone ticks it.
- **The "new release" page fails with "tag name has already been taken"** when a release already exists on that tag. Use `/releases/edit/<tag>` ("Update release") instead, or delete only the release entry (`gh release delete <tag>` keeps the tag) and publish anew on the existing tag.
- **Moving the major tag (`v1`) after a minor release is a tag force-push.** That is the normal convention for actions and is not a push to `main`.
- **Pin consumers by commit SHA with a `# vX.Y.Z` comment** so updates are explicit and reviewable.
- **Dogfood in CI.** A CI job that runs `uses: ./` against real data catches breakage that unit tests on the script do not.

Related: [[github-token-automation-gotchas]].
