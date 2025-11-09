from dataclasses import dataclass, field
from typing import List

@dataclass
class Summer:
    line: str
    power_profile: List[float] = field(default_factory=list)

    def __init__(self, line, power_profile):
        self.line = line
        # convert to list of floats, ignore or convert NaN-like values to 0.0
        self.power_profile = []
        for v in power_profile:
            try:
                self.power_profile.append(float(v))
            except Exception:
                # fallback to 0.0 for non-convertible entries
                self.power_profile.append(0.0)

    def average(self) -> float:
        if not self.power_profile:
            return 0.0
        return sum(self.power_profile) / len(self.power_profile)
