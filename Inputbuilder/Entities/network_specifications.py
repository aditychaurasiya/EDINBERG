from dataclasses import dataclass

@dataclass
class Network_specifications:
    line: str
    size: float
    line_impedance: float
    line_length: float

    def __post_init__(self):
        # basic conversions/validation
        try:
            self.size = float(self.size)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid size for line {self.line}: {self.size}")
        try:
            self.line_impedance = float(self.line_impedance)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid line_impedance for line {self.line}: {self.line_impedance}")
        try:
            self.line_length = float(self.line_length)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid line_length for line {self.line}: {self.line_length}")
