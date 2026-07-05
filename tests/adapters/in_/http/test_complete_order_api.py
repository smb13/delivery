
from uuid import uuid4

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_complete_order(client: AsyncClient) -> None:
    """Test case for complete_order

    Завершить заказ. Заказ не назначен, поэтому ожидается конфликт.
    """
    create_courier_response = await client.post("/api/v1/couriers", json={"name": "Ivan"})
    courier_id = create_courier_response.json()["courierId"]

    new_order = {
        "id": str(uuid4()),
        "address": {
            "country": "RU",
            "city": "Moscow",
            "street": "Tverskaya",
            "house": "1",
            "apartment": "2",
        },
        "volume": 3,
    }
    create_order_response = await client.post("/api/v1/orders", json=new_order)
    order_id = create_order_response.json()["orderId"]

    response = await client.post(
        f"/api/v1/couriers/{courier_id}/orders/{order_id}/complete",
    )

    assert response.status_code == 409
