class Parameter:
    def __init__(self,nominal_voltage,min_voltage,max_voltage,regulation_increase_limit,regulation_decrease_limit):
        self.nominal_voltage = nominal_voltage
        self.min_voltage = min_voltage
        self.max_voltage = max_voltage
        self.regulation_increase_limit = regulation_increase_limit
        self.regulation_decrease_limit = regulation_decrease_limit