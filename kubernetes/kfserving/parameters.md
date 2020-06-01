# Controlling Parameters & Optimizing Explainer Performance

## Parameters
* alibi
    - Ref.
        - [AnchorImage.explain](https://docs.seldon.io/projects/alibi/en/latest/api/alibi.explainers.html?highlight=explain#alibi.explainers.AnchorImage.explain)
        - [Usage](https://docs.seldon.io/projects/alibi/en/latest/methods/Anchors.html#Usage)
    - Parameter spec
        - image (ndarray) – Image to be explained.
        - p_sample (float) – Probability for a pixel to be represented by the average value of its superpixel.
        - threshold (float) – Minimum precision threshold.
        - delta (float) – Used to compute beta.
        - tau (float) – Margin between lower confidence bound and minimum precision of upper bound.
        - batch_size (int) – Batch size used for sampling.
        - coverage_samples (int) – Number of samples used to estimate coverage from during result search.
        - beam_size (int) – The number of anchors extended at each step of new anchors construction.
        - stop_on_first (bool) – If True, the beam search algorithm will return the first anchor that has satisfies the probability constraint.
        - min_samples_start (int) – Min number of initial samples.
        - n_covered_ex (int) – How many examples where anchors apply to store for each anchor sampled during search (both examples where prediction on samples agrees/disagrees with desired_label are stored).
        - binary_cache_size (int) – The result search pre-allocates binary_cache_size batches for storing the binary arrays returned during sampling.
        - cache_margin (int) – When only max(cache_margin, batch_size) positions in the binary cache remain empty, a new cache of the same size is pre-allocated to continue buffering samples.
        - verbose (bool) – Display updates during the anchor search iterations.
        - verbose_every (int) – Frequency of displayed iterations during anchor search process.  
        
        |항목|설명|type|default|
        |---|------|---|---|
        |image|인풋 이미지|np.ndarray||
        |p_sample|-|float|0.5|
        |threshold|Precision 역치값|float|0.95|
        |delta|-|float|0.1|
        |tau|-|float|0.15|
        |batch_size|샘플링에 사용되는 배치 크기|int|100|
        |coverage_samples|-|int|10000|
        |beam_size|-|int|1|
        |stop_on_first|조건을 충족하는 첫번째 케이스에서 중단|int|1|
        |max_anchor_size|-|int|None|
        |min_samples_start|처음 샘플 수 최저값|int|100|
        |n_covered_ex|-|int|10|
        |binary_cache_size|-|int|10000|
        |cache_margin|-|int|1000|
        |verbose|Anchor search 중에 로그를 표출할지 여부|bool|False|
        |verbose_every|-|int|1|
    
    - Performance-related parameters
        - batch_size
            - 클수록 많은 시간 소요
            - anchor_beam에서 arm evaluation에 사용하는 sample 수
            - eg. 비교
                ```
                # batch_size = 10
                # 38회 탐색
                Best: 9 (mean:1.0000000000, n: 1, lb:0.0000) Worst: 0 (mean:0.0000, n: 1, ub:1.0000) B = 1.00
                Best: 5 (mean:1.0000000000, n: 1, lb:0.0000) Worst: 2 (mean:0.0000, n: 1, ub:1.0000) B = 1.00
                Best: 1 (mean:1.0000000000, n: 1, lb:0.0000) Worst: 3 (mean:0.0000, n: 1, ub:1.0000) B = 1.00
                Best: 3 (mean:0.4545454545, n: 11, lb:0.0117) Worst: 4 (mean:0.0000, n: 1, ub:1.0000) B = 0.99
                Best: 3 (mean:0.5238095238, n: 21, lb:0.0731) Worst: 6 (mean:0.0000, n: 1, ub:1.0000) B = 0.93
                ...
                Best: 3 (mean:0.5982905983, n: 351, lb:0.4413) Worst: 10 (mean:0.1935, n: 31, ub:0.7051) B = 0.26
                Best of size  1 :
                3 0.5955678670360111 0.5394992171687749 0.650017370590976
                (3,) mean = 0.60 lb = 0.54 ub = 0.65 coverage: 0.50 n: 361
                Best of size  2 :
                9 1.0 0.9689491337632169 1
                (3, 5) mean = 1.00 lb = 0.97 ub = 1.00 coverage: 0.25 n: 73
                Found eligible anchor  (3, 5) Coverage: 0.2541 Is best? True
                time : 15.808969020843506
                ```
        - stop_on_first
            - 시간 단축
            - 조건을 충족하는 첫번째 Anchor를 return
            - eg. 비교
                - batch_size 50일 때, 21.961s --> (stop_on_first) 20.233s
            
        - p_sample 
            - 높을수록 많은 시간 소요
            ``` 
            # p_sampe = 0.5
            Best: 3 (mean:0.9791666667, n: 48, lb:0.7005) Worst: 5 (mean:0.7826, n: 46, ub:0.9732) B = 0.27
            Best of size  1 :
            3 0.9527027027027027 0.9057125839012374 0.981201171875
            (3,) mean = 0.95 lb = 0.91 ub = 0.98 coverage: 0.50 n: 148
            Found eligible anchor  (3,) Coverage: 0.5035 Is best? True
            time : 6.328887701034546
          
            # p_sampe = 0.8
            Best: 9 (mean:1.0000000000, n: 1, lb:0.0000) Worst: 0 (mean:0.0000, n: 1, ub:1.0000) B = 1.00
            Best: 5 (mean:1.0000000000, n: 1, lb:0.0000) Worst: 2 (mean:0.0000, n: 1, ub:1.0000) B = 1.00
            Best: 1 (mean:1.0000000000, n: 1, lb:0.0000) Worst: 3 (mean:0.0000, n: 1, ub:1.0000) B = 1.00
            Best: 3 (mean:0.5544554455, n: 101, lb:0.2946) Worst: 4 (mean:0.0000, n: 1, ub:1.0000) B = 0.71
            Best: 3 (mean:0.5572139303, n: 201, lb:0.3668) Worst: 6 (mean:0.0000, n: 1, ub:1.0000) B = 0.63
            Best: 3 (mean:0.5714285714, n: 301, lb:0.4133) Worst: 7 (mean:0.0000, n: 1, ub:1.0000) B = 0.59
            Best: 3 (mean:0.5760598504, n: 401, lb:0.4379) Worst: 8 (mean:0.0000, n: 1, ub:1.0000) B = 0.56
            Best: 3 (mean:0.5568862275, n: 501, lb:0.4327) Worst: 10 (mean:0.0000, n: 1, ub:1.0000) B = 0.57
            Best of size  1 :
            3 0.5607321131447587 0.5170610606458352 0.6037840733272088
            (3,) mean = 0.56 lb = 0.52 ub = 0.60 coverage: 0.50 n: 601
            Best of size  2 :
            9 1.0 0.9801753307820971 1
            (3, 5) mean = 1.00 lb = 0.98 ub = 1.00 coverage: 0.25 n: 115
            Found eligible anchor  (3, 5) Coverage: 0.2541 Is best? True
            time : 32.07559609413147
            ```
        
    - Logs-related parameters
        - verbose
            - 변수의 의미
                - n : n_samples
                - lb : lower_bound
                - ub : upper_bound
                - Best -> lt, Worst -> ut
                    - lt (cf. for the high precision result candidates, compute the lower precision bound and keep the index of the result candidate with the lowest lower precision value)
            - eg. 로컬에서 테스트
                ```
                Best: 9 (mean:1.0000000000, n: 1, lb:0.0000) Worst: 0 (mean:0.0000, n: 1, ub:1.0000) B = 1.00
                    ...  
                Best: 3 (mean:0.5568862275, n: 501, lb:0.4327) Worst: 10 (mean:0.0000, n: 1, ub:1.0000) B = 0.57
                Best of size  1 :
                3 0.5607321131447587 0.5170610606458352 0.6037840733272088
                (3,) mean = 0.56 lb = 0.52 ub = 0.60 coverage: 0.50 n: 601
                Best of size  2 :
                9 1.0 0.9801753307820971 1
                (3, 5) mean = 1.00 lb = 0.98 ub = 1.00 coverage: 0.25 n: 115
                Found eligible anchor  (3, 5) Coverage: 0.2541 Is best? True
                time : 32.07559609413147
                ```
                        - Kubernetes Pod(kfserving-container)에서 표출 방법
                - [kfserving logger](https://github.com/kubeflow/kfserving/tree/master/docs/samples/logger/basic)
                    ```
                    ### cloud event logs...
                    # logger 생성
                    apiVersion: serving.knative.dev/v1alpha1
                    kind: Service
                    metadata:
                      name: message-dumper
                    spec:
                      template:
                        spec:
                          containers:
                          - image: gcr.io/knative-releases/github.com/knative/eventing-sources/cmd/event_display
                    
                    kubectl create -f message-dumper.yaml
                    
                    # mobnet-stop.yaml 에 추가
                    logger:
                      url: http://message-dumper.default/
                      mode: all
                  
                    # to see output
                    kubectl logs $(kubectl get pod -l serving.knative.dev/service=message-dumper \
                    -o jsonpath='{.items[0].metadata.name}') user-container
                    ```
                - KFServing Logger
                    - [knative eventing component](https://knative.dev/docs/eventing/getting-started/)
                    ```
                    kubectl label namespace default knative-eventing-injection=enabled
                    ```
                - ENV에 추가 : PYTHONUNBUFFERED=1
        - verbose_every : 매 스텝마다 로그를 남김
        
* KFServing alibiexplainer
    - Ref.
        - [Parser](https://github.com/kubeflow/kfserving/blob/master/python/alibiexplainer/alibiexplainer/parser.py)
    - Parameter spec
        - model_name : default=DEFAULT_EXPLAINER_NAME
        - predictor_host
        - storage_uri : default=os.environ.get(ENV_STORAGE_URI),
        
        
* KFServer
    - http_port : default=DEFAULT_HTTP_PORT (8080)
    - grpc_port : default=DEFAULT_GRPC_PORT (8081)
    - max_buffer_size : default=DEFAULT_MAX_BUFFER_SIZE (104857600)
    - workers : 0
    
## Test Cases
 
