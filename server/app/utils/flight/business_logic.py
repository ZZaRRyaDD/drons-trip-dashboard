import re
import tempfile
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from app.db.models import Flight
from app.schemas.flights import FlightCreateModel, Statistic

regions = gpd.read_file(str(Path(__file__).parent / "admin_4.shp"))


def parse_input_file(content: bytes) -> list[FlightCreateModel]:
    with tempfile.NamedTemporaryFile() as namedFile:
        namedFile.write(content)
        df = pd.read_excel(namedFile.name, header=0)
        df["SID"] = df['SHR'].str.extract(r"SID/([0-9]+)")
        df["TYP"] = df['SHR'].str.extract(r"TYP/[0-9]*([a-zA-Z]+)")

        zona1 = df['SHR'].str.extract(r'/ZONA\s+([^/\s]+)')
        zona2 = df['SHR'].str.extract(r'(\d+[NSС]\d+[EWВ])')
        df["ZONA"] = zona1[0].fillna(zona2[0])
        df["DODEP"] = (
            df['DEP']
            .str.extract(r"ADD\s([0-9]{6})")[0]   
            .pipe(pd.to_datetime, format="%y%m%d") 
            .dt.date                              
        )
        df["TODEP"] = (
            df['DEP']
            .str.extract(r"ATD\s([0-9]{4})")[0]  
            .pipe(pd.to_datetime, format="%H%M") 
            .dt.time                                
        )

        df["DEP_coord"] = df['DEP'].str.extract(r"ADEPZ\s(\d+[NSС]\d+[EWВ])")[0]
        df[["LAT_DEP", "LON_DEP"]] = df["DEP_coord"].apply(lambda x: pd.Series(parse_coord(x)))
        df['REG DEP'] = df.apply(lambda row: reg(row['LON_DEP'], row['LAT_DEP']), axis=1)

        df["DOARR"] = (
            df['ARR']
            .str.extract(r"ADA\s([0-9]{6})")[0]   
            .pipe(pd.to_datetime, format="%y%m%d") 
            .dt.date                               
        )
        df["TOARR"] = (
            df['ARR']
            .str.extract(r"ATA\s([0-9]{4})")[0] 
            .pipe(pd.to_datetime, format="%H%M") 
            .dt.time                                
        )

        df["DEST"] = df['ARR'].str.extract(r"ADARRZ\s(\d+[NSС]\d+[EWВ])")[0]
        df[["LAT_ARR", "LON_ARR"]] = df["DEST"].apply(lambda x: pd.Series(parse_coord(x)))
        df['REG ARR'] = df.apply(lambda row: reg(row['LON_ARR'], row['LAT_ARR']), axis=1)

        cols = ["Центр ЕС ОрВД", "SID", "TYP", "DODEP", "TODEP", 'REG DEP', "LAT_DEP", "LON_DEP", "DOARR", "TOARR", 'REG ARR', "LAT_ARR", "LON_ARR"]
        df_new = df[cols].copy()

        df_new = df_new.rename(columns={
            "Центр ЕС ОрВД": "Center",
            "DODEP": "DepDate",
            "TODEP": "DepTime",
            "DOARR": "ArrDate",
            "TOARR": "ArrTime",
            "LAT_DEP": "DepLat",
            "LON_DEP": "DepLon",
            "LAT_ARR": "ArrLat",
            "LON_ARR": "ArrLon",
            "REG DEP": "RegDep",
            "REG ARR": "RegArr",
        })

    flights = []
    for _, row in df_new.iterrows():
        flight = FlightCreateModel(
            sid=row["SID"],
            type_aircraft=row["TYP"] if row["TYP"] and pd.notna(row["TYP"]) else None,
            departure_date=row["DepDate"] if row["DepDate"] and pd.notna(row["DepDate"]) else None,
            departure_time=row["DepTime"] if row["DepTime"] and pd.notna(row["DepTime"]) else None,
            reg_departure=row["RegDep"] if row["RegDep"] and pd.notna(row["RegDep"]) else None,
            departure_latitude=round(row["DepLat"],3 ) if row["DepLat"] and pd.notna(row["DepLat"]) else None,
            departure_longitude=round(row["DepLon"],3) if row["DepLon"] and pd.notna(row["DepLon"]) else None,
            arrival_date=row["ArrDate"] if row["ArrDate"] and pd.notna(row["ArrDate"]) else None,
            arrival_time=row["ArrTime"] if row["ArrTime"] and pd.notna(row["ArrTime"]) else None,
            reg_arrival=row["RegArr"] if row["RegArr"] and pd.notna(row["RegArr"]) else None,
            arrival_latitude=round(row["ArrLat"],3) if row["ArrLat"] and pd.notna(row["ArrLat"]) else None,
            arrival_longitude=round(row["ArrLon"], 3) if row["ArrLon"] and pd.notna(row["ArrLon"]) else None,
        )
        flights.append(flight)
    
    return flights


