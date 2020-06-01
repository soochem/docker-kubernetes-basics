# KFServing Explainer

## Introduction to Explainer
1. [Parameters](parameters.md)
2. [Tests](./test/test.md)

## Install
- Prerequisite
  - Knative
      0. Test Version : v1.14.0
         1. Eventing
            ```
            kubectl apply --filename https://github.com/knative/eventing/releases/download/v0.14.0/eventing-crds.yaml
            kubectl apply --filename https://github.com/knative/eventing/releases/download/v0.14.0/eventing-core.yaml
           
            output:
                ...
                validatingwebhookconfiguration.admissionregistration.k8s.io/config.webhook.eventing.knative.dev created
                mutatingwebhookconfiguration.admissionregistration.k8s.io/webhook.eventing.knative.dev created
                validatingwebhookconfiguration.admissionregistration.k8s.io/validation.webhook.eventing.knative.dev created
                secret/eventing-webhook-certs created
                mutatingwebhookconfiguration.admissionregistration.k8s.io/sinkbindings.webhook.sources.knative.dev created
            ```
            ```
            # 추가 적용
            kubectl apply  --selector knative.dev/crd-install=true \\
            --filename https://github.com/knative/eventing/releases/download/v0.14.0/eventing.yaml
            kubectl apply --filename https://github.com/knative/eventing/releases/download/v0.14.0/eventing.yaml
            kubectl apply --filename https://github.com/knative/eventing/releases/download/v0.14.0/in-memory-channel.yaml
            kubectl apply --filename https://github.com/knative/eventing/releases/download/v0.14.0/channel-broker.yaml
            ```
            
        2. Monitoring
            ```
            # Cores
            kubectl apply --filename https://github.com/knative/serving/releases/download/v0.14.0/monitoring-core.yaml
            # Prometheus & Grafana 
            kubectl apply --filename https://github.com/knative/serving/releases/download/v0.14.0/monitoring-metrics-prometheus.yaml
            
            output:
                ...
                clusterrolebinding.rbac.authorization.k8s.io/prometheus-system created
                service/prometheus-system-np created
                statefulset.apps/prometheus-system created
            ```
        
        3. Logging
            ```
            Kibana-* 추가
            kubectl apply --filename https://github.com/knative/serving/releases/download/v0.14.0/monitoring-logs-elasticsearch.yaml
            ```
  - Alibi
      0. Test Version : v0.1.2
      1. 특징
          - Python 라이브러리 오픈소스
          - 목적 : ML model 설명, black-box & instance based model 설명
          - ref. [docs](https://docs.seldon.io/projects/alibi/en/stable/)
      2. [Python] requirements.txt
          ```
           alibi>=0.1.2
           numpy>=1.8.2
           tensorflow>=1.13.1
           joblib>=0.13.0
           dill>=0.2.7.1
           ```
          - Error #1
              ```
               Building wheel for shap (setup.py) ... error
               gcc: error trying to exec 'cc1plus': execvp: 그런 파일이나 디렉터리가 없습니다
               ```
              - Solution #1
                  ```
                   sudo yum install gcc gcc-c++
                   sudo apt-get install g++ (ubutu)
                   ```
      3. Setting envirionments
          ```
          conda create -n test_env python={my_version}
          activate test_env
          pip install -r requirements.txt
          ```
   
## What Is Explainer?
- Kfserving은 1 종류의 Explainer 오픈소스를 제공하고 있다. (Alibi)
- Kfserving은 3 종류의 Explainer Type (Anchors methods)를 제공하고 있다.
    - 지원되는 Model 종류 : black-box
    - 지원되는 Data 종류 : Text, Tabular, Images
    - cf. 전체 Alibi Explainer 종류 (6가지)
        ```
         'AnchorTabular',
         'AnchorText',
         'AnchorImage',
         'CEM',
         'CounterFactual',
         'CounterFactualProto'
         'KernelShap'
        ```
- 어떤 결과를 보여주는가?
    - Text
    - Tabular
    - Images
        - Segmentation 기법 이용 (Hyperparameter Tuning을 추천한다.)
        - Superpixel을 생성
            - 예시 그림   
                ![origin](https://docs.seldon.io/projects/alibi/en/stable/_images/persiancat.png)
                ![superpixel](https://docs.seldon.io/projects/alibi/en/stable/_images/persiancatsegm.png)
            - Superpixel과 SLIC : superpixel이란 perceptually meaningful pixels를 모아 그룹화한 것
            
        - Output : Black-box Model에서 가장 의미 있는 Semgment를 보여준다.   
            ![output](https://docs.seldon.io/projects/alibi/en/stable/_images/persiancatanchor.png)
- REST API
    - cf. Tensorflow REST API
        - POST http://host:port/v1/models/${MODEL_NAME}[/versions/${MODEL_VERSION}]:predict

## Quick Starts
- Inference Service 생성
  - InferenceService 생성 시 yaml 파일에서 spec으로 준다.
      ```
       kind: "InferenceService"
       metadata:
         name: "imagenet"
       spec:
         default:
           predictor:
             tensorflow:
               storageUri: "gs://seldon-models/tfserving/imagenet/model"
               resources:
                 requests:
                   cpu: 0.1
                   memory: 5Gi
                 limits:
                   memory: 10Gi
           explainer:
             alibi:
               type: AnchorImages
               storageUri: "gs://seldon-models/tfserving/imagenet/explainer"
               config:
                 batch_size: "25"
               resources:
                 requests:
                   cpu: 0.1
                   memory: 5Gi
                 limits:
                   memory: 10Gi
       ```
- Inference를 위한 Input 준비
  - Input Data Type: json
  - 이미지 읽어오기
       ```
       # get image and convert it to np array
       def get_image_data():
           data = []
           image_shape = (299, 299, 3)  # change to my shape
           target_size = image_shape[:2]
           image = Image.open("./cat-prediction.png").convert('RGB')
           image = np.expand_dims(image.resize(target_size), axis=0)
           data.append(image)
           data = np.concatenate(data, axis=0)
           return data
       ```
  - 데이터(json) 저장
       ```
       # array to list, list to json (dict)
       data = get_image_data()
       images = preprocess_input(data)
    
       payload = {
           "instances": [images[0].tolist()]
       }
      
       file_path = "./input_image.json"
       with open(file_path, 'w') as outfile:
           json.dump(payload, outfile)
       ```
 
- Inference (Explain)
    - 요청
      1. Python (requests module 사용)
          - python3 test_imagenet.py --op=explain
      2. Curl
          - curl -v -H "Host: imagenet.sklearn.example.com" http://{external_ip}:31380/v1/models/imagenet:explain -d @./input_image.json    
          - curl option   
            --connect-timeout : 300 / in second   
            --max-time : 900 / in second
    - 결과
      - Custom MobileNet   
        ex.   
        ```
        export INFERENCE_NS="default"
        # 예제
        #export MODEL_NAME="imagenet"
        #export INPUT_PATH="@./input_image.json"
        # Custom
        #export MODEL_NAME="mobnet"
        export MODEL_NAME="mobnet-full"
        export INPUT_PATH="@./dogs_image.json"
        
        # Delay 조정
        #kubectl -n $INFERENCE_NS wait --for=condition=ready --timeout=90s\
        #    inferenceservice $MODEL_NAME
        export CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        export SERVICE_HOSTNAME=$(kubectl -n $INFERENCE_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
        echo "$CLUSTER_IP, $SERVICE_HOSTNAME"
        
        curl -v -H "Host: ${SERVICE_HOSTNAME}" http://${CLUSTER_IP}/v1/models/${MODEL_NAME}:predict -d ${INPUT_PATH} > ./output_predict.json        
        curl -v -H "Host: ${SERVICE_HOSTNAME}" http://${CLUSTER_IP}/v1/models/${MODEL_NAME}:explain -d ${INPUT_PATH} > ./output_explain.json
        ```
        
        ```
        # to compare (Explainer, Predictor, Transformer full set)
        MODEL_NAME="mobilenet-fullstack"
        SERVICE_HOSTNAME=$(kubectl -n $INFERENCE_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
        echo "$CLUSTER_IP, $SERVICE_HOSTNAME"
        
        curl -v -H "Host: ${SERVICE_HOSTNAME}" http://{cluster_ip}/v1/models/mobnet:explain -d @./dogs_image.json > ./output_explain.json
        
        output:
            * About to connect() to {cluster_ip} port 80 (#0)
            *   Trying {cluster_ip}...
              % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                             Dload  Upload   Total   Spent    Left  Speed
              0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0* Connected to {cluster_ip} port 80 (#0)
            > POST /v1/models/mobilenet-fullstack:explain HTTP/1.1
            > User-Agent: curl/7.29.0
            > Accept: */*
            > Host: mobilenet-fullstack.default.{cluster_ip}.xip.io
            > Content-Length: 3208634
            > Content-Type: application/x-www-form-urlencoded
            > Expect: 100-continue
            >
            < HTTP/1.1 100 Continue
            } [data not shown]
            100 3133k    0     0  100 3133k      0  16688  0:03:12  0:03:12 --:--:--     0< HTTP/1.1 200 OK
            < content-length: 17225838
            < content-type: application/json; charset=UTF-8
            < date: Mon, 25 May 2020 08:31:48 GMT
            < server: istio-envoy
            < x-envoy-upstream-service-time: 192782
            <
            { [data not shown]
            100 19.4M  100 16.4M  100 3133k  88894  16558  0:03:13  0:03:13 --:--:-- 3894k
            * Connection #0 to host {cluster_ip} left intact
        ```
      
      - [Log] Transformer kfserving-container
        ```
        │ [I 200527 02:07:00 mobilenet_transformer:158] dict_keys(['predictions'])
        │ [I 200527 02:07:00 mobilenet_transformer:116] postprocess_fn:input: type: <class 'list'> shape
        │ [I 200527 02:07:00 mobilenet_transformer:126] postprocess_fn:output: type: <class 'list'> shap
        │ [I 200527 02:07:00 mobilenet_transformer:164] postprocess:output: type: <class 'dict'> shape:
        │ [I 200527 02:07:00 web:2250] 200 POST /v1/models/mobnet-full:predict (127.0.0.1) 10190.23ms
        │ [I 200527 02:07:00 mobilenet_transformer:138] preprocess:input: type: <class 'list'> shape: [l
        │ [I 200527 02:07:00 mobilenet_transformer:89] preprocess_fn:input: type:<class 'list'> shape:[l
        │ [I 200527 02:07:01 mobilenet_transformer:107] preprocess_fn:output: type: <class 'list'> shape
        │ [I 200527 02:07:01 mobilenet_transformer:142] preprocess:input: type: <class 'list'> shape: [l
        │ [I 200527 02:07:01 mobilenet_transformer:148] preprocess:output: type: <class 'dict'> shape: [
        │ [I 200527 02:07:01 mobilenet_transformer:156] postprocess:input: type: <class 'dict'> shape: [
        │ [I 200527 02:07:01 mobilenet_transformer:158] dict_keys(['predictions'])
        │ [I 200527 02:07:01 mobilenet_transformer:116] postprocess_fn:input: type: <class 'list'> shape
        │ [I 200527 02:07:01 mobilenet_transformer:126] postprocess_fn:output: type: <class 'list'> shap
        │ [I 200527 02:07:01 mobilenet_transformer:164] postprocess:output: type: <class 'dict'> shape:
        │ [I 200527 02:07:01 web:2250] 200 POST /v1/models/mobnet-full:predict (127.0.0.1) 433.92ms
        ```
      - [Log] Explainer kfserving-container
        ```
        │ [I 200527 02:04:26 __main__:116] Extra args: {'batch_size': 20}
        │ [I 200527 02:04:26 storage:35] Copying contents of /mnt/models to local
        │ [I 200527 02:04:26 __main__:125] Loading Alibi model
        │ [I 200527 02:04:26 explainer:47] Predict URL set to mobnet-full-transformer-default.default
        │ [I 200527 02:04:26 kfserver:88] Registering model: mobnet-full
        │ [I 200527 02:04:26 kfserver:77] Listening on port 8080
        │ [I 200527 02:04:26 kfserver:79] Will fork 0 workers
        │ [I 200527 02:04:26 process:126] Starting 4 processes
        │ [I 200527 02:04:47 anchor_images:35] Calling explain on image of shape ((1, 224, 224, 3),)
        │ /usr/local/lib/python3.7/site-packages/alibi/explainers/anchor_image.py:58: FutureWarning: ski
        │   self.segmentation_fn = lambda x: fn_options[segmentation_fn](x, **segmentation_kwargs)
        │ [I 200527 02:07:01 explainer:75] Explanation: {'anchor': array([[[  0,   0,   0],
        |                 ...
        │             [[ 0.1686275 , -0.23921567, -0.54509807],
        │             [ 0.1686275 , -0.23921567, -0.54509807],
        │             [ 0.20784318, -0.19999999, -0.50588238],
        │             ...,
        │             [ 0.96078432,  0.95294118,  0.70980394],
        │             [ 1.        ,  1.        ,  0.7647059 ],
        │             [ 0.99215686,  0.98431373,  0.74117649]],
        │
        │            [[ 0.26274514, -0.14509803, -0.45098037],
        │             [ 0.19215691, -0.21568626, -0.52156866],
        │             [ 0.21568632, -0.19215685, -0.49803919],
        │             ...,
        │             [ 0.93725491,  0.93725491,  0.67058825],
        │             [ 1.        ,  1.        ,  0.77254903],
        │             [ 0.99215686,  0.98431373,  0.74117649]]]), 'prediction': 530}, 'meta': {'name': 'AnchorImage'}}
        │ [I 200527 02:07:06 web:2250] 200 POST /v1/models/mobnet-full:explain (127.0.0.1) 138540.48m
        ```
      - 변수 조정
        - batch = 1
            ```
            output:
                | [I 200527 02:16:20 __main__:116] Extra args: {'batch_size': 1}
                   ...
                | [ 0.97647059,  0.97647059,  0.70980394]]]), 'prediction': 530}, 'meta': {'name': '
                │ [I 200527 05:06:52 web:2250] 200 POST /v1/models/mobnet-full:explain (127.0.0.1) 182604.28ms
            ```
            247 POST 요청 (Transformer)
        - batch = 100
            ```
            output: 
                /workspace/mobilenet_transformer.py:23: DeprecationWarning: Using or importing the ABCs from '
                │   assert isinstance(iterable, collections.Iterable), 'Not an Iterable.'
                │ [I 200527 05:53:36 mobilenet_transformer:138] preprocess:input: type: <class 'list'> shape: [l
                │
                    ...
                
            ```
        - 실행횟수 count
          kubectl -n $INFERENCE_NS logs \
          "$(kubectl -n $INFERENCE_NS get pods -l model=$MODEL_NAME,component=transformer \
          -o jsonpath='{.items[0].metadata.name}')" -c kfserving-container > transformer.log
          
          (vim) %s/prediction//gn
          grep -i -o prediction ./transformer.log|wc -l
          grep -c prediction ./transformer.log 
          
 
  - Error #1. kubectl describe inferenceservice imagenet  
      - Solution: Wait for a second (until Explainer is created)
          ```
           Status:                False
           Type:                  Ready
           Last Transition Time:  2020-05-13T08:24:04Z
           Message:               Failed to reconcile explainer
           Reason:                ExplainerHostnameUnknown
           ```
  
  - Error #2. python test_imagenet.py
       - Solution
          - default --> namespace in `headers = {'Host':'imagenet.default.example.com'}`
          - python test_imagenet.py --clutser-ip=$CLUSTER_IP
          ```
           requests.exceptions.ConnectionError: HTTPConnectionPool(host='none', port=80):
           Max retries exceeded with url: /v1/models/imagenet:predict
           (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7f4ada9d7650>:
           Failed to establish a new connection: [Errno -2] Name or service not known'))
           ```
   
  - Error #3. Connetction aborted (108)
       ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
      - 한 번의 응답 후 connection을 닫아버림. 해당 url에 아무 정보도 없다는 것일 수 있다.
      - url 주소를 다시 확인, namespace 등이 바르게 설정되어 있는가?

  - Error #4.
       ```
       raise ConnectionError(e, request=request)
       requests.exceptions.ConnectionError: HTTPConnectionPool(host='none', port=80): Max retries exceeded with url: /v1/models/imagenet:predict (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7f1add1d0510>: Failed to establish a new connection: [Errno -2] Name or service not known'))
       ```
      - Solution 
          - Check if your $CLUSTER_IP exits : `echo $CLUSTER_IP`
          - Redo
              ```
               INGRESS_GATEWAY=istio-ingressgateway
               export CLUSTER_IP=$(kubectl -n istio-system get service $INGRESS_GATEWAY -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
               echo $INGRESS_GATEWAY, CLUSTER_IP
               ```
  - Error #5. 
      - Internal Server Error (500)
         - explainer.dill의 문제일 가능성 높다. 

      - Upstream time out (504)
         - (원인 밝히는 중 : response time이 길어져서, 또는 transformer가 Explainer 동작에 필요)
         - Solution
                - transformer를 사용하면 응답이 빠르다. (kfserving alibiexplainer 결함 추정)
                - batch_size를 작게하고 stop_in_first를 사용한다.
              ```
              config:
                batch_size: "25"
                stop_in_first: "True"
              ```

- cf. Inference 결과 (Prection)
  ```
   curl -v -H "Host: imagenet.sklearn.example.com" http://{external_ip}:31380/v1/models/imagenet:predict -d @./input_image.json
   output: 
       * About to connect() to {external_ip} port 31380 (#0)
       *   Trying {external_ip}...
       * Connected to {external_ip} ({external_ip}) port 31380 (#0)
       > POST /v1/models/imagenet:predict HTTP/1.1
       > User-Agent: curl/7.29.0
       > Accept: */*
       > Host: imagenet.sklearn.example.com
       > Content-Length: 3718458
       > Content-Type: application/x-www-form-urlencoded
       > Expect: 100-continue
       >
       < HTTP/1.1 100 Continue
       < HTTP/1.1 200 OK
       < content-length: 15826
       < content-type: application/json
       < date: Wed, 13 May 2020 09:12:41 GMT
       < x-envoy-upstream-service-time: 8287
       < server: istio-envoy
       <
       {
           "predictions": [[3.16306723e-05, 1.35796718e-05, 5.8721751e-05, 3.79929515e-05, 2.23336483e-05,
           8.18260305e-05, 2.03333893e-05, 2.97131901e-05, 3.50741939e-05, 0.000116876072, 5.42406742e-05, ...
   ```
