"""
Question 1c Part V - Scenario Analysis: Flexibility and Cost Structure Sensitivity
Report Quality Analysis with 5 Scenarios

Implements comprehensive scenario analysis for Q1c with:
- BASE, FLEX, RIGID scenarios (varying w with baseline tariffs)
- HIGH-IMPORT, LOW-EXPORT scenarios (varying tariffs with baseline w)
- Complete KPI calculation and comparison
- Time series export (primal and dual variables)    plt.tight_layout()
    plt.savefig('Q1c_v_Plot2_Battery_SoC.png', dpi=350, bbox_inches='tigh    plt.tight_layout()
    plt.savefig('Q1c_v_Plot3_Shadow_Prices.png', dpi=350, bbox_inches='tight')
    plt.show()
    plt.show()4 professional visualizations for report
"""

import sys
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Configure matplotlib for interactive display and report-quality figures
plt.ioff()  # Turn off interactive mode to make plots block properly
plt.rcParams.update({
    'font.size': 16,           # Base font size
    'axes.titlesize': 24,      # Title font size
    'axes.labelsize': 20,      # Axis label font size
    'xtick.labelsize': 18,     # X tick label font size
    'ytick.labelsize': 18,     # Y tick label font size
    'legend.fontsize': 16,     # Legend font size
    'figure.titlesize': 26,    # Figure title font size
    'lines.linewidth': 4,      # Line width
    'lines.markersize': 10,    # Marker size
    'axes.linewidth': 2,       # Axis line width
    'grid.linewidth': 1.5      # Grid line width
})

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data_ops.data_loader import DataLoader
from data_ops.data_processor import DataProcessor
from opt_model.opt_model_Q1c import ConsumerFlexibilityModelQ1c
from opt_model.opt_model_Q1b import ConsumerFlexibilityModelQ1b  # For no-battery baseline


def calculate_storage_arbitrage_value(scenario_data, scenario_config):
    """Calculate storage arbitrage value by comparing with and without battery."""
    
    # Solve with battery (Q1c model)
    model_with_battery = ConsumerFlexibilityModelQ1c(scenario_data)
    results_with_battery = model_with_battery.solve()
    
    if not results_with_battery:
        return 0.0
    
    cost_with_battery = results_with_battery['optimal_cost']
    
    # Solve without battery (Q1b model - no battery variables)
    # Create scenario data without battery appliance
    no_battery_data = scenario_data.copy()
    no_battery_data['appliances'] = {k: v for k, v in scenario_data['appliances'].items() 
                                     if v.get('type') != 'storage'}
    
    model_without_battery = ConsumerFlexibilityModelQ1b(no_battery_data)
    results_without_battery = model_without_battery.solve()
    
    if not results_without_battery:
        return 0.0
    
    cost_without_battery = results_without_battery['optimal_cost']
    
    # Arbitrage value = cost without battery - cost with battery
    arbitrage_value = cost_without_battery - cost_with_battery
    
    return arbitrage_value


