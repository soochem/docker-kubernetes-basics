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
        
    - Performance-related parameters
        - batch_size : anchor_beam에서 arm evaluation에 사용하는 sample 수 
        - stop_on_first : p_sample을 충족하는 첫번째 Anchor를 return
        
    - Logs-related parameters
        - verbose
        - verbose_every
        
* KFServing alibiexplainer
    - Ref.
        - [Parser](https://github.com/kubeflow/kfserving/blob/master/python/alibiexplainer/alibiexplainer/parser.py)
    - Parameter spec
        ```
        model_name : default=DEFAULT_EXPLAINER_NAME
        predictor_host
        storage_uri : default=os.environ.get(ENV_STORAGE_URI),
        ```
    
## Test Cases
 
