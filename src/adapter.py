import logging
import base64
import io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, ClassVar, Dict, Iterable, List, Literal, Optional, Type

from docling_core.types.doc import BoundingBox, CoordOrigin, NodeItem
from docling_core.types.doc.document import PictureItem
from docling_core.types.doc.page import BoundingRectangle, TextCell
from PIL import Image

from docling.models.base_ocr_model import BaseOcrModel
from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.base_models import Page
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import (
    OcrOptions,
    PictureDescriptionBaseOptions,
)
from docling.exceptions import OperationNotAllowed
from docling.models.base_model import ItemAndImageEnrichmentElement
from docling.models.picture_description_base_model import PictureDescriptionBaseModel
from docling.utils.profiling import TimeRecorder
from mistralai import Mistral, models
from mistralai.types import UNSET, UNSET_SENTINEL


_log = logging.getLogger(__name__)


def _image_to_data_url(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    payload = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{payload}"

class MistralOcrOptions(OcrOptions):
    kind: ClassVar[Literal["mistral"]] = "mistral"
    api_key: str
    model: str = "mistral-ocr-latest"

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
        self._available = True

    def _to_docling_format(self, resp: Optional[models.OCRResponse], page: Page) -> List[TextCell]:
        """Convert a Mistral OCR response into Docling text cells."""
        if resp is None or not getattr(resp, "pages", None):
            return []

        # The SDK returns one OCRPageObject per processed page. We call it per page, so pick the first.
        page_data = resp.pages[0]
        page_text = (page_data.markdown or "").strip()
        if not page_text:
            return []

        width = getattr(getattr(page, "size", None), "width", 1.0) or 1.0
        height = getattr(getattr(page, "size", None), "height", 1.0) or 1.0

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
                    high_res_image = backend.get_page_image(scale=1.0)
                except Exception:  # pragma: no cover - defensive, follows Docling pattern
                    _log.exception("Mistral OCR failed to render page image")
                    yield page
                    continue

                try:
                    resp = self.client.ocr.process(
                        model=self.model,
                        document={
                            "type": "image_url",
                            "image_url": _image_to_data_url(high_res_image),
                        },
                    )
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


class MistralPictureDescriptionOptions(PictureDescriptionBaseOptions):
    kind: ClassVar[Literal["mistral_api"]] = "mistral_api"

    api_key: str
    model: str = "pixtral-12b-2409"
    prompt: str = "Describe this image in a few sentences."
    temperature: float = 0.2
    max_output_tokens: int = 300
    concurrency: int = 2
    timeout_seconds: float = 30.0
    base_url: Optional[str] = None
    provenance: str = "mistral-picture-description"


class MistralPictureDescriptionModel(PictureDescriptionBaseModel):
    OPTIONS_CLASS = MistralPictureDescriptionOptions

    @classmethod
    def get_options_type(cls) -> Type[PictureDescriptionBaseOptions]:
        return MistralPictureDescriptionOptions

    def __init__(
        self,
        *,
        enabled: bool,
        enable_remote_services: bool,
        artifacts_path: Optional[Path],
        options: MistralPictureDescriptionOptions,
        accelerator_options: AcceleratorOptions,
    ):
        super().__init__(
            enabled=enabled,
            enable_remote_services=enable_remote_services,
            artifacts_path=artifacts_path,
            options=options,
            accelerator_options=accelerator_options,
        )
        self.options: MistralPictureDescriptionOptions
        self.images_scale = self.options.scale
        self.elements_batch_size = self.options.batch_size
        self.concurrency = max(1, self.options.concurrency)
        self.provenance = self.options.provenance or self.options.model
        self._timeout_ms = (
            int(self.options.timeout_seconds * 1000)
            if self.options.timeout_seconds is not None
            else None
        )
        self._client: Optional[Mistral] = None

        if self.enabled:
            if not enable_remote_services:
                raise OperationNotAllowed(
                    "Set pipeline_options.enable_remote_services=True to use Mistral picture descriptions."
                )

            self._client = Mistral(
                api_key=self.options.api_key,
                server_url=self.options.base_url,
                timeout_ms=self._timeout_ms,
            )

    def prepare_element(
        self,
        conv_res: ConversionResult,
        element: NodeItem,
    ) -> Optional[ItemAndImageEnrichmentElement]:
        try:
            return super().prepare_element(conv_res, element)
        except IndexError:
            if isinstance(element, PictureItem):
                fallback = element.get_image(conv_res.document)
                if fallback is not None:
                    return ItemAndImageEnrichmentElement(
                        item=element,
                        image=fallback,
                    )
            return None

    def _annotate_images(self, images: Iterable[Image.Image]) -> Iterable[str]:
        if not self.enabled or self._client is None:
            return []

        def _describe(image: Image.Image) -> str:
            messages: List[Dict[str, Any]] = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": _image_to_data_url(image)},
                        },
                        {"type": "text", "text": self.options.prompt},
                    ],
                }
            ]

            try:
                response = self._client.chat.complete(
                    model=self.options.model,
                    messages=messages,
                    temperature=self.options.temperature,
                    max_tokens=self.options.max_output_tokens,
                )
            except Exception as exc:  # pragma: no cover - shielding API errors
                _log.warning("Mistral picture description failed: %s", exc)
                return ""

            content = response.choices[0].message.content
            if content in (UNSET, UNSET_SENTINEL) or content is None:
                content = (
                    response.model_dump()
                    .get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", [])
                )

            if isinstance(content, str):
                return content.strip()

            texts: List[str] = []
            if isinstance(content, list):
                for chunk in content:
                    text_value: Optional[str]
                    if isinstance(chunk, dict):
                        text_value = chunk.get("text") or chunk.get("content")
                    else:
                        text_value = getattr(chunk, "text", None)
                    if text_value:
                        texts.append(text_value.strip())

            return "\n".join(texts)

        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            yield from executor.map(_describe, images)

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


def register_mistral_picture_description_plugin(
    allow_external_plugins: bool = False,
) -> None:
    """Register the local Mistral picture description model with Docling."""
    from docling.models.factories import get_picture_description_factory

    factory = get_picture_description_factory(
        allow_external_plugins=allow_external_plugins
    )
    if MistralPictureDescriptionOptions in factory.classes:
        return

    factory.register(
        MistralPictureDescriptionModel,
        plugin_name="local_adapter",
        plugin_module_name=__name__,
    )
