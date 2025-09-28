import os
import sys
from pathlib import Path
import warnings

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import ConvertPipelineOptions, PdfPipelineOptions
from docling_core.transforms.serializer.markdown import MarkdownDocSerializer, MarkdownParams

# Make local adapters importable (src/adapter.py)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(CURRENT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from dotenv import load_dotenv  # type: ignore

load_dotenv()
from adapter import (
    MistralOcrOptions,
    MistralPictureDescriptionOptions,
    register_mistral_ocr_plugin,
    register_mistral_picture_description_plugin,
)
from picture_serializer import CommentPictureSerializer

from pypdf import PdfReader

# Suppress benign RuntimeWarnings coming from Docling confidence aggregation
# (e.g., "Mean of empty slice") when metrics are not applicable for a format.
warnings.filterwarnings(
    "ignore", category=RuntimeWarning, message="Mean of empty slice"
)

def should_ocr_pdf(path: str | Path, *, sample_pages: int = 5, char_threshold: int = 200) -> bool:
    """
    Decide whether to OCR a PDF based on presence of a text layer.

    Heuristic:
    - Read up to `sample_pages` from the start.
    - If the average extracted characters per page < `char_threshold`,
      consider it a scanned PDF and enable OCR.

    If pypdf is unavailable or an error occurs, default to True (safer to OCR).
    """
    try:
        reader = PdfReader(str(path))
        num_pages = len(reader.pages)
        if num_pages == 0:
            return True
        pages_to_check = min(sample_pages, num_pages)
        total_chars = 0
        checked = 0
        for i in range(pages_to_check):
            try:
                text = reader.pages[i].extract_text() or ""
            except Exception:
                text = ""
            total_chars += len(text.strip())
            checked += 1
        if checked == 0:
            return True
        avg_chars = total_chars / checked
        return avg_chars < char_threshold
    except Exception:
        # On any unexpected error, err on the side of enabling OCR
        return True


mistral_key = os.getenv("MISTRAL_KEY")
if not mistral_key:
    raise RuntimeError(
        "Missing MISTRAL_KEY. Set it in .env or environment."
    )

# Source can be a path or URL; we use local path for now
source = "data/2509.04343v1.pdf"

# Decide OCR policy per file/format
do_ocr = False
suffix = Path(source).suffix.lower()
if suffix == ".pdf":
    do_ocr = should_ocr_pdf(source)
elif suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif", ".webp"}:
    # Image formats require OCR
    do_ocr = True
else:
    # Text-native formats (docx, pptx, html, md, csv) default to no OCR
    do_ocr = False

picture_prompt = (
    "Summarize the picture in 2-3 sentences, capturing layout, text, and key visuals."
)
picture_options_pdf = MistralPictureDescriptionOptions(
    api_key=mistral_key,
    prompt=picture_prompt,
    temperature=0.0,
    concurrency=2,
)

opts = PdfPipelineOptions(
    do_ocr=do_ocr,
    allow_external_plugins=True,
    enable_remote_services=True,
    generate_picture_images=True,
    images_scale=1.0,
    do_picture_description=True,
    picture_description_options=picture_options_pdf,
    ocr_options=MistralOcrOptions(api_key=mistral_key),
)

register_mistral_ocr_plugin(
    allow_external_plugins=opts.allow_external_plugins
)
register_mistral_picture_description_plugin(
    allow_external_plugins=opts.allow_external_plugins
)

converter = DocumentConverter(
    allowed_formats=[
        InputFormat.PDF,
        InputFormat.IMAGE,
        InputFormat.DOCX,
        InputFormat.HTML,
        InputFormat.PPTX,
        # InputFormat.ASCIIDOC,
        # InputFormat.CSV,
        # InputFormat.MD,
    ],
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=opts)
    },
)

pptx_option = converter.format_to_options.get(InputFormat.PPTX)
if pptx_option is not None:
    pptx_option.pipeline_options = ConvertPipelineOptions(
        allow_external_plugins=True,
        enable_remote_services=True,
        do_picture_description=True,
        picture_description_options=picture_options_pdf.model_copy(deep=True),
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
