"""Language normalization and PaddleOCR model-profile selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


LANGUAGE_MAP = {
    "eng": "en",
    "chi_sim": "ch",
    "chi_tra": "chinese_cht",
    "fra": "fr",
    "deu": "german",
    "jpn": "japan",
    "kor": "korean",
    "spa": "spanish",
    "rus": "ru",
    "ara": "ar",
    "hin": "hi",
    "san": "sa",
    "mar": "mr",
    "nep": "ne",
    "bho": "bho",
    "mai": "mai",
    "por": "pt",
    "ita": "it",
    "tur": "tr",
    "vie": "vi",
    "tha": "th",
}

# PaddleOCR PP-OCRv5 ships a dedicated Devanagari recognizer that covers
# Hindi, Sanskrit, Marathi, Nepali, Bhojpuri, Maithili and English, among
# other Devanagari-script languages.
DEVANAGARI_LANGUAGE_CODES = frozenset(
    {
        "hin",
        "san",
        "mar",
        "nep",
        "bho",
        "mai",
        "hi",
        "sa",
        "mr",
        "ne",
    }
)

ENGLISH_LANGUAGE_CODES = frozenset({"eng", "en"})

# Keep the broad set historically exposed by the plugin, while adding the
# OCRmyPDF/Tesseract codes needed for native Devanagari multi-language use.
SUPPORTED_LANGUAGE_CODES = frozenset(
    {
        "en",
        "ch",
        "chinese_cht",
        "ta",
        "te",
        "ka",
        "latin",
        "ar",
        "cy",
        "da",
        "de",
        "es",
        "et",
        "fr",
        "ga",
        "hi",
        "sa",
        "mr",
        "ne",
        "bho",
        "mai",
        "it",
        "ja",
        "ko",
        "la",
        "nl",
        "no",
        "oc",
        "pt",
        "ro",
        "ru",
        "sr",
        "sv",
        "tr",
        "uk",
        "vi",
        "eng",
        "chi_sim",
        "chi_tra",
        "deu",
        "fra",
        "spa",
        "rus",
        "jpn",
        "kor",
        "ara",
        "hin",
        "san",
        "mar",
        "nep",
        "por",
        "ita",
        "tur",
        "vie",
        "tha",
    }
)


@dataclass(frozen=True)
class ModelProfile:
    """Resolved PaddleOCR settings for one OCRmyPDF invocation."""

    requested_languages: tuple[str, ...]
    paddle_lang: str
    hocr_language: str
    ocr_version: str | None = None
    recognition_model_name: str | None = None
    profile_name: str = "default"


def normalize_languages(languages: Iterable[str] | None) -> tuple[str, ...]:
    """Normalize OCRmyPDF language input and split accidental '+' groups."""
    normalized: list[str] = []
    for language in languages or ():
        for code in str(language).split("+"):
            code = code.strip().lower()
            if code and code not in normalized:
                normalized.append(code)
    return tuple(normalized or ("eng",))


def select_model_profile(
    languages: Iterable[str] | None,
    *,
    explicit_ocr_version: str | None = None,
    explicit_recognition_model_name: str | None = None,
) -> ModelProfile:
    """Choose a multilingual PaddleOCR recognition profile.

    PP-OCRv6 is used by default. If any requested language uses Devanagari,
    switch to PaddleOCR's PP-OCRv5 Devanagari recognizer. That single model
    natively recognizes English plus Hindi, Sanskrit and several related
    Devanagari-script languages.
    """
    requested = normalize_languages(languages)
    primary = requested[0]
    mapped_primary = LANGUAGE_MAP.get(primary, primary)

    if explicit_recognition_model_name:
        return ModelProfile(
            requested_languages=requested,
            paddle_lang=mapped_primary,
            hocr_language=primary,
            ocr_version=explicit_ocr_version,
            recognition_model_name=explicit_recognition_model_name,
            profile_name="custom",
        )

    uses_devanagari = any(code in DEVANAGARI_LANGUAGE_CODES for code in requested)
    if uses_devanagari:
        unsupported = [
            code
            for code in requested
            if code not in DEVANAGARI_LANGUAGE_CODES
            and code not in ENGLISH_LANGUAGE_CODES
        ]
        if unsupported:
            joined = ", ".join(unsupported)
            raise ValueError(
                "The automatic Devanagari profile can be mixed with English, "
                "but not with these requested languages: "
                f"{joined}. Use --paddle-rec-model to select a custom "
                "multilingual recognizer."
            )

        hocr_language = next(
            (
                code
                for code in requested
                if code in DEVANAGARI_LANGUAGE_CODES
            ),
            primary,
        )
        representative = next(
            (
                code
                for code in requested
                if code in DEVANAGARI_LANGUAGE_CODES
            ),
            "hin",
        )
        return ModelProfile(
            requested_languages=requested,
            paddle_lang=LANGUAGE_MAP.get(representative, representative),
            hocr_language=hocr_language,
            # PaddleOCR 3.x natively maps PP-OCRv5 + a Devanagari language
            # to PP-OCRv5_server_det + devanagari_PP-OCRv5_mobile_rec.
            ocr_version=explicit_ocr_version or "PP-OCRv5",
            recognition_model_name=None,
            profile_name="devanagari",
        )

    return ModelProfile(
        requested_languages=requested,
        paddle_lang=mapped_primary,
        hocr_language=primary,
        ocr_version=explicit_ocr_version,
        recognition_model_name=None,
        profile_name="default",
    )
