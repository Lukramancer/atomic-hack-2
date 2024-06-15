from io import BytesIO

from .detection import make_predict


def get_description(image) -> tuple[BytesIO, str]:
    return make_predict(image)
