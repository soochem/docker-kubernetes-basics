# Usage of Ablibi Anchors
* 특별히 AnchorImage에 집중
* Version: Alibi v0.4.0

1. 대상 모델
    - 블랙박스
    - 분류
    - 이미지, 텍스트, 정형 데이터

3. Anchors: 생성 및 사용
    - 초기화
        ```
        explainer = AnchorImage(predict_fn, image_shape, segmentation_fn='slic',
                                segmentation_kwargs={'n_segments': 15, 'compactness': 20, 'sigma': .5},
                                images_background=None)
        ```
   
    Q) 궁금증
    * predict_fn은 아무 함수나 넣어도 될까?
    
    * segmentation_fn 종류 별 차이점은?
    
    * images_background란?
        
    * 사용
        ```
        explanation = explainer.explain(image, p_sample=.5)
        ```
        * explainer: AnchorImage
        * image: 인풋
        * explanation: 아웃풋
    
2. Anchors의 input



3. Explainations: Anchors의 output