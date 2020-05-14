# KFServing Explainer

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
          - python3 test_imagenet2.py --op=explain
      2. Curl
          - curl -v -H "Host: imagenet.sklearn.example.com" http://{external_ip}:31380/v1/models/imagenet:explain -d @./input_image.json    
    - 결과 
      - Error #1. 응답없음
          - Solution :

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
          - python test_imagenet.py -- clutser-ip=$CLUSTER_IP
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
          - redo
              ```
               INGRESS_GATEWAY=istio-ingressgateway
               export CLUSTER_IP=$(kubectl -n istio-system get service $INGRESS_GATEWAY -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
               echo $INGRESS_GATEWAY, CLUSTER_IP
               ```