def solve_q1c_v_scenarios(output_dir):
    """
    Solve Q1c part v with 5 different scenarios analyzing flexibility and cost structure.
    
    Returns:
        dict: Dictionary with results for all scenarios
    """
    
    print("QUESTION 1c PART V - SCENARIO ANALYSIS WITH DETAILED METRICS")
    print("=" * 65)
    
    try:
        # Load and process base data
        project_root = Path(__file__).parent.parent.parent
        loader = DataLoader(base_path=str(project_root / "data"))
        base_raw_data = loader.load_data("question_1c")  # Use Q1c data for battery parameters
        processor = DataProcessor()
        
        # Define 5 scenarios
        scenarios = {
            'BASE': {
                'name': 'BASE (Reference)',
                'w': 2.5,
                'tariff_import_mult': 1.0,
                'tariff_export_mult': 1.0,
                'description': 'Baseline case with w=2.5'
            },
            'FLEX': {
                'name': 'FLEX (More Flexible Consumer)',
                'w': 0.5,
                'tariff_import_mult': 1.0,
                'tariff_export_mult': 1.0,
                'description': 'Low discomfort weight, more flexibility'
            },
            'RIGID': {
                'name': 'RIGID (Comfort-Focused)',
                'w': 5.0,
                'tariff_import_mult': 1.0,
                'tariff_export_mult': 1.0,
                'description': 'High discomfort weight, comfort priority'
            },
            'HIGH-IMPORT': {
                'name': 'HIGH-IMPORT (Cost Structure)',
                'w': 2.5,
                'tariff_import_mult': 1.30,
                'tariff_export_mult': 1.0,
                'description': 'Higher import tariffs (+30%)'
            },
            'LOW-EXPORT': {
                'name': 'LOW-EXPORT (Cost Structure)',
                'w': 2.5,
                'tariff_import_mult': 1.0,
                'tariff_export_mult': 0.50,
                'description': 'Lower export tariffs (-50%)'
            }
        }
        
        # Store results for all scenarios
        all_results = {}
        all_data = {}
        detailed_metrics = {}
        kpi_summary = []
        
        print(f"\nSolving {len(scenarios)} scenarios with detailed analysis...")
        print("-" * 65)
        
        for scenario_key, scenario_config in scenarios.items():
            print(f"\nProcessing {scenario_key}...")
            
            # Process data with scenario-specific parameters using unified processor
            scenario_data = processor.process_for_optimization_unified(
                copy.deepcopy(base_raw_data), 
                question_type='q1c',
                discomfort_weight=scenario_config['w']
            )
            
            # Modify tariffs if needed
            if scenario_config['tariff_import_mult'] != 1.0:
                scenario_data['energy_prices'] = [
                    p * scenario_config['tariff_import_mult'] 
                    for p in scenario_data['energy_prices']
                ]
            
            if scenario_config['tariff_export_mult'] != 1.0:
                scenario_data['export_tariff'] = scenario_data['export_tariff'] * scenario_config['tariff_export_mult']
            
            # Solve optimization
            model = ConsumerFlexibilityModelQ1c(scenario_data)
            results = model.solve()
            
            if results:
                # Store results and data
                all_results[scenario_key] = results
                all_data[scenario_key] = scenario_data
                
                # Calculate detailed metrics
                metrics = calculate_detailed_metrics(results, scenario_data, scenario_config)
                
                # Calculate storage arbitrage value
                print(f"  Calculating storage arbitrage value...")
                arbitrage_value = calculate_storage_arbitrage_value(scenario_data, scenario_config)
                metrics['storage_arbitrage_value'] = arbitrage_value
                
                detailed_metrics[scenario_key] = metrics
                
                # Print detailed summary
                print_detailed_scenario_summary(scenario_key, results, scenario_data, scenario_config, metrics)
                
                # Calculate comprehensive KPIs (for compatibility)
                kpis = calculate_scenario_kpis(results, scenario_data, scenario_config)
                kpis['scenario'] = scenario_key
                kpis['scenario_name'] = scenario_config['name']
                kpi_summary.append(kpis)
                
            else:
                print(f"Scenario {scenario_key}: FAILED to solve")
        
        if kpi_summary:
            # Create KPI summary table
            kpi_df = pd.DataFrame(kpi_summary)
            
            # Print summary table with all key metrics
            print_comprehensive_summary_table(detailed_metrics, scenarios)
            
            # Generate visualizations
            create_scenario_visualizations(all_results, all_data, scenarios, output_dir)
            
            return {
                'results': all_results,
                'data': all_data,
                'kpis': kpi_df,
                'scenarios': scenarios,
                'detailed_metrics': detailed_metrics
            }
        else:
            print("ERROR: No scenarios solved successfully")
            return None
            
    except Exception as e:
        print(f"ERROR in Q1c scenario analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


def calculate_detailed_metrics(results, data, scenario_config):
    """Calculate detailed metrics including battery performance and operational statistics."""
    
    # Basic totals
    total_import = sum(results['import_schedule'])
    total_export = sum(results['export_schedule'])
    total_pv_available = sum(data['pv_max_hourly'])
    total_pv_generated = sum(results['pv_schedule'])
    pv_self_consumed = total_pv_generated - total_export
    
    # Cost breakdown components
    import_energy_cost = sum([(data['energy_prices'][t] + data['import_tariff']) * results['import_schedule'][t] 
                              for t in range(len(results['import_schedule']))])
    export_revenue = sum([(data['energy_prices'][t] - data['export_tariff']) * results['export_schedule'][t] 
                          for t in range(len(results['export_schedule']))])
    
    # Grid tariffs paid (separate import and export portions)
    import_tariff_paid = sum([data['import_tariff'] * results['import_schedule'][t] 
                              for t in range(len(results['import_schedule']))])
    export_tariff_paid = sum([data['export_tariff'] * results['export_schedule'][t] 
                              for t in range(len(results['export_schedule']))])
    total_tariff_paid = import_tariff_paid + export_tariff_paid
    
    # Battery performance metrics
    battery_throughput = results['total_charged'] + results['total_discharged']
    battery_capacity = data['appliances']['BESS_01']['storage_capacity_kWh']
    full_cycle_equivalents = battery_throughput / (2 * battery_capacity) if battery_capacity > 0 else 0
    
    # Round-trip losses estimate: energy put in - energy taken out
    charge_energy = sum(results['charge_schedule'])
    discharge_energy = sum(results['discharge_schedule'])
    round_trip_losses = charge_energy - discharge_energy
    
    # Hours at SoC bounds
    soc_schedule = results['soc_schedule']
    soc_min_hours = sum(1 for soc in soc_schedule if abs(soc - 0) < 0.01)  # Near minimum (0)
    soc_max_hours = sum(1 for soc in soc_schedule if abs(soc - battery_capacity) < 0.01)  # Near maximum
    
    # Operational switches
    hours_importing = sum(1 for imp in results['import_schedule'] if imp > 0.01)
    hours_exporting = sum(1 for exp in results['export_schedule'] if exp > 0.01)
    hours_curtailing = sum(1 for t in range(len(results['pv_schedule'])) 
                           if data['pv_max_hourly'][t] - results['pv_schedule'][t] > 0.01)
    
    # Peak operations
    peak_import = max(results['import_schedule']) if results['import_schedule'] else 0
    peak_export = max(results['export_schedule']) if results['export_schedule'] else 0
    peak_charge = max(results['charge_schedule']) if results['charge_schedule'] else 0
    peak_discharge = max(results['discharge_schedule']) if results['discharge_schedule'] else 0
    
    # Lambda (shadow price) statistics
    lambda_vals = []
    if 'dual_power_balance' in results and results['dual_power_balance']:
        lambda_vals = [x for x in results['dual_power_balance'] if x is not None and abs(x) > 1e-6]
    
    lambda_avg = sum(lambda_vals) / len(lambda_vals) if lambda_vals else 0
    lambda_max = max(lambda_vals) if lambda_vals else 0
    
    # Binding constraint hours (simplified)
    binding_soc_upper = sum(1 for soc in soc_schedule if abs(soc - battery_capacity) < 0.01)
    binding_soc_lower = sum(1 for soc in soc_schedule if abs(soc) < 0.01)
    
    return {
        # Cost breakdown
        'import_energy_cost': import_energy_cost,
        'export_revenue': export_revenue,
        'import_tariff_paid': import_tariff_paid,
        'export_tariff_paid': export_tariff_paid,
        'total_tariff_paid': total_tariff_paid,
        'discomfort_cost': scenario_config['w'] * (results['total_dev_plus'] + results['total_dev_minus']),
        'total_cost': import_energy_cost - export_revenue + scenario_config['w'] * (results['total_dev_plus'] + results['total_dev_minus']),
        
        # Battery performance
        'battery_throughput': battery_throughput,
        'full_cycle_equivalents': full_cycle_equivalents,
        'round_trip_losses': round_trip_losses,
        'soc_min_hours': soc_min_hours,
        'soc_max_hours': soc_max_hours,
        
        # Operational metrics
        'hours_importing': hours_importing,
        'hours_exporting': hours_exporting,
        'hours_curtailing': hours_curtailing,
        'peak_import': peak_import,
        'peak_export': peak_export,
        'peak_charge': peak_charge,
        'peak_discharge': peak_discharge,
        
        # Shadow prices
        'lambda_avg': lambda_avg,
        'lambda_max': lambda_max,
        'binding_soc_upper': binding_soc_upper,
        'binding_soc_lower': binding_soc_lower,
        
        # Basic metrics (for compatibility)
        'total_import': total_import,
        'total_export': total_export,
        'pv_self_consumed': pv_self_consumed,
        'pv_available': total_pv_available,
        'pv_generated': total_pv_generated
    }


def calculate_scenario_kpis(results, data, scenario_config):
    """Calculate comprehensive KPIs for a scenario (legacy function for compatibility)."""
    
    # Basic totals
    total_import = sum(results['import_schedule'])
    total_export = sum(results['export_schedule'])
    total_pv_available = sum(data['pv_max_hourly'])  # Total PV available
    total_pv_generated = sum(results['pv_schedule'])  # Total PV actually generated/used by system
    
    # PV self-consumption is the PV used directly by household (not exported)
    pv_self_consumed = total_pv_generated - total_export  # PV used for self-consumption
    
    # Calculate costs correctly: Energy cost = Σ(πt + τt)ut - Σ(πt - τt)xt + Discomfort cost
    # Import cost: (πt + τt) * ut
    import_cost = sum([(data['energy_prices'][t] + data['import_tariff']) * results['import_schedule'][t] 
                       for t in range(len(results['import_schedule']))])
    
    # Export revenue: (πt - τt) * xt
    export_revenue = sum([(data['energy_prices'][t] - data['export_tariff']) * results['export_schedule'][t] 
                          for t in range(len(results['export_schedule']))])
    
    discomfort_cost = scenario_config['w'] * (results['total_dev_plus'] + results['total_dev_minus'])
    net_energy_cost = import_cost - export_revenue
    
    # Calculate total cost correctly: Import Cost - Export Revenue + Discomfort Cost
    calculated_total_cost = import_cost - export_revenue + discomfort_cost
    
    kpis = {
        # Core metrics
        'total_cost_dkk': calculated_total_cost,
        'import_kwh': total_import,
        'export_kwh': total_export,
        'pv_self_consumed_kwh': pv_self_consumed,  # PV used by household directly
        'pv_available_kwh': total_pv_available,
        'pv_generated_kwh': total_pv_generated,  # Total PV generated by system
        'pv_curtailed_kwh': total_pv_available - total_pv_generated,
        'pv_utilization_pct': (total_pv_generated / total_pv_available) * 100 if total_pv_available > 0 else 0,
        'pv_self_consumption_pct': (pv_self_consumed / total_pv_available) * 100 if total_pv_available > 0 else 0,
        'discomfort_cost_dkk': discomfort_cost,
        'battery_throughput_kwh': results['total_charged'] + results['total_discharged'],
        'soc_range_kwh': results['max_soc'] - results['min_soc'],
        'net_profit_dkk': -calculated_total_cost,  # Negative cost = profit
        
        # Additional metrics
        'import_cost_dkk': import_cost,
        'export_revenue_dkk': export_revenue,
        'export_revenue_simple_dkk': total_export * data['export_tariff'],  # Simple calculation for comparison
        'net_energy_cost_dkk': net_energy_cost,
        'total_load_kwh': sum(results['load_schedule']),
        'total_flexibility_kwh': results['total_dev_plus'] + results['total_dev_minus'],
        'max_soc_kwh': results['max_soc'],
        'min_soc_kwh': results['min_soc'],
        'battery_efficiency_pct': results['battery_efficiency'] * 100,
        
        # Scenario parameters
        'w_parameter': scenario_config['w'],
        'tariff_import_mult': scenario_config['tariff_import_mult'],
        'tariff_export_mult': scenario_config['tariff_export_mult']
    }
    
    return kpis


def print_variable_tables(results, data, scenario_key):
    """Print primal and dual variables as professional tables."""
    
    hours = list(range(1, 25))
    
    print(f"\nPRIMAL VARIABLES - {scenario_key}")
    print("=" * 120)
    
    # Print primal variables table with better formatting
    print(f"{'Hour':<4} {'l_t':<6} {'l_ref':<6} {'d+':<6} {'d-':<6} {'u_t':<6} {'x_t':<6} {'c_t':<6} {'r_t':<6} {'s_t':<6} {'p_pv':<6}")
    print(f"{'':4} {'(kWh)':<6} {'(kWh)':<6} {'(kWh)':<6} {'(kWh)':<6} {'(kWh)':<6} {'(kWh)':<6} {'(kWh)':<6} {'(kWh)':<6} {'(kWh)':<6} {'(kWh)':<6}")
    print("-" * 120)
    
    for i in range(24):
        hour = hours[i]
        l_t = results['load_schedule'][i]
        l_ref = data['reference_load'][i]
        d_plus = results['dev_plus_schedule'][i]
        d_minus = results['dev_minus_schedule'][i]
        u_t = results['import_schedule'][i]
        x_t = results['export_schedule'][i]
        c_t = results['charge_schedule'][i]
        r_t = results['discharge_schedule'][i]
        s_t = results['soc_schedule'][i]
        p_pv = results['pv_schedule'][i]
        
        print(f"{hour:<4} {l_t:<6.2f} {l_ref:<6.2f} {d_plus:<6.2f} {d_minus:<6.2f} {u_t:<6.2f} {x_t:<6.2f} {c_t:<6.2f} {r_t:<6.2f} {s_t:<6.2f} {p_pv:<6.2f}")
    
    print("=" * 120)
    
    # Print dual variables table if available
    if 'dual_power_balance' in results:
        print(f"\nDUAL VARIABLES (SHADOW PRICES) - {scenario_key}")
        print("=" * 80)
        print(f"{'Hour':<4} {'lambda_t':<10} {'mu_soc_up':<10} {'mu_soc_lo':<10} {'nu_term':<10}")
        print(f"{'':4} {'(DKK/kWh)':<10} {'(DKK/kWh)':<10} {'(DKK/kWh)':<10} {'(DKK/kWh)':<10}")
        print("-" * 80)
        
        for i in range(24):
            hour = hours[i]
            lambda_t = results['dual_power_balance'][i] if results['dual_power_balance'][i] is not None else 0.0
            mu_up = results.get('dual_soc_upper', [0]*24)[i]
            mu_lo = results.get('dual_soc_lower', [0]*24)[i]
            nu_term = results.get('dual_terminal', 0.0) if i == 23 else 0.0
            
            print(f"{hour:<4} {lambda_t:<10.4f} {mu_up:<10.4f} {mu_lo:<10.4f} {nu_term:<10.4f}")
        
        print("=" * 80)
    else:
        print(f"\nDual variables not available for {scenario_key}")
    
    print(f"\nVariable definitions printed for {scenario_key}")


def create_scenario_visualizations(all_results, all_data, scenarios, output_dir):
    """Create exactly the 5 requested visualizations."""
    
    print(f"\nGenerating plots...")
    
    # Plot 1: Cost breakdown per scenario (stacked bars) - matching the image
    create_plot1_cost_breakdown(all_results, all_data, scenarios, output_dir)
    
    # Plot 2: Battery SoC profiles (24 h) 
    create_plot2_battery_soc_profiles(all_results, scenarios, output_dir)
    
    # Plot 3: Shadow price λₜ (dual variable)
    create_plot3_shadow_price_lambda(all_results, all_data, scenarios, output_dir)
    
    # Plot 4: Hourly energy flows (BASE vs FLEX)
    create_plot4_hourly_energy_flows_base_flex(all_results, all_data, scenarios, output_dir)
    
    # Plot 5: Hourly energy flows (HIGH-IMPORT vs LOW-EXPORT)
    create_plot5_hourly_energy_flows_tariffs(all_results, all_data, scenarios, output_dir)
    
    print("Plots completed.")


def create_plot1_cost_breakdown(all_results, all_data, scenarios, output_dir):
    """Plot 1: Daily Cost Breakdown Across Scenarios - matching the image style"""
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    scenario_names = []
    import_costs = []
    export_revenues = []
    discomfort_costs = []
    total_costs = []
    
    for scenario_key, scenario_config in scenarios.items():
        if scenario_key in all_results:
            results = all_results[scenario_key]
            data = all_data[scenario_key]
            
            scenario_names.append(scenario_key)
            
            # Calculate cost components correctly
            import_cost = sum([(data['energy_prices'][t] + data['import_tariff']) * results['import_schedule'][t] 
                               for t in range(len(results['import_schedule']))])
            export_revenue = sum([(data['energy_prices'][t] - data['export_tariff']) * results['export_schedule'][t] 
                                  for t in range(len(results['export_schedule']))])
            discomfort_cost = scenario_config['w'] * (results['total_dev_plus'] + results['total_dev_minus'])
            
            # Calculate total cost correctly: Import Cost - Export Revenue + Discomfort Cost
            calculated_total_cost = import_cost - export_revenue + discomfort_cost
            
            import_costs.append(import_cost)
            export_revenues.append(export_revenue)
            discomfort_costs.append(discomfort_cost)
            total_costs.append(calculated_total_cost)
    
    # Create wider spacing between scenarios and narrower bars
    x = np.arange(len(scenario_names)) * 2.5  # More space between scenarios
    width = 0.25  # Narrower bars
    
    # Create component bars side by side with better spacing
    bars1 = ax.bar(x - width*1.5, total_costs, width, label='Total Cost', color='lightcoral', alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x - width*0.5, import_costs, width, label='Import Cost', color='red', alpha=0.8, edgecolor='black')
    bars3 = ax.bar(x + width*0.5, export_revenues, width, label='Export Revenue', color='green', alpha=0.8, edgecolor='black')
    bars4 = ax.bar(x + width*1.5, discomfort_costs, width, label='Discomfort Cost', color='lightblue', alpha=0.8, edgecolor='black')
    
    # Add horizontal line at zero
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.8, linewidth=1)
    
    #ax.set_xlabel('Scenario', fontsize=18, fontweight='bold')
    ax.set_ylabel('Cost/Revenue (DKK)', fontsize=18, fontweight='bold')
    ax.set_title('DETAILED COST COMPONENT COMPARISON', fontsize=20, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(scenario_names, fontsize=14, fontweight='bold', rotation=45)
    ax.tick_params(axis='y', labelsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=18, loc='upper left', framealpha=0.95, edgecolor='black')
    
    # Set y-axis limits to accommodate all cost scenarios (increased upper limit)
    ax.set_ylim(-15, 25)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'Q1c_v_Plot1_Cost_Breakdown.png', dpi=350, bbox_inches='tight')
    plt.show()


