from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from microarch.delivery.application_properties import ApplicationProperties
from microarch.delivery.config.application_event_publisher import ApplicationEventPublisher
from microarch.delivery.default_domain_event_publisher import DefaultDomainEventPublisher
from microarch.delivery.global_exception_handler import (
    DatabaseSettings,
    KafkaConsumerSettings,
    register_global_exception_handler,
)


def create_database_engine(settings: DatabaseSettings | None = None) -> AsyncEngine:
    db_settings = settings or DatabaseSettings()
    return create_async_engine(db_settings.url, echo=True)


def create_app(
    *,
    properties: ApplicationProperties | None = None,
    engine: AsyncEngine | None = None,
) -> FastAPI:
    app_properties = properties or ApplicationProperties()
    db_settings = DatabaseSettings()
    kafka_settings = KafkaConsumerSettings()

    db_engine = engine or create_database_engine(db_settings)
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    event_publisher = ApplicationEventPublisher()
    domain_event_publisher = DefaultDomainEventPublisher(event_publisher)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        yield
        await db_engine.dispose()

    app = FastAPI(
        title="Delivery Service",
        description="Microservice for managing orders",
        lifespan=lifespan,
    )

    app.state.properties = app_properties
    app.state.db_engine = db_engine
    app.state.session_factory = session_factory
    app.state.event_publisher = event_publisher
    app.state.domain_event_publisher = domain_event_publisher
    app.state.kafka_bootstrap_servers = kafka_settings.host
    app.state.kafka_consumer_group = kafka_settings.consumer_group

    register_global_exception_handler(app)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def main() -> None:
    import uvicorn

    from microarch.delivery.global_exception_handler import ServerSettings

    settings = ServerSettings()
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=settings.http_port)


if __name__ == "__main__":
    main()
