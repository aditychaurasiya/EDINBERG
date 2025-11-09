import pandas as pd
from Entities.network_specifications import Network_specifications
from Entities.summer import Summer
from Entities.winter import Winter
from Entities.parameter import Parameter


class InputBuilder:
    def __init__(self):
        self.path = 'DATA (1)\\'
        self.network_specifications_list = []
        self.summer_list = []
        self.winter_list = []
        self.parameters = {}

    def build(self):
        self.read_network_specifications(self.path + 'network_specifications.xlsx')
        self.read_summer_data(self.path + 'summer.xlsx')
        self.read_winter_data(self.path + 'winter.xlsx')
        self.read_parameters()

    def read_network_specifications(self, filepath):
        network_specifications_df = pd.read_excel(filepath)
        for index, row in network_specifications_df.iterrows():
            line = row['line']
            size = row['size']
            line_impedance = row['line_impedance']
            line_length = row['line_length']
            network_spec = Network_specifications(line, size, line_impedance, line_length)
            self.network_specifications_list.append(network_spec)

    def read_summer_data(self, filepath):
        summer_df = pd.read_excel(filepath)
        for index, row in summer_df.iterrows():
            line = row['line']
            summer_power_profile = list(row[1:])   # assuming first column is 'line', rest are power values
            summer_data = Summer(line, summer_power_profile)
            self.summer_list.append(summer_data)

    def read_winter_data(self, filepath):
        winter_df = pd.read_excel(filepath)
        for index, row in winter_df.iterrows():
            line = row['line']
            winter_power_profile = list(row[1:])   # assuming first column is 'line', rest are power values
            winter_data = Winter(line, winter_power_profile)
            self.winter_list.append(winter_data)

    def read_parameters(self):
        self.nominal_voltage = 230          # V
        self.min_voltage = 207              # V
        self.max_voltage = 253              # V
        self.regulation_increase_limit = 0.05   # +5%
        self.regulation_decrease_limit = -0.05  # -5%
        parameter = Parameter(self.nominal_voltage, self.min_voltage, self.max_voltage,
                              self.regulation_increase_limit, self.regulation_decrease_limit)
        self.parameters = parameter
