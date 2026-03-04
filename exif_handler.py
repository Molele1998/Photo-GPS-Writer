# -*- coding: utf-8 -*-
import os
import piexif
from PIL import Image
from datetime import datetime, timezone
from typing import Optional, Tuple
from gps_parser import GPSPoint

class ExifHandler:
    PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.cr2', '.nef', '.arw', '.dng'}

    @staticmethod
    def is_photo_file(file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ExifHandler.PHOTO_EXTENSIONS

    @staticmethod
    def get_photo_time(file_path: str) -> Optional[datetime]:
        try:
            exif_dict = piexif.load(file_path)
            if 'Exif' in exif_dict:
                if piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
                    dt_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
                    dt = datetime.strptime(dt_str, '%Y:%m:%d %H:%M:%S')
                    return dt.replace(tzinfo=timezone.utc)
        except Exception:
            pass
        
        try:
            mtime = os.path.getmtime(file_path)
            dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
            return dt
        except Exception:
            return None

    @staticmethod
    def decimal_to_dms(decimal_degrees: float, ref_pos: str, ref_neg: str) -> Tuple[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]], str]:
        degrees = int(abs(decimal_degrees))
        minutes_float = (abs(decimal_degrees) - degrees) * 60
        minutes = int(minutes_float)
        seconds_float = (minutes_float - minutes) * 60
        seconds = int(seconds_float * 10000)
        
        dms = (
            (degrees, 1),
            (minutes, 1),
            (seconds, 10000)
        )
        
        ref = ref_pos if decimal_degrees >= 0 else ref_neg
        return dms, ref

    @staticmethod
    def write_gps_to_exif(file_path: str, point: GPSPoint) -> bool:
        try:
            exif_dict = piexif.load(file_path)
            
            lat_dms, lat_ref = ExifHandler.decimal_to_dms(point.lat, 'N', 'S')
            lon_dms, lon_ref = ExifHandler.decimal_to_dms(point.lon, 'E', 'W')
            
            gps_ifd = {}
            gps_ifd[piexif.GPSIFD.GPSVersionID] = (2, 0, 0, 0)
            gps_ifd[piexif.GPSIFD.GPSLatitude] = lat_dms
            gps_ifd[piexif.GPSIFD.GPSLatitudeRef] = lat_ref
            gps_ifd[piexif.GPSIFD.GPSLongitude] = lon_dms
            gps_ifd[piexif.GPSIFD.GPSLongitudeRef] = lon_ref
            
            if point.ele is not None:
                gps_ifd[piexif.GPSIFD.GPSAltitude] = (int(point.ele * 100), 100)
                gps_ifd[piexif.GPSIFD.GPSAltitudeRef] = 0 if point.ele >= 0 else 1
            
            if point.time:
                time_str = point.time.strftime('%Y:%m:%d %H:%M:%S')
                gps_ifd[piexif.GPSIFD.GPSDateStamp] = time_str[:10].encode('utf-8')
                gps_ifd[piexif.GPSIFD.GPSTimeStamp] = (
                    (point.time.hour, 1),
                    (point.time.minute, 1),
                    (point.time.second, 1)
                )
            
            exif_dict['GPS'] = gps_ifd
            exif_bytes = piexif.dump(exif_dict)
            
            with Image.open(file_path) as img:
                img.save(file_path, exif=exif_bytes)
            
            return True
        except Exception as e:
            print(f"Failed to write EXIF: {file_path}, error: {e}")
            return False
