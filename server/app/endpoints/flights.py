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
from app.utils.flight import parse_input_file

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
    from_: Optional[date] = Query(..., alias="from", description="DD-MM-YYYY"),
    to: Optional[date] = Query(..., description="DD-MM-YYYY"),
    top: bool = Query(True, description="Если true — сортировать по newest first"),
    count: Optional[int] = Query(10, ge=1, le=50, description="Макс. число записей"),
    linear_from: Optional[str] = Query(None, alias="linear-from", description="MM-YYYY"),
    linear_to: Optional[str]= Query(None, alias="linear-to", description="MM-YYYY"),
    region: str = Query(None, description='Регион (строка, кавычки не обязательны)'),
    session: AsyncSession = Depends(get_session),
):
    flights = await FlightRepository().get_statistic(
        session=session,
        departure_date=from_,
        arrival_date=to,
        top=top,
        count=count,
        linear_from=linear_from,
        linear_to=linear_to,
        region=region,
    )


@api_router.post(
    "/files/",
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
