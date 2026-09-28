# Releasing

Releases are intentionally driven from the GitHub Actions UI. The release
workflow validates `main`, creates the Git tag, builds the distribution,
optionally publishes it to PyPI, and creates the GitHub Release with generated
release notes and the built wheel/sdist attached.

The distribution name is `ocrmypdf-paddleocr-plus`. The Python import and
OCRmyPDF plugin name remain `ocrmypdf_paddleocr`.

## One-time repository setup

### 1. Make `main` the default branch

GitHub only exposes manually dispatched workflows reliably from the repository's
default branch. After the feature PR is merged, set **Settings -> Branches ->
Default branch** to `main`.

### 2. Configure PyPI Trusted Publishing

In PyPI, create a pending Trusted Publisher for:

- PyPI project: `ocrmypdf-paddleocr-plus`
- GitHub owner: `MarkFazekas`
- Repository: `ocrmypdf-paddleocr`
- Workflow: `release.yml`
- Environment: `pypi`

In GitHub, create the `pypi` environment under **Settings -> Environments**.
Optional approval protection is recommended.

No PyPI API token or GitHub secret is required.

## Create a release from the GitHub UI

1. Merge release-ready changes to `main`.
2. Open **Actions -> Release -> Run workflow**.
3. In the branch selector choose **main**.
4. Enter the version **without** the `v` prefix, for example `0.2.0`.
5. Choose whether this is a prerelease.
6. Leave **Publish to PyPI** enabled for a normal release.
7. Click **Run workflow**.

The workflow then:

1. Refuses to run unless the selected ref is exactly `main`.
2. Runs the lightweight test suite.
3. Creates annotated tag `v<VERSION>` on the exact `main` commit.
4. Reuses the tag safely on a rerun only if it already points at that same commit.
5. Builds the wheel and source distribution with `setuptools-scm`.
6. Runs `twine check`.
7. Publishes through PyPI Trusted Publishing (unless disabled).
8. Creates the GitHub Release with generated notes.
9. Attaches the built wheel and source distribution to the GitHub Release.

The PyPI upload uses `skip-existing`, and the release step reuses an existing
matching tag/release, so a failed run can normally be retried safely.

## Dry release without PyPI

For testing the tag/build/GitHub Release flow, disable **Publish to PyPI** in
the workflow form. This still creates the tag and GitHub Release, so use a real
prerelease version such as `0.2.0rc1`, not a throwaway final version.

## Local validation

Before merging release changes:

```bash
python -m pip install -e '.[dev]'
pytest -q
rm -rf dist/
python -m build
python -m twine check dist/*
```

Do not manually create the release tag before the workflow unless you are
recovering from a failed run. The workflow is designed to own tag creation.
