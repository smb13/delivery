from fastapi import FastAPI, Request
from fastapi.responses import Response
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    http_port: int = 8082


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_", extra="ignore")

    host: str = "localhost"
    port: int = 5432
    name: str = "delivery"
    user: str = "username"
    password: str = "secret"
    sslmode: str = "disable"

    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}?sslmode={self.sslmode}"
        )


class KafkaConsumerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KAFKA_", extra="ignore")

    host: str = "localhost:9092"
    consumer_group: str = "delivery-group"


def register_global_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def handle_unexpected(_request: Request, _exc: Exception) -> Response:
        return Response(status_code=500)
