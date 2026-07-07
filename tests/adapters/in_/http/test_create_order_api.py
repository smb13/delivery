
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine

from libs.errs.result import Result
from microarch.delivery.config.container import create_schema, drop_schema
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.ports.geo_client import IGeoClient
from microarch.delivery.main import create_app

pytestmark = pytest.mark.asyncio


async def test_create_order(engine: AsyncEngine) -> None:
    """Test case for create_order

    Создать заказ
    """
    await drop_schema(engine)
    await create_schema(engine)

    geo_client = AsyncMock(spec=IGeoClient)
    geo_client.get_location.return_value = Result.success(Location.must_create(5, 5))

    app = create_app(engine=engine, geo_client=geo_client)
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
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
        geo_client.get_location.assert_awaited_once()
