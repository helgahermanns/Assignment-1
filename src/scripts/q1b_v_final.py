"""
Question 1 Part V - Consumer Energy Flexibility Analysis
Final version with exactly what you want:

PART 1: 4 W-Variation Scenarios (w = 0.5, 1.5, 2.5, 5.0)
- Plot 1: Load profiles comparison with energy prices
- Plot 2: Cost breakdown (energy cost, energy revenue, discomfort cost)
- Plot 3: Daily energy balance summary (import, export, consumption, PV used)
- Plot 4: Consumer under-consumption patterns

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

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data_ops.data_loader import DataLoader
from data_ops.data_processor import DataProcessor
from opt_model.opt_model_Q1b import ConsumerFlexibilityModelQ1b

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
        else:
            print(f"❌ No solution found for w = {w}")
    
    return scenario_results

def create_w_variation_plots(scenario_results):
    """Create the 4 plots for w-variation analysis"""
    
    # Plot 1: Load profiles comparison with energy prices
    print("📊 Creating Plot 1: Load Profiles with Energy Prices...")
    create_load_profiles_comparison(scenario_results)
    
    # Plot 2: Cost breakdown
    print("📊 Creating Plot 2: Cost Breakdown...")
    create_cost_breakdown_analysis(scenario_results)
    
    # Plot 3: Daily energy balance summary
    print("📊 Creating Plot 3: Daily Energy Balance Summary...")
    create_energy_balance_summary(scenario_results)
    
    # Plot 4: Consumer under-consumption patterns
    print("📊 Creating Plot 4: Under-Consumption Patterns...")
    create_under_consumption_patterns(scenario_results)

def create_load_profiles_comparison(scenario_results):
    """Plot 1: Load profiles for all 4 scenarios with energy prices"""
    fig, ax1 = plt.subplots(figsize=(16, 10))
    
    hours = np.arange(1, 25)
    # Actual energy prices from bus_params.json
    energy_prices = [1.1, 1.05, 1.0, 0.9, 0.85, 1.01, 1.05, 1.2, 1.4, 1.6, 1.5, 1.1, 
                    1.05, 1.0, 0.95, 1.0, 1.2, 1.5, 2.1, 2.5, 2.2, 1.8, 1.4, 1.2]
    
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
                label=f'Actual Load (w={scenario["weight"]})', alpha=0.9)
    
    # Secondary y-axis for energy prices
    ax2 = ax1.twinx()
    ax2.step(hours, energy_prices, where='mid', color='purple', linewidth=2, 
            linestyle=':', label='Energy Price', alpha=0.8)
    ax2.set_ylabel('Energy Price (DKK/kWh)', fontsize=12, color='purple')
    ax2.tick_params(axis='y', labelcolor='purple')
    
    # Formatting
    ax1.set_xlabel('Hour of Day', fontsize=12)
    ax1.set_ylabel('Load Consumption (kWh)', fontsize=12)
    ax1.set_xlim(0.5, 24.5)
    ax1.set_xticks(range(1, 25, 2))
    ax1.grid(True, alpha=0.3)
    
    plt.title('Load Profiles Comparison with Energy Prices', fontsize=16, fontweight='bold')
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig('Q1b_v_Load_Profiles_Comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_cost_breakdown_analysis(scenario_results):
    """Plot 2: Cost breakdown with energy cost, revenue, and discomfort"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    scenarios = [s['name'] for s in scenario_results]
    
    # Calculate cost components
    energy_costs = []
    energy_revenues = []
    discomfort_costs = []
    
    for scenario in scenario_results:
        results = scenario['results']
        
        # Use actual energy prices from bus_params.json
        energy_prices = [1.1, 1.05, 1.0, 0.9, 0.85, 1.01, 1.05, 1.2, 1.4, 1.6, 1.5, 1.1, 
                        1.05, 1.0, 0.95, 1.0, 1.2, 1.5, 2.1, 2.5, 2.2, 1.8, 1.4, 1.2]
        
        # Energy cost (imports)
        energy_cost = sum(
            (energy_prices[t] + 0.5) * imp  # energy_price + import_tariff
            for t, imp in enumerate(results['import_schedule'])
        )
        
        # Energy revenue (exports)
        energy_revenue = sum(
            (energy_prices[t] - 0.4) * exp  # energy_price - export_tariff
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
    
    # Add value labels on bars
    for i, (e_cost, e_rev, d_cost) in enumerate(zip(energy_costs, energy_revenues, discomfort_costs)):
        ax.text(i - width, e_cost + 0.5, f'{e_cost:.1f}', ha='center', va='bottom', fontsize=10)
        ax.text(i, -e_rev - 0.5, f'{e_rev:.1f}', ha='center', va='top', fontsize=10)
        ax.text(i + width, d_cost + 0.5, f'{d_cost:.1f}', ha='center', va='bottom', fontsize=10)
    
    ax.set_xlabel('Scenarios', fontsize=12)
    ax.set_ylabel('Cost/Revenue (DKK)', fontsize=12)
    ax.set_title('Cost Breakdown Analysis: Energy vs Discomfort', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('Q1b_v_Cost_Breakdown_Analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_energy_balance_summary(scenario_results):
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
        ax.text(i - 1.5*width, imp + 0.5, f'{imp:.1f}', ha='center', va='bottom', fontsize=9)
        ax.text(i - 0.5*width, exp + 0.5, f'{exp:.1f}', ha='center', va='bottom', fontsize=9)
        ax.text(i + 0.5*width, cons + 0.5, f'{cons:.1f}', ha='center', va='bottom', fontsize=9)
        ax.text(i + 1.5*width, pv + 0.5, f'{pv:.1f}', ha='center', va='bottom', fontsize=9)
    
    ax.set_xlabel('Scenarios', fontsize=12)
    ax.set_ylabel('Energy (kWh)', fontsize=12)
    ax.set_title('Daily Energy Balance Summary', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('Q1b_v_Energy_Balance_Summary.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_under_consumption_patterns(scenario_results):
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
    
    ax.set_title('Consumer Under-Consumption Patterns by Scenario', fontsize=16, fontweight='bold')
    ax.set_xlabel('Hour of Day', fontsize=12)
    ax.set_ylabel('Under-consumption (kWh)', fontsize=12)
    ax.set_xlim(0.5, 24.5)
    ax.set_xticks(range(1, 25, 2))
    ax.grid(True, alpha=0.3)
    ax.legend()
    
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
    
    # Define consumer types with different load profiles
    consumer_configs = [
        {
            'name': 'Tech Enthusiast',
            'load_multipliers': [0.5, 0.4, 0.3, 0.3, 0.3, 0.4, 0.6, 0.8, 1.2, 1.4, 1.3, 1.2, 
                               1.1, 1.0, 1.1, 1.3, 1.5, 1.8, 2.2, 2.5, 2.3, 1.8, 1.2, 0.8]
        },
        {
            'name': 'Work from Home',
            'load_multipliers': [0.6, 0.5, 0.4, 0.4, 0.5, 0.7, 1.0, 1.2, 1.4, 1.3, 1.2, 1.1, 
                               1.0, 1.1, 1.2, 1.3, 1.4, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7]
        },
        {
            'name': 'Traditional Family',
            'load_multipliers': [0.4, 0.3, 0.3, 0.3, 0.4, 0.8, 1.5, 2.0, 1.8, 1.2, 1.0, 0.9, 
                               0.8, 0.9, 1.0, 1.2, 1.4, 1.8, 2.2, 2.0, 1.6, 1.2, 0.8, 0.6]
        },
        {
            'name': 'Senior Fixed Schedule',
            'load_multipliers': [0.5, 0.4, 0.4, 0.4, 0.5, 0.8, 1.2, 1.5, 1.3, 1.1, 1.0, 1.0, 
                               1.1, 1.2, 1.1, 1.0, 0.9, 1.0, 1.2, 1.4, 1.2, 1.0, 0.8, 0.6]
        }
    ]
    
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
                
                print(f"✅ Solution found: Total Cost = {results['optimal_cost']:.2f} DKK")
                print(f"   Energy Cost = {results['energy_cost']:.2f} DKK")
                print(f"   Discomfort Cost = {results['discomfort_penalty']:.2f} DKK")
                print(f"   Flexibility = {flexibility_pct:.1f}%")
            else:
                print(f"❌ No solution found for {consumer_type}")
                
        except Exception as e:
            print(f"⚠️ Error processing {consumer_type}: {e}")
    
    return scenario_results

def create_consumer_load_plots(consumer_results):
    """Create 4 individual consumer plots + 1 cost breakdown"""
    
    # Create 4 individual consumer plots
    for i, consumer in enumerate(consumer_results):
        print(f"📊 Creating Consumer Plot {i+1}: {consumer['name']}...")
        create_individual_consumer_plot(consumer, i+1)
    
    # Create combined cost breakdown
    print("📊 Creating Consumer Cost Breakdown...")
    create_consumer_cost_breakdown(consumer_results)

def create_individual_consumer_plot(consumer, plot_num):
    """Create individual plot for one consumer type"""
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    hours = np.arange(1, 25)
    # Actual energy prices from bus_params.json
    energy_prices = [1.1, 1.05, 1.0, 0.9, 0.85, 1.01, 1.05, 1.2, 1.4, 1.6, 1.5, 1.1, 
                    1.05, 1.0, 0.95, 1.0, 1.2, 1.5, 2.1, 2.5, 2.2, 1.8, 1.4, 1.2]
    results = consumer['results']
    
    # Plot loads using step plots
    ax1.step(hours, results['reference_load'], where='mid', linestyle='--', color='black', 
            linewidth=3, label='Reference Load', alpha=0.8)
    ax1.step(hours, results['load_schedule'], where='mid', color='blue', linewidth=3, 
            label='Actual Load', alpha=0.9)
    
    # Secondary y-axis for energy prices
    ax2 = ax1.twinx()
    ax2.step(hours, energy_prices, where='mid', color='red', linewidth=2, 
            linestyle=':', label='Energy Price', alpha=0.8)
    ax2.set_ylabel('Energy Price (DKK/kWh)', fontsize=12, color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    
    # Formatting
    ax1.set_xlabel('Hour of Day', fontsize=12)
    ax1.set_ylabel('Load Consumption (kWh)', fontsize=12, color='blue')
    ax1.set_xlim(0.5, 24.5)
    ax1.set_xticks(range(1, 25, 2))
    ax1.grid(True, alpha=0.3)
    
    plt.title(f'Load Profile: {consumer["name"]} (w={consumer["weight"]} DKK/kWh)', 
             fontsize=14, fontweight='bold')
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(f'Q1b_v_Consumer_{plot_num}_{consumer["name"].replace(" ", "_")}.png', 
               dpi=300, bbox_inches='tight')
    plt.show()

def create_consumer_cost_breakdown(consumer_results):
    """Create cost breakdown for all consumer types"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    consumers = [c['name'] for c in consumer_results]
    
    # Calculate cost components - use the actual results from optimization
    energy_costs = [c['results']['energy_cost'] for c in consumer_results]
    discomfort_costs = [c['results']['discomfort_penalty'] for c in consumer_results]
    
    # Calculate energy revenues separately (exports generate revenue)
    energy_prices = [1.1, 1.05, 1.0, 0.9, 0.85, 1.01, 1.05, 1.2, 1.4, 1.6, 1.5, 1.1, 
                    1.05, 1.0, 0.95, 1.0, 1.2, 1.5, 2.1, 2.5, 2.2, 1.8, 1.4, 1.2]
    energy_revenues = []
    for consumer in consumer_results:
        results = consumer['results']
        # Energy revenue is from exports (positive value)
        energy_revenue = sum(
            (energy_prices[t] - 0.4) * exp  # energy_price - export_tariff
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
        ax.text(i - width, e_cost + 0.5, f'{e_cost:.1f}', ha='center', va='bottom', fontsize=10)
        ax.text(i, -e_rev - 0.5, f'{e_rev:.1f}', ha='center', va='top', fontsize=10)
        ax.text(i + width, d_cost + 0.5, f'{d_cost:.1f}', ha='center', va='bottom', fontsize=10)
    
    ax.set_xlabel('Consumer Types', fontsize=12)
    ax.set_ylabel('Cost/Revenue (DKK)', fontsize=12)
    ax.set_title('Consumer Cost Breakdown: Energy vs Discomfort', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(consumers, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('Q1b_v_Consumer_Cost_Breakdown.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Main execution function"""
    print("🚀 Q1b.v - Final Analysis: Exactly What You Want!")
    print("=" * 60)
    
    try:
        # PART 1: W-Variation Analysis (4 scenarios, 4 plots)
        print("PART 1: W-Variation Analysis")
        print("-" * 40)
        w_results = solve_w_variation_scenarios()
        
        if w_results:
            create_w_variation_plots(w_results)
            print("✅ Part 1 Complete: 4 W-variation plots created!")
        
        # PART 2: Consumer Load Profile Analysis (4 consumers, 5 plots)
        print("\nPART 2: Consumer Load Profile Analysis")
        print("-" * 40)
        consumer_results = solve_consumer_load_scenarios()
        
        if consumer_results:
            create_consumer_load_plots(consumer_results)
            print("✅ Part 2 Complete: 5 Consumer profile plots created!")
        
        print("\n" + "=" * 60)
        print("🎉 ANALYSIS COMPLETE!")
        print("=" * 60)
        print("📊 Total Plots Generated: 9")
        print("   PART 1 (W-variation): 4 plots")
        print("     - Load profiles comparison")
        print("     - Cost breakdown analysis")
        print("     - Energy balance summary")
        print("     - Under-consumption patterns")
        print("   PART 2 (Consumer types): 5 plots")
        print("     - 4 individual consumer plots")
        print("     - 1 consumer cost breakdown")
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()