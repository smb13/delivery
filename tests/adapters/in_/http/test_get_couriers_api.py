
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_get_couriers(client: AsyncClient) -> None:
    """Test case for get_couriers

    Получить всех курьеров
    """
    await client.post("/api/v1/couriers", json={"name": "Ivan"})

    response = await client.get("/api/v1/couriers")

    assert response.status_code == 200
    couriers = response.json()
    assert len(couriers) == 1
    assert couriers[0]["name"] == "Ivan"
