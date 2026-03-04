# -*- coding: utf-8 -*-
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from gps_parser import GPSPoint

class GPSMatcher:
    def __init__(self, gps_points: List[GPSPoint]):
        self.gps_points = sorted(gps_points, key=lambda p: p.time)
        self.time_index = {p.time: i for i, p in enumerate(self.gps_points)}
        self.times = [p.time for p in self.gps_points]

    def find_closest_point(self, photo_time: datetime, max_time_diff: int = 3600) -> Optional[GPSPoint]:
        if not self.gps_points:
            return None
        
        if photo_time.tzinfo is None:
            photo_time = photo_time.replace(tzinfo=timezone.utc)
        
        left = 0
        right = len(self.times) - 1
        
        while left <= right:
            mid = (left + right) // 2
            if self.times[mid] < photo_time:
                left = mid + 1
            else:
                right = mid - 1
        
        candidates = []
        if right >= 0:
            candidates.append(right)
        if left < len(self.times):
            candidates.append(left)
        
        best_point = None
        min_diff = float('inf')
        
        for idx in candidates:
            point = self.gps_points[idx]
            diff = abs((point.time - photo_time).total_seconds())
            if diff < min_diff:
                min_diff = diff
                best_point = point
        
        if best_point and min_diff <= max_time_diff:
            return best_point
        return None

    def interpolate_point(self, photo_time: datetime) -> Optional[GPSPoint]:
        if not self.gps_points or len(self.gps_points) < 2:
            return None
        
        if photo_time.tzinfo is None:
            photo_time = photo_time.replace(tzinfo=timezone.utc)
        
        before = None
        after = None
        
        for i in range(len(self.gps_points) - 1):
            p1 = self.gps_points[i]
            p2 = self.gps_points[i + 1]
            if p1.time <= photo_time <= p2.time:
                before = p1
                after = p2
                break
        
        if before is None or after is None:
            return None
        
        total_seconds = (after.time - before.time).total_seconds()
        if total_seconds == 0:
            return before
        
        ratio = (photo_time - before.time).total_seconds() / total_seconds
        
        lat = before.lat + (after.lat - before.lat) * ratio
        lon = before.lon + (after.lon - before.lon) * ratio
        ele = None
        if before.ele is not None and after.ele is not None:
            ele = before.ele + (after.ele - before.ele) * ratio
        
        return GPSPoint(lat=lat, lon=lon, time=photo_time, ele=ele)
