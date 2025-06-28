# 환경변수 및 설정
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = "Kickon API"
    api_version: str = "v1"

    openai_api_key: str 

    class Config:
        env_file = ".env"

settings = Settings()