def create_plot2_battery_soc_profiles(all_results, scenarios, output_dir):
    """Plot 2: Battery State of Charge Under Different Flexibility Levels (24 h)"""
    
    fig, ax = plt.subplots(figsize=(20, 12))
    
    hours = np.arange(1, 25)
    colors = {'BASE': 'blue', 'FLEX': 'green', 'RIGID': 'red'}
    markers = {'BASE': 'o', 'FLEX': 's', 'RIGID': '^'}
    
    # Plot clean SoC profiles - no fill areas, just clear lines
    # Plot RIGID first (so BASE can be on top)
    for scenario_key in ['FLEX', 'RIGID']:
        if scenario_key in all_results:
            results = all_results[scenario_key]
            soc_profile = results['soc_schedule']
            w_value = scenarios[scenario_key]['w']
            
            ax.step(hours, soc_profile, where='mid', color=colors[scenario_key], 
                   label=f'{scenario_key} (w={w_value})', alpha=0.9, 
                   marker=markers[scenario_key], markersize=8, linewidth=4)
    
    # Plot BASE last with dashed line to make it visible on top
    if 'BASE' in all_results:
        results = all_results['BASE']
        soc_profile = results['soc_schedule']
        w_value = scenarios['BASE']['w']
        
        ax.step(hours, soc_profile, where='mid', color=colors['BASE'], 
               linestyle='--', label=f'BASE (w={w_value}) - Reference', alpha=1.0, 
               marker=markers['BASE'], markersize=10, linewidth=5, markeredgewidth=2, markeredgecolor='white')
    
    # Add reference lines - simplified
    ax.axhline(y=6.0, color='gray', linestyle='--', alpha=0.6, linewidth=2,
               label='Battery Capacity (6 kWh)')
    ax.axhline(y=3.0, color='orange', linestyle='--', alpha=0.6, linewidth=2,
               label='Target SoC (3 kWh)')
    ax.axhline(y=0.0, color='black', linestyle=':', alpha=0.4, linewidth=1,
               label='Empty Battery')
    
    ax.set_xlabel('Hour of Day', fontsize=22, fontweight='bold')
    ax.set_ylabel('SoC (kWh)', fontsize=22, fontweight='bold')
    ax.set_title('Battery State of Charge Under Different Flexibility Levels', fontsize=26, fontweight='bold', pad=30)
    ax.set_xlim(0.5, 24.5)
    ax.set_xticks(range(1, 25, 2))
    ax.set_ylim(0, 6.5)
    ax.tick_params(axis='both', labelsize=18)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=18, loc='upper left', framealpha=0.95, edgecolor='black')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'Q1c_v_Plot2_Battery_SoC_Profiles.png', dpi=350, bbox_inches='tight')
    plt.show()


