import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_move_courier(client: AsyncClient) -> None:
    """Test case for move_courier

    Переместить курьера
    """
    create_response = await client.post("/api/v1/couriers", json={"name": "Ivan"})
    courier_id = create_response.json()["courierId"]

    response = await client.post(
        f"/api/v1/couriers/{courier_id}/move",
        json={"x": 5, "y": 5},
    )

    assert response.status_code == 200


async def test_move_courier_returns_bad_request_for_out_of_range_location(
    client: AsyncClient,
) -> None:
    """Координаты вне доменного диапазона должны возвращать 400."""
    create_response = await client.post("/api/v1/couriers", json={"name": "Ivan"})
    courier_id = create_response.json()["courierId"]

    response = await client.post(
        f"/api/v1/couriers/{courier_id}/move",
        json={"x": 0, "y": 5},
    )

    assert response.status_code == 400
