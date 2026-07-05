from __future__ import annotations

from microarch.delivery.adapters.out.postgres.models import (
    AssignmentModel,
    CourierModel,
    OrderModel,
)
from microarch.delivery.core.domain.model.courier.assignment import (
    Assignment,
    AssignmentStatus,
)
from microarch.delivery.core.domain.model.courier.courier import Courier
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.order.order import Order
from microarch.delivery.core.domain.model.order.order_status import OrderStatus
from microarch.delivery.core.domain.model.volume import Volume


class OrderMapper:
    @staticmethod
    def to_model(order: Order) -> OrderModel:
        return OrderModel(
            id=order.id,
            location_x=order.location.x,
            location_y=order.location.y,
            volume=order.volume.value,
            status=order.status.name,
        )

    @staticmethod
    def to_domain(model: OrderModel) -> Order:
        return Order(
            id=model.id,
            location=Location.must_create(model.location_x, model.location_y),
            volume=Volume.must_create(model.volume),
            status=OrderStatus[model.status],
        )


class AssignmentMapper:
    @staticmethod
    def to_model(assignment: Assignment, courier_id: object) -> AssignmentModel:
        return AssignmentModel(
            id=assignment.id,
            courier_id=courier_id,
            order_id=assignment.order_id,
            volume=assignment.volume.value,
            location_x=assignment.location.x,
            location_y=assignment.location.y,
            status=assignment.status.name,
        )

    @staticmethod
    def to_domain(model: AssignmentModel) -> Assignment:
        return Assignment(
            id=model.id,
            order_id=model.order_id,
            volume=Volume.must_create(model.volume),
            location=Location.must_create(model.location_x, model.location_y),
            status=AssignmentStatus[model.status],
        )


class CourierMapper:
    @staticmethod
    def to_model(courier: Courier) -> CourierModel:
        model = CourierModel(
            id=courier.id,
            name=courier.name,
            location_x=courier.location.x,
            location_y=courier.location.y,
            max_volume=courier.max_volume.value,
        )
        model.assignments = [
            AssignmentMapper.to_model(assignment, courier.id)
            for assignment in courier._assignments
        ]
        return model

    @staticmethod
    def to_domain(model: CourierModel) -> Courier:
        return Courier(
            id=model.id,
            name=model.name,
            location=Location.must_create(model.location_x, model.location_y),
            max_volume=Volume.must_create(model.max_volume),
            assignments=[
                AssignmentMapper.to_domain(assignment_model)
                for assignment_model in model.assignments
            ],
        )
