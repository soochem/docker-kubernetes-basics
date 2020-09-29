import argparse
import matplotlib.pyplot as plt
from tensorflow.keras.applications.mobilenet import MobileNet, preprocess_input, decode_predictions
# from alibi.datasets import fetch_imagenet
import numpy as np
import requests
import json
import os
from PIL import Image
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

PREDICT_TEMPLATE = 'http://{0}/v1/models/mobnet-full:predict'
EXPLAIN_TEMPLATE = 'http://{0}/v1/models/mobnet-full:explain'
IMG_SHAPE = (224, 224, 3)


def get_image_data():
    data = []
    image_shape = IMG_SHAPE
    target_size = image_shape[:2]
    image = Image.open("./dogs.jpeg").convert('RGB')
    image = np.expand_dims(image.resize(target_size), axis=0)
    data.append(image)
    data = np.concatenate(data, axis=0)
    return data


def predict(model_name, namespace, cluster_ip):
    data = get_image_data()
    images = preprocess_input(data)

    payload = {
        "instances": [images[0].tolist()]
    }

    # sending post request to TensorFlow Serving server
    headers = {'Host': model_name + '.' + namespace + '.' + cluster_ip + '.xip.io'}
    print(headers)
    url = PREDICT_TEMPLATE.format(cluster_ip)
    print("Calling ", url)
    r = requests.post(url, json=payload, headers=headers)
    resp_json = json.loads(r.content.decode('utf-8'))
    preds = np.array(resp_json["predictions"])
    label = decode_predictions(preds, top=1)

    plt.imshow(data[0])
    plt.title(label[0])
    plt.show()


def explain(model_name, namespace, cluster_ip):
    data = get_image_data()
    images = preprocess_input(data)

    payload = {
        "instances": [images[0].tolist()]
    }

    # sending post request to TensorFlow Serving server
    headers = {'Host': model_name + '.' + namespace + '.' + cluster_ip + '.xip.io'}
    print(headers)
    url = EXPLAIN_TEMPLATE.format(cluster_ip)
    print("Calling ", url)
    r = requests.post(url, json=payload, headers=headers, timeout=36000)
    if r.status_code == 200:
        explanation = json.loads(r.content.decode('utf-8'))
        exp_arr = np.array(explanation['anchor'])

        # save
        with open("exp_output.json", 'wb') as f:
            json.dump(exp_arr, f)  # ndarray?

        f, axarr = plt.subplots(1, 2)
        axarr[0].imshow(data[0])
        axarr[1].imshow(explanation['anchor'])
        plt.show()
    else:
        print("Received response code and content", r.status_code, r.content)


# to parse
parser = argparse.ArgumentParser()
parser.add_argument('--model_name', default=os.environ.get("MODEL_NAME"))
parser.add_argument('--namespace', default=os.environ.get("INFERENCE_NS"))
parser.add_argument('--cluster_ip', default=os.environ.get("CLUSTER_IP"), help='Cluster IP of Istio Ingress Gateway')
parser.add_argument('--op', choices=["predict", "explain"], default="predict",
                    help='Operation to run')
args, _ = parser.parse_known_args()

if __name__ == "__main__":
    if args.op == "predict":
        predict(args.model_name, args.namespace, args.cluster_ip)
    elif args.op == "explain":
        explain(args.model_name, args.namespace, args.cluster_ip)

# to test
# cluster_ip = os.environ.get("CLUSTER_IP")
# predict("default", cluster_ip)
# predict("default", cluster_ip)
