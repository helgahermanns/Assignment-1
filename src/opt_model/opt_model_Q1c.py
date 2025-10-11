from pathlib import Path
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB


class ConsumerFlexibilityModelQ1c:
    """
    Optimization model for consumer energy flexibility with battery storage - Question 1c.
    
    Implements the linear programming formulation for Question 1c:
    - Extends Q1b with battery storage dynamics and constraints
    - Minimizes daily energy procurement cost and discomfort cost
    - Manages PV generation, flexible load, battery storage, and grid interactions
    - Includes battery charge/discharge variables and state of charge dynamics
    - Uses tie-breaker epsilon to prevent simultaneous charge/discharge
    """

    def __init__(self, data: dict):
        """
        Initialize the optimization model with data.
        
        Args:
            data: Dictionary containing optimization parameters from DataLoader
        """
        self.data = data
        self.T = data['T']  # Time horizon (24 hours)
        
        # Battery parameters from unified data structure (storage appliance BESS_01)
        appliances = data.get('appliances', {})
        if 'BESS_01' not in appliances:
            raise ValueError("BESS_01 storage parameters not found in appliances data")
            
        storage_params = appliances['BESS_01']
        if storage_params.get('type') != 'storage':
            raise ValueError("BESS_01 is not a storage appliance")
            
        self.s_max = storage_params['storage_capacity_kWh']  # Maximum battery capacity (kWh)
        self.eta_c = storage_params['charging_efficiency']    # Charging efficiency
        self.eta_r = storage_params['discharging_efficiency'] # Discharge efficiency
        self.c_max = storage_params['max_charge_power_kW']    # Maximum charge rate (kW)
        self.r_max = storage_params['max_discharge_power_kW'] # Maximum discharge rate (kW)
        self.s_0 = self.s_max / 2  # Initial SoC (50% of capacity)
        self.s_T = self.s_max / 2  # Final SoC (50% of capacity)
        self.epsilon = 1e-3 # Small epsilon for tie-breaker (increased to prevent simultaneous charge/discharge)
        
        # Create Gurobi model
        self.model = gp.Model("ConsumerFlexibilityQ1c")
        self.model.setParam('OutputFlag', 0)  # Disable Gurobi output
        
        # Initialize variables and constraints
        self._create_variables()
        self._create_constraints()
        self._set_objective()
        
    def _create_variables(self):
        """Create decision variables for the optimization model."""
        
        # Decision variables for each time period t
        self.load = self.model.addVars(self.T, name="load", lb=0)  # ℓt
        self.pv_used = self.model.addVars(self.T, name="pv_used", lb=0)  # pt^PV
        self.import_grid = self.model.addVars(self.T, name="import", lb=0)  # ut
        self.export_grid = self.model.addVars(self.T, name="export", lb=0)  # xt
        
        # Deviation variables for flexibility (from Q1b)
        self.dev_plus = self.model.addVars(self.T, name="dev_plus", lb=0)   # dt^+ (over-consumption)
        self.dev_minus = self.model.addVars(self.T, name="dev_minus", lb=0)  # dt^- (under-consumption)
        
        # Battery variables (new for Q1c)
        self.charge = self.model.addVars(self.T, name="charge", lb=0, ub=self.c_max)     # ct (charge rate, kW)
        self.discharge = self.model.addVars(self.T, name="discharge", lb=0, ub=self.r_max) # rt (discharge rate, kW)
        self.soc = self.model.addVars(self.T, name="soc", lb=0, ub=self.s_max)           # st (state of charge, kWh)
        
        # Model variables created
        
    def _create_constraints(self):
        """Create all constraints for the optimization model based on the specification."""
        
        # Constraint (11): Battery dynamics - et = et-1 + η_ch*ct - (1/η_dis)*dt for all t
        self.battery_dynamics = []
        
        # Initial state (t=0): e0 = e^target + η_ch*c0 - d0/η_dis
        self.battery_dynamics.append(
            self.model.addConstr(
                self.soc[0] == self.s_0 + self.eta_c * self.charge[0] - self.discharge[0] / self.eta_r,
                name="battery_dynamics_0"))
        
        # Subsequent states (t=1 to T-1): et = et-1 + η_ch*ct - dt/η_dis
        for t in range(1, self.T):
            self.battery_dynamics.append(
                self.model.addConstr(
                    self.soc[t] == self.soc[t-1] + self.eta_c * self.charge[t] - self.discharge[t] / self.eta_r,
                    name=f"battery_dynamics_{t}"))
        
        # Constraint (12): Battery energy limits - 0 ≤ et ≤ E^max for all t
        # (Already handled by variable bounds: lb=0, ub=self.s_max)
        
        # Constraint (13): Battery power limits - 0 ≤ ct ≤ P_ch^max, 0 ≤ dt ≤ P_dis^max for all t
        # (Already handled by variable bounds for charge and discharge)
        
        # Constraint (14): Boundary condition - e0 = eT = e^target  
        self.initial_soc = self.model.addConstr(
            self.soc[0] >= self.s_0, name="initial_soc_min")  # Allow flexibility in initial state
        self.final_soc = self.model.addConstr(
            self.soc[self.T-1] == self.s_T, name="final_soc")
        
        # Constraint (15): Extended power balance - ℓt = pt^PV + dt - ct + ut - xt for all t
        self.energy_balance = self.model.addConstrs(
            (self.load[t] == self.pv_used[t] + self.discharge[t] - self.charge[t] 
             + self.import_grid[t] - self.export_grid[t] for t in range(self.T)), 
            name="energy_balance")
        
        # Constraint (16): Load and PV limits - 0 ≤ ℓt ≤ L_t^max, 0 ≤ pt^PV ≤ pt^PV,max for all t
        self.load_max_constrs = self.model.addConstrs(
            (self.load[t] <= self.data['load_max'] for t in range(self.T)), 
            name="load_max")
        self.pv_max_constrs = self.model.addConstrs(
            (self.pv_used[t] <= self.data['pv_max_hourly'][t] for t in range(self.T)), 
            name="pv_max")
        
        # Constraint (17): Non-negativity - ut, xt, ct, dt, dt^+, dt^- ≥ 0 for all t
        # (Already handled by variable bounds lb=0)
        
        # Additional constraints from Q1b for flexibility
        # Deviation constraint: ℓt - ℓt^ref = dt^+ - dt^- for all t
        self.deviation_balance = self.model.addConstrs(
            (self.load[t] - self.data['reference_load'][t] == 
             self.dev_plus[t] - self.dev_minus[t] for t in range(self.T)), 
            name="deviation_balance")
        
        # Grid import/export limits (practical constraints)
        self.import_max_constrs = self.model.addConstrs(
            (self.import_grid[t] <= self.data['max_import'] for t in range(self.T)), 
            name="import_max")
        self.export_max_constrs = self.model.addConstrs(
            (self.export_grid[t] <= self.data['max_export'] for t in range(self.T)), 
            name="export_max")
        
        # Constraints created
        
    def _set_objective(self):
        """Set the objective function to minimize daily energy procurement cost, discomfort cost, and battery tie-breaker."""
        
        # Energy cost: Σ(πt + τt)ut - Σ(πt - τt)xt (from clear formulation)
        import_costs = gp.quicksum(
            (self.data['energy_prices'][t] + self.data['import_tariff']) * self.import_grid[t]
            for t in range(self.T))
        
        export_revenues = gp.quicksum(
            (self.data['energy_prices'][t] - self.data['export_tariff']) * self.export_grid[t]
            for t in range(self.T))
        
        energy_cost = import_costs - export_revenues
        
        # Discomfort costs: Σ[w(dt^+ + dt^-)]
        discomfort_cost = gp.quicksum(
            self.data['discomfort_weight'] * (self.dev_plus[t] + self.dev_minus[t])
            for t in range(self.T))
        
        # Battery tie-breaker: ε * Σ(ct + rt) to discourage simultaneous charge/discharge
        # This keeps the problem linear while avoiding binary variables
        battery_tiebreaker = self.epsilon * gp.quicksum(
            self.charge[t] + self.discharge[t] for t in range(self.T))
        
        # Total objective: minimize total cost
        total_cost = energy_cost + discomfort_cost + battery_tiebreaker
        
        self.model.setObjective(total_cost, GRB.MINIMIZE)
        
        # Objective function set
        
    def solve(self):
        """
        Solve the optimization model and return results.
        
        Returns:
            dict: Dictionary containing optimal solution and key metrics
        """
        
        # Optimize the model
        self.model.optimize()
        
        # Check solution status
        if self.model.status == GRB.OPTIMAL:
            
            # Extract solution values
            results = self._extract_solution()
            return results
            
        elif self.model.status == GRB.INFEASIBLE:
            print("Model is infeasible")
            self.model.computeIIS()
            self.model.write("infeasible_model_Q1c.ilp")
            return None
            
        elif self.model.status == GRB.UNBOUNDED:
            print("Model is unbounded")
            return None
            
        else:
            print(f"Optimization terminated with status {self.model.status}")
            return None
    
    def _extract_solution(self):
        """Extract solution values and compute key metrics."""
        
        # Extract decision variable values
        load_schedule = [self.load[t].x for t in range(self.T)]
        pv_schedule = [self.pv_used[t].x for t in range(self.T)]
        import_schedule = [self.import_grid[t].x for t in range(self.T)]
        export_schedule = [self.export_grid[t].x for t in range(self.T)]
        dev_plus_schedule = [self.dev_plus[t].x for t in range(self.T)]
        dev_minus_schedule = [self.dev_minus[t].x for t in range(self.T)]
        
        # Extract battery variables (new for Q1c)
        charge_schedule = [self.charge[t].x for t in range(self.T)]
        discharge_schedule = [self.discharge[t].x for t in range(self.T)]
        soc_schedule = [self.soc[t].x for t in range(self.T)]
        
        # Calculate cost components
        total_imported = sum(import_schedule)
        total_exported = sum(export_schedule)
        
        energy_cost = sum(
            (self.data['energy_prices'][t] + self.data['import_tariff']) * import_schedule[t] -
            (self.data['energy_prices'][t] - self.data['export_tariff']) * export_schedule[t]
            for t in range(self.T))
        
        discomfort_penalty = sum(
            self.data['discomfort_weight'] * (dev_plus_schedule[t] + dev_minus_schedule[t])
            for t in range(self.T))
        
        battery_tiebreaker_cost = self.epsilon * sum(
            charge_schedule[t] + discharge_schedule[t] for t in range(self.T))
        
        # Calculate battery metrics
        total_charged = sum(charge_schedule)
        total_discharged = sum(discharge_schedule)
        energy_stored = sum(self.eta_c * c for c in charge_schedule)  # Energy actually stored
        energy_retrieved = sum(d / self.eta_r for d in discharge_schedule)  # Energy actually retrieved
        battery_efficiency = energy_retrieved / energy_stored if energy_stored > 0 else 0
        
        # Get dual variables (shadow prices) with error handling
        try:
            # Extract dual variables using Gurobi's Pi attribute
            dual_energy = [self.energy_balance[t].Pi for t in range(self.T)]
            dual_deviation = [self.deviation_balance[t].Pi for t in range(self.T)]
            dual_battery = [self.battery_dynamics[t].Pi for t in range(self.T)]
            dual_final_soc = self.final_soc.Pi
            
            # Store power balance dual as lambda_t for easy access
            dual_power_balance = dual_energy
            
        except (AttributeError, Exception) as e:
            # Fallback if dual variables not available
            dual_energy = [0.0 for t in range(self.T)]
            dual_deviation = [0.0 for t in range(self.T)]
            dual_battery = [0.0 for t in range(self.T)]
            dual_final_soc = 0.0
            dual_power_balance = [0.0 for t in range(self.T)]
            print(f"Warning: Dual variables not available ({e}), using zeros")
        
        # Calculate summary statistics
        results = {
            # Objective and costs
            'optimal_cost': self.model.objVal,
            'energy_cost': energy_cost,
            'discomfort_penalty': discomfort_penalty,
            'battery_tiebreaker_cost': battery_tiebreaker_cost,
            
            # Schedules
            'load_schedule': load_schedule,
            'pv_schedule': pv_schedule,
            'import_schedule': import_schedule,
            'export_schedule': export_schedule,
            'dev_plus_schedule': dev_plus_schedule,
            'dev_minus_schedule': dev_minus_schedule,
            'charge_schedule': charge_schedule,
            'discharge_schedule': discharge_schedule,
            'soc_schedule': soc_schedule,
            
            # Energy totals
            'total_energy_consumed': sum(load_schedule),
            'total_pv_used': sum(pv_schedule),
            'total_imported': total_imported,
            'total_exported': total_exported,
            'total_dev_plus': sum(dev_plus_schedule),
            'total_dev_minus': sum(dev_minus_schedule),
            
            # Battery metrics
            'total_charged': total_charged,
            'total_discharged': total_discharged,
            'energy_stored': energy_stored,
            'energy_retrieved': energy_retrieved,
            'battery_efficiency': battery_efficiency,
            'initial_soc': self.s_0,
            'final_soc': soc_schedule[-1] if soc_schedule else self.s_T,
            'max_soc': max(soc_schedule) if soc_schedule else 0,
            'min_soc': min(soc_schedule) if soc_schedule else 0,
            
            # Reference data
            'reference_load': self.data['reference_load'],
            'pv_max_hourly': self.data['pv_max_hourly'],
            'energy_prices': self.data['energy_prices'],
            
            # Dual variables (shadow prices)
            'dual_energy': dual_energy,
            'dual_deviation': dual_deviation,
            'dual_battery': dual_battery,
            'dual_final_soc': dual_final_soc,
            'dual_power_balance': dual_power_balance,  # Lambda_t for power balance constraint
            'avg_dual_energy': np.mean([abs(d) for d in dual_energy]),
            'avg_dual_deviation': np.mean([abs(d) for d in dual_deviation]),
            'avg_dual_battery': np.mean([abs(d) for d in dual_battery]),
            'peak_dual_import': max([abs(d) for d in dual_energy]),
            'peak_dual_export': min([d for d in dual_energy]),
        }
        
        return results
    
    def print_solution_summary(self, results):
        """Print a comprehensive summary of the solution."""
        
        print("\n" + "="*60)
        print("SOLUTION SUMMARY - Q1c with Battery Storage")
        print("="*60)
        
        print(f"\n🔋 BATTERY PERFORMANCE:")
        print(f"   Initial SoC: {results['initial_soc']:.2f} kWh")
        print(f"   Final SoC: {results['final_soc']:.2f} kWh")
        print(f"   Max SoC: {results['max_soc']:.2f} kWh")
        print(f"   Min SoC: {results['min_soc']:.2f} kWh")
        print(f"   Total Charged: {results['total_charged']:.2f} kW·h")
        print(f"   Total Discharged: {results['total_discharged']:.2f} kW·h")
        print(f"   Round-trip Efficiency: {results['battery_efficiency']*100:.1f}%")
        
        print(f"\n💰 COST BREAKDOWN:")
        print(f"   Total Cost: {results['optimal_cost']:.2f} DKK")
        print(f"   Energy Cost: {results['energy_cost']:.2f} DKK")
        print(f"   Discomfort Cost: {results['discomfort_penalty']:.2f} DKK")
        print(f"   Battery Tie-breaker: {results['battery_tiebreaker_cost']:.6f} DKK")
        
        print(f"\n⚡ ENERGY BALANCE:")
        print(f"   Total Consumption: {results['total_energy_consumed']:.2f} kWh")
        print(f"   PV Used: {results['total_pv_used']:.2f} kWh")
        print(f"   Grid Import: {results['total_imported']:.2f} kWh")
        print(f"   Grid Export: {results['total_exported']:.2f} kWh")
        
        print(f"\n📊 FLEXIBILITY METRICS:")
        print(f"   Over-consumption: {results['total_dev_plus']:.2f} kWh")
        print(f"   Under-consumption: {results['total_dev_minus']:.2f} kWh")
        
        reference_sum = sum(results['reference_load'])
        flexibility_used = results['total_dev_plus'] + results['total_dev_minus']
        flexibility_pct = (flexibility_used / reference_sum) * 100
        print(f"   Flexibility Utilized: {flexibility_pct:.1f}% of reference load")
        
        print(f"\n🔴 SHADOW PRICES (Dual Variables):")
        print(f"   Avg Energy Balance Dual: {results['avg_dual_energy']:.4f} DKK/kWh")
        print(f"   Avg Deviation Balance Dual: {results['avg_dual_deviation']:.4f} DKK/kWh")
        print(f"   Avg Battery Dynamics Dual: {results['avg_dual_battery']:.4f} DKK/kWh")
        print(f"   Final SoC Dual: {results['dual_final_soc']:.4f} DKK/kWh")
        
        print("="*60)