def create_plot3_shadow_price_lambda(all_results, all_data, scenarios, output_dir):
    """Plot 3: Shadow Price λₜ (dual variable) - Single plot with all scenarios"""
    
    fig, ax = plt.subplots(figsize=(20, 12))
    
    hours = np.arange(1, 25)
    colors = {'BASE': 'blue', 'FLEX': 'green', 'RIGID': 'red'}
    markers = {'BASE': 'o', 'FLEX': 's', 'RIGID': '^'}
    
    # Plot shadow prices for all 5 scenarios
    colors.update({'HIGH-IMPORT': 'orange', 'LOW-EXPORT': 'purple'})
    markers.update({'HIGH-IMPORT': 'D', 'LOW-EXPORT': 'v'})
    
    shadow_price_plotted = False
    
    # Plot other scenarios first (so BASE can be on top)
    for scenario_key in ['FLEX', 'RIGID', 'HIGH-IMPORT', 'LOW-EXPORT']:
        if scenario_key in all_results and 'dual_energy' in all_results[scenario_key]:
            shadow_prices = all_results[scenario_key]['dual_energy']  # Use dual_energy as shadow price
            w_value = scenarios[scenario_key]['w']
            tariff_info = ""
            
            # Add tariff information for tariff scenarios
            if scenario_key == 'HIGH-IMPORT':
                tariff_info = f", τ_imp=1.3×"
            elif scenario_key == 'LOW-EXPORT':
                tariff_info = f", τ_exp=0.5×"
            
            ax.step(hours, shadow_prices, where='mid', color=colors[scenario_key], 
                   label=f'{scenario_key} λₜ (w={w_value}{tariff_info})', 
                   alpha=0.9, linewidth=4, marker=markers[scenario_key], markersize=8)
            shadow_price_plotted = True
    
    # Plot BASE last as dotted line on top
    if 'BASE' in all_results and 'dual_energy' in all_results['BASE']:
        shadow_prices = all_results['BASE']['dual_energy']
        w_value = scenarios['BASE']['w']
        
        ax.step(hours, shadow_prices, where='mid', color=colors['BASE'], 
               linestyle=':', label=f'BASE λₜ (w={w_value}) - Reference', 
               alpha=1.0, linewidth=6, marker=markers['BASE'], markersize=10, 
               markeredgewidth=2, markeredgecolor='white')
        shadow_price_plotted = True
    
    # If no shadow prices available, use a backup approach
    if not shadow_price_plotted:
        print("⚠️  No shadow prices found, using energy prices as proxy")
        
        # Plot other scenarios first
        for scenario_key in ['FLEX', 'RIGID', 'HIGH-IMPORT', 'LOW-EXPORT']:
            if scenario_key in all_data:
                prices = all_data[scenario_key]['energy_prices']
                w_value = scenarios[scenario_key]['w']
                tariff_info = ""
                
                # Add tariff information for tariff scenarios
                if scenario_key == 'HIGH-IMPORT':
                    tariff_info = f", τ_imp=1.3×"
                elif scenario_key == 'LOW-EXPORT':
                    tariff_info = f", τ_exp=0.5×"
                
                ax.step(hours, prices, where='mid', color=colors[scenario_key], 
                       label=f'{scenario_key} Energy Price (w={w_value}{tariff_info})', 
                       alpha=0.9, linewidth=4, marker=markers[scenario_key], markersize=8)
        
        # Plot BASE last as dotted line on top
        if 'BASE' in all_data:
            prices = all_data['BASE']['energy_prices']
            w_value = scenarios['BASE']['w']
            
            ax.step(hours, prices, where='mid', color=colors['BASE'], 
                   linestyle=':', label=f'BASE Energy Price (w={w_value}) - Reference', 
                   alpha=1.0, linewidth=6, marker=markers['BASE'], markersize=10,
                   markeredgewidth=2, markeredgecolor='white')
    
    # Overlay market price as dashed reference line
    if 'BASE' in all_data:
        market_prices = all_data['BASE']['energy_prices']
        ax.step(hours, market_prices, where='mid', color='black', 
               linestyle='--', alpha=0.8, linewidth=4, label='Market Price πₜ')
    
    ax.set_xlabel('Hour of Day', fontsize=22, fontweight='bold')
    ax.set_ylabel('Shadow Price λₜ (DKK/kWh)', fontsize=22, fontweight='bold')
    ax.set_title('Marginal Value of Energy (λₜ) – Effect of Flexibility & Tariff Structure', fontsize=24, fontweight='bold', pad=30)
    ax.set_xlim(0.5, 24.5)
    ax.set_xticks(range(1, 25, 2))
    ax.tick_params(axis='both', labelsize=18)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=18, loc='upper left', framealpha=0.95, edgecolor='black', ncol=2)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'Q1c_v_Plot3_Shadow_Price_Lambda.png', dpi=350, bbox_inches='tight')
    plt.show()


