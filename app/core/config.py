# 환경변수 및 설정
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = "Kickon API"
    api_version: str = "v1"

    openai_api_key: str
    youtube_api_key: str
    mongo_uri: str
    database_url: str
    
    aws_account_id: str
    aws_region: str
    lambda_function_name: str
    s3_bucket: str     
    s3_prefix: str   

    class Config:
        env_file = ".env"

settings = Settings()