 
from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

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

# Ensure local src/ packages are importable when running from source checkout.
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from extraction.adapter import (
    register_mistral_ocr_plugin,
    register_mistral_picture_description_plugin,
)
from extraction.mistral_cost_tracker import mistral_cost_tracker
from extraction.ocr_policy import OcrPolicyDecider
from extraction.pipeline_option import (
    build_asciidoc_pipeline_options,
    build_csv_pipeline_options,
    build_docx_pipeline_options,
    build_html_pipeline_options,
    build_image_pipeline_options,
    build_markdown_pipeline_options,
    build_pdf_pipeline_options,
    build_pptx_pipeline_options,
)
from extraction.picture_serializer import CommentPictureSerializer


def main() -> None:
    """Run the document conversion pipeline."""
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

    # Source can be a path or URL; we use local path for now
    source = "data/Screenshot 2568-07-18 at 12.10.26.png"

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

    # Save markdown to file
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = Path(source).stem
    with (output_dir / f"{doc_filename}.md").open("w", encoding="utf-8") as fp:
        fp.write(markdown)

    print(f"Saved markdown to {output_dir / f'{doc_filename}.md'}")
    print(f"Mean_grade: {result.confidence.mean_grade.value}")
    print(mistral_cost_tracker.format_report())


if __name__ == "__main__":
    main()
