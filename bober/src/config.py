from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, BaseModel
from pydantic_settings import BaseSettings

PROJECT_DIR = Path(__file__).parent.parent


class Security(BaseModel):
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []


class Server(BaseModel):
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 8080
    SERVER_WORKERS: int = 1
    API_PREFIX: str = "/api"
    DOCS_URL: str = "/docs"
    OPENAPI_URL: str = "/openapi.json"
    REDOC_URL: str = "/redoc"
    OPENAPI_PREFIX: str = ""
    DEBUG: bool = True


class Settings(BaseSettings):
    security: Security
    server: Server


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        security=Security(),
        server=Server(),
    )
