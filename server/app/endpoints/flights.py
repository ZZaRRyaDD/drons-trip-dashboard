import os
from datetime import date
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.connection import get_session
from app.db.repository import FlightRepository
from app.schemas.flights import Statistic
from app.utils.flight import format_flight_data, parse_input_file

api_router = APIRouter(
    prefix="/flights",
    tags=["Flights"],
)

@api_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Statistic,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad parameters for registration",
        },
    },
)
async def get_statistic( # pylint: disable=too-many-arguments, unused-variable, too-many-positional-arguments
    _: Request,
    from_: Optional[date] = Query(date(2025,1,1), alias="from", description="DD-MM-YYYY"),
    to: Optional[date] = Query(date.today(), description="DD-MM-YYYY"),
    region: str = Query(None, description='Регион'),
    flag_full_dataset: bool = Query(False, description='Игнорированиие среза данных'),
    session: AsyncSession = Depends(get_session),
):
    flights = await FlightRepository().get_statistic(
        session=session,
        departure_date_from=from_,
        departure_date_to=to,
        region=region,
        flag_full_dataset=flag_full_dataset,
    )

    return format_flight_data(flights)


@api_router.post(
    "/upload/",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad parameters",
        },
    },
)
async def create_file(
    file: UploadFile = File(),
    session: AsyncSession = Depends(get_session),
):
    if os.path.splitext(file.filename)[-1] != ".xlsx":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Incorrect file extension",
        )

    if file.size  == 0:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="File is empty",
        )

    content = await file.read()
    flights = parse_input_file(content)

    await FlightRepository().create_batch(session=session, objs_in=flights)
