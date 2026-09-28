# OCRmyPDF PaddleOCR Plus

A maintained fork of the PaddleOCR engine plugin for
[OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF).

This fork is based on the batched single-model implementation from upstream
PR #6 and adds practical multilingual model selection, quieter CPU inference,
runtime tuning, tests, CI, and a PyPI release workflow.

## Highlights

- **One PaddleOCR model per process** with batched page inference instead of
  recreating models for every page.
- **Native English + Hindi + Sanskrit support** through PaddleOCR's official
  PP-OCRv5 Devanagari recognition model.
- **PP-OCRv6 for normal English OCR** by default.
- **Quiet CPU defaults**: oneDNN/MKLDNN is disabled unless explicitly enabled,
  avoiding the repeated `ReduceMeanCheckIfOneDNNSupport` console output seen
  with some PaddlePaddle versions.
- Suppresses Paddle's non-actionable `No ccache found` inference warning.
- CPU thread, batch size, model family, detector, and recognizer overrides.
- Optional PaddleOCR-VL support.
- Prepared for **PyPI Trusted Publishing**.

## Installation

OCRmyPDF still needs its normal operating-system dependencies. On Debian/Ubuntu
or WSL, installing the distro package is a convenient way to get them:

```bash
sudo apt update
sudo apt install ocrmypdf
```

### PyPI

The fork is published under a separate distribution name because
`ocrmypdf-paddleocr` is already owned by another PyPI maintainer.

```bash
pip install ocrmypdf-paddleocr-plus
```

For an isolated global OCRmyPDF CLI with `uv`:

```bash
uv tool install --python 3.11 \
  --with ocrmypdf-paddleocr-plus \
  ocrmypdf
hash -r
```

The Python import/plugin name intentionally stays unchanged:

```text
ocrmypdf_paddleocr
```

### Install directly from GitHub

Before the first PyPI release, or when testing a branch:

```bash
uv tool install --force --python 3.11 \
  --with 'ocrmypdf-paddleocr-plus @ git+https://github.com/MarkFazekas/ocrmypdf-paddleocr.git' \
  ocrmypdf
hash -r
```

## Basic usage

```bash
ocrmypdf \
  --plugin ocrmypdf_paddleocr \
  --language eng \
  --jobs 2 \
  --paddle-batch-size 2 \
  --output-type pdf \
  --optimize 0 \
  input.pdf output.pdf
```

## English, Hindi and Sanskrit

OCRmyPDF uses Tesseract-style language codes. This fork understands the
language list instead of silently using only the first entry.

For a document containing English, Hindi and Sanskrit:

```bash
ocrmypdf \
  --plugin ocrmypdf_paddleocr \
  --language eng+hin+san \
  --jobs 2 \
  --paddle-batch-size 2 \
  --output-type pdf \
  --optimize 0 \
  input.pdf output.pdf
```

When any supported Devanagari language is requested, the plugin automatically
uses PaddleOCR's official PP-OCRv5 Devanagari pipeline:

```text
PP-OCRv5_server_det
devanagari_PP-OCRv5_mobile_rec
```

That recognition model is multilingual and includes English plus Devanagari
languages, so mixed English/Hindi/Sanskrit pages can be recognized in one pass.

Common OCRmyPDF codes:

| OCRmyPDF code | Paddle code | Language |
|---|---|---|
| `eng` | `en` | English |
| `hin` | `hi` | Hindi |
| `san` | `sa` | Sanskrit |
| `mar` | `mr` | Marathi |
| `nep` | `ne` | Nepali |
| `bho` | `bho` | Bhojpuri |
| `mai` | `mai` | Maithili |

English-only OCR keeps PaddleOCR's normal/current English model selection
(PP-OCRv6 on supported PaddleOCR versions).

The automatic Devanagari profile accepts English plus Devanagari languages.
An unrelated mixed-script request such as `hin+fra` is rejected instead of
silently selecting the wrong recognizer. Advanced users can override the
models explicitly.

## Performance and batching

The plugin shares one PaddleOCR instance across OCRmyPDF worker threads.
Requests are collected into batches controlled by `--paddle-batch-size`.

A good CPU starting point is:

```bash
--jobs 2 --paddle-batch-size 2
```

Paddle itself uses multiple CPU threads, so a high OCRmyPDF `--jobs` value is
usually counterproductive.

You can tune Paddle's CPU thread count:

```bash
--paddle-cpu-threads 8
```

## Quiet CPU mode and oneDNN

On CPU, this fork disables oneDNN/MKLDNN by default. This avoids noisy output
such as:

