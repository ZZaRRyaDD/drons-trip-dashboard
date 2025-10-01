import pandas as pd
import re
from datetime import datetime
from typing import Dict, Any, List
import geopandas as gpd
from shapely.geometry import Point

# df = pd.read_excel('2025.xlsx', header=0)
regions = gpd.read_file("admin_4.shp")

# Словарь для перевода номера дня недели в строку
DAY_NAMES = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']

def transform(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Преобразует DataFrame в список полётов в требуемом формате.
    """
    # Обрабатываем исходные данные
    df_processed = _process_dataframe(df)
    
    flights = []
    
    for idx, row in df_processed.iterrows():
        try:
            # Получаем даты и времена с заполнением пропусков
            takeoff_date = row['DepDate']
            takeoff_time = row['DepTime']
            landing_date = row['ArrDate']
            landing_time = row['ArrTime']
            
            # Создаем datetime объекты для вычисления длительности
            # Если дата или время отсутствуют, используем значения по умолчанию
            takeoff_datetime = _safe_datetime_combine(takeoff_date, takeoff_time)
            landing_datetime = _safe_datetime_combine(landing_date, landing_time)
            
            # Если оба datetime валидны, вычисляем длительность
            if takeoff_datetime and landing_datetime and landing_datetime >= takeoff_datetime:
                duration_minutes = (landing_datetime - takeoff_datetime).total_seconds() / 60
                # Проверяем разумность длительности (не более 48 часов)
                if duration_minutes > 2880:
                    duration_minutes = None
            else:
                duration_minutes = None
            
            # Вычисляем день недели вылета
            takeoff_day_of_week = DAY_NAMES[takeoff_datetime.weekday()] if takeoff_datetime else "Не заполнено"
            
            # Формируем координаты с заполнением пропусков
            takeoff_coords = {
                "lat": row['DepLat'] if pd.notna(row['DepLat']) else "Не заполнено",
                "lon": row['DepLon'] if pd.notna(row['DepLon']) else "Не заполнено"
            }
            
            landing_coords = {
                "lat": row['ArrLat'] if pd.notna(row['ArrLat']) else "Не заполнено",
                "lon": row['ArrLon'] if pd.notna(row['ArrLon']) else "Не заполнено"
            }
            
            # Обрабатываем регионы с заполнением пропусков
            takeoff_region = row['takeoff_region'] if pd.notna(row['takeoff_region']) else "Не заполнено"
            landing_region = row['landing_region'] if pd.notna(row['landing_region']) else "Не заполнено"
            
            # Форматируем даты и время с заполнением пропусков
            takeoff_time_str = takeoff_time.strftime("%H:%M:%S") if takeoff_time and pd.notna(takeoff_time) else "Не заполнено"
            takeoff_date_str = takeoff_date.strftime("%Y-%m-%d") if takeoff_date and pd.notna(takeoff_date) else "Не заполнено"
            landing_time_str = landing_time.strftime("%H:%M:%S") if landing_time and pd.notna(landing_time) else "Не заполнено"
            landing_date_str = landing_date.strftime("%Y-%m-%d") if landing_date and pd.notna(landing_date) else "Не заполнено"
            
            flight = {
                "id": idx,
                "takeoff_region": takeoff_region,
                "landing_region": landing_region,
                "takeoff_time": takeoff_time_str,
                "takeoff_date": takeoff_date_str,
                "landing_time": landing_time_str,
                "landing_date": landing_date_str,
                "takeoff_day_of_week": takeoff_day_of_week,
                "takeoffCoords": takeoff_coords,
                "landingCoords": landing_coords,
                "duration": round(duration_minutes, 2) if duration_minutes else "Не заполнено",
            }
            flights.append(flight)
        except Exception as e:
            # Пропускаем строки с ошибками обработки
            print(f"Ошибка обработки строки {idx}: {e}")
            continue
    
    return flights

def _process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Обрабатывает исходный DataFrame и извлекает необходимые поля.
    """
    df_processed = df.copy()
    
    # Векторизованные операции для извлечения данных
    df_processed["SID"] = df_processed['SHR'].str.extract(r"SID/([0-9]+)").fillna("Не заполнено")
    df_processed["TYP"] = df_processed['SHR'].str.extract(r"TYP/[0-9]*([a-zA-Z]+)").fillna("Не заполнено")

    zona1 = df_processed['SHR'].str.extract(r'/ZONA\s+([^/\s]+)')
    zona2 = df_processed['SHR'].str.extract(r'(\d+[NSС]\d+[EWВ])')
    df_processed["ZONA"] = zona1[0].fillna(zona2[0]).fillna("Не заполнено")
    
    # Даты и время вылета с обработкой пропусков
    df_processed["DODEP"] = (
        df_processed['DEP']
        .str.extract(r"ADD\s([0-9]{6})")[0]   
        .pipe(pd.to_datetime, format="%y%m%d", errors='coerce') 
        .dt.date                              
    )
    df_processed["TODEP"] = (
        df_processed['DEP']
        .str.extract(r"ATD\s([0-9]{4})")[0]  
        .apply(_safe_time_parse)
    )

    # Координаты вылета - векторизованная версия
    df_processed["DEP_coord"] = df_processed['DEP'].str.extract(r"ADEPZ\s(\d+[NSС]\d+[EWВ])")[0]
    
    # Векторизованный парсинг координат
    coords_dep = df_processed["DEP_coord"].apply(_parse_coord_vectorized)
    df_processed["LAT_DEP"] = coords_dep.str[0]
    df_processed["LON_DEP"] = coords_dep.str[1]
    
    print("Обработка регионов вылета...")
    
    # Оптимизированное определение регионов для вылета
    df_processed['takeoff_region'] = _reg_vectorized(df_processed['LON_DEP'], df_processed['LAT_DEP'], regions)
    print("Регионы вылета обработаны")

    # Даты и время посадки с обработкой пропусков
    df_processed["DOARR"] = (
        df_processed['ARR']
        .str.extract(r"ADA\s([0-9]{6})")[0]   
        .pipe(pd.to_datetime, format="%y%m%d", errors='coerce') 
        .dt.date                               
    )
    df_processed["TOARR"] = (
        df_processed['ARR']
        .str.extract(r"ATA\s([0-9]{4})")[0] 
        .apply(_safe_time_parse)
    )

    # Координаты посадки - векторизованная версия
    df_processed["DEST"] = df_processed['ARR'].str.extract(r"ADARRZ\s(\d+[NSС]\d+[EWВ])")[0]
    coords_arr = df_processed["DEST"].apply(_parse_coord_vectorized)
    df_processed["LAT_ARR"] = coords_arr.str[0]
    df_processed["LON_ARR"] = coords_arr.str[1]
    
    # Оптимизированное определение регионов для посадки
    df_processed['landing_region'] = _reg_vectorized(df_processed['LON_ARR'], df_processed['LAT_ARR'], regions)
    
    # Заполняем пропущенные значения для категориальных полей
    df_processed = _fill_missing_values(df_processed)
    
    cols = ["SID", "TYP", "DODEP", "TODEP", 'takeoff_region', "LAT_DEP", "LON_DEP", 
            "DOARR", "TOARR", 'landing_region', "LAT_ARR", "LON_ARR"]
    
    df_result = df_processed[cols].rename(columns={
        "DODEP": "DepDate",
        "TODEP": "DepTime",
        "DOARR": "ArrDate",
        "TOARR": "ArrTime",
        "LAT_DEP": "DepLat",
        "LON_DEP": "DepLon",
        "LAT_ARR": "ArrLat",
        "LON_ARR": "ArrLon"
    })
    
    # Статистика по пропускам
    _print_missing_stats(df_result)
    
    return df_result

def _safe_time_parse(time_str):
    """Безопасный парсинг времени с обработкой ошибок."""
    if pd.isna(time_str):
        return None
    
    try:
        return pd.to_datetime(time_str, format="%H%M", errors='coerce').time()
    except:
        return None

def _safe_datetime_combine(date, time):
    """Безопасное объединение даты и времени."""
    if pd.isna(date) or pd.isna(time):
        return None
    
    try:
        return datetime.combine(date, time)
    except:
        return None

def _fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Заполняет пропущенные значения для категориальных полей.
    """
    df_filled = df.copy()
    
    # Заполняем категориальные поля
    categorical_columns = ['takeoff_region', 'landing_region', 'SID', 'TYP', 'ZONA']
    for col in categorical_columns:
        if col in df_filled.columns:
            df_filled[col] = df_filled[col].fillna("Не заполнено")
    
    return df_filled

def _print_missing_stats(df: pd.DataFrame):
    """Выводит статистику по пропущенным значениям."""
    print("\n=== СТАТИСТИКА ПО ПРОПУСКАМ ===")
    
    for col in df.columns:
        missing_count = df[col].isna().sum()
        total_count = len(df)
        if missing_count > 0:
            print(f"{col}: {missing_count} пропусков из {total_count} ({missing_count/total_count*100:.1f}%)")
    
    print("=" * 50)

def _reg_vectorized(lons, lats, regions_gdf):
    """
    Векторизованная версия определения региона для координат.
    """
    # Создаем GeoDataFrame для всех точек сразу
    valid_mask = lons.notna() & lats.notna()
    
    if not valid_mask.any():
        return pd.Series(["Не заполнено"] * len(lons), index=lons.index)
    
    # Создаем точки только для валидных координат
    valid_lons = lons[valid_mask]
    valid_lats = lats[valid_mask]
    
    points = [Point(lon, lat) for lon, lat in zip(valid_lons, valid_lats)]
    points_gdf = gpd.GeoDataFrame(geometry=points, index=valid_lons.index, crs=regions_gdf.crs)
    
    # Пространственное соединение
    joined = gpd.sjoin(points_gdf, regions_gdf, how='left', predicate='within')
    
    # Создаем результат с правильным соответствием индексов
    result = pd.Series(["Не заполнено"] * len(lons), index=lons.index, dtype=object)
    
    # Присваиваем значения по индексу, избегая проблемы с булевыми значениями Series
    for idx in joined.index:
        # Проверяем наличие столбца и получаем значение
        if 'name_ru' in joined.columns:
            # Получаем значение и проверяем, не является ли оно NaN
            value = joined.loc[idx, 'name_ru']
            if isinstance(value, pd.Series):
                # Если это Series (несколько регионов для одной точки), берем первое значение
                if len(value) > 0 and not pd.isna(value.iloc[0]):
                    result.loc[idx] = value.iloc[0]
            else:
                # Если это скалярное значение
                if not pd.isna(value):
                    result.loc[idx] = value
    
    return result

def _parse_coord_vectorized(coord: str):
    """
    Векторизованная версия парсинга координат.
    """
    if not isinstance(coord, str) or coord.strip() == "":
        return (None, None)
    
    match = re.match(r"(\d+[NSС])(\d+[EWВ])", coord)
    if not match:
        return (None, None)
    
    lat_raw, lon_raw = match.groups()
    lat_raw = lat_raw.replace("С", "N")
    lon_raw = lon_raw.replace("В", "E")
    return (_parse_dms_vectorized(lat_raw), _parse_dms_vectorized(lon_raw))

def _parse_dms_vectorized(part: str) -> float:
    """Векторизованная версия парсинга DMS в десятичные градусы."""
    if not part:
        return None
        
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

# print(transform(df)[:4])