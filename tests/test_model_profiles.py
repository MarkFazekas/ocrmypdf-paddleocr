from ocrmypdf_paddleocr.model_profiles import (
    normalize_languages,
    select_model_profile,
)


def test_normalize_plus_separated_languages():
    assert normalize_languages(["eng+hin+san"]) == ("eng", "hin", "san")


def test_devanagari_profile_supports_english_hindi_sanskrit():
    profile = select_model_profile(["eng", "hin", "san"])

    assert profile.profile_name == "devanagari"
    assert profile.paddle_lang == "hi"
    assert profile.ocr_version == "PP-OCRv5"
    assert profile.recognition_model_name == "devanagari_PP-OCRv5_mobile_rec"
    assert profile.hocr_language in {"hin", "san"}


def test_sanskrit_alone_uses_devanagari_profile():
    profile = select_model_profile(["san"])
    assert profile.recognition_model_name == "devanagari_PP-OCRv5_mobile_rec"


def test_english_keeps_default_profile():
    profile = select_model_profile(["eng"])
    assert profile.profile_name == "default"
    assert profile.paddle_lang == "en"
    assert profile.recognition_model_name is None


def test_incompatible_mixed_profile_is_rejected():
    try:
        select_model_profile(["hin", "fra"])
    except ValueError as exc:
        assert "Devanagari" in str(exc)
    else:
        raise AssertionError("Expected incompatible language mix to fail")


def test_explicit_recognizer_overrides_auto_selection():
    profile = select_model_profile(
        ["eng", "hin", "san"],
        explicit_ocr_version="PP-OCRv5",
        explicit_recognition_model_name="my_custom_recognizer",
    )
    assert profile.profile_name == "custom"
    assert profile.recognition_model_name == "my_custom_recognizer"
