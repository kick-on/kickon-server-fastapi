from pydantic import BaseSettings

class Settings(BaseSettings):
    project_name: str = "Kickon API"
    api_version: str = "v1"

    class Config:
        env_file = ".env"

settings = Settings()