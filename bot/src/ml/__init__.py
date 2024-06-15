from PIL.Image import Image

from .detection import make_predict


def predict(image) -> str | tuple[tuple[Image, list[tuple[Image, str]]], str]:
    return make_predict(image)