```text
ReduceMeanCheckIfOneDNNSupport
```

and avoids the oneDNN compatibility path that has caused failures with some
PaddlePaddle releases.

If oneDNN is stable on your machine and you want to benchmark its speedup:

```bash
--paddle-enable-mkldnn
```

Internal Paddle/PaddleX INFO logging is also hidden by default. To show it:

```bash
--paddle-show-log
```

## Paddle-specific options

| Option | Meaning |
|---|---|
| `--paddle-engine classic|vl` | Classic OCR pipeline or PaddleOCR-VL |
| `--paddle-batch-size N` | Maximum pages sent to one Paddle batch |
| `--paddle-cpu-threads N` | Paddle inference threads on CPU |
| `--paddle-enable-mkldnn` | Opt in to oneDNN/MKLDNN on CPU |
| `--paddle-show-log` | Show Paddle/PaddleX internal INFO logs |
| `--paddle-use-gpu` | Use a GPU-enabled PaddlePaddle installation |
| `--paddle-ocr-version VERSION` | Override OCR family, e.g. `PP-OCRv5` |
| `--paddle-det-model NAME` | Override detector model name |
| `--paddle-rec-model NAME` | Override recognition model name |
| `--paddle-det-model-dir DIR` | Use a local detector model directory |
| `--paddle-rec-model-dir DIR` | Use a local recognizer model directory |
| `--paddle-cls-model-dir DIR` | Use a local orientation model directory |

Example explicit model selection:

```bash
ocrmypdf --plugin ocrmypdf_paddleocr \
  --paddle-det-model PP-OCRv5_server_det \
  --paddle-rec-model devanagari_PP-OCRv5_mobile_rec \
  input.pdf output.pdf
```

## Batch a directory of PDFs

Example using an `og/` input directory and `ocr/` output directory:

```bash
mkdir -p ocr

find og -maxdepth 1 -type f -iname '*.pdf' -print0 |
while IFS= read -r -d '' f; do
    out="ocr/$(basename "$f")"

    if [ -f "$out" ]; then
        echo "SKIP: $out already exists"
        continue
    fi

    echo "OCR: $f -> $out"
    ocrmypdf \
        --plugin ocrmypdf_paddleocr \
        --language eng \
        --jobs 2 \
        --paddle-batch-size 2 \
        --output-type pdf \
        --optimize 0 \
        "$f" "$out"
done
```

## PaddleOCR-VL

Install the optional dependencies:

```bash
pip install 'ocrmypdf-paddleocr-plus[vl]'
```

Then:

```bash
ocrmypdf --plugin ocrmypdf_paddleocr \
  --paddle-engine vl input.pdf output.pdf
```

VL is substantially heavier than the classic OCR pipeline.

## Development

```bash
python -m pip install -e '.[dev]'
pytest -q
python -m build
python -m twine check dist/*
```

CI validates the lightweight language/model-selection tests and package build.
Full Paddle inference is intentionally an integration test because the runtime
and model downloads are large.

## PyPI release

Releases are manual but fully automated: open **Actions -> Release -> Run
workflow**, select the `main` branch, enter a version such as `0.2.0`, and
run it. The workflow tests the code, creates the Git tag, builds and validates
the package, publishes through PyPI Trusted Publishing, creates the GitHub
Release, and attaches the wheel/sdist.

See [RELEASING.md](RELEASING.md) for the one-time `main` default-branch and
PyPI Trusted Publisher setup.

The distribution name is:

```text
ocrmypdf-paddleocr-plus
```

while the import and plugin name remains:

```text
ocrmypdf_paddleocr
```

## Troubleshooting

### The system OCRmyPDF runs instead of the uv-installed one

Check:

```bash
type -a ocrmypdf
```

If the shell cached `/usr/bin/ocrmypdf` after an `uv tool install`, refresh
the command cache:

```bash
hash -r
```

### PaddlePaddle version

The PyPI package currently pins PaddlePaddle to the 3.2.x line because that is
the stable CPU combination used by this fork. The plugin disables MKLDNN by
default to avoid the noisy/problematic oneDNN path.

## Credits

This fork builds on:

- [clefru/ocrmypdf-paddleocr](https://github.com/clefru/ocrmypdf-paddleocr)
- upstream PR #6 by
  [phu54321](https://github.com/clefru/ocrmypdf-paddleocr/pull/6)
- [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddlePaddle](https://github.com/PaddlePaddle/Paddle)

## License

MPL-2.0. See [LICENSE](LICENSE).
