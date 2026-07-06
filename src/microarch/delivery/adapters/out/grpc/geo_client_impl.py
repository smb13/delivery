from __future__ import annotations

import grpc
from libs.errs.error import Error
from libs.errs.result import Result
from microarch.delivery.adapters.out.grpc import geo_pb2, geo_pb2_grpc
from microarch.delivery.core.domain.model.address import Address
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.ports.geo_client import IGeoClient


class GeoClientImpl(IGeoClient):
    """gRPC-клиент к сервису Geo."""

    def __init__(self, host: str, port: int) -> None:
        self._target = f"{host}:{port}"

    async def get_location(self, address: Address) -> Result[Location, Error]:
        async with grpc.aio.insecure_channel(self._target) as channel:
            stub = geo_pb2_grpc.GeoStub(channel)
            request = geo_pb2.GetGeolocationRequest(street=address.street)

            try:
                response = await stub.GetGeolocation(request)
            except grpc.RpcError as exc:
                return Result.failure(
                    Error.of(
                        "geo.service.error",
                        f"Geo service call failed: {exc.details() or exc.code()}",
                    ),
                )

            location_result = Location.create(
                response.location.x,
                response.location.y,
            )
            if location_result.is_failure:
                return Result.failure(location_result.get_error())

            return Result.success(location_result.get_value())
