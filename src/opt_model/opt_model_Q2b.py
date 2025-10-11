"""
Question 2b - Battery Investment Optimization Model

This model extends the Q1 framework to optimize battery capacity (E_B) as an investment decision.
Key differences from Q1c:
- Battery capacity E_B is a decision variable (not fixed)
- Power characteristics scale linearly with capacity
- 10-year total cost objective including capital investment
- Supports scenario analysis across tariff structures and consumer preferences
"""

from pathlib import Path
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
from typing import Optional, List, Dict, Any


class BatteryInvestmentModelQ2b:
    """
    Optimization model for battery investment analysis - Question 2b.
    
    Implements the optimization problem formulated in the assignment:
    - Decision variable: Battery capacity E_B [kWh] 
    - Minimizes 10-year total cost: investment + operational costs
    - Linear scaling of battery power characteristics with capacity
    - Extends Q1 consumer flexibility framework
    """

    def __init__(self, data: Dict[str, Any], investment_cost_per_kwh: float = 6000.0, 
                 battery_sizes_to_test: Optional[List[float]] = None):
        """
        Initialize the battery investment optimization model.
        
        Args:
            data: Dictionary containing optimization parameters from DataLoader
            investment_cost_per_kwh: Capital cost per kWh of battery capacity [DKK/kWh]
            battery_sizes_to_test: List of battery sizes to evaluate [kWh]. If None, uses sweep approach.
        """
        self.data = data
        self.T = data['T']  # Time horizon (24 hours)
        self.investment_cost = investment_cost_per_kwh  # C_inv [DKK/kWh]
        self.lifetime_days = 365 * 10  # N_d = 3,650 days
        
        # Battery scaling parameters from Q1 reference (BESS_01 as 1 kWh baseline)
        # From problem statement: characteristics scale linearly and uniformly
        appliances = data.get('appliances', {})
        if 'BESS_01' in appliances:
            ref_battery = appliances['BESS_01']
            self.ref_capacity = ref_battery['storage_capacity_kWh']  # Reference: 1 kWh
            self.ref_charge_power = ref_battery['max_charge_power_kW']  # r^ch_max = 0.15 kW per kWh
            self.ref_discharge_power = ref_battery['max_discharge_power_kW']  # r^dis_max = 0.30 kW per kWh
        else:
            # Use problem statement parameters as fallback
            self.ref_capacity = 1.0  # 1 kWh reference
            self.ref_charge_power = 0.15  # 0.15 kW per kWh capacity
            self.ref_discharge_power = 0.30  # 0.30 kW per kWh capacity
            
        # Charging/discharging efficiencies (remain constant regardless of size)
        self.eta_ch = 0.9   # η_ch = 0.9
        self.eta_dis = 0.9  # η_dis = 0.9 (round-trip efficiency = 0.81)
        
        # Battery sizes to evaluate
        if battery_sizes_to_test is None:
            self.battery_sizes = [0, 3, 6, 9, 12, 15]  # Standard sweep [kWh]
        else:
            self.battery_sizes = battery_sizes_to_test
            
        # Store results for each battery size
        self.size_results = {}
        
        # Epsilon for numerical stability
        self.epsilon = 1e-3
        
    def solve_for_battery_size(self, E_B: float):
        """
        Solve the optimization for a specific battery capacity.
        
        Args:
            E_B: Battery capacity [kWh]
            
        Returns:
            dict: Optimization results for this battery size
        """
        
        # Create Gurobi model for this battery size
        model = gp.Model(f"BatteryInvestment_EB_{E_B}")
        model.setParam('OutputFlag', 0)  # Disable output
        
        # Battery power limits scale with capacity
        P_ch_max = self.ref_charge_power * E_B  # Charge power limit [kW]
        P_dis_max = self.ref_discharge_power * E_B  # Discharge power limit [kW]
        
        # Decision variables for each time period t
        load = model.addVars(self.T, name="load", lb=0)  # ℓ_t
        pv_used = model.addVars(self.T, name="pv_used", lb=0)  # p_t^PV
        import_grid = model.addVars(self.T, name="import", lb=0)  # u_t
        export_grid = model.addVars(self.T, name="export", lb=0)  # x_t
        
        # Flexibility deviation variables (from Q1b)
        dev_plus = model.addVars(self.T, name="dev_plus", lb=0)   # d_t^+
        dev_minus = model.addVars(self.T, name="dev_minus", lb=0)  # d_t^-
        
        # Battery variables (only if E_B > 0)
        if E_B > 0:
            charge = model.addVars(self.T, name="charge", lb=0, ub=P_ch_max)     # p_t^ch
            discharge = model.addVars(self.T, name="discharge", lb=0, ub=P_dis_max) # p_t^dis
            soc = model.addVars(self.T, name="soc", lb=0, ub=E_B)                # SoC_t
        else:
            # No battery variables for E_B = 0
            charge = {t: 0 for t in range(self.T)}
            discharge = {t: 0 for t in range(self.T)}
            soc = {t: 0 for t in range(self.T)}
        
        # === CONSTRAINTS ===
        
        # Power balance constraint: ℓ_t = p_t^PV + u_t - x_t + p_t^dis - p_t^ch
        energy_balance = model.addConstrs(
            (load[t] == pv_used[t] + import_grid[t] - export_grid[t] +
             (discharge[t] if E_B > 0 else 0) - (charge[t] if E_B > 0 else 0)
             for t in range(self.T)), 
            name="energy_balance")
        
        # Load limits: 0 ≤ ℓ_t ≤ ℓ_t^max
        model.addConstrs(
            (load[t] <= self.data['load_max'] for t in range(self.T)), 
            name="load_max")
        
        # PV limits: 0 ≤ p_t^PV ≤ p_t^PV,max
        model.addConstrs(
            (pv_used[t] <= self.data['pv_max_hourly'][t] for t in range(self.T)), 
            name="pv_max")
        
        # Flexibility constraints: ℓ_t - ℓ_t^ref = d_t^+ - d_t^-
        model.addConstrs(
            (load[t] - self.data['reference_load'][t] == dev_plus[t] - dev_minus[t]
             for t in range(self.T)), 
            name="deviation_balance")
        
        # Grid import/export limits (practical constraints)
        model.addConstrs(
            (import_grid[t] <= self.data['max_import'] for t in range(self.T)), 
            name="import_max")
        model.addConstrs(
            (export_grid[t] <= self.data['max_export'] for t in range(self.T)), 
            name="export_max")
        
        # Battery constraints (only if E_B > 0)
        if E_B > 0:
            # Battery dynamics: SoC_t+1 = SoC_t + η_ch*p_t^ch - p_t^dis/η_dis
            # Initial condition: SoC_1 = SoC_0 + η_ch*p_0^ch - p_0^dis/η_dis
            model.addConstr(
                soc[0] == E_B/2 + self.eta_ch * charge[0] - discharge[0] / self.eta_dis,  # type: ignore
                name="battery_dynamics_0")
            
            for t in range(1, self.T):
                model.addConstr(
                    soc[t] == soc[t-1] + self.eta_ch * charge[t] - discharge[t] / self.eta_dis,  # type: ignore
                    name=f"battery_dynamics_{t}")
            
            # Cyclic boundary condition: SoC_1 = SoC_24 (daily cycling)
            model.addConstr(
                soc[self.T-1] == E_B/2, name="cyclic_soc")  # type: ignore
        
        # === OBJECTIVE FUNCTION ===
        
        # Daily energy costs
        import_costs = gp.quicksum(
            (self.data['energy_prices'][t] + self.data['import_tariff']) * import_grid[t]
            for t in range(self.T))
        
        export_revenues = gp.quicksum(
            (self.data['energy_prices'][t] - self.data['export_tariff']) * export_grid[t]
            for t in range(self.T))
        
        daily_energy_cost = import_costs - export_revenues
        
        # Daily discomfort costs
        daily_discomfort_cost = gp.quicksum(
            self.data['discomfort_weight'] * (dev_plus[t] + dev_minus[t])
            for t in range(self.T))
        
        # Daily operational costs
        daily_operational_cost = daily_energy_cost + daily_discomfort_cost
        
        # Investment cost (upfront)
        investment_cost = self.investment_cost * E_B
        
        # 10-year total cost: J(E_B) = C_inv * E_B + N_d * C_day(E_B)
        total_10yr_cost = investment_cost + self.lifetime_days * daily_operational_cost
        
        # Add small tie-breaker to prevent simultaneous charge/discharge
        if E_B > 0:
            battery_tiebreaker = self.epsilon * gp.quicksum(
                charge[t] + discharge[t] for t in range(self.T))
            total_10yr_cost += battery_tiebreaker
        
        model.setObjective(total_10yr_cost, GRB.MINIMIZE)
        
        # === SOLVE ===
        
        model.optimize()
        
        if model.status != GRB.OPTIMAL:
            print(f"Warning: Non-optimal solution for E_B = {E_B} kWh (status: {model.status})")
            return None
        
        # === EXTRACT RESULTS ===
        
        # Extract solution values
        load_schedule = [load[t].x for t in range(self.T)]
        pv_schedule = [pv_used[t].x for t in range(self.T)]
        import_schedule = [import_grid[t].x for t in range(self.T)]
        export_schedule = [export_grid[t].x for t in range(self.T)]
        dev_plus_schedule = [dev_plus[t].x for t in range(self.T)]
        dev_minus_schedule = [dev_minus[t].x for t in range(self.T)]
        
        if E_B > 0:
            charge_schedule = [charge[t].x for t in range(self.T)]  # type: ignore
            discharge_schedule = [discharge[t].x for t in range(self.T)]  # type: ignore
            soc_schedule = [soc[t].x for t in range(self.T)]  # type: ignore
        else:
            charge_schedule = [0.0 for t in range(self.T)]
            discharge_schedule = [0.0 for t in range(self.T)]
            soc_schedule = [0.0 for t in range(self.T)]
        
        # Calculate key metrics
        total_imported = sum(import_schedule)
        total_exported = sum(export_schedule)
        net_import = total_imported - total_exported
        
        pv_available = sum(self.data['pv_max_hourly'])
        pv_used = sum(pv_schedule)
        pv_self_consumption_pct = (pv_used / pv_available * 100) if pv_available > 0 else 0
        
        # Daily costs
        daily_energy_cost_val = sum(
            (self.data['energy_prices'][t] + self.data['import_tariff']) * import_schedule[t] -
            (self.data['energy_prices'][t] - self.data['export_tariff']) * export_schedule[t]
            for t in range(self.T))
        
        daily_discomfort_cost_val = sum(
            self.data['discomfort_weight'] * (dev_plus_schedule[t] + dev_minus_schedule[t])
            for t in range(self.T))
        
        daily_operational_cost_val = daily_energy_cost_val + daily_discomfort_cost_val
        
        # Investment costs
        investment_cost_val = self.investment_cost * E_B
        
        # 10-year totals
        total_10yr_cost_val = model.objVal
        total_10yr_operational = self.lifetime_days * daily_operational_cost_val
        
        # Battery metrics
        if E_B > 0:
            total_charged = sum(charge_schedule)
            total_discharged = sum(discharge_schedule)
            battery_throughput = (total_charged + total_discharged) / 2  # Average of charge/discharge
            full_cycles_per_day = battery_throughput / E_B if E_B > 0 else 0
            
            # SoC bounds analysis
            max_soc = max(soc_schedule) if soc_schedule else 0
            min_soc = min(soc_schedule) if soc_schedule else 0
            hours_at_max = sum(1 for s in soc_schedule if s >= 0.95 * E_B)
            hours_at_min = sum(1 for s in soc_schedule if s <= 0.05 * E_B)
            
            # Peak power flows
            peak_charge = max(charge_schedule) if charge_schedule else 0
            peak_discharge = max(discharge_schedule) if discharge_schedule else 0
        else:
            total_charged = total_discharged = battery_throughput = full_cycles_per_day = 0
            max_soc = min_soc = hours_at_max = hours_at_min = 0
            peak_charge = peak_discharge = 0
        
        # Peak grid flows
        peak_import = max(import_schedule) if import_schedule else 0
        peak_export = max(export_schedule) if export_schedule else 0
        
        return {
            # Battery configuration
            'battery_capacity': E_B,
            'charge_power_limit': P_ch_max,
            'discharge_power_limit': P_dis_max,
            
            # Costs and economics
            'total_10yr_cost': total_10yr_cost_val,
            'investment_cost': investment_cost_val,
            'daily_operational_cost': daily_operational_cost_val,
            'daily_energy_cost': daily_energy_cost_val,
            'daily_discomfort_cost': daily_discomfort_cost_val,
            'total_10yr_operational': total_10yr_operational,
            
            # Energy flows
            'total_imported': total_imported,
            'total_exported': total_exported,
            'net_import': net_import,
            'pv_used': pv_used,
            'pv_available': pv_available,
            'pv_self_consumption_pct': pv_self_consumption_pct,
            
            # Battery operation
            'total_charged': total_charged,
            'total_discharged': total_discharged,
            'battery_throughput': battery_throughput,
            'full_cycles_per_day': full_cycles_per_day,
            'max_soc': max_soc,
            'min_soc': min_soc,
            'hours_at_max_soc': hours_at_max,
            'hours_at_min_soc': hours_at_min,
            'peak_charge_power': peak_charge,
            'peak_discharge_power': peak_discharge,
            
            # Grid interaction
            'peak_import_power': peak_import,
            'peak_export_power': peak_export,
            
            # Schedules (for detailed analysis)
            'load_schedule': load_schedule,
            'pv_schedule': pv_schedule,
            'import_schedule': import_schedule,
            'export_schedule': export_schedule,
            'charge_schedule': charge_schedule,
            'discharge_schedule': discharge_schedule,
            'soc_schedule': soc_schedule,
            'dev_plus_schedule': dev_plus_schedule,
            'dev_minus_schedule': dev_minus_schedule,
        }
    
    def solve_battery_sweep(self):
        """
        Solve for all battery sizes in the sweep.
        
        Returns:
            dict: Results for all battery sizes
        """
        
        print(f"Solving battery investment sweep for {len(self.battery_sizes)} sizes...")
        print(f"Battery sizes: {self.battery_sizes} kWh")
        print(f"Investment cost: {self.investment_cost} DKK/kWh")
        print("-" * 50)
        
        results = {}
        
        for E_B in self.battery_sizes:
            print(f"Solving for E_B = {E_B} kWh...")
            
            result = self.solve_for_battery_size(E_B)
            
            if result is not None:
                results[E_B] = result
                
                # Quick summary
                print(f"  10-year cost: {result['total_10yr_cost']:.0f} DKK")
                print(f"  Daily operational: {result['daily_operational_cost']:.2f} DKK/day")
                if E_B > 0:
                    print(f"  Investment: {result['investment_cost']:.0f} DKK")
                    print(f"  PV self-consumption: {result['pv_self_consumption_pct']:.1f}%")
            else:
                print(f"  Failed to solve for E_B = {E_B} kWh")
        
        print("-" * 50)
        print(f"Completed sweep. Solved {len(results)}/{len(self.battery_sizes)} sizes.")
        
        return results
    
    def calculate_investment_metrics(self, results: dict):
        """
        Calculate investment analysis metrics from sweep results.
        
        Args:
            results: Dictionary of results from solve_battery_sweep()
            
        Returns:
            dict: Investment analysis metrics
        """
        
        if not results or 0 not in results:
            print("Error: No baseline (E_B=0) results available")
            return {}
        
        baseline = results[0]  # No battery case
        baseline_daily_cost = baseline['daily_operational_cost']
        
        analysis = {}
        
        for E_B, result in results.items():
            if result is None:
                continue
                
            # Daily savings vs no battery
            daily_savings = baseline_daily_cost - result['daily_operational_cost']
            annual_savings = daily_savings * 365
            
            # Simple payback period (years)
            if E_B > 0 and daily_savings > 0:
                payback_years = result['investment_cost'] / annual_savings
                profitable = payback_years <= 10
            else:
                payback_years = float('inf') if E_B > 0 else 0
                profitable = False if E_B > 0 else True  # No investment always "profitable"
            
            # Net present value (simple, no discounting as per problem statement)
            npv_10yr = annual_savings * 10 - result['investment_cost']
            
            analysis[E_B] = {
                'battery_size': E_B,
                'total_10yr_cost': result['total_10yr_cost'],
                'daily_operational_cost': result['daily_operational_cost'],
                'daily_savings': daily_savings,
                'annual_savings': annual_savings,
                'investment_cost': result['investment_cost'],
                'payback_years': payback_years,
                'profitable_10yr': profitable,
                'npv_10yr': npv_10yr,
                'pv_self_consumption_pct': result['pv_self_consumption_pct'],
                'full_cycles_per_day': result['full_cycles_per_day'],
                'net_import': result['net_import'],
            }
        
        # Find optimal battery size (minimum 10-year cost)
        min_cost = min(r['total_10yr_cost'] for r in analysis.values())
        optimal_sizes = [E_B for E_B, r in analysis.items() if r['total_10yr_cost'] == min_cost]
        optimal_E_B = optimal_sizes[0] if optimal_sizes else 0
        
        return {
            'by_size': analysis,
            'optimal_E_B': optimal_E_B,
            'optimal_cost': min_cost,
            'baseline_cost': baseline['total_10yr_cost'],
            'max_savings': baseline['total_10yr_cost'] - min_cost,
        }
    
    def print_investment_summary(self, analysis: dict):
        """Print summary of investment analysis."""
        
        if not analysis or 'by_size' not in analysis:
            print("No analysis results to display")
            return
        
        print("\n" + "="*70)
        print("BATTERY INVESTMENT ANALYSIS SUMMARY")
        print("="*70)
        
        print(f"\n🔋 OPTIMAL INVESTMENT:")
        print(f"   Optimal Battery Size: {analysis['optimal_E_B']} kWh")
        print(f"   Optimal 10-Year Cost: {analysis['optimal_cost']:.0f} DKK")
        print(f"   Baseline Cost (No Battery): {analysis['baseline_cost']:.0f} DKK")
        print(f"   Maximum 10-Year Savings: {analysis['max_savings']:.0f} DKK")
        
        print(f"\n📊 SIZE COMPARISON:")
        print(f"{'Size [kWh]':<12}{'10yr Cost':<12}{'Daily Save':<12}{'Payback':<12}{'PV Self%':<10}{'Profit?'}")
        print("-" * 70)
        
        for E_B in sorted(analysis['by_size'].keys()):
            data = analysis['by_size'][E_B]
            payback_str = f"{data['payback_years']:.1f}y" if data['payback_years'] < 50 else "∞"
            profit_str = "Yes" if data['profitable_10yr'] else "No"
            
            print(f"{E_B:<12.0f}{data['total_10yr_cost']:<12.0f}"
                  f"{data['daily_savings']:<12.2f}{payback_str:<12}"
                  f"{data['pv_self_consumption_pct']:<10.1f}{profit_str}")
        
        print("="*70)