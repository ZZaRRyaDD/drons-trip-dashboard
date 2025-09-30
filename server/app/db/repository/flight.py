from datetime import date, time
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Flight
from app.schemas.flights import FlightCreateModel

from .base import BaseRepository


class FlightRepository(BaseRepository[Flight, FlightCreateModel, None]):
    def __init__(self):
        super().__init__(Flight)

    async def create_batch(
        self,
        session: AsyncSession,
        *, objs_in: list[FlightCreateModel] | list[dict[str, Any]],
    ) -> None:
        for obj in objs_in:
            if isinstance(obj, dict):
                obj_in_data = obj
            else:
                obj_in_data = jsonable_encoder(obj)
            db_obj = self.model(**obj_in_data)  # type: ignore
            if obj_in_data["arrival_date"]:
                db_obj.arrival_date = date.fromisoformat(obj_in_data["arrival_date"])

            if obj_in_data["departure_date"]:
                db_obj.departure_date = date.fromisoformat(obj_in_data["departure_date"])

            if obj_in_data["arrival_time"]:
                db_obj.arrival_time = time.fromisoformat(obj_in_data["arrival_time"])

            if obj_in_data["departure_time"]:
                db_obj.departure_time = time.fromisoformat(obj_in_data["departure_time"])

            session.add(db_obj)
        await session.commit()

    async def get_statistic(  # pylint: disable=unused-argument, too-many-arguments
        self,
        session: AsyncSession,
        *, departure_date: date, arrival_date: date, top: bool, count: int,
        linear_from: str | None, linear_to: str | None, region: str,
    ) -> list[Flight]:
        region_clean = region.strip().strip('"').strip("'")
        query = select(self.model).where(
            or_(
                self.model.reg_departure.ilike(f"%{region_clean}%"),
                self.model.reg_arrival.ilike(f"%{region_clean}%"),
            ),
        )



        query = query.limit(count)

        result = await session.execute(query)
        return result.scalar()
