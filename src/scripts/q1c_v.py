"""
Question 1c Part V - Scenario Analysis: Flexibility and Cost Structure Sensitivity
Report Quality Analysis with 5 Scenarios

Implements comprehensive scenario analysis for Q1c with:
- BASE, FLEX, RIGID scenarios (varying w with baseline tariffs)
- HIGH-IMPORT, LOW-EXPORT scenarios (varying tariffs with baseline w)
- Complete KPI calculation and comparison
- Time series export (primal and dual variables)
- 4 professional visualizations for report
"""

import sys
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Configure matplotlib for report-quality figures
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


def solve_q1c_v_scenarios():
    """
    Solve Q1c part v with 5 different scenarios analyzing flexibility and cost structure.
    
    Returns:
        dict: Dictionary with results for all scenarios
    """
    
    print("QUESTION 1c PART V - SCENARIO ANALYSIS: FLEXIBILITY & COST STRUCTURE")
    print("=" * 80)
    
    try:
        # Load and process base data
        project_root = Path(__file__).parent.parent.parent
        loader = DataLoader(base_path=str(project_root / "data"))
        base_raw_data = loader.load_data("question_1b")
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
        kpi_summary = []
        
        print(f"\n🎯 Solving {len(scenarios)} scenarios...")
        print("-" * 60)
        
        for scenario_key, scenario_config in scenarios.items():
            print(f"\n📊 Scenario: {scenario_config['name']}")
            print(f"   Description: {scenario_config['description']}")
            print(f"   Parameters: w={scenario_config['w']}, "
                  f"τ_imp={scenario_config['tariff_import_mult']:.2f}×base, "
                  f"τ_exp={scenario_config['tariff_export_mult']:.2f}×base")
            
            # Process data with scenario-specific parameters
            scenario_data = processor.process_for_optimization_q1b(
                copy.deepcopy(base_raw_data), scenario_config['w']
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
                print(f"   ✅ Solved successfully - Total Cost: {results['optimal_cost']:.2f} DKK")
                
                # Store results and data
                all_results[scenario_key] = results
                all_data[scenario_key] = scenario_data
                
                # Calculate comprehensive KPIs
                kpis = calculate_scenario_kpis(results, scenario_data, scenario_config)
                kpis['scenario'] = scenario_key
                kpis['scenario_name'] = scenario_config['name']
                kpi_summary.append(kpis)
                
                # Export time series data
                export_time_series(results, scenario_data, scenario_key)
                
            else:
                print(f"   ❌ Failed to solve")
        
        if kpi_summary:
            # Create KPI summary table
            kpi_df = pd.DataFrame(kpi_summary)
            print("\n" + "="*100)
            print("SCENARIO COMPARISON - KEY PERFORMANCE INDICATORS")
            print("="*100)
            print(kpi_df.to_string(index=False, float_format='%.3f'))
            
            # Save KPI summary
            kpi_df.to_csv('Q1c_v_KPI_Summary.csv', index=False)
            print(f"\n💾 KPI Summary saved to: Q1c_v_KPI_Summary.csv")
            
            # Generate visualizations
            create_scenario_visualizations(all_results, all_data, scenarios)
            
            return {
                'results': all_results,
                'data': all_data,
                'kpis': kpi_df,
                'scenarios': scenarios
            }
        else:
            print("❌ No scenarios solved successfully")
            return None
            
    except Exception as e:
        print(f"❌ Error in Q1c scenario analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


def calculate_scenario_kpis(results, data, scenario_config):
    """Calculate comprehensive KPIs for a scenario."""
    
    # Basic totals
    total_import = sum(results['import_schedule'])
    total_export = sum(results['export_schedule'])
    total_pv_generation = sum(results['pv_schedule'])
    pv_used = total_pv_generation - total_export
    
    # Calculate costs
    import_cost = sum([imp * price for imp, price in zip(results['import_schedule'], data['energy_prices'])])
    export_revenue = sum(results['export_schedule']) * data['export_tariff']  # Use single export tariff
    discomfort_cost = scenario_config['w'] * (results['total_dev_plus'] + results['total_dev_minus'])
    net_energy_cost = import_cost - export_revenue
    
    kpis = {
        # Core metrics
        'total_cost_dkk': results['optimal_cost'],
        'import_kwh': total_import,
        'export_kwh': total_export,
        'pv_used_kwh': pv_used,
        'pv_self_consumption_pct': (pv_used / total_pv_generation) * 100 if total_pv_generation > 0 else 0,
        'discomfort_cost_dkk': discomfort_cost,
        'battery_throughput_kwh': results['total_charged'] + results['total_discharged'],
        'soc_range_kwh': results['max_soc'] - results['min_soc'],
        'net_profit_dkk': -results['optimal_cost'],  # Negative cost = profit
        
        # Additional metrics
        'import_cost_dkk': import_cost,
        'export_revenue_dkk': export_revenue,
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


def export_time_series(results, data, scenario_key):
    """Export primal and dual variables time series to CSV."""
    
    hours = list(range(1, 25))
    
    # Primal variables time series
    primal_data = {
        'hour': hours,
        'load_actual': results['load_schedule'],
        'load_reference': data['reference_load'],
        'dev_plus': results['dev_plus_schedule'],
        'dev_minus': results['dev_minus_schedule'],
        'grid_import': results['import_schedule'],
        'grid_export': results['export_schedule'],
        'battery_charge': results['charge_schedule'],
        'battery_discharge': results['discharge_schedule'],
        'battery_soc': results['soc_schedule'],
        'pv_generation': results['pv_schedule'],
        'energy_price': data['energy_prices'],
        'export_tariff': [data['export_tariff']] * 24  # Single tariff repeated for all hours
    }
    
    primal_df = pd.DataFrame(primal_data)
    primal_df.to_csv(f'Q1c_v_{scenario_key}_Primal_TimeSeries.csv', index=False)
    
    # Dual variables (shadow prices) - if available from model
    if 'dual_power_balance' in results:
        dual_data = {
            'hour': hours,
            'lambda_power_balance': results['dual_power_balance'],
            'alpha_soc_dynamics': results.get('dual_soc_dynamics', [0]*24),
            'mu_soc_lower': results.get('dual_soc_lower', [0]*24),
            'mu_soc_upper': results.get('dual_soc_upper', [0]*24),
            'gamma_charge_upper': results.get('dual_charge_upper', [0]*24),
            'gamma_discharge_upper': results.get('dual_discharge_upper', [0]*24)
        }
        
        dual_df = pd.DataFrame(dual_data)
        dual_df.to_csv(f'Q1c_v_{scenario_key}_Dual_TimeSeries.csv', index=False)
    
    print(f"   📁 Time series exported: Q1c_v_{scenario_key}_*_TimeSeries.csv")


def create_scenario_visualizations(all_results, all_data, scenarios):
    """Create exactly the 4 requested visualizations."""
    
    print(f"\n📊 Creating 4 Requested Plots...")
    print("-" * 60)
    
    # Plot 1: Cost breakdown per scenario (stacked bars)
    create_plot1_cost_breakdown(all_results, all_data, scenarios)
    
    # Plot 2: Battery SoC profiles (24 h) 
    create_plot2_battery_soc_profiles(all_results, scenarios)
    
    # Plot 3: Shadow price λₜ (dual variable)
    create_plot3_shadow_price_lambda(all_results, all_data, scenarios)
    
    # Plot 4: Hourly energy flows (primal)
    create_plot4_hourly_energy_flows(all_results, all_data, scenarios)
    
    print("✅ All 4 requested plots completed!")


def create_plot1_cost_breakdown(all_results, all_data, scenarios):
    """Plot 1: Daily Cost Breakdown Across Scenarios (stacked bars)"""
    
    fig, ax = plt.subplots(figsize=(20, 12))
    
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
            
            # Calculate cost components
            import_cost = sum([imp * price for imp, price in zip(results['import_schedule'], data['energy_prices'])])
            export_revenue = sum(results['export_schedule']) * data['export_tariff']  # Single export tariff
            discomfort_cost = scenario_config['w'] * (results['total_dev_plus'] + results['total_dev_minus'])
            
            import_costs.append(import_cost)
            export_revenues.append(export_revenue)
            discomfort_costs.append(discomfort_cost)
            total_costs.append(results['optimal_cost'])
    
    x = np.arange(len(scenario_names))
    width = 0.6
    
    # Create stacked bars
    bars1 = ax.bar(x, import_costs, width, label='Import Cost', color='red', alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x, [-rev for rev in export_revenues], width, bottom=import_costs, 
                   label='Export Revenue', color='green', alpha=0.8, edgecolor='black')
    bars3 = ax.bar(x, discomfort_costs, width, 
                   bottom=[imp - rev for imp, rev in zip(import_costs, export_revenues)],
                   label='Discomfort Cost', color='orange', alpha=0.8, edgecolor='black')
    
    # Add total cost markers
    ax.scatter(x, total_costs, color='black', s=100, marker='D', label='Total Cost', zorder=5)
    
    # Add value labels
    for i, (total, imp, exp, dis) in enumerate(zip(total_costs, import_costs, export_revenues, discomfort_costs)):
        ax.text(i, max(total + 2, imp - exp + dis + 2), f'Total: {total:.1f}', 
                ha='center', va='bottom', fontsize=16, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.9))
    
    ax.set_xlabel('Scenario', fontsize=22, fontweight='bold')
    ax.set_ylabel('Cost (DKK)', fontsize=22, fontweight='bold')
    ax.set_title('Daily Cost Breakdown Across Scenarios', fontsize=26, fontweight='bold', pad=30)
    ax.set_xticks(x)
    ax.set_xticklabels(scenario_names, fontsize=18, fontweight='bold')
    ax.tick_params(axis='y', labelsize=18)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=16, loc='upper left', framealpha=0.95, edgecolor='black')
    
    # Add horizontal line at zero
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.8, linewidth=2)
    
    plt.tight_layout()
    plt.savefig('Q1c_v_Plot1_Cost_Breakdown.png', dpi=350, bbox_inches='tight')
    plt.close()
    print("✅ Plot 1: Daily Cost Breakdown Across Scenarios saved")


