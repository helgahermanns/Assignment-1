from pathlib import Path
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB


class ConsumerFlexibilityModel:
    """
    Optimization model for consumer energy flexibility using Gurobipy.
    
    Implements the linear programming formulation for Question 1a:
    - Minimizes daily energy procurement cost
    - Manages PV generation, flexible load, and grid interactions
    - Respects technical and operational constraints
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
        self.model = gp.Model("ConsumerFlexibility")
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
        
        print(f"Created variables for {self.T} time periods")
        
    def _create_constraints(self):
        """Create all constraints for the optimization model."""
        
        # 1. Energy balance constraint: ℓt = pt^PV + ut - xt for all t
        self.energy_balance = self.model.addConstrs(
            (self.load[t] == self.pv_used[t] + self.import_grid[t] - self.export_grid[t]
             for t in range(self.T)), name="energy_balance")
        
        # 2. Load limits: 0 ≤ ℓt ≤ L_max for all t
        self.load_max_constrs = self.model.addConstrs(
            (self.load[t] <= self.data['load_max'] for t in range(self.T)), 
            name="load_max")
        
        # 3. PV generation limits: 0 ≤ pt^PV ≤ pt^PV,max for all t
        self.pv_max_constrs = self.model.addConstrs(
            (self.pv_used[t] <= self.data['pv_max_hourly'][t] for t in range(self.T)), 
            name="pv_max")
        
        # 4. Grid import limits: 0 ≤ ut ≤ 1000 for all t
        self.import_max_constrs = self.model.addConstrs(
            (self.import_grid[t] <= self.data['max_import'] for t in range(self.T)), 
            name="import_max")
        
        # 5. Grid export limits: 0 ≤ xt ≤ 500 for all t
        self.export_max_constrs = self.model.addConstrs(
            (self.export_grid[t] <= self.data['max_export'] for t in range(self.T)), 
            name="export_max")
        
        # 6. Minimum daily energy consumption: Σ ℓt ≥ E^min
        self.min_energy_constr = self.model.addConstr(
            gp.quicksum(self.load[t] for t in range(self.T)) >= self.data['min_daily_energy'],
            name="min_daily_energy")
        
        print("Created all constraints")
        
    def _set_objective(self):
        """Set the objective function to minimize daily energy procurement cost."""
        
        # Objective: min Σ[(πt + τ^imp)ut - (πt - τ^exp)xt]
        import_costs = gp.quicksum(
            (self.data['energy_prices'][t] + self.data['import_tariff']) * self.import_grid[t]
            for t in range(self.T))
        
        export_revenues = gp.quicksum(
            (self.data['energy_prices'][t] - self.data['export_tariff']) * self.export_grid[t]
            for t in range(self.T))
        
        self.model.setObjective(import_costs - export_revenues, GRB.MINIMIZE)
        print("Set objective function")
        
    def solve(self):
        """Solve the optimization model and return results."""
        
        print("\nSolving optimization model...")
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
        
        results = {
            'optimal_cost': self.model.objVal,
            'load_schedule': [self.load[t].x for t in range(self.T)],
            'pv_schedule': [self.pv_used[t].x for t in range(self.T)],
            'import_schedule': [self.import_grid[t].x for t in range(self.T)],
            'export_schedule': [self.export_grid[t].x for t in range(self.T)],
            'total_energy_consumed': sum(self.load[t].x for t in range(self.T)),
            'total_pv_used': sum(self.pv_used[t].x for t in range(self.T)),
            'total_imported': sum(self.import_grid[t].x for t in range(self.T)),
            'total_exported': sum(self.export_grid[t].x for t in range(self.T))
        }
        
        return results
        
    def print_summary(self, results):
        """Print a summary of the optimization results."""
        
        print("\n" + "="*60)
        print("OPTIMIZATION RESULTS SUMMARY")
        print("="*60)
        print(f"Optimal Daily Cost: {results['optimal_cost']:.2f} DKK")
        print(f"Total Energy Consumed: {results['total_energy_consumed']:.2f} kWh")
        print(f"Total PV Used: {results['total_pv_used']:.2f} kWh")
        print(f"Total Imported: {results['total_imported']:.2f} kWh") 
        print(f"Total Exported: {results['total_exported']:.2f} kWh")
        print("="*60)
        
        # Check if minimum energy constraint is satisfied
        if results['total_energy_consumed'] >= self.data['min_daily_energy']:
            print(f"✓ Minimum energy constraint satisfied ({self.data['min_daily_energy']} kWh)")
        else:
            print(f"✗ Minimum energy constraint violated!")
            
    def get_hourly_schedule_df(self, results):
        """Return results as a pandas DataFrame for easy viewing."""
        
        df = pd.DataFrame({
            'Hour': range(1, self.T + 1),
            'Energy_Price': self.data['energy_prices'],
            'PV_Available': self.data['pv_max_hourly'],
            'PV_Used': results['pv_schedule'],
            'Load': results['load_schedule'],
            'Import': results['import_schedule'],
            'Export': results['export_schedule']
        })
        
        return df