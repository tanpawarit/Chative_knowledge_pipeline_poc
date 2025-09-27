import logging
import base64
import io
from pathlib import Path
from typing import ClassVar, Iterable, List, Literal, Optional, Type

from docling_core.types.doc import BoundingBox, CoordOrigin
from docling_core.types.doc.page import BoundingRectangle, TextCell

from docling.models.base_ocr_model import BaseOcrModel
from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.base_models import Page
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import OcrOptions
from docling.utils.profiling import TimeRecorder
from mistralai import Mistral, models


_log = logging.getLogger(__name__)

class MistralOcrOptions(OcrOptions):
    kind: ClassVar[Literal["mistral"]] = "mistral"
    api_key: str
    model: str = "mistral-ocr-latest"
    lang: List[str] = ["english","thai"]   

class MistralOcrModel(BaseOcrModel):
    OPTIONS_CLASS = MistralOcrOptions

    def __init__(
        self,
        *,
        enabled: bool,
        artifacts_path: Optional[Path],
        options: MistralOcrOptions,
        accelerator_options: AcceleratorOptions,
    ):
        super().__init__(
            enabled=enabled,
            artifacts_path=artifacts_path,
            options=options,
            accelerator_options=accelerator_options,
        )
        self.client = Mistral(api_key=options.api_key)
        self.model = options.model
        self.scale = 1.0
        self._available = True

    def recognize_page(self, pil_image, lang=None):
        # Convert page to base64 PNG
        buf = io.BytesIO()
        pil_image.save(buf, format="PNG")
        image_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        resp = self.client.ocr.process(
            model=self.model,
            document={"type": "image_url", "image_url": f"data:image/png;base64,{image_b64}"}
        )
        return resp

    def _to_docling_format(self, resp: Optional[models.OCRResponse], page: Page) -> List[TextCell]:
        """Convert a Mistral OCR response into Docling text cells."""
        if resp is None or not getattr(resp, "pages", None):
            return []

        # The SDK returns one OCRPageObject per processed page. We call it per page, so pick the first.
        page_data = resp.pages[0]
        page_text = (page_data.markdown or "").strip()
        if not page_text:
            return []

        width = getattr(getattr(page, "size", None), "width", None)
        height = getattr(getattr(page, "size", None), "height", None)
        if not width or not height:
            # Fallback to unit square if page dimensions are unavailable.
            width = height = 1.0

        bbox = BoundingBox(
            l=0.0,
            t=0.0,
            r=float(width),
            b=float(height),
            coord_origin=CoordOrigin.TOPLEFT,
        )
        rect = BoundingRectangle.from_bounding_box(bbox)

        return [
            TextCell(
                index=0,
                rect=rect,
                text=page_text,
                orig=page_text,
                confidence=1.0,
                from_ocr=True,
            )
        ]

    def __call__(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:
        if not self.enabled:
            yield from page_batch
            return

        for page in page_batch:
            if not self._available:
                yield page
                continue

            backend = getattr(page, "_backend", None)
            if backend is None or not backend.is_valid():
                yield page
                continue

            with TimeRecorder(conv_res, "ocr"):
                try:
                    high_res_image = backend.get_page_image(scale=self.scale)
                except Exception:  # pragma: no cover - defensive, follows Docling pattern
                    _log.exception("Mistral OCR failed to render page image")
                    yield page
                    continue

                try:
                    resp = self.recognize_page(high_res_image, lang=self.options.lang)
                except Exception as exc:  # pragma: no cover - surface SDK failures without crashing pipeline
                    if self._available:
                        _log.warning("Mistral OCR request failed: %s", exc)
                    self._available = False
                    yield page
                    continue

                ocr_cells = self._to_docling_format(resp, page)
                if ocr_cells:
                    self.post_process_cells(ocr_cells, page)

            yield page

    @classmethod
    def get_options_type(cls) -> Type[OcrOptions]:
        return MistralOcrOptions


def register_mistral_ocr_plugin(allow_external_plugins: bool = False) -> None:
    """Register the local Mistral OCR model with Docling's factory."""
    from docling.models.factories import get_ocr_factory

    factory = get_ocr_factory(allow_external_plugins=allow_external_plugins)
    if MistralOcrOptions in factory.classes:
        return

    factory.register(
        MistralOcrModel,
        plugin_name="local_adapter",
        plugin_module_name=__name__,
    )