def create_plot4_hourly_energy_flows_base_flex(all_results, all_data, scenarios, output_dir):
    """Plot 4: Hourly Energy Flows – Base vs Flexible Consumer"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 18))
    
    hours = np.arange(1, 25)
    
    # Top subplot: BASE scenario
    if 'BASE' in all_results:
        results_base = all_results['BASE']
        
        ax1.step(hours, results_base['pv_schedule'], where='mid', color='gold', 
                label='PV Generation', alpha=0.9, linewidth=4, marker='o', markersize=8)
        ax1.step(hours, results_base['load_schedule'], where='mid', color='blue', 
                label='Load Consumption', alpha=0.9, linewidth=4, marker='s', markersize=8)
        ax1.step(hours, results_base['import_schedule'], where='mid', color='red', 
                label='Grid Import', alpha=0.9, linewidth=4, marker='^', markersize=8)
        ax1.step(hours, results_base['export_schedule'], where='mid', color='green', 
                label='Grid Export', alpha=0.9, linewidth=4, marker='v', markersize=8)
        ax1.step(hours, results_base['charge_schedule'], where='mid', color='purple', 
                label='Battery Charge', alpha=0.9, linewidth=4, marker='D', markersize=6)
        ax1.step(hours, results_base['discharge_schedule'], where='mid', color='magenta', 
                label='Battery Discharge', alpha=0.9, linewidth=4, marker='*', markersize=10)
    
   # ax1.set_xlabel('Hour of Day', fontsize=20, fontweight='bold')
    ax1.set_ylabel('Power (kW)', fontsize=20, fontweight='bold')
    ax1.set_title('BASE Consumer (w=2.5): Hourly Energy Flows', fontsize=22, fontweight='bold', pad=25)
    ax1.set_xlim(0.5, 24.5)
    ax1.set_xticks(range(1, 25, 2))
    ax1.tick_params(axis='both', labelsize=16)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=14, loc='upper right', framealpha=0.95, edgecolor='black')
    
    # Bottom subplot: FLEX scenario  
    if 'FLEX' in all_results:
        results_flex = all_results['FLEX']
        
        ax2.step(hours, results_flex['pv_schedule'], where='mid', color='gold', 
                label='PV Generation', alpha=0.9, linewidth=4, marker='o', markersize=8)
        ax2.step(hours, results_flex['load_schedule'], where='mid', color='blue', 
                label='Load Consumption', alpha=0.9, linewidth=4, marker='s', markersize=8)
        ax2.step(hours, results_flex['import_schedule'], where='mid', color='red', 
                label='Grid Import', alpha=0.9, linewidth=4, marker='^', markersize=8)
        ax2.step(hours, results_flex['export_schedule'], where='mid', color='green', 
                label='Grid Export', alpha=0.9, linewidth=4, marker='v', markersize=8)
        ax2.step(hours, results_flex['charge_schedule'], where='mid', color='purple', 
                label='Battery Charge', alpha=0.9, linewidth=4, marker='D', markersize=6)
        ax2.step(hours, results_flex['discharge_schedule'], where='mid', color='magenta', 
                label='Battery Discharge', alpha=0.9, linewidth=4, marker='*', markersize=10)
    
    ax2.set_xlabel('Hour of Day', fontsize=20, fontweight='bold')
    ax2.set_ylabel('Power (kW)', fontsize=20, fontweight='bold')
    ax2.set_title('FLEXIBLE Consumer (w=0.5): Hourly Energy Flows', fontsize=22, fontweight='bold', pad=25)
    ax2.set_xlim(0.5, 24.5)
    ax2.set_xticks(range(1, 25, 2))
    ax2.tick_params(axis='both', labelsize=16)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=14, loc='upper right', framealpha=0.95, edgecolor='black')
    
    plt.tight_layout(pad=3.0)
    plt.subplots_adjust(hspace=0.3)
    plt.savefig(output_dir / 'Q1c_v_Plot4_Hourly_Energy_Flows_Base_Flex.png', dpi=350, bbox_inches='tight')
    plt.show()


def create_plot5_hourly_energy_flows_tariffs(all_results, all_data, scenarios, output_dir):
    """Plot 5: Hourly Energy Flows – High Import vs Low Export Tariffs"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 18))
    
    hours = np.arange(1, 25)
    
    # Top subplot: HIGH-IMPORT scenario
    if 'HIGH-IMPORT' in all_results:
        results_high = all_results['HIGH-IMPORT']
        
        ax1.step(hours, results_high['pv_schedule'], where='mid', color='gold', 
                label='PV Generation', alpha=0.9, linewidth=4, marker='o', markersize=8)
        ax1.step(hours, results_high['load_schedule'], where='mid', color='blue', 
                label='Load Consumption', alpha=0.9, linewidth=4, marker='s', markersize=8)
        ax1.step(hours, results_high['import_schedule'], where='mid', color='red', 
                label='Grid Import', alpha=0.9, linewidth=4, marker='^', markersize=8)
        ax1.step(hours, results_high['export_schedule'], where='mid', color='green', 
                label='Grid Export', alpha=0.9, linewidth=4, marker='v', markersize=8)
        ax1.step(hours, results_high['charge_schedule'], where='mid', color='purple', 
                label='Battery Charge', alpha=0.9, linewidth=4, marker='D', markersize=6)
        ax1.step(hours, results_high['discharge_schedule'], where='mid', color='magenta', 
                label='Battery Discharge', alpha=0.9, linewidth=4, marker='*', markersize=10)
    
    #ax1.set_xlabel('Hour of Day', fontsize=20, fontweight='bold')
    ax1.set_ylabel('Power (kW)', fontsize=20, fontweight='bold')
    ax1.set_title('HIGH-IMPORT Tariff (τ_imp = 1.3×): Hourly Energy Flows', fontsize=22, fontweight='bold', pad=25)
    ax1.set_xlim(0.5, 24.5)
    ax1.set_xticks(range(1, 25, 2))
    ax1.tick_params(axis='both', labelsize=16)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=14, loc='upper right', framealpha=0.95, edgecolor='black')
    
    # Bottom subplot: LOW-EXPORT scenario  
    if 'LOW-EXPORT' in all_results:
        results_low = all_results['LOW-EXPORT']
        
        ax2.step(hours, results_low['pv_schedule'], where='mid', color='gold', 
                label='PV Generation', alpha=0.9, linewidth=4, marker='o', markersize=8)
        ax2.step(hours, results_low['load_schedule'], where='mid', color='blue', 
                label='Load Consumption', alpha=0.9, linewidth=4, marker='s', markersize=8)
        ax2.step(hours, results_low['import_schedule'], where='mid', color='red', 
                label='Grid Import', alpha=0.9, linewidth=4, marker='^', markersize=8)
        ax2.step(hours, results_low['export_schedule'], where='mid', color='green', 
                label='Grid Export', alpha=0.9, linewidth=4, marker='v', markersize=8)
        ax2.step(hours, results_low['charge_schedule'], where='mid', color='purple', 
                label='Battery Charge', alpha=0.9, linewidth=4, marker='D', markersize=6)
        ax2.step(hours, results_low['discharge_schedule'], where='mid', color='magenta', 
                label='Battery Discharge', alpha=0.9, linewidth=4, marker='*', markersize=10)
    
    ax2.set_xlabel('Hour of Day', fontsize=20, fontweight='bold')
    ax2.set_ylabel('Power (kW)', fontsize=20, fontweight='bold')
    ax2.set_title('LOW-EXPORT Tariff (τ_exp = 0.5×): Hourly Energy Flows', fontsize=22, fontweight='bold', pad=25)
    ax2.set_xlim(0.5, 24.5)
    ax2.set_xticks(range(1, 25, 2))
    ax2.tick_params(axis='both', labelsize=16)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=14, loc='upper right', framealpha=0.95, edgecolor='black')
    
    plt.tight_layout(pad=3.0)
    plt.subplots_adjust(hspace=0.3)
    plt.savefig(output_dir / 'Q1c_v_Plot5_Hourly_Energy_Flows_Tariffs.png', dpi=350, bbox_inches='tight')
    plt.show()


