import enum

from pydantic import BaseModel, Field


class Weekday(enum.Enum):
    Monday = "Пн"
    Tuesday = "Вт"
    Wednesday = "Ср"
    Thursday = "Чт"
    Friday = "Пт"
    Saturday = "Сб"
    Sunday = "Вс"


class CountByRegion(BaseModel):
    region: str
    count_flights: int = Field(ge=1)


class Statistic(BaseModel):
    total_count_flights: int = Field(ge=1)
    total_duration: int = Field(ge=1)
    mean_duration: int = Field(ge=1)
    count_flights_per_weekday: list[dict[Weekday, int]]
    distribution_by_flight_duration: list[dict[str, int]]
    distribution_by_type: dict[str, int]
    distribution_null_features: dict[str, int]
    count_flights_by_month: list[dict[str, int]]
