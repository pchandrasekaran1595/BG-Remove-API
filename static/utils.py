import io
import cv2
import onnx
import base64
import numpy as np
import onnxruntime as ort

from PIL import Image

import warnings
warnings.filterwarnings("ignore")

ort.set_default_logger_severity(3)


class Model(object):
    def __init__(self, lightweight: bool = False) -> None:
        self.ort_session = None
        self.size: int = 320
        self.mean: list = [0.485, 0.456, 0.406]
        self.std: list = [0.229, 0.224, 0.225]

        if lightweight:
            path: str = "static/models/u2netp.onnx"
        else:
            path: str = "static/models/u2net.onnx"

        model = onnx.load(path)
        onnx.checker.check_model(model)
        self.ort_session = ort.InferenceSession(
            path, providers=["AzureExecutionProvider", "CPUExecutionProvider"]
        )

    async def infer(self, image: np.ndarray) -> np.ndarray:
        h, w, _ = image.shape

        image = image / 255
        image = cv2.resize(
            src=image, dsize=(self.size, self.size), interpolation=cv2.INTER_AREA
        ).transpose(2, 0, 1)
        for i in range(image.shape[0]):
            image[i, :, :] = (image[i, :, :] - self.mean[i]) / self.std[i]
        image = np.expand_dims(image, axis=0)
        input = {self.ort_session.get_inputs()[0].name: image.astype("float32")}
        result = self.ort_session.run(None, input)
        result = result[0].squeeze()
        result = np.clip(result * 255, 0, 255).astype("uint8")
        return cv2.resize(src=result, dsize=(w, h), interpolation=cv2.INTER_CUBIC)


models = [Model(), Model(True)]


class Processor:
    @staticmethod
    def decode_image(data) -> tuple:
        return np.array(Image.open(io.BytesIO(data)).convert("RGB"))

    @staticmethod
    def encode_image_to_base64(
        header: str = "data:image/png;base64",
        image: np.ndarray = None,
        use_alpha: bool = True,
    ) -> str:
        if use_alpha:
            image = cv2.cvtColor(src=image, code=cv2.COLOR_RGBA2BGRA)
        else:
            image = cv2.cvtColor(src=image, code=cv2.COLOR_RGB2BGR)
        _, imageData = cv2.imencode(".png", image)
        imageData = base64.b64encode(imageData)
        imageData = str(imageData).replace("b'", "").replace("'", "")
        imageData = header + "," + imageData
        return imageData

    @staticmethod
    def preprocess_replace_bg_image(image: np.ndarray, w: int, h: int) -> np.ndarray:
        return cv2.resize(src=image, dsize=(w, h), interpolation=cv2.INTER_CUBIC)

    @staticmethod
    def write_to_temp(image: np.ndarray, filename: str, use_alpha: bool) -> None:
        if use_alpha:
            cv2.imwrite(filename, cv2.cvtColor(src=image, code=cv2.COLOR_RGBA2BGRA))
        else:
            cv2.imwrite(filename, cv2.cvtColor(src=image, code=cv2.COLOR_RGB2BGR))

    @staticmethod
    def get_transparent_image(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        return np.concatenate((image, np.expand_dims(mask, axis=2)), axis=2)

    @staticmethod
    def get_bg_color_replaced_image(
        image: np.ndarray, mask: np.ndarray, color: tuple
    ) -> np.ndarray:

        image = np.concatenate((image, np.expand_dims(mask, axis=2)), axis=2)
        mask = image[:, :, 3] == 0
        image[mask] = color
        return cv2.cvtColor(src=image, code=cv2.COLOR_RGBA2RGB)
