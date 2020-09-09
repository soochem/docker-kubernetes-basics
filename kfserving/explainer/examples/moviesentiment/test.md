# AnchorText - MovieSentiment Test

1. Pre-requisites
    - alibi == 0.3.2
    - dill>=0.2.7.1
    - numpy>=1.8.2
    - scikit-learn == 0.20.3
    - joblib>=0.13.0
    - plotly>=4.2.1
    
2. Inference
    ```
    export INFERENCE_NS="default"
    export MODEL_NAME="moviesentiment"
    export INPUT_PATH="@./input_data.json"
    
    export CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    export SERVICE_HOSTNAME=$(kubectl -n $INFERENCE_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
    echo "$CLUSTER_IP, $SERVICE_HOSTNAME"
    
    curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH > ./output_predict.json
    curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:explain -d $INPUT_PATH > ./output_explain.json
    
    # or online prediction
    curl -H "Host: ${MODEL_NAME}.default.example.com" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict \
    -d '{"instances":["a visually flashy but narratively opaque and emotionally vapid exercise ."]}'
    # another test
    curl -H "Host: ${MODEL_NAME}.default.example.com" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict \ 
    -d '{"instances":["a touching , sophisticated film that almost seems like a documentary in the way it captures an italian immigrant family on the brink of major changes ."]}'
    # explain
    curl -H "Host: ${MODEL_NAME}.default.example.com" http://$CLUSTER_IP/v1/models/$MODEL_NAME:explain \
    -d '{"instances":["a visually flashy but narratively opaque and emotionally vapid exercise ."]}'

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