# MobileNet Test

1. Pre-requisites
    - alibi == 0.3.2
    - tensorflow == 1.15.3
    
2. Inference
    ```
    export INFERENCE_NS="pavin"
    export MODEL_NAME="mobnet-gs"
    export INPUT_PATH="@./data/dog_images.json"
    export INPUT_PATH="@./data/dog_image.json"
    
    export CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    export SERVICE_HOSTNAME=$(kubectl -n $INFERENCE_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
    echo "$CLUSTER_IP, $SERVICE_HOSTNAME"
    
    curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH > ./output_predict2.json
    curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/mobnet-gs:explain -d $INPUT_PATH > ./output_explain2.json
    ```   
   
3. log
    ```
    # transformer
    kubectl -n $INFERENCE_NS logs \
          "$(kubectl -n $INFERENCE_NS get pods -l model=$MODEL_NAME,component=transformer \
          -o jsonpath='{.items[0].metadata.name}')" -c kfserving-container > transformer.log
    # predictor 
    kubectl -n $INFERENCE_NS logs \
          "$(kubectl -n $INFERENCE_NS get pods -l model=$MODEL_NAME,component=predictor \
          -o jsonpath='{.items[0].metadata.name}')" -c kfserving-container > predictor.log
    # explainer
    kubectl -n $INFERENCE_NS logs \
          "$(kubectl -n $INFERENCE_NS get pods -l model=$MODEL_NAME,component=explainer \
          -o jsonpath='{.items[0].metadata.name}')" -c kfserving-container > explainer.log
    ```