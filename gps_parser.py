# -*- coding: utf-8 -*-
import gpxpy
import gpxpy.gpx
import fitparse
from datetime import datetime, timezone
import os
from typing import List, Tuple, Optional

class GPSPoint:
    def __init__(self, lat: float, lon: float, time: datetime, ele: Optional[float] = None):
        self.lat = lat
        self.lon = lon
        self.time = time
        self.ele = ele

class GPSParser:
    @staticmethod
    def parse_gpx(file_path: str) -> List[GPSPoint]:
        points = []
        with open(file_path, 'r', encoding='utf-8') as f:
            gpx = gpxpy.parse(f)
        
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if point.time:
                        points.append(GPSPoint(
                            lat=point.latitude,
                            lon=point.longitude,
                            time=point.time,
                            ele=point.elevation
                        ))
        
        return points

    @staticmethod
    def parse_fit(file_path: str) -> List[GPSPoint]:
        points = []
        fitfile = fitparse.FitFile(file_path)
        
        for record in fitfile.get_messages('record'):
            data = {}
            for field in record:
                data[field.name] = field.value
            
            if 'position_lat' in data and 'position_long' in data and 'timestamp' in data:
                lat = data['position_lat'] * (180.0 / 2**31)
                lon = data['position_long'] * (180.0 / 2**31)
                time = data['timestamp']
                
                if time.tzinfo is None:
                    time = time.replace(tzinfo=timezone.utc)
                
                ele = data.get('altitude')
                points.append(GPSPoint(lat=lat, lon=lon, time=time, ele=ele))
        
        return points

    @staticmethod
    def parse(file_path: str) -> List[GPSPoint]:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.gpx':
            return GPSParser.parse_gpx(file_path)
        elif ext == '.fit':
            return GPSParser.parse_fit(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def get_gpx_time_range(file_path: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        try:
            points = GPSParser.parse_gpx(file_path)
            if not points:
                return None, None
            times = [p.time for p in points]
            return min(times), max(times)
        except Exception:
            return None, None

    @staticmethod
    def rename_gpx_by_time(file_path: str) -> str:
        start_time, end_time = GPSParser.get_gpx_time_range(file_path)
        if not start_time or not end_time:
            return file_path
        
        dir_name = os.path.dirname(file_path)
        start_str = start_time.strftime("%Y%m%d_%H%M%S")
        end_str = end_time.strftime("%Y%m%d_%H%M%S")
        new_name = f"{start_str}_{end_str}.gpx"
        new_path = os.path.join(dir_name, new_name)
        
        if new_path != file_path:
            counter = 1
            while os.path.exists(new_path):
                new_name = f"{start_str}_{end_str}_{counter}.gpx"
                new_path = os.path.join(dir_name, new_name)
                counter += 1
            os.rename(file_path, new_path)
        
        return new_path
