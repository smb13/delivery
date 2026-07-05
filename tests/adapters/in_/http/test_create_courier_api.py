
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_create_courier(client: AsyncClient) -> None:
    """Test case for create_courier

    Добавить курьера
    """
    response = await client.post("/api/v1/couriers", json={"name": "Ivan"})

    assert response.status_code == 201
    assert "courierId" in response.json()
