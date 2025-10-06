from __future__ import annotations

import os
import warnings

from docling.document_converter import (
    AsciiDocFormatOption,
    CsvFormatOption,
    DocumentConverter,
    HTMLFormatOption,
    ImageFormatOption,
    MarkdownFormatOption,
    PdfFormatOption,
    PowerpointFormatOption,
    WordFormatOption,
)
from docling.datamodel.base_models import InputFormat
from docling_core.transforms.serializer.markdown import (
    MarkdownDocSerializer,
    MarkdownParams,
)
from dotenv import load_dotenv  # type: ignore

from src.cost_management.infrastructure.mistral_cost_tracker import (
    mistral_cost_tracker,
)
from src.document_extraction.domain.ocr_policy import OcrPolicyDecider
from src.document_extraction.infrastructure.adapter import (
    register_mistral_ocr_plugin,
    register_mistral_picture_description_plugin,
)
from src.document_extraction.infrastructure.pipeline_option import (
    build_asciidoc_pipeline_options,
    build_csv_pipeline_options,
    build_docx_pipeline_options,
    build_html_pipeline_options,
    build_image_pipeline_options,
    build_markdown_pipeline_options,
    build_pdf_pipeline_options,
    build_pptx_pipeline_options,
)
from src.document_extraction.infrastructure.picture_serializer import (
    CommentPictureSerializer,
)


def run_extraction(source: str) -> str:
    """Convert a document into Markdown and return the serialized text."""
    load_dotenv()

    # Suppress benign RuntimeWarnings coming from Docling confidence aggregation
    # (e.g., "Mean of empty slice") when metrics are not applicable for a format.
    warnings.filterwarnings(
        "ignore", category=RuntimeWarning, message="Mean of empty slice"
    )

    mistral_key = os.getenv("MISTRAL_KEY")
    if not mistral_key:
        raise RuntimeError(
            "Missing MISTRAL_KEY. Set it in .env or environment."
        )

    # Reset usage tracking for a fresh run and apply any runtime pricing overrides.
    mistral_cost_tracker.reset()
    mistral_cost_tracker.configure_from_environment()

    # Decide OCR policy per file/format
    policy = OcrPolicyDecider()
    do_ocr = policy.should_ocr(source)

    pdf_pipeline_opts = build_pdf_pipeline_options(
        mistral_key,
        do_ocr=do_ocr,
    )
    image_pipeline_opts = build_image_pipeline_options(mistral_key)
    pptx_pipeline_opts = build_pptx_pipeline_options(mistral_key)
    docx_pipeline_opts = build_docx_pipeline_options(mistral_key)
    html_pipeline_opts = build_html_pipeline_options(mistral_key)
    asciidoc_pipeline_opts = build_asciidoc_pipeline_options(mistral_key)
    csv_pipeline_opts = build_csv_pipeline_options(mistral_key)
    markdown_pipeline_opts = build_markdown_pipeline_options(mistral_key)

    register_mistral_ocr_plugin(
        allow_external_plugins=pdf_pipeline_opts.allow_external_plugins
    )
    register_mistral_picture_description_plugin(
        allow_external_plugins=pdf_pipeline_opts.allow_external_plugins
    )

    converter = DocumentConverter(
        allowed_formats=[
            InputFormat.PDF,
            InputFormat.IMAGE,
            InputFormat.DOCX,
            InputFormat.HTML,
            InputFormat.PPTX,
            InputFormat.ASCIIDOC,
            InputFormat.CSV,
            InputFormat.MD,
        ],
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_pipeline_opts),
            InputFormat.IMAGE: ImageFormatOption(pipeline_options=image_pipeline_opts),
            InputFormat.PPTX: PowerpointFormatOption(
                pipeline_options=pptx_pipeline_opts
            ),
            InputFormat.DOCX: WordFormatOption(pipeline_options=docx_pipeline_opts),
            InputFormat.HTML: HTMLFormatOption(pipeline_options=html_pipeline_opts),
            InputFormat.ASCIIDOC: AsciiDocFormatOption(
                pipeline_options=asciidoc_pipeline_opts
            ),
            InputFormat.CSV: CsvFormatOption(pipeline_options=csv_pipeline_opts),
            InputFormat.MD: MarkdownFormatOption(
                pipeline_options=markdown_pipeline_opts
            ),
        },
    )

    print(f"OCR policy: do_ocr={do_ocr} for {source}")
    result = converter.convert(source)

    serializer = MarkdownDocSerializer(
        doc=result.document,
        picture_serializer=CommentPictureSerializer(),
        params=MarkdownParams(),
    )
    markdown = serializer.serialize().text

    print(f"Mean_grade: {result.confidence.mean_grade.value}")
    print(mistral_cost_tracker.format_report())

    return markdown


def main_extraction(source: str) -> str:
    """Wrapper that returns the extracted Markdown string."""
    return run_extraction(source)
