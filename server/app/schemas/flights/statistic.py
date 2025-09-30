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


class CountFlightsPerWeekday(BaseModel):
    weekday: Weekday
    count_flights: int = Field(ge=1)


class DistributionByFlightDuration(BaseModel):
    label: str
    flight_duration: int = Field(ge=1)


class CountFlightByMonth(BaseModel):
    label: str
    flight_count: int = Field(ge=1)


class CountByRegion(BaseModel):
    region: str
    count_flights: int = Field(ge=1)


class Statistic(BaseModel):
    total_count_flights: int = Field(ge=1)
    total_duration: int = Field(ge=1)
    mean_duration: int = Field(ge=1)
    count_flights_per_weekday: list[CountFlightsPerWeekday]
    distribution_by_flight_duration: list[DistributionByFlightDuration]
    top_regions_by_landing: list[CountByRegion]
    antitop_regions_by_landing: list[CountByRegion]
    top_regions_by_takeoff: list[CountByRegion]
    antitop_regions_by_takeoff: list[CountByRegion]
    distribution_by_type: dict[str, int]
    distribution_null_features: dict[str, int]
    count_flights_by_month: list[CountFlightByMonth]

