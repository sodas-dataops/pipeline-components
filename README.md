# SODASops: Containerized Pipeline Components

SODASops는 다양한 유형의 데이터를 대상으로 분석, 전처리, 시각화, 변환 작업을 수행하는 데이터 파이프라인 기술을 포함하며, 본 서브프로젝트는 개별 태스크 컴포넌트를 구현한 **컨테이너형 데이터 파이프라인 컴포넌트 컬렉션**입니다.
모든 태스크는 독립적인 Python 컨테이너로 구성되며, Argo Workflows, Kubernetes 기반 데이터 워크플로우 환경에서 컨테이너로 쉽게 동작할 수 있도록 개발되었습니다.

## 지원 컴포넌트 목록

**CSV 기반 연산**

- [`csv-arithmetic-operation`](./csv-arithmetic-operation/)
- [`csv-change-column-name`](./csv-change-column-name/)
- [`csv-column-concat`](./csv-column-concat/)
- [`csv-cosine-similarity`](./csv-cosine-similarity/)
- [`csv-date-time-formatter`](./csv-date-time-formatter/)
- [`csv-delete-missing-value`](./csv-delete-missing-value/)
- [`csv-embedding`](./csv-embedding/)
- [`csv-from-parquet`](./csv-from-parquet/)
- [`csv-get-latlon`](./csv-get-latlon/)
- [`csv-join`](./csv-join/)
- [`csv-merge`](./csv-merge/)
- [`csv-regex`](./csv-regex/)
- [`csv-sort`](./csv-sort/)
- [`csv-statistic-summary`](./csv-statistic-summary/)
- [`csv-tokenize`](./csv-tokenize/)
- [`csv-transform`](./csv-transform/)
- [`csv-wordcount`](./csv-wordcount/)

**CSV 기반 시각화**

- [`csv-visualization-barchart`](./csv-visualization-barchart/)
- [`csv-visualization-boxplot`](./csv-visualization-boxplot/)
- [`csv-visualization-histogram`](./csv-visualization-histogram/)
- [`csv-visualization-map`](./csv-visualization-map/)
- [`csv-visualization-pairplot`](./csv-visualization-pairplot/)
- [`csv-visualization-piechart`](./csv-visualization-piechart/)
- [`csv-visualization-wordcloud`](./csv-visualization-wordcloud/)

**JSON 처리**

- [`json-merge`](./json-merge/)
- [`json-merge-from-directory`](./json-merge-from-directory/)
- [`json-to-csv`](./json-to-csv/)
- [`json-upload`](./json-upload/)

**기타 데이터 유틸리티**

- [`csv-to-json`](./csv-to-json/)
- [`upload-object-file-to-restapi`](./upload-object-file-to-restapi/)
- [`sodas-append-dataset-to-datasetseries`](./sodas-append-dataset-to-datasetseries/)

---

## 구성 구조

각 컴포넌트는 다음 구조를 가집니다:

```
component/
├── config
│   └── config.py     # 설정값 정의
├── tmp/              # 임시 파일
├── .dockerignore     # 컨테이너 빌드 제외
├── algorithm.py      # 로직 구현
├── Dockerfile        # 컨테이너 빌드 정의
├── main.py           # Entrypoint
├── requirements.txt  # 의존성
└── test.py           # 로직 테스트
```

---

## 실행 방식

### TBD

## 라이선스

Licensed under the [SODASops License and Service Agreement](LICENSE).

## 기여 및 문의

담당자: Siwoon Son (ETRI CybreBrain Section)
이메일: siwoonson@etri.re.kr