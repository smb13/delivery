from collections.abc import Iterable

from libs.ddd.aggregate import Aggregate
from libs.ddd.domain_event_publisher import DomainEventPublisher
from microarch.delivery.config.application_event_publisher import ApplicationEventPublisher


class DefaultDomainEventPublisher(DomainEventPublisher):
    def __init__(self, publisher: ApplicationEventPublisher) -> None:
        self._publisher = publisher

    def publish(self, aggregates: Iterable[Aggregate]) -> None:
        for aggregate in aggregates:
            for event in aggregate.get_domain_events():
                self._publisher.publish_event(event)
