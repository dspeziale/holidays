from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

@dataclass
class Location:
    entity_name: str
    entity_id: str
    _raw_location: str = field(repr=False)
    location: list[str] = field(init=False)

    def __post_init__(self):
        self.location = self._raw_location.split(",")

@dataclass(frozen=True)
class Airport:
    title: str
    entity_id: str
    skyId: str

@dataclass
class SkyscannerResponse:
    json: dict
    session_id: str
    search_payload: dict
    origin: Airport
    destination: Optional[Airport] = None

    @property
    def itineraries(self) -> list:
        """Returns the list of itineraries from the response."""
        try:
            return self.json.get("itineraries", {}).get("results", [])
        except:
            return []

    @property
    def search_status(self) -> str:
        """Returns the search status (e.g., 'complete')."""
        try:
            return self.json.get("context", {}).get("status", "unknown")
        except:
            return "error"

@dataclass
class Coordinates:
    latitude: float
    longitude: float 

class CabinClass(Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"

class SpecialTypes(Enum):
    ANYTIME = "anytime"
    EVERYWHERE = "everywhere"
