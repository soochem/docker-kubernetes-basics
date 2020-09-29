
import kfserving
from typing import List, Dict
from PIL import Image
import torchvision.transforms as transforms
import logging
import io
import numpy as np
import base64

logging.basicConfig(level=kfserving.constants.KFSERVING_LOGLEVEL)

transform = transforms.Compose(
        [transforms.ToTensor(),
         transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])


def image_transform(instance):
    byte_array = base64.b64decode(instance['image_bytes']['b64'])
    image = Image.open(io.BytesIO(byte_array))
    a = np.asarray(image)
    im = Image.fromarray(a)
    res = transform(im)
    logging.info(res)
    return res.tolist()


class ImageTransformer(kfserving.KFModel):
    def __init__(self, name: str, predictor_host: str):
        super().__init__(name)
        self.predictor_host = predictor_host

    def preprocess(self, inputs: Dict) -> Dict:
        return {'instances': [image_transform(instance) for instance in inputs['instances']]}

    def postprocess(self, inputs: List) -> List:
        return inputs