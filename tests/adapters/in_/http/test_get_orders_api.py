
from uuid import uuid4

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_get_orders(client: AsyncClient) -> None:
    """Test case for get_orders

    Получить все незавершенные заказы
    """
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
    await client.post("/api/v1/orders", json=new_order)

    response = await client.get("/api/v1/orders/active")

    assert response.status_code == 200
    orders = response.json()
    assert len(orders) == 1
    assert orders[0]["id"] == new_order["id"]