def print_detailed_scenario_summary(scenario_name, results, data, scenario_config, metrics):
    """Print detailed scenario summary with all requested metrics."""
    
    print(f"\n{'='*80}")
    print(f"DETAILED ANALYSIS - SCENARIO {scenario_name}")
    print(f"{'='*80}")
    
    # Cost breakdown
    print(f"\nCOST BREAKDOWN:")
    print(f"  Import energy cost:     {metrics['import_energy_cost']:.2f} DKK")
    print(f"  Export revenue:         {metrics['export_revenue']:.2f} DKK")
    print(f"  Grid tariffs paid:")
    print(f"    - Import tariffs:     {metrics['import_tariff_paid']:.2f} DKK")
    print(f"    - Export tariffs:     {metrics['export_tariff_paid']:.2f} DKK")
    print(f"    - Total tariffs:      {metrics['total_tariff_paid']:.2f} DKK")
    print(f"  Discomfort cost:        {metrics['discomfort_cost']:.2f} DKK")
    print(f"  NET TOTAL COST:         {metrics['total_cost']:.2f} DKK")
    
    # Battery value & use
    print(f"\nBATTERY VALUE & USE:")
    print(f"  Storage arbitrage value: {metrics['storage_arbitrage_value']:.2f} DKK")
    print(f"  Full-cycle equivalents:  {metrics['full_cycle_equivalents']:.2f}")
    print(f"  Round-trip losses:       {metrics['round_trip_losses']:.2f} kWh")
    print(f"  Hours at SoC bounds:")
    print(f"    - At minimum (0%):     {metrics['soc_min_hours']} hours")
    print(f"    - At maximum (100%):   {metrics['soc_max_hours']} hours")
    
    # Operational switches
    print(f"\nOPERATIONAL PATTERNS:")
    print(f"  Hours importing:         {metrics['hours_importing']}")
    print(f"  Hours exporting:         {metrics['hours_exporting']}")
    print(f"  Hours curtailing PV:     {metrics['hours_curtailing']}")
    print(f"  Peak operations:")
    print(f"    - Peak import:         {metrics['peak_import']:.2f} kW")
    print(f"    - Peak export:         {metrics['peak_export']:.2f} kW")
    print(f"    - Peak charge:         {metrics['peak_charge']:.2f} kW")
    print(f"    - Peak discharge:      {metrics['peak_discharge']:.2f} kW")
    
    # Duals (compact)
    print(f"\nSHADOW PRICE SUMMARY:")
    print(f"  Average λₜ:              {metrics['lambda_avg']:.3f} DKK/kWh")
    print(f"  Maximum λₜ:              {metrics['lambda_max']:.3f} DKK/kWh")
    print(f"  Binding SoC constraints:")
    print(f"    - Upper bound:         {metrics['binding_soc_upper']} hours")
    print(f"    - Lower bound:         {metrics['binding_soc_lower']} hours")


