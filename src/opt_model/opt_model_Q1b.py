from pathlib import Path
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB


class ConsumerFlexibilityModelQ1b:
    """
    Optimization model for consumer energy flexibility using Gurobipy - Question 1b.
    
    Implements the linear programming formulation for Question 1b:
    - Minimizes daily energy procurement cost and discomfort cost
    - Manages PV generation, flexible load with preference deviations, and grid interactions
    - Includes deviation variables to measure flexibility from reference consumption
    - Uses discomfort cost coefficients for increasing or decreasing consumption
    """

    def __init__(self, data: dict):
        """
        Initialize the optimization model with data.
        
        Args:
            data: Dictionary containing optimization parameters from DataLoader
        """
        self.data = data
        self.T = data['T']  # Time horizon (24 hours)
        
        # Create Gurobi model
        self.model = gp.Model("ConsumerFlexibilityQ1b")
        self.model.setParam('OutputFlag', 1)  # Enable output
        
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
        
        # Deviation variables for flexibility (Question 1b)
        self.dev_plus = self.model.addVars(self.T, name="dev_plus", lb=0)   # dt^+ (over-consumption)
        self.dev_minus = self.model.addVars(self.T, name="dev_minus", lb=0)  # dt^- (under-consumption)
        
        print(f"Created variables for {self.T} time periods including deviation variables")
        
    def _create_constraints(self):
        """Create all constraints for the optimization model."""
        
        # 1. Energy balance constraint: ℓt = pt^PV + ut - xt for all t
        self.energy_balance = self.model.addConstrs(
            (self.load[t] == self.pv_used[t] + self.import_grid[t] - self.export_grid[t]
             for t in range(self.T)), name="energy_balance")
        
        # 2. Deviation constraint: ℓt - ℓt^ref = dt^+ - dt^- for all t
        # This replaces the minimum daily energy constraint from Q1a
        self.deviation_balance = self.model.addConstrs(
            (self.load[t] - self.data['reference_load'][t] == 
             self.dev_plus[t] - self.dev_minus[t] for t in range(self.T)), 
            name="deviation_balance")
        
        # 3. Load limits: 0 ≤ ℓt ≤ L_max for all t
        self.load_max_constrs = self.model.addConstrs(
            (self.load[t] <= self.data['load_max'] for t in range(self.T)), 
            name="load_max")
        
        # 4. PV generation limits: 0 ≤ pt^PV ≤ pt^PV,max for all t
        self.pv_max_constrs = self.model.addConstrs(
            (self.pv_used[t] <= self.data['pv_max_hourly'][t] for t in range(self.T)), 
            name="pv_max")
        
        # 5. Grid import limits: 0 ≤ ut ≤ 1000 for all t
        self.import_max_constrs = self.model.addConstrs(
            (self.import_grid[t] <= self.data['max_import'] for t in range(self.T)), 
            name="import_max")
        
        # 6. Grid export limits: 0 ≤ xt ≤ 500 for all t
        self.export_max_constrs = self.model.addConstrs(
            (self.export_grid[t] <= self.data['max_export'] for t in range(self.T)), 
            name="export_max")
        
        print("Created all constraints including deviation constraints")
        
    def _set_objective(self):
        """Set the objective function to minimize daily energy procurement cost and discomfort cost."""
        
        # Energy procurement costs: Σ[(πt + τ^imp)ut - (πt - τ^exp)xt]
        import_costs = gp.quicksum(
            (self.data['energy_prices'][t] + self.data['import_tariff']) * self.import_grid[t]
            for t in range(self.T))
        
        export_revenues = gp.quicksum(
            (self.data['energy_prices'][t] - self.data['export_tariff']) * self.export_grid[t]
            for t in range(self.T))
        
        # Discomfort penalty: w * Σ[dt^+ + dt^-] (minimize total absolute deviations)
        discomfort_penalty = gp.quicksum(
            self.data['discomfort_weight'] * (self.dev_plus[t] + self.dev_minus[t])
            for t in range(self.T))
        
        # Total objective: minimize (energy costs + discomfort penalty)
        total_cost = import_costs - export_revenues + discomfort_penalty
        
        self.model.setObjective(total_cost, GRB.MINIMIZE)
        print("Set objective function with energy and discomfort costs")
        
    def solve(self):
        """Solve the optimization model and return results."""
        
        print("\nSolving Q1b optimization model...")
        self.model.optimize()
        
        if self.model.status == GRB.OPTIMAL:
            print(f"Optimal solution found!")
            print(f"Optimal objective value: {self.model.objVal:.2f} DKK")
            return self._extract_results()
        else:
            print(f"Optimization failed with status: {self.model.status}")
            return None
            
    def _extract_results(self):
        """Extract and structure the optimization results."""
        
        # Calculate cost components
        energy_cost = sum(
            (self.data['energy_prices'][t] + self.data['import_tariff']) * self.import_grid[t].x -
            (self.data['energy_prices'][t] - self.data['export_tariff']) * self.export_grid[t].x
            for t in range(self.T))
        
        discomfort_penalty = sum(
            self.data['discomfort_weight'] * (self.dev_plus[t].x + self.dev_minus[t].x)
            for t in range(self.T))
        
        # Extract dual variables (shadow prices)
        dual_energy_balance = [self.energy_balance[t].Pi for t in range(self.T)]
        dual_deviation_balance = [self.deviation_balance[t].Pi for t in range(self.T)]
        dual_import_max = [self.import_max_constrs[t].Pi for t in range(self.T)]
        dual_export_max = [self.export_max_constrs[t].Pi for t in range(self.T)]
        
        results = {
            'optimal_cost': self.model.objVal,
            'energy_cost': energy_cost,
            'discomfort_penalty': discomfort_penalty,
            'load_schedule': [self.load[t].x for t in range(self.T)],
            'pv_schedule': [self.pv_used[t].x for t in range(self.T)],
            'import_schedule': [self.import_grid[t].x for t in range(self.T)],
            'export_schedule': [self.export_grid[t].x for t in range(self.T)],
            'dev_plus_schedule': [self.dev_plus[t].x for t in range(self.T)],
            'dev_minus_schedule': [self.dev_minus[t].x for t in range(self.T)],
            'reference_load': self.data['reference_load'],
            'total_energy_consumed': sum(self.load[t].x for t in range(self.T)),
            'total_pv_used': sum(self.pv_used[t].x for t in range(self.T)),
            'total_imported': sum(self.import_grid[t].x for t in range(self.T)),
            'total_exported': sum(self.export_grid[t].x for t in range(self.T)),
            'total_dev_plus': sum(self.dev_plus[t].x for t in range(self.T)),
            'total_dev_minus': sum(self.dev_minus[t].x for t in range(self.T)),
            # Dual variables (shadow prices)
            'dual_energy_balance': dual_energy_balance,
            'dual_deviation_balance': dual_deviation_balance,
            'dual_import_max': dual_import_max,
            'dual_export_max': dual_export_max,
            'avg_dual_energy': sum(dual_energy_balance)/len(dual_energy_balance),
            'avg_dual_deviation': sum(dual_deviation_balance)/len(dual_deviation_balance),
            'peak_dual_import': max(dual_import_max),
            'peak_dual_export': max(dual_export_max)
        }
        
        return results
        
    def print_summary(self, results):
        """Print a summary of the optimization results."""
        
        print("\n" + "="*60)
        print("Q1B OPTIMIZATION RESULTS SUMMARY")
        print("="*60)
        print(f"Optimal Total Cost: {results['optimal_cost']:.2f} DKK")
        print(f"  - Energy Cost: {results['energy_cost']:.2f} DKK")
        print(f"  - Discomfort Cost: {results['discomfort_cost']:.2f} DKK")
        print(f"Total Energy Consumed: {results['total_energy_consumed']:.2f} kWh")
        print(f"Total Reference Energy: {sum(results['reference_load']):.2f} kWh")
        print(f"Total PV Used: {results['total_pv_used']:.2f} kWh")
        print(f"Total Imported: {results['total_imported']:.2f} kWh") 
        print(f"Total Exported: {results['total_exported']:.2f} kWh")
        print(f"Total Over-consumption: {results['total_dev_plus']:.2f} kWh")
        print(f"Total Under-consumption: {results['total_dev_minus']:.2f} kWh")
        print("="*60)
        
        # Calculate flexibility metrics
        flexibility_ratio = (results['total_dev_plus'] + results['total_dev_minus']) / sum(results['reference_load']) * 100
        print(f"Flexibility Usage: {flexibility_ratio:.1f}% of reference load")
        
    def get_hourly_schedule_df(self, results):
        """Return results as a pandas DataFrame for easy viewing."""
        
        df = pd.DataFrame({
            'Hour': range(1, self.T + 1),
            'Energy_Price': self.data['energy_prices'],
            'PV_Available': self.data['pv_max_hourly'],
            'Reference_Load': results['reference_load'],
            'Actual_Load': results['load_schedule'],
            'PV_Used': results['pv_schedule'],
            'Import': results['import_schedule'],
            'Export': results['export_schedule'],
            'Dev_Plus': results['dev_plus_schedule'],
            'Dev_Minus': results['dev_minus_schedule'],
            'Discomfort_Cost_Plus': self.data['discomfort_cost_plus'],
            'Discomfort_Cost_Minus': self.data['discomfort_cost_minus']
        })
        
        return df
        
    def analyze_flexibility_usage(self, results):
        """Analyze how flexibility is being used throughout the day."""
        
        print("\n" + "="*60)
        print("FLEXIBILITY ANALYSIS")
        print("="*60)
        
        df = self.get_hourly_schedule_df(results)
        
        # Find hours with significant deviations
        significant_plus = df[df['Dev_Plus'] > 0.1]
        significant_minus = df[df['Dev_Minus'] > 0.1]
        
        if not significant_plus.empty:
            print("Hours with over-consumption (>0.1 kWh):")
            for _, row in significant_plus.iterrows():
                print(f"  Hour {row['Hour']:2d}: +{row['Dev_Plus']:.2f} kWh "
                      f"(Price: {row['Energy_Price']:.1f} DKK/kWh)")
        
        if not significant_minus.empty:
            print("Hours with under-consumption (>0.1 kWh):")
            for _, row in significant_minus.iterrows():
                print(f"  Hour {row['Hour']:2d}: -{row['Dev_Minus']:.2f} kWh "
                      f"(Price: {row['Energy_Price']:.1f} DKK/kWh)")
        
        print("="*60)