from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import timedelta

from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from taskiq.cli.scheduler.run import SchedulerLoop

from microarch.delivery.adapters.in_.kafka import (
    BasketConfirmedIntegrationEventHandler,
    KafkaConsumer,
)
from microarch.delivery.adapters.out.grpc.geo_client_impl import GeoClientImpl
from microarch.delivery.adapters.out.kafka.order_events_producer import (
    OrderEventsKafkaProducer,
)
from microarch.delivery.application_properties import ApplicationProperties
from microarch.delivery.core.ports.domain_event_publisher import IDomainEventPublisher
from microarch.delivery.core.ports.geo_client import IGeoClient
from microarch.delivery.core.ports.integration_event_consumer import (
    IIntegrationEventConsumer,
)
from microarch.delivery.default_domain_event_publisher import (
    DefaultDomainEventPublisher,
)
from microarch.delivery.global_exception_handler import (
    DatabaseSettings,
    KafkaConsumerSettings,
    register_global_exception_handler,
)
from microarch.delivery.tasks import configure_taskiq, scheduler


def create_database_engine(settings: DatabaseSettings | None = None) -> AsyncEngine:
    db_settings = settings or DatabaseSettings()
    return create_async_engine(db_settings.url, echo=True)


def create_app(
    *,
    properties: ApplicationProperties | None = None,
    engine: AsyncEngine | None = None,
    geo_client: IGeoClient | None = None,
    integration_event_consumer: IIntegrationEventConsumer | None = None,
    order_events_producer: IDomainEventPublisher | None = None,
) -> FastAPI:
    app_properties = properties or ApplicationProperties()
    db_settings = DatabaseSettings()
    kafka_settings = KafkaConsumerSettings()

    db_engine = engine or create_database_engine(db_settings)
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    app_geo_client = geo_client or GeoClientImpl(
        host=app_properties.grpc.geo_service.host,
        port=app_properties.grpc.geo_service.port,
    )

    basket_confirmed_handler = BasketConfirmedIntegrationEventHandler(
        session_factory=session_factory,
        geo_client=app_geo_client,
    )
    app_integration_event_consumer = integration_event_consumer or KafkaConsumer(
        bootstrap_servers=kafka_settings.host,
        group_id=kafka_settings.consumer_group,
        topic=app_properties.kafka.basket_events_topic,
        handler=basket_confirmed_handler,
    )

    app_order_events_producer = order_events_producer

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        nonlocal app_order_events_producer

        order_events_kafka_producer: AIOKafkaProducer | None = None
        if app_order_events_producer is None:
            order_events_kafka_producer = AIOKafkaProducer(
                bootstrap_servers=kafka_settings.host,
            )
            await order_events_kafka_producer.start()
            app_order_events_producer = OrderEventsKafkaProducer(
                producer=order_events_kafka_producer,
                topic=app_properties.kafka.order_events_topic,
            )

        domain_event_publisher = DefaultDomainEventPublisher(
            app_order_events_producer,
        )
        _app.state.domain_event_publisher = domain_event_publisher

        configure_taskiq(db_engine, domain_event_publisher)
        await scheduler.startup()
        for source in scheduler.sources:
            await source.startup()

        scheduler_loop = SchedulerLoop(scheduler)
        scheduler_task = asyncio.create_task(
            scheduler_loop.run(loop_interval=timedelta(seconds=1)),
        )
        await app_integration_event_consumer.start()

        yield

        await app_integration_event_consumer.stop()
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass
        await scheduler.shutdown()
        for source in scheduler.sources:
            await source.shutdown()
        if order_events_kafka_producer is not None:
            await order_events_kafka_producer.stop()
        await db_engine.dispose()

    app = FastAPI(
        title="Delivery Service",
        description="Microservice for managing orders",
        lifespan=lifespan,
    )

    app.state.properties = app_properties
    app.state.db_engine = db_engine
    app.state.session_factory = session_factory
    app.state.domain_event_publisher = None
    app.state.geo_client = app_geo_client
    app.state.kafka_bootstrap_servers = kafka_settings.host
    app.state.kafka_consumer_group = kafka_settings.consumer_group
    app.state.integration_event_consumer = app_integration_event_consumer
    app.state.order_events_producer = app_order_events_producer

    register_global_exception_handler(app)

    from microarch.delivery.adapters.in_.http.api.complete_order_api import (
        router as complete_order_router,
    )
    from microarch.delivery.adapters.in_.http.api.create_courier_api import (
        router as create_courier_router,
    )
    from microarch.delivery.adapters.in_.http.api.create_order_api import (
        router as create_order_router,
    )
    from microarch.delivery.adapters.in_.http.api.get_couriers_api import (
        router as get_couriers_router,
    )
    from microarch.delivery.adapters.in_.http.api.get_orders_api import (
        router as get_orders_router,
    )
    from microarch.delivery.adapters.in_.http.api.move_courier_api import (
        router as move_courier_router,
    )

    app.include_router(create_order_router)
    app.include_router(create_courier_router)
    app.include_router(get_couriers_router)
    app.include_router(get_orders_router)
    app.include_router(move_courier_router)
    app.include_router(complete_order_router)

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