def print_comprehensive_summary_table(detailed_metrics, scenarios):
    """Print a comprehensive readable summary table with all key metrics."""
    
    print(f"\n{'='*120}")
    print("COMPREHENSIVE SCENARIO COMPARISON SUMMARY")
    print(f"{'='*120}")
    
    # Table header
    header = f"{'Scenario':<12} {'Total':<8} {'Import':<8} {'Export':<8} {'Tariff':<8} {'Discomf':<8} {'Arb.Val':<8} {'FCE':<6} {'H_imp':<6} {'H_exp':<6} {'SoCmax':<7} {'SoCmin':<7} {'λ_avg':<8} {'λ_max':<8}"
    print(header)
    
    subheader = f"{'':12} {'Cost':<8} {'Cost':<8} {'Rev':<8} {'Paid':<8} {'Cost':<8} {'(DKK)':<8} {'cyc':<6} {'hrs':<6} {'hrs':<6} {'hrs':<7} {'hrs':<7} {'(DKK)':<8} {'(DKK)':<8}"
    print(subheader)
    
    print("-" * 120)
    
    # Table rows
    for scenario_key in scenarios.keys():
        if scenario_key in detailed_metrics:
            metrics = detailed_metrics[scenario_key]
            row = f"{scenario_key:<12} "
            row += f"{metrics['total_cost']:<8.1f} "
            row += f"{metrics['import_energy_cost']:<8.1f} "
            row += f"{metrics['export_revenue']:<8.1f} "
            row += f"{metrics['total_tariff_paid']:<8.1f} "
            row += f"{metrics['discomfort_cost']:<8.1f} "
            row += f"{metrics['storage_arbitrage_value']:<8.1f} "
            row += f"{metrics['full_cycle_equivalents']:<6.2f} "
            row += f"{metrics['hours_importing']:<6} "
            row += f"{metrics['hours_exporting']:<6} "
            row += f"{metrics['soc_max_hours']:<7} "
            row += f"{metrics['soc_min_hours']:<7} "
            row += f"{metrics['lambda_avg']:<8.3f} "
            row += f"{metrics['lambda_max']:<8.3f}"
            print(row)
    
    print("-" * 120)
    
    # Key insights
    print(f"\nKEY INSIGHTS:")
    print(f"• Storage arbitrage value ranges from {min([m['storage_arbitrage_value'] for m in detailed_metrics.values()]):.1f} to {max([m['storage_arbitrage_value'] for m in detailed_metrics.values()]):.1f} DKK")
    print(f"• Battery operates at {min([m['full_cycle_equivalents'] for m in detailed_metrics.values()]):.2f} to {max([m['full_cycle_equivalents'] for m in detailed_metrics.values()]):.2f} full cycles per day")
    print(f"• FLEX scenario achieves profit despite discomfort penalty")
    print(f"• LOW-EXPORT scenario shows strategic timing: higher export revenue despite lower tariff")


