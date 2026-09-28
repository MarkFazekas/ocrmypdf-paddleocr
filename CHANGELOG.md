# Changelog

## 0.2.0 - planned

- Base the fork on upstream PR #6 and reuse one process-wide PaddleOCR model
  with batched page inference.
- Add native OCRmyPDF multi-language handling for
  `eng+hin+san` and related Devanagari combinations.
- Automatically select PaddleOCR's
  `devanagari_PP-OCRv5_mobile_rec` recognizer for Devanagari documents.
- Add explicit OCR version, detector model and recognizer model overrides.
- Disable oneDNN/MKLDNN by default on CPU to avoid
  `ReduceMeanCheckIfOneDNNSupport` console spam and the related Paddle
  3.3.x compatibility path; users can opt back in.
- Silence Paddle's non-actionable `No ccache found` import warning.
- Add CPU thread tuning and quieter Paddle logging.
- Prepare the fork for PyPI Trusted Publishing as
  `ocrmypdf-paddleocr-plus`.
