# Releasing to PyPI

The original distribution name `ocrmypdf-paddleocr` is already registered on
PyPI by another maintainer. This fork therefore publishes as
`ocrmypdf-paddleocr-plus`. The Python import and OCRmyPDF plugin name remain
`ocrmypdf_paddleocr`.

## One-time setup

1. Sign in to PyPI.
2. Configure a **pending Trusted Publisher** for the project
   `ocrmypdf-paddleocr-plus`:
   - Owner: `MarkFazekas`
   - Repository: `ocrmypdf-paddleocr`
   - Workflow: `publish.yml`
   - Environment: `pypi`
3. In GitHub, create the `pypi` environment under
   **Settings -> Environments**. Optional approval protection is recommended.

No long-lived PyPI API token is needed.

## Release checklist

1. Ensure CI is green on `master`.
2. Update `CHANGELOG.md`.
3. Choose the version and create a tag, for example:

   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

4. Create a GitHub Release for that tag.
5. Publishing the GitHub Release triggers `.github/workflows/publish.yml`.
6. Verify the resulting project page and install in a clean environment:

   ```bash
   python -m venv /tmp/ocrmypdf-paddleocr-plus-test
   source /tmp/ocrmypdf-paddleocr-plus-test/bin/activate
   pip install ocrmypdf-paddleocr-plus
   ocrmypdf --plugin ocrmypdf_paddleocr --help
   ```

## Local package validation

Before tagging, it is useful to verify the artifacts locally:

```bash
python -m pip install build twine
rm -rf dist/
python -m build
python -m twine check dist/*
```

The package uses `setuptools-scm`; the release version is derived from the
Git tag.
