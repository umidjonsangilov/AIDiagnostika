from math import radians, sin, cos, sqrt, atan2


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def nearest_clinic(lat: float, lon: float, clinics: list) -> object | None:
    """clinics — Clinic ORM ob'ektlari ro'yxati. latitude/longitude bo'lgan eng yaqinini qaytaradi."""
    candidates = [c for c in clinics if c.latitude is not None and c.longitude is not None]
    if not candidates:
        return None
    return min(candidates, key=lambda c: haversine_km(lat, lon, c.latitude, c.longitude))
