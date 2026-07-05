
from uuid import uuid4

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_create_order(client: AsyncClient) -> None:
    """Test case for create_order

    Создать заказ
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

    response = await client.post("/api/v1/orders", json=new_order)

    assert response.status_code == 201
    assert response.json()["orderId"] == new_order["id"]
