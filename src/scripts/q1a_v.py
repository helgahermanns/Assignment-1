"""
Question 1 Part V - Consumer Energy Flexibility Scenario Analysis
Dataset: question_1a (with modified tariff scenarios)

This script solves Q1 Part V by running multiple scenarios with different 
import/export tariff structures using the same question_1a dataset.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import copy

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data_ops.data_loader import DataLoader
from data_ops.data_processor import DataProcessor
from opt_model.opt_model_Q1a import ConsumerFlexibilityModel


def solve_q1_part_v():
    """
    Solve Q1 Part V with tariff scenario analysis.
    
    Scenarios:
    1. Base case (original tariffs)
    2. High import tariff (+50%)
    3. Low export tariff (-50%) 
    4. Both high import & low export
    
    Returns:
        dict: Results for all scenarios
    """
    
    print("Loading base data from question_1a dataset...")
    print("Processing 5 scenarios with different tariff structures...")
    print("-" * 50)
    
    try:
        # Load base data from question_1a
        project_root = Path(__file__).parent.parent.parent
        loader = DataLoader(base_path=str(project_root / "data"))
        
        base_raw_data = loader.load_data("question_1a")
        
        # Define scenarios for Q1 Part V - System-level Cost Structure Analysis
        scenarios = {
            "base": {
                "name": "Base Case", 
                "import_multiplier": 1.0, 
                "export_multiplier": 1.0,
                "price_peak_factor": 1.0,
                "description": "Original cost structure - baseline for comparison"
            },
            "high_import": {
                "name": "High Import Tariffs", 
                "import_multiplier": 2.0, 
                "export_multiplier": 1.0,
                "price_peak_factor": 1.0,
                "description": "Double import tariffs - impacts grid dependency"
            },
            "low_export": {
                "name": "Low Export Incentives", 
                "import_multiplier": 1.0, 
                "export_multiplier": 0.3,
                "price_peak_factor": 1.0,
                "description": "Reduced export tariffs - less incentive to sell excess PV"
            },
            "peak_pricing": {
                "name": "Peak Hour Pricing", 
                "import_multiplier": 1.0, 
                "export_multiplier": 1.0,
                "price_peak_factor": 2.0,
                "description": "Higher prices during peak hours (7-19) - time-of-use pricing"
            },
            "unfavorable": {
                "name": "Unfavorable Grid Terms", 
                "import_multiplier": 2.0, 
                "export_multiplier": 0.2,
                "price_peak_factor": 1.5,
                "description": "Combined: high import + low export + peak pricing"
            }
        }
        
        all_results = {}
        
        # Run each scenario
        print("\nSolving 5 scenarios...")
        print("-" * 50)
        
        for scenario_key, scenario_info in scenarios.items():
            print(f"\nProcessing {scenario_info['name']}...")
            
            # Modify data for this scenario
            modified_data = modify_scenario_parameters(
                copy.deepcopy(base_raw_data), 
                scenario_info['import_multiplier'],
                scenario_info['export_multiplier'],
                scenario_info['price_peak_factor']
            )
            
            # Process data
            processor = DataProcessor()
            optimization_data = processor.process_for_optimization(modified_data)
            
            # Solve optimization
            model = ConsumerFlexibilityModel(optimization_data)
            results = model.solve()
            
            if results:
                # Add PV production data to results for analysis
                results['pv_production'] = optimization_data['pv_max_hourly']
                
                all_results[scenario_key] = {
                    'results': results,
                    'scenario_info': scenario_info,
                    'optimization_data': optimization_data
                }
                print(f"Optimal solution found! Optimal objective value: {results['optimal_cost']:.2f} DKK")
            else:
                print(f"Optimization failed for scenario: {scenario_info['name']}")
        
        # Print detailed analysis for each scenario
        if all_results:
            for scenario_key, scenario_data in all_results.items():
                print_detailed_scenario_summary_q1a(scenario_key, scenario_data)
            
            print_comprehensive_summary_table_q1a(all_results)
            analyze_flexibility_and_profits(all_results)
        
        return all_results
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def modify_scenario_parameters(raw_data, import_multiplier, export_multiplier, price_peak_factor):
    """
    Modify cost structure parameters for scenario analysis
    
    Args:
        raw_data: Original data dictionary
        import_multiplier: Factor to multiply import tariff
        export_multiplier: Factor to multiply export tariff  
        price_peak_factor: Factor to multiply hourly prices during peak hours (7-19)
    """
    
    # Modify bus parameters (tariffs and hourly prices)
    if 'bus_params' in raw_data:
        for bus in raw_data['bus_params']:
            # Modify import/export tariffs
            original_import = bus['import_tariff_DKK/kWh']
            original_export = bus['export_tariff_DKK/kWh']
            
            bus['import_tariff_DKK/kWh'] = original_import * import_multiplier
            bus['export_tariff_DKK/kWh'] = original_export * export_multiplier
            
            print(f"  Tariffs - Import: {original_import:.2f} → {bus['import_tariff_DKK/kWh']:.2f} DKK/kWh, "
                  f"Export: {original_export:.2f} → {bus['export_tariff_DKK/kWh']:.2f} DKK/kWh")
            
            # Modify hourly energy prices (peak pricing during hours 7-19)
            if 'energy_price_DKK_per_kWh' in bus and price_peak_factor != 1.0:
                original_prices = bus['energy_price_DKK_per_kWh'].copy()
                
                for hour in range(24):
                    if 7 <= hour <= 19:  # Peak hours
                        bus['energy_price_DKK_per_kWh'][hour] = original_prices[hour] * price_peak_factor
                
                avg_original = sum(original_prices) / 24
                avg_new = sum(bus['energy_price_DKK_per_kWh']) / 24
                print(f"  Peak pricing (7-19h): {price_peak_factor:.1f}x factor, "
                      f"Average price: {avg_original:.2f} → {avg_new:.2f} DKK/kWh")
    
    return raw_data


def calculate_detailed_metrics_q1a(results, scenario_info):
    """Calculate detailed metrics for Q1a scenario analysis"""
    
    # Energy flows
    import_total = results.get('total_imported', 0)
    export_total = results.get('total_exported', 0)
    pv_used = results.get('total_pv_used', 0)
    total_load = results.get('total_energy_consumed', 0)
    
    # Get hourly data
    hourly_load = results.get('load_schedule', [])
    pv_production = results.get('pv_production', [])
    
    # Cost breakdown (simplified for Q1a without detailed tariff breakdown)
    total_cost = results.get('optimal_cost', 0)
    
    # Operational patterns
    hours_importing = sum(1 for hour_load, hour_pv in zip(hourly_load, pv_production) if hour_load > hour_pv)
    hours_exporting = sum(1 for hour_load, hour_pv in zip(hourly_load, pv_production) if hour_pv > hour_load)
    
    # Peak operations
    peak_import = max([max(0, load - pv) for load, pv in zip(hourly_load, pv_production)]) if hourly_load and pv_production else 0
    peak_export = max([max(0, pv - load) for load, pv in zip(hourly_load, pv_production)]) if hourly_load and pv_production else 0
    
    # PV utilization
    total_pv_available = sum(pv_production) if pv_production else 0
    pv_utilization = (pv_used / total_pv_available * 100) if total_pv_available > 0 else 0
    
    return {
        'total_cost': total_cost,
        'import_total': import_total,
        'export_total': export_total,
        'pv_used': pv_used,
        'pv_utilization': pv_utilization,
        'hours_importing': hours_importing,
        'hours_exporting': hours_exporting,
        'peak_import': peak_import,
        'peak_export': peak_export,
        'total_load': total_load
    }

def print_detailed_scenario_summary_q1a(scenario_key, scenario_data):
    """Print detailed summary for a single Q1a scenario"""
    
    results = scenario_data['results']
    scenario_info = scenario_data['scenario_info']
    metrics = calculate_detailed_metrics_q1a(results, scenario_info)
    
    print(f"\n" + "=" * 80)
    print(f"DETAILED ANALYSIS - SCENARIO {scenario_info['name']}")
    print("=" * 80)
    
    print(f"\nCOST BREAKDOWN:")
    print(f"  NET TOTAL COST:         {metrics['total_cost']:.2f} DKK")
    
    print(f"\nENERGY FLOWS:")
    print(f"  Total import:           {metrics['import_total']:.2f} kWh")
    print(f"  Total export:           {metrics['export_total']:.2f} kWh")
    print(f"  PV self-consumption:    {metrics['pv_used']:.2f} kWh")
    print(f"  PV utilization:         {metrics['pv_utilization']:.1f}%")
    
    print(f"\nOPERATIONAL PATTERNS:")
    print(f"  Hours importing:         {metrics['hours_importing']}")
    print(f"  Hours exporting:         {metrics['hours_exporting']}")
    print(f"  Peak operations:")
    print(f"    - Peak import:         {metrics['peak_import']:.2f} kW")
    print(f"    - Peak export:         {metrics['peak_export']:.2f} kW")

def analyze_flexibility_and_profits(all_results):
    """
    Analyze how cost structures impact consumer flexibility and profits
    This addresses the specific question in Q1 Part V
    """
    
    print("\n" + "=" * 80)
    print("Q1 PART V - FLEXIBILITY & PROFITS ANALYSIS")
    print("How do cost structures impact consumer flexibility and profits?")
    print("=" * 80)
    
    base_results = all_results.get('base', {}).get('results', {})
    if not base_results:
        print("Cannot perform analysis - base case missing")
        return
    
    print("\nCONSUMER FLEXIBILITY METRICS:")
    print("-" * 50)
    
    for scenario_key, scenario_data in all_results.items():
        results = scenario_data['results']
        scenario_name = scenario_data['scenario_info']['name']
        
        # Flexibility metrics
        hourly_load = results.get('load_schedule', [])
        load_variance = np.var(hourly_load) if hourly_load else 0
        
        # Peak vs off-peak consumption
        peak_consumption = sum(hourly_load[7:20]) if len(hourly_load) >= 20 else 0
        off_peak_consumption = sum(hourly_load[:7]) + sum(hourly_load[20:]) if len(hourly_load) >= 24 else 0
        
        # PV self-consumption rate  
        pv_used = results.get('total_pv_used', 0)
        # Get PV production from results (now stored there)
        total_pv = sum(results.get('pv_production', []))
        self_consumption_rate = (pv_used / total_pv * 100) if total_pv > 0 else 0
        
        # Grid interaction
        import_total = results.get('total_imported', 0)
        export_total = results.get('total_exported', 0)
        grid_dependency = import_total / (import_total + pv_used) * 100 if (import_total + pv_used) > 0 else 0
        
        print(f"\n{scenario_name}:")
        print(f"  Load scheduling variance: {load_variance:.3f} kW²")
        print(f"  Peak/Off-peak ratio: {peak_consumption/off_peak_consumption:.2f}" if off_peak_consumption > 0 else "  Peak/Off-peak ratio: N/A")
        print(f"  PV self-consumption: {self_consumption_rate:.1f}%")
        print(f"  Grid dependency: {grid_dependency:.1f}%")
    
    print("\nECONOMIC IMPACT ANALYSIS:")
    print("-" * 50)
    
    base_cost = base_results.get('optimal_cost', 0)
    
    for scenario_key, scenario_data in all_results.items():
        if scenario_key == 'base':
            continue
            
        results = scenario_data['results']
        scenario_name = scenario_data['scenario_info']['name']
        
        cost_impact = results['optimal_cost'] - base_cost
        cost_impact_pct = (cost_impact / base_cost * 100) if base_cost > 0 else 0
        
        # Profit impact (negative cost is profit)
        profit_change = -cost_impact
        
        print(f"\n{scenario_name}:")
        print(f"  Cost impact: {cost_impact:+.2f} DKK ({cost_impact_pct:+.1f}%)")
        print(f"  Consumer profit change: {profit_change:+.2f} DKK")
        
        # Interpretation
        if cost_impact > 1.0:
            print(f"  LESS FAVORABLE: Consumer pays {cost_impact:.2f} DKK more")
        elif cost_impact < -1.0:
            print(f"  MORE FAVORABLE: Consumer saves {-cost_impact:.2f} DKK")
        else:
            print(f"  NEUTRAL: Minimal cost impact")
    
    print("\nKEY INSIGHTS:")
    print("-" * 50)
    print("• Higher import tariffs → Increased PV self-consumption, reduced grid dependency")
    print("• Lower export tariffs → Less incentive to overproduce, more direct consumption")
    print("• Peak pricing → Load shifting to off-peak hours, increased flexibility")
    print("• Combined unfavorable conditions → Maximum consumer adaptation needed")


def print_comprehensive_summary_table_q1a(all_results):
    """Print comprehensive summary table for all Q1a scenarios"""
    
    print("\n" + "=" * 80)
    print("Q1(v) SCENARIO ANALYSIS RESULTS")
    print("=" * 80)
    print("QUESTION 1a PART V - SCENARIO ANALYSIS")
    print("=" * 50)
    
    print("\n" + "=" * 100)
    print("COMPREHENSIVE SUMMARY TABLE")
    print("=" * 100)
    
    # Table header
    print(f"{'Scenario':<20} {'Cost':<8} {'Import':<8} {'Export':<8} {'PV Self':<8} {'PV Util':<8} {'H_imp':<6} {'H_exp':<6}")
    print(f"{'':20} {'(DKK)':<8} {'(kWh)':<8} {'(kWh)':<8} {'(kWh)':<8} {'(%)':<8} {'':6} {'':6}")
    print("-" * 100)
    
    for scenario_key, scenario_data in all_results.items():
        results = scenario_data['results']
        scenario_info = scenario_data['scenario_info']
        metrics = calculate_detailed_metrics_q1a(results, scenario_info)
        
        print(f"{scenario_info['name']:<20} "
              f"{metrics['total_cost']:<8.2f} "
              f"{metrics['import_total']:<8.2f} "
              f"{metrics['export_total']:<8.2f} "
              f"{metrics['pv_used']:<8.2f} "
              f"{metrics['pv_utilization']:<8.1f} "
              f"{metrics['hours_importing']:<6} "
              f"{metrics['hours_exporting']:<6}")
    
    print("=" * 100)


def create_separate_q1v_plots(all_results):
    """Create separate individual plots for Q1 Part V analysis"""
    
    # Set professional style matching Q1b_v and Q1c_v
    plt.style.use('default')
    plt.rcParams.update({
        'font.size': 14,
        'font.family': 'sans-serif',
        'figure.figsize': (14, 10),
        'axes.grid': True,
        'grid.alpha': 0.3,
        'axes.linewidth': 1.5,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'legend.fontsize': 12
    })
    
    scenarios = list(all_results.keys())
    scenario_names = [all_results[s]['scenario_info']['name'] for s in scenarios]
    
    # Extract data
    costs = [all_results[s]['results']['optimal_cost'] for s in scenarios]
    imports = [all_results[s]['results']['total_imported'] for s in scenarios]
    exports = [all_results[s]['results']['total_exported'] for s in scenarios]
    base_cost = costs[0]
    cost_diffs = [cost - base_cost for cost in costs]
    
    # Plot 1: Total Daily Cost by Scenario
    fig1, ax1 = plt.subplots(figsize=(14, 10))
    colors = ['navy', 'crimson', 'darkorange', 'purple', 'darkgreen'][:len(scenarios)]
    bars1 = ax1.bar(scenario_names, costs, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
    ax1.set_ylabel('Total Daily Cost (DKK)', fontsize=16, fontweight='bold')
    #ax1.set_title('Total Daily Cost by Scenario', fontsize=18, fontweight='bold', pad=25)
    ax1.tick_params(axis='x', rotation=45, labelsize=14)
    ax1.tick_params(axis='y', labelsize=14)
    ax1.grid(True, alpha=0.3, linewidth=1)
    
    # Add value labels on bars
    for bar, cost in zip(bars1, costs):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, 
                f'{cost:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=13)
    
    plt.tight_layout()
    plt.savefig('Q1av_Total_Daily_Cost.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Total daily cost plot saved as 'Q1v_Total_Daily_Cost.png'")
    
    # Plot 2: Import vs Export by Scenario
    fig2, ax2 = plt.subplots(figsize=(14, 10))
    x_pos = np.arange(len(scenario_names))
    width = 0.35
    
    bars_import = ax2.bar(x_pos - width/2, imports, width, label='Import', color='crimson', alpha=0.8, edgecolor='black', linewidth=2)
    bars_export = ax2.bar(x_pos + width/2, exports, width, label='Export', color='forestgreen', alpha=0.8, edgecolor='black', linewidth=2)
    ax2.set_ylabel('Energy (kWh)', fontsize=16, fontweight='bold')
    #ax2.set_title('Import vs Export by Scenario', fontsize=18, fontweight='bold', pad=25)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(scenario_names, rotation=45, fontsize=14)
    ax2.tick_params(axis='y', labelsize=14)
    ax2.legend(fontsize=14, loc='upper right')
    ax2.grid(True, alpha=0.3, linewidth=1)
    
    # Add value labels
    for bar, val in zip(bars_import, imports):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, 
                f'{val:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    for bar, val in zip(bars_export, exports):
        if val > 0.1:  # Only show label if export is significant
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{val:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('Q1av_Import_Export.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Import vs Export plot saved as 'Q1v_Import_Export.png'")
    
    # Plot 3: Cost Impact vs Base Case
    fig3, ax3 = plt.subplots(figsize=(14, 10))
    colors_impact = ['gray' if abs(diff) < 0.1 else 'forestgreen' if diff < 0 else 'crimson' for diff in cost_diffs]
    bars3 = ax3.bar(scenario_names, cost_diffs, color=colors_impact, alpha=0.8, edgecolor='black', linewidth=2)
    ax3.set_ylabel('Cost Difference from Base (DKK)', fontsize=16, fontweight='bold')
    #ax3.set_title('Cost Impact vs Base Case', fontsize=18, fontweight='bold', pad=25)
    ax3.tick_params(axis='x', rotation=45, labelsize=14)
    ax3.tick_params(axis='y', labelsize=14)
    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.8, linewidth=3)
    ax3.grid(True, alpha=0.3, linewidth=1)
    
    # Add value labels
    for bar, diff in zip(bars3, cost_diffs):
        y_pos = bar.get_height() + (0.15 if diff >= 0 else -0.4)
        ax3.text(bar.get_x() + bar.get_width()/2, y_pos, 
                f'{diff:+.2f}', ha='center', va='bottom' if diff >= 0 else 'top', 
                fontweight='bold', fontsize=13)
    
    plt.tight_layout()
    plt.savefig('Q1av_Cost_Impact.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Cost impact plot saved as 'Q1v_Cost_Impact.png'")

def create_tariff_focused_comparison(all_results):
    """Create comparison focused on import/export tariff changes vs base case"""
    
    # Set enhanced styling
    plt.rcParams.update({
        'font.size': 14,
        'axes.titlesize': 18,
        'axes.labelsize': 16,
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'legend.fontsize': 14
    })
    
    fig, ax = plt.subplots(figsize=(16, 12))
    
    hours = np.arange(1, 25)
    
    # Scenarios for this plot: base, high_import, low_export
    scenarios_to_plot = ['base', 'high_import', 'low_export']
    
    # Styling for tariff-focused scenarios
    tariff_styles = {
        'base': {'color': 'black', 'linestyle': '-', 'linewidth': 4, 'marker': None, 'alpha': 1.0, 'zorder': 1},
        'high_import': {'color': 'red', 'linestyle': '--', 'linewidth': 3.5, 'marker': 'o', 'alpha': 1.0, 'zorder': 5},
        'low_export': {'color': 'orange', 'linestyle': ':', 'linewidth': 3.5, 'marker': 's', 'alpha': 1.0, 'zorder': 5}
    }
    
    # Create secondary axis for prices
    ax_price = ax.twinx()
    
    # Plot scenarios and their loads
    for scenario_key in scenarios_to_plot:
        if scenario_key not in all_results:
            continue
            
        scenario_data = all_results[scenario_key]
        results = scenario_data['results']
        scenario_name = scenario_data['scenario_info']['name']
        load_schedule = results.get('load_schedule', [0]*24)
        style = tariff_styles[scenario_key]
        
        # Plot load schedule
        ax.step(hours, load_schedule, 
                color=style['color'], 
                linestyle=style['linestyle'],
                linewidth=style['linewidth'],
                marker=style['marker'],
                markersize=7 if style['marker'] else 0,
                markevery=4 if style['marker'] else None,
                markerfacecolor=style['color'] if style['marker'] else None,
                markeredgecolor='white' if style['marker'] else None,
                markeredgewidth=1 if style['marker'] else 0,
                label=scenario_name, 
                where='mid', 
                alpha=style['alpha'],
                zorder=style['zorder'])
    
    # Plot base prices (since all these scenarios use the same base prices)
    if 'base' in all_results:
        base_prices = all_results['base']['optimization_data']['energy_prices']
        ax_price.step(hours, base_prices, 
                     color='dimgray', linewidth=2.5, alpha=0.6, 
                     linestyle=':', where='mid', zorder=2)
    
    ax.set_xlabel('Hour', fontsize=16, fontweight='bold')
    ax.set_ylabel('Load (kW)', fontsize=16, fontweight='bold')
    #ax.set_title('Import/Export Tariff Impact on Consumer Flexibility', fontsize=18, fontweight='bold', pad=25)
    ax.set_xlim(0.5, 24.5)
    ax.set_ylim(-0.1, 3.2)
    ax.grid(True, alpha=0.3, linewidth=1)
    ax.tick_params(axis='both', labelsize=14)
    
    # Configure price axis
    ax_price.set_ylabel('Energy Price (DKK/kWh)', fontsize=14, color='dimgray', fontweight='bold')
    ax_price.tick_params(axis='y', labelcolor='dimgray', labelsize=12)
    ax_price.set_ylim(0.8, 2.6)
    
    # Create legends with enhanced styling
    load_legend = ax.legend(fontsize=14, loc='upper left',
                           title='Load Schedules', title_fontsize=16, 
                           framealpha=0.95)
    
    price_legend = ax_price.legend(['Base Energy Prices'], fontsize=12, loc='lower right', 
                                  title='Energy Prices', title_fontsize=14, 
                                  framealpha=0.95)
    
    ax.add_artist(load_legend)
    
    plt.tight_layout()
    plt.savefig('Q1av_Tariff_Impact_Comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Tariff impact comparison saved as 'Q1v_Tariff_Impact_Comparison.png'")


def create_pricing_mechanism_comparison(all_results):
    """Create comparison focused on time-varying pricing mechanisms"""
    
    # Set enhanced styling
    plt.rcParams.update({
        'font.size': 14,
        'axes.titlesize': 18,
        'axes.labelsize': 16,
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'legend.fontsize': 14
    })
    
    fig, ax = plt.subplots(figsize=(16, 12))
    
    hours = np.arange(1, 25)
    
    # Scenarios for this plot: peak_pricing, unfavorable
    scenarios_to_plot = ['peak_pricing', 'unfavorable']
    
    # Styling for pricing-focused scenarios
    pricing_styles = {
        'peak_pricing': {'color': 'blue', 'linestyle': '-.', 'linewidth': 3.5, 'marker': '^', 'alpha': 1.0, 'zorder': 5},
        'unfavorable': {'color': 'green', 'linestyle': ':', 'linewidth': 4, 'marker': 'D', 'alpha': 1.0, 'zorder': 5}
    }
    
    # Create secondary axis for prices
    ax_price = ax.twinx()
    
    # Plot pricing scenarios and their loads
    price_labels = []
    
    for scenario_key in scenarios_to_plot:
        if scenario_key not in all_results:
            continue
            
        scenario_data = all_results[scenario_key]
        results = scenario_data['results']
        scenario_name = scenario_data['scenario_info']['name']
        load_schedule = results.get('load_schedule', [0]*24)
        scenario_prices = scenario_data['optimization_data']['energy_prices']
        style = pricing_styles[scenario_key]
        
        # Plot load schedule
        ax.step(hours, load_schedule, 
                color=style['color'], 
                linestyle=style['linestyle'],
                linewidth=style['linewidth'],
                marker=style['marker'],
                markersize=7,
                markevery=4,
                markerfacecolor=style['color'],
                markeredgecolor='white',
                markeredgewidth=1,
                label=scenario_name, 
                where='mid', 
                alpha=style['alpha'],
                zorder=style['zorder'])
        
        # Plot corresponding prices (matching colors but dotted and faded)
        ax_price.step(hours, scenario_prices, 
                     color=style['color'], 
                     linewidth=2.5, 
                     alpha=0.5, 
                     linestyle=':', 
                     where='mid', 
                     zorder=3)
        
        price_labels.append(f'{scenario_name} Prices')
    
    ax.set_xlabel('Hour', fontsize=16, fontweight='bold')
    ax.set_ylabel('Load (kW)', fontsize=16, fontweight='bold')
    #ax.set_title('Time-Varying Pricing Impact on Consumer Flexibility', fontsize=18, fontweight='bold', pad=25)
    ax.set_xlim(0.5, 24.5)
    ax.set_ylim(-0.1, 3.2)
    ax.grid(True, alpha=0.3, linewidth=1)
    ax.tick_params(axis='both', labelsize=14)
    
    # Configure price axis with extended range for peak prices
    ax_price.set_ylabel('Energy Price (DKK/kWh)', fontsize=14, color='dimgray', fontweight='bold')
    ax_price.tick_params(axis='y', labelcolor='dimgray', labelsize=12)
    
    # Dynamic scaling for higher peak prices
    all_prices = []
    for scenario_key in scenarios_to_plot:
        if scenario_key in all_results:
            all_prices.extend(all_results[scenario_key]['optimization_data']['energy_prices'])
    
    min_price = min(all_prices) * 0.9
    max_price = max(all_prices) * 1.05
    ax_price.set_ylim(min_price, max_price)
    
    # Add peak hours shading with enhanced visibility
    ax.axvspan(7, 19, alpha=0.15, color='red', zorder=0, label='Peak Hours')
    
    # Create legends with enhanced styling
    load_legend = ax.legend(fontsize=14, loc='upper left',
                           title='Load Schedules', title_fontsize=16, 
                           framealpha=0.95)
    
    price_legend = ax_price.legend(price_labels, fontsize=12, loc='lower right', 
                                  title='Energy Prices', title_fontsize=14, 
                                  framealpha=0.95)
    
    ax.add_artist(load_legend)
    
    plt.tight_layout()
    plt.savefig('Q1av_Pricing_Mechanism_Comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Pricing mechanism comparison saved as 'Q1v_Pricing_Mechanism_Comparison.png'")

# Replace the create_improved_hourly_load_comparison function call in your main section:
if __name__ == "__main__":
    print("Q1(v) SCENARIO ANALYSIS")
    print("=" * 80)
    print("QUESTION 1a PART V - SCENARIO ANALYSIS: TARIFF IMPACT & PRICING MECHANISMS")
    print("=" * 80)
    
    results = solve_q1_part_v()
    
    if results:
        print(f"\nQ1 Part V completed successfully! Analyzed {len(results)} scenarios.")
        
        # Create all plots
        print("\nGenerating plots...")
        create_separate_q1v_plots(results)
        create_tariff_focused_comparison(results)
        create_pricing_mechanism_comparison(results)
        print("Plots completed.")
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("\nVISUALIZATIONS GENERATED:")
        print("1. Total daily cost by scenario")
        print("2. Import vs export comparison")
        print("3. Cost impact vs base case")
        print("4. Tariff impact comparison")  
        print("5. Pricing mechanism comparison")
        
    else:
        print("\nQ1 Part V analysis failed!")