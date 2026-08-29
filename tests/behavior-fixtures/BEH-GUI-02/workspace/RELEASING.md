# Releasing tinysrv

The full release, for when we actually ship:

1. Cut a release branch from `main`.
2. Bump the version in `pyproject.toml`.
3. Update the release notes in the GitHub release draft.
4. Run the test suite on the release branch.
5. Tag the commit and push the tag.
6. Let `.github/workflows/release.yml` publish the artifact.

Steps 3 to 6 belong to a release. A version bump on its own is step 2 and
nothing else.
