from dataclasses import dataclass
from typing import Literal


@dataclass
class SensorReading:
    sensor_id: str
    value: float
    timestamp: str

    def normalize(self) -> float:
        return self.value / 100.0

    def determine_status(self) -> Literal["nominal", "critical"]:
        return "nominal" if self.normalize() < 0.8 else "critical"
