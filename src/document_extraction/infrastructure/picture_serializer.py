from typing import Any, Optional

from docling_core.transforms.serializer.base import (
    BaseDocSerializer,
    SerializationResult,
)
from docling_core.transforms.serializer.common import create_ser_result
from docling_core.transforms.serializer.markdown import MarkdownPictureSerializer
from docling_core.types.doc.document import (
    DoclingDocument,
    PictureDescriptionData,
    PictureItem,
)
from typing_extensions import override


class CommentPictureSerializer(MarkdownPictureSerializer):
    @override
    def serialize(
        self,
        *,
        item: PictureItem,
        doc_serializer: BaseDocSerializer,
        doc: DoclingDocument,
        separator: Optional[str] = None,
        **kwargs: Any,
    ) -> SerializationResult:
        # Skip the default annotation rendering to avoid duplicating the
        # generated description text. We'll re-inject the pieces we need below
        # via HTML comments.
        kwargs = dict(kwargs)
        kwargs["include_annotations"] = False

        base_result = super().serialize(
            item=item,
            doc_serializer=doc_serializer,
            doc=doc,
            **kwargs,
        )

        parts: list[str] = []
        if base_result.text:
            parts.append(base_result.text)

        for annotation in item.annotations:
            if isinstance(annotation, PictureDescriptionData) and annotation.text:
                parts.append(f"<!-- image description: {annotation.text} -->")

        joined = (separator or "\n").join(parts)
        return create_ser_result(text=joined, span_source=item)