def parse_dms(part: str) -> float:
    direction = part[-1].upper()
    digits = part[:-1]

    if direction in "NS":
        deg_len = 2  
    else:
        deg_len = 3 

    d = int(digits[:deg_len])
    m = int(digits[deg_len:deg_len+2]) if len(digits) >= deg_len+2 else 0
    s = int(digits[deg_len+2:deg_len+4]) if len(digits) >= deg_len+4 else 0

    dd = d + m/60 + s/3600
    if direction in "SW": 
        dd *= -1
    return dd

def parse_coord(coord: str):
    if not isinstance(coord, str) or coord.strip() == "":
        return None, None
    
    match = re.match(r"(\d+[NSС])(\d+[EWВ])", coord)
    if not match:
        return None, None
    
    lat_raw, lon_raw = match.groups()
    lat_raw = lat_raw.replace("С", "N")
    lon_raw = lon_raw.replace("В", "E")
    return parse_dms(lat_raw), parse_dms(lon_raw)


def reg(lon, lat):
    point = Point(lon, lat)
    region = regions[regions.contains(point)]
    if len(region) > 0:
        return region['name_ru'].values[0]
    return None


def format_flight_data(flights: list[Flight]):
    total_count_flights = len(flights)

    durations = []
    for flight in flights:
        if flight.departure_date and flight.departure_time and flight.arrival_date and flight.arrival_time:
            dep_dt = datetime.combine(flight.departure_date, flight.departure_time)
            arr_dt = datetime.combine(flight.arrival_date, flight.arrival_time)
            if arr_dt < dep_dt:
                arr_dt += timedelta(days=1)
            duration = (arr_dt - dep_dt).total_seconds() / 60
            durations.append(duration)

    total_duration = sum(durations)
    mean_duration = total_duration / len(durations) if durations else 0

    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    count_flights_per_weekday = [{} for _ in range(7)]
    weekday_counts = Counter()
    for flight in flights:
        if flight.departure_date:
            weekday = flight.departure_date.weekday()
            weekday_counts[weekdays[weekday]] += 1
    for i, day in enumerate(weekdays):
        count_flights_per_weekday[i] = {day: weekday_counts[day]}

    bins = [
        ('< 10 мин', 10),
        ('10 - 30 мин', 30),
        ('30 мин - 1 ч', 60),
        ('1 - 2 ч', 120),
        ('2 - 4 ч', 240),
        ('4 - 8 ч', 480),
        ('8 - 12 ч', 720),
        ('12 - 24 ч', 1440),
        ('24+ ч', float('inf'))
    ]
    distribution_by_flight_duration = [{} for _ in range(len(bins))]

    duration_dist = Counter()
    for dur in durations:
        for label, limit in bins:
            if dur <= limit:
                duration_dist[label] += 1
                break
    for i, bin in enumerate(bins):
        for label, count in duration_dist.items():
            if label == bin[0]:
                distribution_by_flight_duration[i] = {label: count}
                break

    type_counts = Counter(f.type_aircraft for f in flights if f.type_aircraft)
    distribution_by_type = dict(type_counts)

    null_features = Counter()
    for f in flights:
        if not f.arrival_date:
            null_features["Дата посадки"] += 1
        if not f.arrival_time:
            null_features["Время посадки"] += 1
        if not f.reg_arrival:
            null_features["Регион посадки"] += 1
        if not f.arrival_latitude:
            null_features["Широта региона посадки"] += 1
        if not f.arrival_longitude:
            null_features["Долгота региона посадки"] += 1
        if not f.type_aircraft:
            null_features["Тип ВС"] += 1
        if not f.departure_date:
            null_features["Дата вылета"] += 1
        if not f.departure_time:
            null_features["Время вылета"] += 1
        if not f.reg_departure:
            null_features["Регион вылета"] += 1
        if not f.departure_latitude:
            null_features["Широта региона вылета"] += 1
        if not f.departure_longitude:
            null_features["Долгота региона вылета"] += 1
    distribution_null_features = dict(null_features)

    month_counts = Counter()
    for f in flights:
        if f.departure_date:
            month_key = f.departure_date.strftime("%m.%Y")
            month_counts[month_key] += 1
    count_flights_by_month = [{k: v} for k, v in sorted(month_counts.items())]

    return Statistic(
        total_count_flights=total_count_flights,
        total_duration=round(total_duration),
        mean_duration=round(mean_duration),
        count_flights_per_weekday=count_flights_per_weekday,
        distribution_by_flight_duration=distribution_by_flight_duration,
        distribution_by_type=distribution_by_type,
        distribution_null_features=distribution_null_features,
        count_flights_by_month=count_flights_by_month,
    )