def create_plot2_battery_soc_profiles(all_results, scenarios):
    """Plot 2: Battery State of Charge Under Different Flexibility Levels (24 h)"""
    
    fig, ax = plt.subplots(figsize=(20, 12))
    
    hours = np.arange(1, 25)
    colors = {'BASE': 'blue', 'FLEX': 'green', 'RIGID': 'red'}
    markers = {'BASE': 'o', 'FLEX': 's', 'RIGID': '^'}
    
    # Plot SoC profiles for flexibility scenarios only
    for scenario_key in ['FLEX', 'BASE', 'RIGID']:
        if scenario_key in all_results:
            results = all_results[scenario_key]
            soc_profile = results['soc_schedule']
            w_value = scenarios[scenario_key]['w']
            
            ax.step(hours, soc_profile, where='mid', color=colors[scenario_key], 
                   label=f'{scenario_key} (w={w_value})', alpha=0.9, 
                   marker=markers[scenario_key], markersize=10, linewidth=5)
            
            # Add subtle fill area
            ax.fill_between(hours, 0, soc_profile, alpha=0.1, color=colors[scenario_key])
    
    # Add reference lines
    ax.axhline(y=6.0, color='darkred', linestyle='--', alpha=0.7, linewidth=3,
               label='Battery Capacity (6 kWh)')
    ax.axhline(y=3.0, color='orange', linestyle='--', alpha=0.7, linewidth=3,
               label='Target SoC (3 kWh)')
    ax.axhline(y=0.0, color='black', linestyle=':', alpha=0.5, linewidth=2,
               label='Empty Battery')
    
    ax.set_xlabel('Hour of Day', fontsize=22, fontweight='bold')
    ax.set_ylabel('Battery State of Charge (kWh)', fontsize=22, fontweight='bold')
    ax.set_title('Battery State of Charge Under Different Flexibility Levels', fontsize=26, fontweight='bold', pad=30)
    ax.set_xlim(0.5, 24.5)
    ax.set_xticks(range(1, 25, 2))
    ax.set_ylim(-0.2, 6.2)
    ax.tick_params(axis='both', labelsize=18)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=18, loc='upper left', framealpha=0.95, edgecolor='black')
    
    # Add summary text
    summary_text = "FLEXIBILITY SHOWS HOW BATTERY CYCLING CHANGES:\n"
    for scenario_key in ['FLEX', 'BASE', 'RIGID']:
        if scenario_key in all_results:
            soc_range = all_results[scenario_key]['max_soc'] - all_results[scenario_key]['min_soc']
            throughput = all_results[scenario_key]['total_charged'] + all_results[scenario_key]['total_discharged']
            summary_text += f"• {scenario_key}: SoC Range={soc_range:.1f} kWh, Throughput={throughput:.1f} kWh\n"
    
    ax.text(0.02, 0.98, summary_text, transform=ax.transAxes, fontsize=16, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.95),
            verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig('Q1c_v_Plot2_Battery_SoC_Profiles.png', dpi=350, bbox_inches='tight')
    plt.close()
    print("✅ Plot 2: Battery State of Charge Under Different Flexibility Levels saved")


