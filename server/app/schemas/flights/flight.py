from datetime import date, time

from pydantic import BaseModel, Field


class FlightCreateModel(BaseModel):
    sid: int = Field(ge=1)
    type_aircraft: str
    departure_date: date | None
    departure_time: time | None
    reg_departure: str | None
    departure_latitude: float | None
    departure_longitude: float | None
    arrival_date: date | None
    arrival_time: time | None
    reg_arrival: str | None
    arrival_latitude: float | None
    arrival_longitude: float | None

    class Config:
        arbitrary_types_allowed = True

