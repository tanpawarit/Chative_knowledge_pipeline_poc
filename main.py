import os
import sys
from pathlib import Path
import warnings

from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    PowerpointFormatOption,
    ImageFormatOption,
    WordFormatOption,
    HTMLFormatOption,
    AsciiDocFormatOption,
    CsvFormatOption,
    MarkdownFormatOption,
)
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

class OcrPolicyDecider:
    """Encapsulate heuristics for deciding when to run OCR."""

    IMAGE_SUFFIXES = {
        ".png",
        ".jpg",
        ".jpeg",
        ".tif",
        ".tiff",
        ".bmp",
        ".gif",
        ".webp",
    }

    def __init__(self, *, sample_pages: int = 5, char_threshold: int = 200) -> None:
        self.sample_pages = sample_pages
        self.char_threshold = char_threshold

    def should_ocr(self, path: str | Path) -> bool:
        suffix = Path(path).suffix.lower()
        if suffix == ".pdf":
            return self._should_ocr_pdf(path)
        if suffix in self.IMAGE_SUFFIXES:
            return True
        return False

    def _should_ocr_pdf(self, path: str | Path) -> bool:
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
            pages_to_check = min(self.sample_pages, num_pages)
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
            return avg_chars < self.char_threshold
        except Exception:
            # On any unexpected error, err on the side of enabling OCR
            return True


mistral_key = os.getenv("MISTRAL_KEY")
if not mistral_key:
    raise RuntimeError(
        "Missing MISTRAL_KEY. Set it in .env or environment."
    )

# Source can be a path or URL; we use local path for now
source = "data/Cryptography.pdf"

# Decide OCR policy per file/format
policy = OcrPolicyDecider()
do_ocr = policy.should_ocr(source)

# Shared factory helpers ensure each format gets a fresh options instance
def make_picture_description_options() -> MistralPictureDescriptionOptions:
    return MistralPictureDescriptionOptions(api_key=mistral_key)


def make_remote_convert_options() -> ConvertPipelineOptions:
    return ConvertPipelineOptions(
        allow_external_plugins=True,
        enable_remote_services=True,
        do_picture_description=True,
        picture_description_options=make_picture_description_options(),
    )


# Specific pipeline options for PDF
pdf_pipeline_opts = PdfPipelineOptions(
    do_ocr=do_ocr,
    allow_external_plugins=True,
    enable_remote_services=True,
    generate_picture_images=True,
    images_scale=2.0,
    do_picture_description=True,
    picture_description_options=make_picture_description_options(),
    ocr_options=MistralOcrOptions(api_key=mistral_key),
)

# Images go through the PDF pipeline machinery, so mirror the remote config
image_pipeline_opts = PdfPipelineOptions(
    do_ocr=True,
    allow_external_plugins=True,
    enable_remote_services=True,
    generate_picture_images=True,
    images_scale=2.0,
    do_picture_description=True,
    picture_description_options=make_picture_description_options(),
    ocr_options=MistralOcrOptions(api_key=mistral_key),
)

# Specific pipeline options for document formats (no OCR, but remote picture captions)
pptx_pipeline_opts = make_remote_convert_options()
docx_pipeline_opts = make_remote_convert_options()
html_pipeline_opts = make_remote_convert_options()
asciidoc_pipeline_opts = make_remote_convert_options()
csv_pipeline_opts = make_remote_convert_options()
markdown_pipeline_opts = make_remote_convert_options()

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
        InputFormat.PPTX: PowerpointFormatOption(pipeline_options=pptx_pipeline_opts),
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
