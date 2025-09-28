import base64
import io
from PIL import Image


def _image_to_data_url(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    payload = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{payload}"