def create_plot3_shadow_price_lambda(all_results, all_data, scenarios):
    """Plot 3: Marginal Value of Energy (λₜ) – Effect of Flexibility"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 16))
    
    hours = np.arange(1, 25)
    
    # Top subplot: Shadow prices (if available) or Energy prices comparison
    if 'dual_power_balance' in all_results.get('BASE', {}):
        # Plot actual shadow prices
        for scenario_key in ['BASE', 'FLEX']:
            if scenario_key in all_results and 'dual_power_balance' in all_results[scenario_key]:
                shadow_prices = all_results[scenario_key]['dual_power_balance']
                w_value = scenarios[scenario_key]['w']
                color = 'blue' if scenario_key == 'BASE' else 'green'
                
                ax1.step(hours, shadow_prices, where='mid', color=color, 
                       label=f'{scenario_key} Shadow Price λₜ (w={w_value})', 
                       alpha=0.9, linewidth=5, marker='o', markersize=8)
        
        # Overlay market price as reference
        if 'BASE' in all_data:
            retail_prices = all_data['BASE']['energy_prices']
            ax1.step(hours, retail_prices, where='mid', color='gray', 
                   linestyle='--', alpha=0.7, linewidth=3, label='Market Price πₜ')
            
        ax1.set_ylabel('Shadow Price λₜ (DKK/kWh)', fontsize=20, fontweight='bold')
        ax1.set_title('Marginal Value of Energy (λₜ) – Effect of Flexibility', fontsize=24, fontweight='bold', pad=20)
        
    else:
        # Fallback: Show energy price comparison across scenarios
        for scenario_key in ['BASE', 'FLEX', 'RIGID']:
            if scenario_key in all_data:
                prices = all_data[scenario_key]['energy_prices']
                color = {'BASE': 'blue', 'FLEX': 'green', 'RIGID': 'red'}[scenario_key]
                w_value = scenarios[scenario_key]['w']
                
                ax1.step(hours, prices, where='mid', color=color, 
                       label=f'{scenario_key} Energy Price (w={w_value})', 
                       alpha=0.9, linewidth=4, marker='o', markersize=8)
        
        ax1.set_ylabel('Energy Price (DKK/kWh)', fontsize=20, fontweight='bold')
        ax1.set_title('Energy Prices Across Flexibility Scenarios', fontsize=24, fontweight='bold', pad=20)
    
    ax1.tick_params(axis='both', labelsize=16)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=16, loc='upper right', framealpha=0.95, edgecolor='black')
    ax1.set_xlim(0.5, 24.5)
    ax1.set_xticks(range(1, 25, 2))
    
    # Bottom subplot: Total cost comparison over time (cumulative)
    scenario_names = []
    total_costs = []
    
    for scenario_key in ['BASE', 'FLEX', 'RIGID']:
        if scenario_key in all_results:
            scenario_names.append(scenario_key)
            total_costs.append(all_results[scenario_key]['optimal_cost'])
    
    x = np.arange(len(scenario_names))
    bars = ax2.bar(x, total_costs, color=['blue', 'green', 'red'], alpha=0.8, width=0.6, 
                   edgecolor='black', linewidth=2)
    
    # Add value labels
    for bar, cost in zip(bars, total_costs):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + (abs(height)*0.02),
                f'{cost:.2f} DKK', ha='center', va='bottom', 
                fontsize=18, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9))
    
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.8, linewidth=2)
    ax2.set_xlabel('Scenario', fontsize=20, fontweight='bold')
    ax2.set_ylabel('Total Daily Cost (DKK)', fontsize=20, fontweight='bold')
    ax2.set_title('Total Cost Comparison: Effect of Flexibility', fontsize=24, fontweight='bold', pad=20)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f'{name}\n(w={scenarios[name]["w"]})' for name in scenario_names], 
                        fontsize=16, fontweight='bold')
    ax2.tick_params(axis='y', labelsize=16)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('Q1c_v_Plot3_Shadow_Price_Lambda.png', dpi=350, bbox_inches='tight')
    plt.close()
    print("✅ Plot 3: Marginal Value of Energy (λₜ) – Effect of Flexibility saved")


def create_plot4_hourly_energy_flows(all_results, all_data, scenarios):
    """Plot 4: Hourly Energy Flows – Base vs Flexible Consumer"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 16))
    
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
    
    ax1.set_ylabel('Power (kW)', fontsize=20, fontweight='bold')
    ax1.set_title('BASE Consumer (w=2.5): Hourly Energy Flows', fontsize=24, fontweight='bold', pad=20)
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
    ax2.set_title('FLEXIBLE Consumer (w=0.5): Hourly Energy Flows', fontsize=24, fontweight='bold', pad=20)
    ax2.set_xlim(0.5, 24.5)
    ax2.set_xticks(range(1, 25, 2))
    ax2.tick_params(axis='both', labelsize=16)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=14, loc='upper right', framealpha=0.95, edgecolor='black')
    
    # Add comparison summary
    if 'BASE' in all_results and 'FLEX' in all_results:
        base_cost = all_results['BASE']['optimal_cost']
        flex_cost = all_results['FLEX']['optimal_cost']
        savings = base_cost - flex_cost
        
        summary_text = f"COMPARISON SUMMARY:\n"
        summary_text += f"• BASE Cost: {base_cost:.2f} DKK\n"
        summary_text += f"• FLEX Cost: {flex_cost:.2f} DKK\n"
        summary_text += f"• Savings: {savings:.2f} DKK ({(savings/abs(base_cost))*100:.1f}%)\n"
        summary_text += f"• Flexibility enables optimal load shifting and battery usage"
        
        fig.text(0.02, 0.02, summary_text, fontsize=16, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.95),
                verticalalignment='bottom')
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)  # Make room for summary text
    plt.savefig('Q1c_v_Plot4_Hourly_Energy_Flows.png', dpi=350, bbox_inches='tight')
    plt.close()
    print("✅ Plot 4: Hourly Energy Flows – Base vs Flexible Consumer saved")


