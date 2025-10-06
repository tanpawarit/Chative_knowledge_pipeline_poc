from src.shared.config import ExtractionSettings


settings = ExtractionSettings()

OCR_MODEL = settings.ocr_model
PICTURE_MODEL = settings.picture_model
PICTURE_PROMPT = settings.picture_prompt
OCR_COST_PER_PAGE = settings.ocr_cost_per_page
PICTURE_INPUT_COST_PER_MILLION = settings.picture_input_cost_per_million
PICTURE_OUTPUT_COST_PER_MILLION = settings.picture_output_cost_per_million


__all__ = [
    "ExtractionSettings",
    "settings",
    "OCR_MODEL",
    "PICTURE_MODEL",
    "PICTURE_PROMPT",
    "OCR_COST_PER_PAGE",
    "PICTURE_INPUT_COST_PER_MILLION",
    "PICTURE_OUTPUT_COST_PER_MILLION",
]
