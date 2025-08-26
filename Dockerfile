# AWS Lambda Python 3.9 베이스 이미지
FROM public.ecr.aws/lambda/python:3.9

# 빌드 툴 설치
RUN yum -y install gcc-c++ swig git make

# 패키지 설치 (캐시 최적화)
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV HF_HOME=/opt/huggingface_cache
ENV TRANSFORMERS_CACHE=/var/task/huggingface_cache

# 모델 캐시 미리 다운로드
RUN mkdir -p $HF_HOME && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 코드 복사
COPY app/ app/
COPY scripts/ scripts/

# Lambda 핸들러 설정
CMD ["scripts.lambda_handler.lambda_handler"]