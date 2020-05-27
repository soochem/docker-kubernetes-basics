import argparse
import matplotlib.pyplot as plt
from tensorflow.keras.applications.mobilenet import MobileNet, preprocess_input, decode_predictions
from alibi.datasets import fetch_imagenet
import numpy as np
import requests
import json
import os
from PIL import Image
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

PREDICT_TEMPLATE = 'http://{0}/v1/models/mobnet:predict'
EXPLAIN_TEMPLATE = 'http://{0}/v1/models/mobnet:explain'


def get_image_data():
    data = []
    image_shape = (224, 224, 3)
    target_size = image_shape[:2]
    image = Image.open("./dogs.jpeg").convert('RGB')
    image = np.expand_dims(image.resize(target_size), axis=0)
    data.append(image)
    data = np.concatenate(data, axis=0)

    # image procsessing
    images = preprocess_input(data)

    payload = {
        "instances": [images[0].tolist()]
    }

    file_path = "./dogs_image.json"
    with open(file_path, 'w') as outfile:
        json.dump(payload, outfile)
    print("printed")

    return data