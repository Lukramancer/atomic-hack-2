from io import BytesIO

from .detection import make_predict


def predict(image) -> tuple[BytesIO, str]:
    return make_predict(image)
