from sqlalchemy import Column, Date, Numeric, String, Time
from sqlalchemy.dialects.postgresql import BIGINT

from app.db import DeclarativeBase


class Flight(DeclarativeBase):
    __tablename__ = 'flights'

    sid = Column(
        "sid",
        BIGINT,
        primary_key=True,
        autoincrement=True,
    )
    type_aircraft = Column(
        "type_aircraft",
        String(128),
        nullable=True,
    )
    departure_date = Column(
        "departure_date",
        Date,
        nullable=True,
    )
    departure_time = Column(
        "departure_time",
        Time,
        nullable=True,
    )
    reg_departure = Column(
        "reg_departure",
        String(128),
        nullable=True,
    )
    departure_latitude = Column(
        "departure_latitude",
        Numeric(10, 8),
        nullable=True,
    )
    departure_longitude = Column(
        "departure_longitude",
        Numeric(11, 8),
        nullable=True,
    )
    arrival_time = Column(
        "arrival_time",
        Time,
        nullable=True,
    )
    arrival_date = Column(
        "arrival_date",
        Date,
        nullable=True,
    )
    reg_arrival = Column(
        "reg_arrival",
        String(128),
        nullable=True,
    )
    arrival_latitude = Column(
        "arrival_latitude",
        Numeric(10, 8),
        nullable=True,
    )
    arrival_longitude = Column(
        "arrival_longitude",
        Numeric(11, 8),
        nullable=True,
    )

    def __repr__(self):
        columns = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return f'<{self.__tablename__}: {", ".join(map(lambda x: f"{x[0]}={x[1]}", columns.items()))}>'
