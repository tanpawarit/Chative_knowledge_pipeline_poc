from docling.datamodel.pipeline_options import ConvertPipelineOptions, PdfPipelineOptions

from extraction.adapter import MistralOcrOptions, MistralPictureDescriptionOptions
from extraction.config import OCR_MODEL, PICTURE_MODEL, PICTURE_PROMPT


def create_picture_description_options(api_key: str) -> MistralPictureDescriptionOptions:
    return MistralPictureDescriptionOptions(
        api_key=api_key,
        model=PICTURE_MODEL,
        prompt=PICTURE_PROMPT,
        temperature=0.2,
        max_output_tokens=300,
        # Conservative settings to reduce timeouts/rate-limit issues
        concurrency=1,
        timeout_seconds=60.0,
        base_url=None,
    )


def build_pdf_pipeline_options(
    api_key: str,
    *,
    do_ocr: bool,
) -> PdfPipelineOptions:
    return PdfPipelineOptions(
        do_ocr=do_ocr,
        allow_external_plugins=True,
        enable_remote_services=True,
        generate_picture_images=True,
        images_scale=2.0,
        do_picture_description=True,
        picture_description_options=create_picture_description_options(api_key),
        ocr_options=MistralOcrOptions(api_key=api_key, model=OCR_MODEL),
    )


def build_image_pipeline_options(api_key: str) -> PdfPipelineOptions:
    return PdfPipelineOptions(
        do_ocr=True,
        allow_external_plugins=True,
        enable_remote_services=True,
        generate_picture_images=True,
        images_scale=2.0,
        do_picture_description=True,
        picture_description_options=create_picture_description_options(api_key),
        ocr_options=MistralOcrOptions(api_key=api_key, model=OCR_MODEL),
    )


def build_pptx_pipeline_options(api_key: str) -> ConvertPipelineOptions:
    return ConvertPipelineOptions(
        allow_external_plugins=True,
        enable_remote_services=True,
        do_picture_description=True,
        picture_description_options=create_picture_description_options(api_key),
    )


def build_docx_pipeline_options(api_key: str) -> ConvertPipelineOptions:
    return ConvertPipelineOptions(
        allow_external_plugins=True,
        enable_remote_services=True,
        do_picture_description=True,
        picture_description_options=create_picture_description_options(api_key),
    )


def build_html_pipeline_options(api_key: str) -> ConvertPipelineOptions:
    return ConvertPipelineOptions(
        allow_external_plugins=True,
        enable_remote_services=True,
        do_picture_description=True,
        picture_description_options=create_picture_description_options(api_key),
    )


def build_asciidoc_pipeline_options(api_key: str) -> ConvertPipelineOptions:
    return ConvertPipelineOptions(
        allow_external_plugins=True,
        enable_remote_services=True,
        do_picture_description=True,
        picture_description_options=create_picture_description_options(api_key),
    )


def build_csv_pipeline_options(api_key: str) -> ConvertPipelineOptions:
    return ConvertPipelineOptions(
        allow_external_plugins=True,
        enable_remote_services=True,
        do_picture_description=True,
        picture_description_options=create_picture_description_options(api_key),
    )


def build_markdown_pipeline_options(api_key: str) -> ConvertPipelineOptions:
    return ConvertPipelineOptions(
        allow_external_plugins=True,
        enable_remote_services=True,
        do_picture_description=True,
        picture_description_options=create_picture_description_options(api_key),
    )


__all__ = [
    "create_picture_description_options",
    "build_pdf_pipeline_options",
    "build_image_pipeline_options",
    "build_pptx_pipeline_options",
    "build_docx_pipeline_options",
    "build_html_pipeline_options",
    "build_asciidoc_pipeline_options",
    "build_csv_pipeline_options",
    "build_markdown_pipeline_options",
]
