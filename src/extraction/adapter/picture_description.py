import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, ClassVar, Dict, Iterable, List, Literal, Optional, Type

from docling_core.types.doc import NodeItem
from docling_core.types.doc.document import PictureItem

from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import PictureDescriptionBaseOptions
from docling.exceptions import OperationNotAllowed
from docling.models.base_model import ItemAndImageEnrichmentElement
from docling.models.picture_description_base_model import PictureDescriptionBaseModel
from mistralai import Mistral
from mistralai.types import UNSET, UNSET_SENTINEL
from PIL import Image

from extraction.adapter.utils import _image_to_data_url
from extraction.config import PICTURE_MODEL, PICTURE_PROMPT
from cost_tracker.mistral_cost_tracker import mistral_cost_tracker


_log = logging.getLogger(__name__)


class MistralPictureDescriptionOptions(PictureDescriptionBaseOptions):
    kind: ClassVar[Literal["mistral_api"]] = "mistral_api"

    api_key: str
    model: str = PICTURE_MODEL
    prompt: str = PICTURE_PROMPT
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

            mistral_cost_tracker.record_chat_completion(
                self.options.model, getattr(response, "usage", None)
            )

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


__all__ = [
    "MistralPictureDescriptionModel",
    "MistralPictureDescriptionOptions",
    "register_mistral_picture_description_plugin",
]
