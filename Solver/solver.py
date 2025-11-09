import numpy as np
from gurobipy import Model, GRB


class Solver:
    def __init__(self, inputBuilder):
        self.inputBuilder = inputBuilder
        self.results = []
        self.feasible_networks = []

    def run(self):
        print("Running Stage 1 Solver with Gurobi MILP...")

        nominal_voltage = self.inputBuilder.nominal_voltage
        min_voltage = self.inputBuilder.min_voltage
        max_voltage = self.inputBuilder.max_voltage

        # Step 1: compute voltages & feasibility for all networks
        for spec in self.inputBuilder.network_specifications_list:
            line_name = spec.line
            size = spec.size
            line_impedance = spec.line_impedance
            line_length = spec.line_length
            total_impedance = line_impedance * line_length

            # Find corresponding summer/winter profiles
            summer_profile = None
            winter_profile = None

            for s in self.inputBuilder.summer_list:
                if s.line == line_name:
                    summer_profile = s.power_profile
                    break

            for w in self.inputBuilder.winter_list:
                if w.line == line_name:
                    winter_profile = w.power_profile
                    break

            # Skip if any profile missing
            if summer_profile is None or winter_profile is None:
                continue

            # Compute node voltages using linearized model
            summer_voltages = self.compute_voltages(nominal_voltage, total_impedance, summer_profile)
            winter_voltages = self.compute_voltages(nominal_voltage, total_impedance, winter_profile)

            # Check if within limits
            summer_ok = self.is_within_limits(summer_voltages, min_voltage, max_voltage)
            winter_ok = self.is_within_limits(winter_voltages, min_voltage, max_voltage)
            feasible = summer_ok and winter_ok

            # Compute regulation effort = maximum relative deviation from nominal
            # (i.e., voltage correction fraction)
            avg_voltage = (np.mean(summer_voltages) + np.mean(winter_voltages)) / 2
            regulation_effort = abs((avg_voltage - nominal_voltage) / nominal_voltage)

            result = {
                "line": line_name,
                "size": size,
                "total_impedance": total_impedance,
                "feasible": feasible,
                "effort": regulation_effort,
            }
            self.results.append(result)

            if feasible:
                self.feasible_networks.append(result)

        print(f"Feasible networks found: {len(self.feasible_networks)}")

        # Step 2: run MILP to select 10 networks (maximize size, minimize effort)
        if len(self.feasible_networks) > 0:
            self.run_milp_selection()
        else:
            print("No feasible networks found, skipping MILP optimization.")

    def compute_voltages(self, nominal_voltage, total_impedance, power_profile):
        """Linearized voltage drop model for serial network."""
        n = len(power_profile)
        voltages = np.zeros(n)
        voltages[0] = nominal_voltage
        cumulative_power = 0
        for i in range(1, n):
            cumulative_power += power_profile[i]
            voltage_drop = (total_impedance / nominal_voltage) * cumulative_power
            voltages[i] = nominal_voltage - voltage_drop
        return voltages

    def is_within_limits(self, voltages, min_v, max_v):
        """Check if all node voltages lie within statutory limits."""
        return np.all((voltages >= min_v) & (voltages <= max_v))

    def run_milp_selection(self):
        """
        MILP with Gurobi:
        Select 10 feasible networks that maximize total size and minimize effort.
        Combined objective: maximize (w1 * total_size - w2 * total_effort)
        """

        print("Building Gurobi MILP model...")

        model = Model("network_selection")
        model.Params.OutputFlag = 0  # silent run

        n = len(self.feasible_networks)
        x = {}
        for i in range(n):
            x[i] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}")

        # Objective components
        total_size = sum(self.feasible_networks[i]["size"] * x[i] for i in range(n))
        total_effort = sum(self.feasible_networks[i]["effort"] * x[i] for i in range(n))

        # Weighting factors (adjustable)
        w1 = 1.0    # weight for size
        w2 = 100.0  # weight for effort (scaled up since effort is small)
        model.setObjective(w1 * total_size - w2 * total_effort, GRB.MAXIMIZE)

        # Constraint: select exactly 10 networks
        model.addConstr(sum(x[i] for i in range(n)) == 10, "select_10")

        # Optimize
        model.optimize()

        selected = []
        for i in range(n):
            if x[i].x > 0.5:
                selected.append(self.feasible_networks[i])

        print("MILP optimization complete.")
        print(f"Selected {len(selected)} networks.")

        self.selected_networks = selected
        for s in selected:
            print(f"  Line: {s['line']}, Size: {s['size']}, Effort: {round(s['effort'], 6)}")