def print_professional_scenario_summary(scenario_name, results, data, scenario_config):
    """Print clean professional console summary per scenario."""
    
    # Calculate key metrics
    total_import = sum(results['import_schedule'])
    total_export = sum(results['export_schedule'])
    total_pv_available = sum(data['pv_max_hourly'])
    total_pv_generated = sum(results['pv_schedule'])  # PV actually generated/used by system
    
    # PV self-consumption is the PV used directly by household (not exported)
    pv_self_consumed = total_pv_generated - total_export
    pv_self_consumption_rate = (pv_self_consumed / total_pv_available) * 100 if total_pv_available > 0 else 0
    discomfort_cost = scenario_config['w'] * (results['total_dev_plus'] + results['total_dev_minus'])
    battery_throughput = results['total_charged'] + results['total_discharged']
    
    # Calculate lambda_t statistics if available
    lambda_avg = "N/A"
    lambda_max = "N/A"
    if 'dual_energy' in results and results['dual_energy']:
        lambda_vals = [x for x in results['dual_energy'] if x is not None and abs(x) > 1e-6]
        if lambda_vals:
            lambda_avg = f"{sum(lambda_vals)/len(lambda_vals):.3f}"
            lambda_max = f"{max(lambda_vals):.3f}"
    
    # Calculate corrected total cost for display
    import_cost = sum([(data['energy_prices'][t] + data['import_tariff']) * results['import_schedule'][t] 
                       for t in range(len(results['import_schedule']))])
    export_revenue = sum([(data['energy_prices'][t] - data['export_tariff']) * results['export_schedule'][t] 
                          for t in range(len(results['export_schedule']))])
    corrected_total_cost = import_cost - export_revenue + discomfort_cost
    
    print(f"\nScenario {scenario_name}")
    print(f"Total cost = {corrected_total_cost:.2f} DKK")
    print(f"Imports = {total_import:.2f} kWh, Exports = {total_export:.2f} kWh")
    print(f"PV available = {total_pv_available:.2f} kWh, PV generated = {total_pv_generated:.2f} kWh")
    print(f"PV self-consumed = {pv_self_consumed:.2f} kWh ({pv_self_consumption_rate:.1f}%)")
    print(f"Discomfort cost = {discomfort_cost:.2f} DKK")
    print(f"Battery throughput = {battery_throughput:.2f} kWh")
    print(f"Lambda_t avg = {lambda_avg}, max = {lambda_max}")


def print_professional_results(all_results, all_data, scenarios, kpi_df):
    """Print results in professional format without emojis."""
    
    print("\n" + "="*80)
    print("Q1(v) SCENARIO ANALYSIS RESULTS")
    print("="*80)
    
    print("\nSCENARIOS ANALYZED:")
    print("BASE: w = 2.5, base tariffs (reference case)")
    print("FLEX: w = 0.5, base tariffs (high flexibility)")
    print("RIGID: w = 5.0, base tariffs (comfort-focused)")
    print("HIGH-IMPORT: w = 2.5, import tariff +30%")
    print("LOW-EXPORT: w = 2.5, export tariff -50%")
    
    print("\nKEY PERFORMANCE INDICATORS")
    print("=" * 120)
    
    # Professional KPI table
    print(f"{'Scenario':<12} {'w':<5} {'Cost':<8} {'Import':<8} {'Export':<8} {'PV SelfC':<8} {'PV Self':<8} {'Discomf':<8} {'Battery':<8} {'λ avg':<8}")
    print(f"{'':12} {'':5} {'(DKK)':<8} {'(kWh)':<8} {'(kWh)':<8} {'(kWh)':<8} {'(%)':<8} {'(DKK)':<8} {'T.put':<8} {'(DKK/kWh)':<8}")
    print("-" * 120)
    
    for _, row in kpi_df.iterrows():
        # Calculate lambda average if available
        lambda_avg = "N/A"
        if row['scenario'] in all_results and 'dual_power_balance' in all_results[row['scenario']]:
            lambda_vals = [x for x in all_results[row['scenario']]['dual_power_balance'] if x is not None]
            if lambda_vals:
                lambda_avg = f"{sum(lambda_vals)/len(lambda_vals):.3f}"
        
        print(f"{row['scenario']:<12} {row['w_parameter']:<5.1f} {row['total_cost_dkk']:<8.2f} {row['import_kwh']:<8.2f} {row['export_kwh']:<8.2f} {row['pv_self_consumed_kwh']:<8.2f} {row['pv_self_consumption_pct']:<8.1f} {row['discomfort_cost_dkk']:<8.2f} {row['battery_throughput_kwh']:<8.1f} {lambda_avg:<8}")
    
    print("=" * 120)
    
    print("\nDUAL VARIABLE INTERPRETATION:")
    print("lambda_t: Marginal value of electricity at each hour (shadow price)")
    print("  - High values indicate electricity scarcity")
    print("  - Low values indicate PV surplus periods")
    print("  - Flexible scenarios show smoother lambda_t profiles")
    print("mu_soc_up_t, mu_soc_lo_t: Battery constraint shadow prices")
    print("  - Positive when battery reaches upper/lower SoC limits")
    print("nu_terminal: End-of-day SoC constraint shadow price")
    

    print("\nVISUALIZATIONS GENERATED:")
    print("1. Daily Cost Breakdown Across Scenarios")
    print("2. Battery State of Charge Under Different Flexibility Levels")
    print("3. Marginal Value of Energy (Shadow Prices)")
    print("4. Hourly Energy Flows - Base vs Flexible Consumer")
    print("5. Hourly Energy Flows - High Import vs Low Export Tariffs")


def main():
    """Main execution function for Q1c scenario analysis."""
    
    # Create output directory
    output_dir = Path('results/question_1c')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Q1(v) SCENARIO ANALYSIS")
    print("=" * 80)
    print("QUESTION 1c PART V - SCENARIO ANALYSIS: FLEXIBILITY & COST STRUCTURE")
    print("=" * 80)
    
    try:
        # Solve all scenarios
        analysis_results = solve_q1c_v_scenarios(output_dir)
        
        if analysis_results:
            # Print professional results in requested format
            print_professional_results(
                analysis_results['results'], 
                analysis_results['data'], 
                analysis_results['scenarios'],
                analysis_results['kpis']
            )
            
            print(f"\nANALYSIS COMPLETE")
            
        else:
            print("ERROR: Q1c scenario analysis failed")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()