"""
Question 1 Part V - Consumer Energy Flexibility Analysis
Final version with exactly what you want:

PART 1: 4 W-Variation Scenarios (w = 0.5, 1.5, 2.5, 5.0)
- Plot 1: Load profiles comparison with energy prices
- Plot 2: Cost breakdown (energy cost, energy revenue, discomfort cost)
- Plot 3: Daily energy balance summary (import, export, consumption, PV used)
- Plot 4: Consumer under-c    # Create 4 individual consumer plots
    for i, consumer in enumerate(consumer_results):
        print(f"📊 Creating Consumer Plot {i+1}: {consumer['name']}...")
        create_individual_consumer_plot(consumer, i+1, system_params)
    
    # Create combined cost breakdown
    print("📊 Creating Consumer Cost Breakdown...")
    create_consumer_cost_breakdown(consumer_results, system_params)on patterns

PART 2: 4 Consumer Load Profile Scenarios (at w = 1.5)
- 4 individual plots: Tech Enthusiast, Work from Home, Traditional Family, Senior Fixed
- 1 combined cost breakdown plot

Total: 9 plots exactly as requested
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import copy

# Configure matplotlib for larger fonts (better for reports)
plt.rcParams.update({
    'font.size': 14,           # Base font size
    'axes.titlesize': 18,      # Title font size
    'axes.labelsize': 16,      # Axis label font size
    'xtick.labelsize': 14,     # X tick label font size
    'ytick.labelsize': 14,     # Y tick label font size
    'legend.fontsize': 14,     # Legend font size
    'figure.titlesize': 20,    # Figure title font size
    'lines.linewidth': 3,      # Line width
    'lines.markersize': 8      # Marker size
})

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data_ops.data_loader import DataLoader
from data_ops.data_processor import DataProcessor
from opt_model.opt_model_Q1b import ConsumerFlexibilityModelQ1b

def load_system_parameters():
    """Load energy prices and system parameters from data files"""
    project_root = Path(__file__).parent.parent.parent
    loader = DataLoader(base_path=str(project_root / "data"))
    
    # Load base data to get energy prices
    base_data = loader.load_data("question_1b")
    
    # Extract energy prices from bus_params
    energy_prices = base_data['bus_params'][0]['energy_price_DKK_per_kWh']
    import_tariff = base_data['bus_params'][0]['import_tariff_DKK/kWh']
    export_tariff = base_data['bus_params'][0]['export_tariff_DKK/kWh']
    
    print(f"✅ Loaded energy prices: {len(energy_prices)} hourly values")
    print(f"✅ Import tariff: {import_tariff} DKK/kWh")
    print(f"✅ Export tariff: {export_tariff} DKK/kWh")
    
    return {
        'energy_prices': energy_prices,
        'import_tariff': import_tariff,
        'export_tariff': export_tariff
    }

def print_solution_summary(scenario_results, consumer_results, system_params):
    """Print comprehensive summary of primal and dual variables for all scenarios"""
    
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE SOLUTION SUMMARY - Q1.b.v")
    print("="*80)
    
    # W-Variation Analysis Summary
    print("\n🔍 PART 1: W-VARIATION ANALYSIS")
    print("-" * 50)
    
    for i, scenario in enumerate(scenario_results):
        results = scenario['results']
        w = scenario['weight']
        
        print(f"\n📈 Scenario {i+1}: w = {w} DKK/kWh")
        print(f"   Total Cost: {results['optimal_cost']:.2f} DKK")
        print(f"   Energy Cost: {results['energy_cost']:.2f} DKK")
        print(f"   Discomfort Cost: {results['discomfort_penalty']:.2f} DKK")
        
        # Key Primal Variables
        print("   🔵 Key Primal Variables:")
        print(f"     • Total Load: {results['total_energy_consumed']:.1f} kWh")
        print(f"     • Grid Import: {results['total_imported']:.1f} kWh")
        print(f"     • Grid Export: {results['total_exported']:.1f} kWh")
        print(f"     • Over-consumption: {results['total_dev_plus']:.1f} kWh")
        print(f"     • Under-consumption: {results['total_dev_minus']:.1f} kWh")
        
        # Key Dual Variables (Shadow Prices)
        print("   🔴 Key Dual Variables (Shadow Prices):")
        print(f"     • Avg Energy Balance Dual: {results['avg_dual_energy']:.3f} DKK/kWh")
        print(f"     • Avg Deviation Balance Dual: {results['avg_dual_deviation']:.3f} DKK/kWh")
        print(f"     • Peak Import Dual: {results['peak_dual_import']:.3f} DKK/kWh")
        print(f"     • Peak Export Dual: {results['peak_dual_export']:.3f} DKK/kWh")
        
        # Flexibility Metrics
        ref_total = sum(results['reference_load'])
        flexibility_used = (results['total_dev_plus'] + results['total_dev_minus'])
        flexibility_pct = (flexibility_used / ref_total) * 100
        print(f"   📊 Flexibility: {flexibility_pct:.1f}% of reference load utilized")
        
        # Profit Analysis (negative cost = profit from grid arbitrage)
        if results['energy_cost'] < 0:
            profit = -results['energy_cost']
            print(f"   💰 Grid Arbitrage Profit: {profit:.2f} DKK")
    
    # Consumer Profile Analysis Summary
    print(f"\n🔍 PART 2: CONSUMER PROFILE ANALYSIS")
    print("-" * 50)
    
    for i, consumer in enumerate(consumer_results):
        results = consumer['results']
        name = consumer['name']
        
        print(f"\n👤 Consumer {i+1}: {name}")
        print(f"   Total Cost: {results['optimal_cost']:.2f} DKK")
        print(f"   Energy Cost: {results['energy_cost']:.2f} DKK")
        print(f"   Discomfort Cost: {results['discomfort_penalty']:.2f} DKK")
        
        # Key Primal Variables
        print("   🔵 Key Primal Variables:")
        print(f"     • Total Load: {results['total_energy_consumed']:.1f} kWh")
        print(f"     • Grid Import: {results['total_imported']:.1f} kWh") 
        print(f"     • Grid Export: {results['total_exported']:.1f} kWh")
        print(f"     • Over-consumption: {results['total_dev_plus']:.1f} kWh")
        print(f"     • Under-consumption: {results['total_dev_minus']:.1f} kWh")
        
        # Key Dual Variables
        print("   🔴 Key Dual Variables (Shadow Prices):")
        print(f"     • Avg Energy Balance Dual: {results['avg_dual_energy']:.3f} DKK/kWh")
        print(f"     • Avg Deviation Balance Dual: {results['avg_dual_deviation']:.3f} DKK/kWh")
        
        # Flexibility and Profit Analysis
        ref_total = sum(results['reference_load'])
        flexibility_used = (results['total_dev_plus'] + results['total_dev_minus'])
        flexibility_pct = (flexibility_used / ref_total) * 100
        print(f"   📊 Flexibility: {flexibility_pct:.1f}% of reference load utilized")
        
        if results['energy_cost'] < 0:
            profit = -results['energy_cost']
            print(f"   💰 Grid Arbitrage Profit: {profit:.2f} DKK")
    
    # Comparative Analysis
    print(f"\n🔍 COMPARATIVE INSIGHTS")
    print("-" * 50)
    
    # W-variation insights
    w_costs = [s['results']['optimal_cost'] for s in scenario_results]
    w_flexibility = []
    for s in scenario_results:
        r = s['results']
        ref_total = sum(r['reference_load'])
        flex_used = r['total_dev_plus'] + r['total_dev_minus']
        w_flexibility.append((flex_used / ref_total) * 100)
    
    print("📈 W-Variation Impact:")
    print(f"   • Cost Range: {min(w_costs):.2f} - {max(w_costs):.2f} DKK")
    print(f"   • Flexibility Range: {min(w_flexibility):.1f}% - {max(w_flexibility):.1f}%")
    print(f"   • Trend: Higher w → Lower flexibility, Higher total cost")
    
    # Consumer insights
    consumer_costs = [c['results']['optimal_cost'] for c in consumer_results]
    consumer_names = [c['name'] for c in consumer_results]
    
    print("👥 Consumer Profile Impact:")
    print(f"   • Cost Range: {min(consumer_costs):.2f} - {max(consumer_costs):.2f} DKK")
    
    # Find most/least flexible consumers
    consumer_flex = []
    for c in consumer_results:
        r = c['results']
        ref_total = sum(r['reference_load'])
        flex_used = r['total_dev_plus'] + r['total_dev_minus']
        consumer_flex.append((flex_used / ref_total) * 100)
    
    most_flexible_idx = consumer_flex.index(max(consumer_flex))
    least_flexible_idx = consumer_flex.index(min(consumer_flex))
    
    print(f"   • Most Flexible: {consumer_names[most_flexible_idx]} ({consumer_flex[most_flexible_idx]:.1f}%)")
    print(f"   • Least Flexible: {consumer_names[least_flexible_idx]} ({consumer_flex[least_flexible_idx]:.1f}%)")
    
    print("="*80)

def get_consumer_configurations():
    """Define consumer load profiles based on realistic usage patterns"""
    consumer_configs = [
        {
            'name': 'Tech Enthusiast',
            'description': 'Late evening peak (19-22h), moderate flexibility',
            'load_multipliers': [0.5, 0.4, 0.3, 0.3, 0.3, 0.4, 0.6, 0.8, 1.2, 1.4, 1.3, 1.2, 
                               1.1, 1.0, 1.1, 1.3, 1.5, 1.8, 2.2, 2.5, 2.3, 1.8, 1.2, 0.8]
        },
        {
            'name': 'Work from Home',
            'description': 'Flat daytime consumption, high flexibility',
            'load_multipliers': [0.6, 0.5, 0.4, 0.4, 0.5, 0.7, 1.0, 1.2, 1.4, 1.3, 1.2, 1.1, 
                               1.0, 1.1, 1.2, 1.3, 1.4, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7]
        },
        {
            'name': 'Traditional Family',
            'description': 'Dual peaks (morning/evening), medium flexibility',
            'load_multipliers': [0.4, 0.3, 0.3, 0.3, 0.4, 0.8, 1.5, 2.0, 1.8, 1.2, 1.0, 0.9, 
                               0.8, 0.9, 1.0, 1.2, 1.4, 1.8, 2.2, 2.0, 1.6, 1.2, 0.8, 0.6]
        },
        {
            'name': 'Senior Fixed Schedule',
            'description': 'Fixed routine, minimal flexibility',
            'load_multipliers': [0.5, 0.4, 0.4, 0.4, 0.5, 0.8, 1.2, 1.5, 1.3, 1.1, 1.0, 1.0, 
                               1.1, 1.2, 1.1, 1.0, 0.9, 1.0, 1.2, 1.4, 1.2, 1.0, 0.8, 0.6]
        }
    ]
    
    print(f"✅ Loaded {len(consumer_configs)} consumer configurations")
    for config in consumer_configs:
        print(f"   - {config['name']}: {config['description']}")
    
    return consumer_configs

def solve_w_variation_scenarios():
    """Solve the 4 w-variation scenarios: 0.5, 1.5, 2.5, 5.0"""
    print("🔄 Starting W-Variation Analysis (4 scenarios)...")
    
    # Load data
    project_root = Path(__file__).parent.parent.parent
    loader = DataLoader(base_path=str(project_root / "data"))
    base_raw_data = loader.load_data("question_1b")
    
    processor = DataProcessor()
    
    # Define w values as requested
    w_values = [0.5, 1.5, 2.5, 5.0]
    scenario_results = []
    
    for w in w_values:
        print(f"\n📊 Solving for w = {w} DKK/kWh...")
        
        # Process data for this w value
        optimization_data = processor.process_for_optimization_q1b(
            copy.deepcopy(base_raw_data), w
        )
        
        # Solve optimization
        model = ConsumerFlexibilityModelQ1b(optimization_data)
        results = model.solve()
        
        if results:
            # Calculate flexibility percentage
            reference_sum = sum(results['reference_load'])
            deviation_sum = sum(abs(actual - ref) for actual, ref in 
                              zip(results['load_schedule'], results['reference_load']))
            flexibility_pct = (deviation_sum / reference_sum) * 100
            
            scenario_results.append({
                'name': f'w = {w}',
                'weight': w,
                'results': results,
                'flexibility_pct': flexibility_pct
            })
            
            print(f"✅ Solution found: Total Cost = {results['optimal_cost']:.2f} DKK")
            print(f"   Energy Cost = {results['energy_cost']:.2f} DKK")
            print(f"   Discomfort Cost = {results['discomfort_penalty']:.2f} DKK")
            print(f"   Flexibility = {flexibility_pct:.1f}%")
            
            # Detailed Primal and Dual Variable Reporting
            print(f"\n🔵 PRIMAL VARIABLES (w = {w} DKK/kWh):")
            print(f"   • Total Load: {results['total_energy_consumed']:.2f} kWh")
            print(f"   • Grid Import: {results['total_imported']:.2f} kWh")
            print(f"   • Grid Export: {results['total_exported']:.2f} kWh")
            print(f"   • PV Used: {results['total_pv_used']:.2f} kWh")
            print(f"   • Over-consumption: {results['total_dev_plus']:.2f} kWh")
            print(f"   • Under-consumption: {results['total_dev_minus']:.2f} kWh")
            
            print(f"\n🔴 DUAL VARIABLES (Shadow Prices, w = {w} DKK/kWh):")
            print(f"   • Avg Energy Balance Dual: {results['avg_dual_energy']:.4f} DKK/kWh")
            print(f"   • Avg Deviation Balance Dual: {results['avg_dual_deviation']:.4f} DKK/kWh")
            print(f"   • Peak Import Dual: {results['peak_dual_import']:.4f} DKK/kWh")
            print(f"   • Peak Export Dual: {results['peak_dual_export']:.4f} DKK/kWh")
            
            # Economic interpretation
            if results['avg_dual_energy'] != 0:
                print(f"   📊 Energy Balance: Shadow price = {results['avg_dual_energy']:.4f}")
                print(f"      → Marginal value of relaxing energy balance constraints")
            if results['avg_dual_deviation'] != 0:
                print(f"   📊 Deviation Balance: Shadow price = {results['avg_dual_deviation']:.4f}")
                print(f"      → Marginal cost of allowing more flexibility deviations")
        else:
            print(f"❌ No solution found for w = {w}")
    
    return scenario_results

def create_w_variation_plots(scenario_results, system_params):
    """Create the 4 plots for w-variation analysis"""
    
    # Plot 1: Load profiles comparison with energy prices
    print("📊 Creating Plot 1: Load Profiles with Energy Prices...")
    create_load_profiles_comparison(scenario_results, system_params)
    
    # Plot 2: Cost breakdown
    print("📊 Creating Plot 2: Cost Breakdown...")
    create_cost_breakdown_analysis(scenario_results, system_params)
    
    # Plot 3: Daily energy balance summary
    print("📊 Creating Plot 3: Daily Energy Balance Summary...")
    create_energy_balance_summary(scenario_results, system_params)
    
    # Plot 4: Consumer under-consumption patterns
    print("📊 Creating Plot 4: Under-Consumption Patterns...")
    create_under_consumption_patterns(scenario_results, system_params)

def create_load_profiles_comparison(scenario_results, system_params):
    """Plot 1: Load profiles for all 4 scenarios with energy prices"""
    fig, ax1 = plt.subplots(figsize=(16, 10))
    
    hours = np.arange(1, 25)
    # Load energy prices from system parameters
    energy_prices = system_params['energy_prices']
    
    # Plot reference load as black dotted line
    if scenario_results:
        reference_load = scenario_results[0]['results']['reference_load']
        ax1.step(hours, reference_load, where='mid', linestyle='--', color='black', 
                linewidth=3, label='Reference Load', alpha=0.8)
    
    # Plot load profiles for each scenario
    colors = ['red', 'blue', 'green', 'orange']
    for i, scenario in enumerate(scenario_results):
        results = scenario['results']
        ax1.step(hours, results['load_schedule'], where='mid', color=colors[i], linewidth=2.5, 
                label=f'Load (w={scenario["weight"]})', alpha=0.9)
    
    # Secondary y-axis for energy prices
    ax2 = ax1.twinx()
    ax2.step(hours, energy_prices, where='mid', color='purple', linewidth=3, 
            linestyle=':', label='Energy Price', alpha=0.8)
    ax2.set_ylabel('Energy Price (DKK/kWh)', fontsize=18, color='purple', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='purple', labelsize=14)
    
    # Formatting with larger fonts
    ax1.set_xlabel('Hour of Day', fontsize=18, fontweight='bold')
    ax1.set_ylabel('Load Consumption (kWh)', fontsize=18, fontweight='bold')
    ax1.set_xlim(0.5, 24.5)
    ax1.set_xticks(range(1, 25, 2))
    ax1.tick_params(labelsize=14)
    ax1.grid(True, alpha=0.3)
    
    plt.title('Load Profiles Comparison with Energy Prices', fontsize=22, fontweight='bold', pad=20)
    
    # Combined legend with larger font
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', framealpha=0.9, fontsize=16)
    
    plt.tight_layout()
    plt.savefig('Q1b_v_Load_Profiles_Comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_cost_breakdown_analysis(scenario_results, system_params):
    """Plot 2: Cost breakdown with energy cost, revenue, and discomfort"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    scenarios = [s['name'] for s in scenario_results]
    energy_prices = system_params['energy_prices']
    import_tariff = system_params['import_tariff']
    export_tariff = system_params['export_tariff']
    
    # Calculate cost components
    energy_costs = []
    energy_revenues = []
    discomfort_costs = []
    
    for scenario in scenario_results:
        results = scenario['results']
        
        # Energy cost (imports)
        energy_cost = sum(
            (energy_prices[t] + import_tariff) * imp
            for t, imp in enumerate(results['import_schedule'])
        )
        
        # Energy revenue (exports)
        energy_revenue = sum(
            (energy_prices[t] - export_tariff) * exp
            for t, exp in enumerate(results['export_schedule'])
        )
        
        energy_costs.append(energy_cost)
        energy_revenues.append(energy_revenue)  
        discomfort_costs.append(results['discomfort_penalty'])
    
    x = np.arange(len(scenarios))
    width = 0.25
    
    # Create grouped bars
    bars1 = ax.bar(x - width, energy_costs, width, label='Energy Cost', color='lightcoral', alpha=0.8)
    bars2 = ax.bar(x, [-rev for rev in energy_revenues], width, label='Energy Revenue', color='lightgreen', alpha=0.8)
    bars3 = ax.bar(x + width, discomfort_costs, width, label='Discomfort Cost', color='lightblue', alpha=0.8)
    
    # Add value labels on bars with larger font
    for i, (e_cost, e_rev, d_cost) in enumerate(zip(energy_costs, energy_revenues, discomfort_costs)):
        ax.text(i - width, e_cost + 0.5, f'{e_cost:.1f}', ha='center', va='bottom', fontsize=14, fontweight='bold')
        ax.text(i, -e_rev - 0.5, f'{e_rev:.1f}', ha='center', va='top', fontsize=14, fontweight='bold')
        ax.text(i + width, d_cost + 0.5, f'{d_cost:.1f}', ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax.set_xlabel('Scenarios', fontsize=18, fontweight='bold')
    ax.set_ylabel('Cost/Revenue (DKK)', fontsize=18, fontweight='bold')
    ax.set_title('Cost Breakdown Analysis: Energy vs Discomfort', fontsize=22, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=16, fontweight='bold')
    ax.tick_params(labelsize=14)
    ax.legend(fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('Q1b_v_Cost_Breakdown_Analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_energy_balance_summary(scenario_results, system_params):
    """Plot 3: Daily energy balance with import, export, consumption, and PV used"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    scenarios = [s['name'] for s in scenario_results]
    
    # Calculate energy balance components
    imports = [sum(s['results']['import_schedule']) for s in scenario_results]
    exports = [sum(s['results']['export_schedule']) for s in scenario_results]
    consumption = [sum(s['results']['load_schedule']) for s in scenario_results]
    pv_used = [sum(s['results']['pv_schedule']) for s in scenario_results]
    
    x = np.arange(len(scenarios))
    width = 0.2
    
    # Create grouped bars
    bars1 = ax.bar(x - 1.5*width, imports, width, label='Grid Import', color='red', alpha=0.8)
    bars2 = ax.bar(x - 0.5*width, exports, width, label='Grid Export', color='green', alpha=0.8)
    bars3 = ax.bar(x + 0.5*width, consumption, width, label='Consumption', color='blue', alpha=0.8)
    bars4 = ax.bar(x + 1.5*width, pv_used, width, label='PV Used', color='gold', alpha=0.8)

    # Add value labels on bars
    for i, (imp, exp, cons, pv) in enumerate(zip(imports, exports, consumption, pv_used)):
        ax.text(i - 1.5*width, imp + 0.5, f'{imp:.1f}', ha='center', va='bottom', fontsize=14, fontweight='bold')
        ax.text(i - 0.5*width, exp + 0.5, f'{exp:.1f}', ha='center', va='bottom', fontsize=14, fontweight='bold')
        ax.text(i + 0.5*width, cons + 0.5, f'{cons:.1f}', ha='center', va='bottom', fontsize=14, fontweight='bold')
        ax.text(i + 1.5*width, pv + 0.5, f'{pv:.1f}', ha='center', va='bottom', fontsize=14, fontweight='bold')

    ax.set_xlabel('Scenarios', fontsize=18, fontweight='bold')
    ax.set_ylabel('Energy (kWh)', fontsize=18, fontweight='bold')
    ax.set_title('Daily Energy Balance Summary', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=16, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('Q1b_v_Energy_Balance_Summary.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_under_consumption_patterns(scenario_results, system_params):
    """Plot 4: Consumer under-consumption patterns - single plot with different colors"""
    fig, ax = plt.subplots(figsize=(16, 8))
    
    hours = np.arange(1, 25)
    colors = ['red', 'blue', 'green', 'orange']
    
    # Plot under-consumption for each scenario
    for i, scenario in enumerate(scenario_results):
        results = scenario['results']
        under_consumption = results['dev_minus_schedule']
        
        # Create bar plot for under-consumption
        ax.bar(hours + i*0.2 - 0.3, under_consumption, width=0.2, 
               color=colors[i], alpha=0.7, label=f'{scenario["name"]}')
    
    ax.set_title('Consumer Under-Consumption Patterns by Scenario', fontsize=22, fontweight='bold', pad=20)
    ax.set_xlabel('Hour of Day', fontsize=18, fontweight='bold')
    ax.set_ylabel('Under-consumption (kWh)', fontsize=18, fontweight='bold')
    ax.set_xlim(0.5, 24.5)
    ax.set_xticks(range(1, 25, 2))
    ax.tick_params(labelsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=16)
    
    plt.tight_layout()
    plt.savefig('Q1b_v_Under_Consumption_Patterns.png', dpi=300, bbox_inches='tight')
    plt.show()

def solve_consumer_load_scenarios():
    """Solve the 4 consumer load profile scenarios at w=1.5"""
    print("\n🔄 Starting Consumer Load Profile Analysis (4 consumer types)...")
    
    # Load data
    project_root = Path(__file__).parent.parent.parent
    loader = DataLoader(base_path=str(project_root / "data"))
    
    processor = DataProcessor()
    scenario_results = []
    fixed_w = 1.5  # Fixed w value for consumer comparison
    
    # Load consumer configurations
    consumer_configs = get_consumer_configurations()
    
    for consumer_config in consumer_configs:
        consumer_type = consumer_config['name']
        load_multipliers = consumer_config['load_multipliers']
        print(f"\n👤 Analyzing {consumer_type}...")
        
        try:
            # Load base data
            base_raw_data = loader.load_data("question_1b")
            
            # Modify the reference load based on consumer type
            base_reference_ratios = base_raw_data['usage_preferences'][0]['load_preferences'][0]['hourly_profile_ratio']
            modified_ratios = [ratio * mult for ratio, mult in zip(base_reference_ratios, load_multipliers)]
            
            # Create modified data for this consumer type
            modified_data = copy.deepcopy(base_raw_data)
            modified_data['usage_preferences'][0]['load_preferences'][0]['hourly_profile_ratio'] = modified_ratios
            
            # Process data for this consumer profile
            optimization_data = processor.process_for_optimization_q1b(modified_data, fixed_w)
            
            # Solve optimization
            model = ConsumerFlexibilityModelQ1b(optimization_data)
            results = model.solve()
            
            if results:
                # Calculate flexibility metrics
                reference_sum = sum(results['reference_load'])
                deviation_sum = sum(abs(actual - ref) for actual, ref in 
                                  zip(results['load_schedule'], results['reference_load']))
                flexibility_pct = (deviation_sum / reference_sum) * 100
                
                scenario_results.append({
                    'name': consumer_type,
                    'weight': fixed_w,
                    'results': results,
                    'flexibility_pct': flexibility_pct
                })
                
                print(f"   Solution found: Total Cost = {results['optimal_cost']:.2f} DKK")
                print(f"   Energy Cost = {results['energy_cost']:.2f} DKK")
                print(f"   Discomfort Cost = {results['discomfort_penalty']:.2f} DKK")
                print(f"   Flexibility = {flexibility_pct:.1f}%")
                
                # Detailed Primal and Dual Variable Reporting for Consumer
                print(f"\n🔵 PRIMAL VARIABLES ({consumer_type}):")
                print(f"   • Total Load: {results['total_energy_consumed']:.2f} kWh")
                print(f"   • Grid Import: {results['total_imported']:.2f} kWh")
                print(f"   • Grid Export: {results['total_exported']:.2f} kWh")
                print(f"   • PV Used: {results['total_pv_used']:.2f} kWh")
                print(f"   • Over-consumption: {results['total_dev_plus']:.2f} kWh")
                print(f"   • Under-consumption: {results['total_dev_minus']:.2f} kWh")
                
                print(f"\n🔴 DUAL VARIABLES ({consumer_type}):")
                print(f"   • Avg Energy Balance Dual: {results['avg_dual_energy']:.4f} DKK/kWh")
                print(f"   • Avg Deviation Balance Dual: {results['avg_dual_deviation']:.4f} DKK/kWh")
                print(f"   • Peak Import Dual: {results['peak_dual_import']:.4f} DKK/kWh")
                print(f"   • Peak Export Dual: {results['peak_dual_export']:.4f} DKK/kWh")
            else:
                print(f"No solution found for {consumer_type}")
                
        except Exception as e:
            print(f"Error processing {consumer_type}: {e}")
    
    return scenario_results

def create_consumer_load_plots(consumer_results, system_params):
    """Create 4 individual consumer plots + 1 cost breakdown"""
    
    # Create 4 individual consumer plots
    for i, consumer in enumerate(consumer_results):
        print(f"📊 Creating Consumer Plot {i+1}: {consumer['name']}...")
        create_individual_consumer_plot(consumer, i+1, system_params)
    
    # Create combined cost breakdown
    print("📊 Creating Consumer Cost Breakdown...")
    create_consumer_cost_breakdown(consumer_results, system_params)

def create_individual_consumer_plot(consumer, plot_num, system_params):
    """Create individual plot for one consumer type"""
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    hours = np.arange(1, 25)
    # Load energy prices from system parameters
    energy_prices = system_params['energy_prices']
    results = consumer['results']
    
    # Plot loads using step plots
    ax1.step(hours, results['reference_load'], where='mid', linestyle='--', color='black', 
            linewidth=3, label='Reference Load', alpha=0.8)
    ax1.step(hours, results['load_schedule'], where='mid', color='blue', linewidth=3, 
            label='Actual Load', alpha=0.9)

    # Secondary y-axis for energy prices
    ax2 = ax1.twinx()
    ax2.step(hours, energy_prices, where='mid', color='red', linewidth=3, 
            linestyle=':', label='Energy Price', alpha=0.8)
    ax2.set_ylabel('Energy Price (DKK/kWh)', fontsize=18, color='red')
    ax2.tick_params(axis='y', labelcolor='red', labelsize=14)
    
    # Formatting with larger fonts
    ax1.set_xlabel('Hour of Day', fontsize=18, fontweight='bold')
    ax1.set_ylabel('Load Consumption (kWh)', fontsize=18, color='blue', fontweight='bold')
    ax1.set_xlim(0.5, 24.5)
    ax1.set_xticks(range(1, 25, 2))
    ax1.tick_params(labelsize=14)
    ax1.grid(True, alpha=0.3)
    
    plt.title(f'Load Profile: {consumer["name"]} (w={consumer["weight"]} DKK/kWh)', fontsize=20, fontweight='bold', pad=20)
    
    # Combined legend with larger font
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', framealpha=0.9, fontsize=16)
    
    plt.tight_layout()
    plt.savefig(f'Q1b_v_Consumer_{plot_num}_{consumer["name"].replace(" ", "_")}.png', 
               dpi=300, bbox_inches='tight')
    plt.show()

def create_consumer_cost_breakdown(consumer_results, system_params):
    """Create cost breakdown for all consumer types"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    consumers = [c['name'] for c in consumer_results]
    energy_prices = system_params['energy_prices']
    import_tariff = system_params['import_tariff']
    export_tariff = system_params['export_tariff']
    
    # Calculate cost components - use the actual results from optimization
    energy_costs = [c['results']['energy_cost'] for c in consumer_results]
    discomfort_costs = [c['results']['discomfort_penalty'] for c in consumer_results]
    
    # Calculate energy revenues separately (exports generate revenue)
    energy_revenues = []
    for consumer in consumer_results:
        results = consumer['results']
        # Energy revenue is from exports (positive value)
        energy_revenue = sum(
            (energy_prices[t] - export_tariff) * exp
            for t, exp in enumerate(results['export_schedule'])
        )
        energy_revenues.append(energy_revenue)
    
    x = np.arange(len(consumers))
    width = 0.25
    
    # Create grouped bars
    bars1 = ax.bar(x - width, energy_costs, width, label='Energy Cost', color='lightcoral', alpha=0.8)
    bars2 = ax.bar(x, [-rev for rev in energy_revenues], width, label='Energy Revenue', color='lightgreen', alpha=0.8)
    bars3 = ax.bar(x + width, discomfort_costs, width, label='Discomfort Cost', color='lightblue', alpha=0.8)
    
    # Add value labels on bars
    for i, (e_cost, e_rev, d_cost) in enumerate(zip(energy_costs, energy_revenues, discomfort_costs)):
        ax.text(i - width, e_cost + 0.5, f'{e_cost:.1f}', ha='center', va='bottom', fontsize=14, fontweight='bold')
        ax.text(i, -e_rev - 0.5, f'{e_rev:.1f}', ha='center', va='top', fontsize=14, fontweight='bold')
        ax.text(i + width, d_cost + 0.5, f'{d_cost:.1f}', ha='center', va='bottom', fontsize=14, fontweight='bold')

    ax.set_xlabel('Consumer Types', fontsize=18, fontweight='bold')
    ax.set_ylabel('Cost/Revenue (DKK)', fontsize=18, fontweight='bold')
    ax.set_title('Consumer Cost Breakdown: Energy vs Discomfort', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(consumers, rotation=45, ha='right', fontsize=16, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('Q1b_v_Consumer_Cost_Breakdown.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Main execution function"""
    print(" Q1b.v - Final Analysis: Exactly What You Want!")
    print("=" * 60)
    
    try:
        # Load system parameters from data files
        print("🔧 Loading System Parameters...")
        system_params = load_system_parameters()
        
        # PART 1: W-Variation Analysis (4 scenarios, 4 plots)
        print("\nPART 1: W-Variation Analysis")
        print("-" * 40)
        w_results = solve_w_variation_scenarios()
        
        if w_results:
            create_w_variation_plots(w_results, system_params)
            print("✅ Part 1 Complete: 4 W-variation plots created!")
        
        # PART 2: Consumer Load Profile Analysis (4 consumers, 5 plots)
        print("\nPART 2: Consumer Load Profile Analysis")
        print("-" * 40)
        consumer_results = solve_consumer_load_scenarios()
        
        if consumer_results:
            create_consumer_load_plots(consumer_results, system_params)
            print("✅ Part 2 Complete: 5 Consumer profile plots created!")
        
        # Print comprehensive solution summary
        print_solution_summary(w_results, consumer_results, system_params)
        
        print("\n" + "=" * 60)
        print("🎉 ANALYSIS COMPLETE!")
        print("=" * 60)
        print(" Total Plots Generated: 9")
        print("   PART 1 (W-variation): 4 plots")
        print("     - Load profiles comparison")
        print("     - Cost breakdown analysis")
        print("     - Energy balance summary")
        print("     - Under-consumption patterns")
        print("   PART 2 (Consumer types): 5 plots")
        print("     - 4 individual consumer plots")
        print("     - 1 consumer cost breakdown")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()