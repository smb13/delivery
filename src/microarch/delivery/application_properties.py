from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GeoServiceSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 5004


class GrpcSettings(BaseModel):
    geo_service: GeoServiceSettings = Field(default_factory=GeoServiceSettings)


class KafkaSettings(BaseModel):
    basket_events_topic: str = "basket.events"
    order_events_topic: str = "order.events"


class ApplicationProperties(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    geo_service_grpc_host: str = Field(
        default="0.0.0.0",
        alias="GEO_SERVICE_GRPC_HOST",
    )
    geo_service_grpc_port: int = Field(
        default=5004,
        alias="GEO_SERVICE_GRPC_PORT",
    )
    kafka_basket_events_topic: str = Field(
        default="basket.events",
        alias="KAFKA_BASKET_EVENTS_TOPIC",
    )
    kafka_order_events_topic: str = Field(
        default="order.events",
        alias="KAFKA_ORDER_EVENTS_TOPIC",
    )

    @property
    def grpc(self) -> GrpcSettings:
        return GrpcSettings(
            geo_service=GeoServiceSettings(
                host=self.geo_service_grpc_host,
                port=self.geo_service_grpc_port,
            ),
        )

    @property
    def kafka(self) -> KafkaSettings:
        return KafkaSettings(
            basket_events_topic=self.kafka_basket_events_topic,
            order_events_topic=self.kafka_order_events_topic,
        )

    @property
    def stocks_events_topic(self) -> str:
        return self.kafka_order_events_topic

    @property
    def baskets_events_topic(self) -> str:
        return self.kafka_basket_events_topic
