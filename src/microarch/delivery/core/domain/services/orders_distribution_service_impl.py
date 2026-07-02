from libs.errs.error import Error
from libs.errs.guard import Guard
from libs.errs.result import Result
from microarch.delivery.core.domain.model.courier.courier import Courier
from microarch.delivery.core.domain.model.order.order import Order
from microarch.delivery.core.domain.model.order.order_status import OrderStatus
from microarch.delivery.core.domain.services.orders_distribution_service import (
    OrdersDistributionService,
)


class OrdersDistributionServiceImpl(OrdersDistributionService):
    def dispatch(
        self,
        order: Order,
        couriers: list[Courier],
    ) -> Result[Courier, Error]:
        err = Guard.combine(
            Guard.against_none(order, "order"),
            Guard.against_none_or_empty_collection(couriers, "couriers"),
        )
        if err is not None:
            return Result.failure(err)

        if order.status != OrderStatus.CREATED:
            return Result.failure(
                Error.of(
                    "order.is.not.created",
                    "Order can be distributed only when it is in Created status",
                ),
            )

        available_couriers = [
            courier for courier in couriers if courier.can_take(order.volume)
        ]
        if not available_couriers:
            return Result.failure(
                OrdersDistributionErrors.no_available_couriers(),
            )

        closest_courier = min(
            available_couriers,
            key=lambda courier: courier.location.distance_to(order.location),
        )

        take_result = closest_courier.take_order(
            order.id,
            order.volume,
            order.location,
        )
        if take_result.is_failure:
            return Result.failure(take_result.get_error())

        assign_result = order.assign()
        if assign_result.is_failure:
            return Result.failure(assign_result.get_error())

        return Result.success(closest_courier)


class OrdersDistributionErrors:
    @staticmethod
    def no_available_couriers() -> Error:
        return Error.of(
            "no.available.courier",
            "No available courier can take the order",
        )
