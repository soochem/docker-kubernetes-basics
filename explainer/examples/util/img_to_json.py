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


def get_image_data(image_paths
                   , image_shape
                   , save_path="./dogs_image.json"):
    data = []
    # image_shape = (224, 224, 3)
    target_size = image_shape[:2]

    for path in image_paths:
        image = Image.open(path).convert('RGB')
        image = np.expand_dims(image.resize(target_size), axis=0)
        data.append(image)

    data = np.concatenate(data, axis=0)
    # print(data)

    # image procsessing
    images = preprocess_input(data)

    payload = {
        # "instances": [images[0].tolist()]
        "instances": images.tolist()
    }

    # save_path = "./dogs_image.json"
    with open(save_path, 'w') as outfile:
        json.dump(payload, outfile)

    print("image converted to json")

    return data

prefix = '../mobilenet/data/'
paths = [prefix+'cat_224.png', prefix+'dog.jpg']
image_shape = (224, 224, 3)
get_image_data(paths, image_shape, prefix+"dog_images.json")