def print_clean_results(all_results, all_data, scenarios, kpi_df):
    """Print results in the exact clean format requested."""
    
    print("\n" + "="*80)
    print("🧩 Q1(v) – RESULTS & OUTPUT")
    print("="*80)
    
    print("\n⚙️ SCENARIOS COMPLETED:")
    print("BASE → w = 2.5, base tariffs")
    print("FLEX → w = 0.5, base tariffs (very flexible)")
    print("RIGID → w = 5.0, base tariffs (comfort-focused)")
    print("HIGH-IMPORT → w = 2.5, τ_imp = 1.3 × base (more expensive imports)")
    print("LOW-EXPORT → w = 2.5, τ_exp = 0.5 × base (less export revenue)")
    
    print("\n📊 KPI SUMMARY TABLE (for report)")
    print("-" * 120)
    
    # Create clean KPI table
    print(f"{'Scenario':<12} {'w':<4} {'Cost (DKK)':<11} {'Import (kWh)':<13} {'Export (kWh)':<13} {'PV used (kWh)':<14} {'PV self-cons (%)':<16} {'Discomfort (DKK)':<16} {'Battery throughput (kWh)':<24} {'SoC range (kWh)':<15}")
    print("-" * 120)
    
    for _, row in kpi_df.iterrows():
        print(f"{row['scenario']:<12} {row['w_parameter']:<4.1f} {row['total_cost_dkk']:<11.2f} {row['import_kwh']:<13.2f} {row['export_kwh']:<13.2f} {row['pv_used_kwh']:<14.2f} {row['pv_self_consumption_pct']:<16.1f} {row['discomfort_cost_dkk']:<16.2f} {row['battery_throughput_kwh']:<24.2f} {row['soc_range_kwh']:<15.2f}")
    
    print("\n⚡ DUAL INTERPRETATION (for discussion)")
    print("lambda_t → marginal value of 1 kWh at each hour (shadow price)")
    print(" • high when electricity scarce, low when PV surplus")
    print(" • flexible case smooths λₜ profile → cheaper overall cost")
    print("mu_soc_up_t, mu_soc_lo_t → positive when battery full/empty → show active limits")
    print("nu_terminal → value of cyclic end-of-day condition")
    
    print("\n🧠 DATA STORED:")
    print("A. Primal variables (decision variables) → saved to CSV files")
    print("   l_t, l_ref_t, d_plus_t, d_minus_t, u_t, x_t, c_t, r_t, s_t, p_pv_t")
    print("B. Dual variables (shadow prices) → saved to CSV files (if available)")
    print("   lambda_t, mu_soc_up_t, mu_soc_lo_t, nu_terminal")
    
    print("\n📈 PLOTS GENERATED (4 total):")
    print("1. Cost breakdown per scenario")
    print("2. Battery SoC profiles (24 h)")  
    print("3. Shadow price λₜ (dual variable)")
    print("4. Hourly energy flows (primal)")


def main():
    """Main execution function for Q1c scenario analysis."""
    
    print("🧩 Q1(v) – To-Do & Output Plan")
    print("=" * 80)
    
    try:
        # Solve all scenarios
        analysis_results = solve_q1c_v_scenarios()
        
        if analysis_results:
            # Print clean results in requested format
            print_clean_results(
                analysis_results['results'], 
                analysis_results['data'], 
                analysis_results['scenarios'],
                analysis_results['kpis']
            )
            
            print(f"\n✅ Analysis Complete!")
            print(f"📁 Files Generated:")
            print(f"   • Q1c_v_KPI_Summary.csv")
            print(f"   • Q1c_v_*_Primal_TimeSeries.csv (5 files)")
            print(f"   • Q1c_v_Plot*.png (4 plots)")
            
        else:
            print("❌ Q1c scenario analysis failed")
            
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()