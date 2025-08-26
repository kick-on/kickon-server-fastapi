# AWS Lambda Python 3.9 베이스 이미지
FROM public.ecr.aws/lambda/python:3.9

# 빌드 툴 설치
RUN yum -y install gcc-c++ swig git make

# Rust 설치 및 PATH 설정
ENV PATH="/root/.cargo/bin:${PATH}"
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y

# 패키지 설치 (캐시 최적화)
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 코드 복사
COPY app/ app/
COPY scripts/ scripts/

# Lambda 핸들러 설정
CMD ["scripts.lambda_handler.lambda_handler"]