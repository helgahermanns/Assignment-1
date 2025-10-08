"""
Question 1b Part V - Consumer Flexibility Scenario Analysis with Discomfort Costs
Dataset: question_1b (with different discomfort cost scenarios)

This script solves Q1b Part V by running multiple scenarios with different 
discomfort cost parameters to analyze flexibility behavior sensitivity.
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


def solve_q1b_part_v():
    """
    Solve Q1b Part V with discomfort cost scenario analysis.
    
    Scenarios:
    1. Low discomfort costs (flexible consumer)
    2. Medium discomfort costs (balanced consumer) 
    3. High discomfort costs (inflexible consumer)
    4. Asymmetric costs (different over/under preferences)
    
    Returns:
        dict: Results for all scenarios
    """
    
    print("QUESTION 1B PART V - DISCOMFORT COST SCENARIO ANALYSIS")
    print("Dataset: question_1b (with different flexibility preferences)")
    print("=" * 70)
    
    try:
        # Load base data from question_1b
        project_root = Path(__file__).parent.parent.parent
        loader = DataLoader(base_path=str(project_root / "data"))
        
        print("Loading base data from question_1b dataset...")
        base_raw_data = loader.load_data("question_1b")
        
        # Define scenarios for Q1b Part V - Economic Threshold Analysis
        # Teacher's VoLL range: 22-174 DKK/kWh, Critical threshold discovered: ~3.0 DKK/kWh
        scenarios = {
            "super_flexible": {
                "name": "Super Flexible",
                "discomfort_weight": 1.0,
                "description": "Extreme price-responsive consumer (w=1.0 DKK/kWh)",
                "archetype": "Complete under-consumption, maximum profit generation"
            },
            "flexible_threshold": {
                "name": "Flexible (Threshold)", 
                "discomfort_weight": 2.9,
                "description": "Just below economic threshold (w=2.9 DKK/kWh)",
                "archetype": "Strategic under-consumption during expensive hours"
            },
            "threshold_crossing": {
                "name": "Threshold Crossing",
                "discomfort_weight": 3.1,
                "description": "Just above economic threshold (w=3.1 DKK/kWh)",
                "archetype": "Mostly follows reference, minimal flexibility"
            },
            "moderate_comfort": {
                "name": "Moderate Comfort",
                "discomfort_weight": 25.0,
                "description": "Mid-range VoLL consumer (w=25 DKK/kWh)",
                "archetype": "Prioritizes comfort, follows reference profile exactly"
            },
            "high_comfort": {
                "name": "High Comfort",
                "discomfort_weight": 100.0,
                "description": "High VoLL consumer (w=100 DKK/kWh)",
                "archetype": "Comfort-critical household, zero tolerance for deviations"
            }
        }
        
        all_results = {}
        processor = DataProcessor()
        
        # Run each scenario
        for scenario_key, scenario_info in scenarios.items():
            print(f"\n--- Running Scenario: {scenario_info['name']} ---")
            print(f"Description: {scenario_info['description']}")
            print(f"Discomfort weight: {scenario_info['discomfort_weight']:.1f} DKK/kWh")
            print(f"Consumer archetype: {scenario_info['archetype']}")
            
            # Process data with scenario-specific discomfort weight
            optimization_data = processor.process_for_optimization_q1b(
                copy.deepcopy(base_raw_data), 
                scenario_info['discomfort_weight']
            )
            
            # Solve optimization
            model = ConsumerFlexibilityModelQ1b(optimization_data)
            results = model.solve()
            
            if results:
                # Store results with scenario info
                all_results[scenario_key] = {
                    'results': results,
                    'scenario_info': scenario_info,
                    'optimization_data': optimization_data
                }
                
                # Print quick summary
                print(f"✓ Total Cost: {results['optimal_cost']:.2f} DKK")
                print(f"  Energy: {results['energy_cost']:.2f} DKK, Discomfort: {results['discomfort_penalty']:.2f} DKK")
                print(f"  Flexibility: +{results['total_dev_plus']:.2f} / -{results['total_dev_minus']:.2f} kWh")
                
                total_reference = sum(results['reference_load'])
                if total_reference > 0:
                    flex_percentage = ((results['total_dev_plus'] + results['total_dev_minus']) / total_reference) * 100
                    print(f"  Total Flexibility: {flex_percentage:.1f}% of reference")
            else:
                print(f"✗ Optimization failed for {scenario_info['name']}")
                all_results[scenario_key] = None
        
        # Generate comparative analysis
        if len([r for r in all_results.values() if r is not None]) >= 2:
            print("\n" + "="*70)
            print("COMPARATIVE SCENARIO ANALYSIS")
            print("="*70)
            
            generate_scenario_comparison(all_results)
            create_comparison_plots(all_results)
        
        return all_results
        
    except Exception as e:
        print(f"ERROR in Q1b Part V: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_scenario_comparison(all_results):
    """Generate detailed comparison between scenarios."""
    
    valid_scenarios = {k: v for k, v in all_results.items() if v is not None}
    
    if len(valid_scenarios) < 2:
        print("Not enough valid scenarios for comparison")
        return
    
    print("\nSCENARIO COMPARISON TABLE")
    print("-" * 80)
    print(f"{'Scenario':<20} {'Total Cost':<12} {'Energy':<10} {'Discomfort':<12} {'Flexibility %':<12}")
    print("-" * 80)
    
    for scenario_key, scenario_data in valid_scenarios.items():
        results = scenario_data['results']
        scenario_info = scenario_data['scenario_info']
        
        total_reference = sum(results['reference_load'])
        flex_percentage = ((results['total_dev_plus'] + results['total_dev_minus']) / total_reference) * 100
        
        print(f"{scenario_info['name']:<20} {results['optimal_cost']:<12.2f} "
              f"{results['energy_cost']:<10.2f} {results['discomfort_penalty']:<12.2f} {flex_percentage:<12.1f}")
    
    print("\nKEY INSIGHTS")
    print("-" * 40)
    
    # Find most and least flexible scenarios
    flexibility_scores = {}
    for scenario_key, scenario_data in valid_scenarios.items():
        results = scenario_data['results']
        total_reference = sum(results['reference_load'])
        flex_score = (results['total_dev_plus'] + results['total_dev_minus']) / total_reference * 100
        flexibility_scores[scenario_key] = flex_score
    
    most_flexible = max(flexibility_scores.keys(), key=lambda k: flexibility_scores[k])
    least_flexible = min(flexibility_scores.keys(), key=lambda k: flexibility_scores[k])
    
    print(f"Most Flexible: {valid_scenarios[most_flexible]['scenario_info']['name']} "
          f"({flexibility_scores[most_flexible]:.1f}% flexibility)")
    print(f"Least Flexible: {valid_scenarios[least_flexible]['scenario_info']['name']} "
          f"({flexibility_scores[least_flexible]:.1f}% flexibility)")
    
    # Cost analysis
    costs = {k: v['results']['optimal_cost'] for k, v in valid_scenarios.items()}
    lowest_cost = min(costs.keys(), key=lambda k: costs[k])
    highest_cost = max(costs.keys(), key=lambda k: costs[k])
    
    print(f"Lowest Total Cost: {valid_scenarios[lowest_cost]['scenario_info']['name']} "
          f"({costs[lowest_cost]:.2f} DKK)")
    print(f"Highest Total Cost: {valid_scenarios[highest_cost]['scenario_info']['name']} "
          f"({costs[highest_cost]:.2f} DKK)")
    
    # Analyze price responsiveness
    analyze_price_responsiveness(valid_scenarios)


def analyze_price_responsiveness(valid_scenarios):
    """Analyze how each scenario responds to energy prices."""
    
    print("\nPRICE RESPONSIVENESS ANALYSIS")
    print("-" * 40)
    
    for scenario_key, scenario_data in valid_scenarios.items():
        results = scenario_data['results']
        optimization_data = scenario_data['optimization_data']
        scenario_info = scenario_data['scenario_info']
        
        energy_prices = optimization_data['energy_prices']
        mean_price = np.mean(energy_prices)
        
        # Categorize hours by price level
        high_price_hours = [i for i, price in enumerate(energy_prices) if price > mean_price]
        low_price_hours = [i for i, price in enumerate(energy_prices) if price <= mean_price]
        
        # Calculate average deviations during high/low price periods
        high_price_over = np.mean([results['dev_plus_schedule'][h] for h in high_price_hours]) if high_price_hours else 0
        high_price_under = np.mean([results['dev_minus_schedule'][h] for h in high_price_hours]) if high_price_hours else 0
        low_price_over = np.mean([results['dev_plus_schedule'][h] for h in low_price_hours]) if low_price_hours else 0
        low_price_under = np.mean([results['dev_minus_schedule'][h] for h in low_price_hours]) if low_price_hours else 0
        
        # Calculate responsiveness score
        responsiveness_score = (low_price_over - high_price_over) + (high_price_under - low_price_under)
        
        print(f"{scenario_info['name']}:")
        print(f"  High prices: +{high_price_over:.3f} / -{high_price_under:.3f} kWh avg")
        print(f"  Low prices:  +{low_price_over:.3f} / -{low_price_under:.3f} kWh avg")
        print(f"  Responsiveness score: {responsiveness_score:.3f}")


def create_comparison_plots(all_results):
    """Create comprehensive comparison plots for all scenarios."""
    
    valid_scenarios = {k: v for k, v in all_results.items() if v is not None}
    
    if len(valid_scenarios) < 2:
        print("Not enough scenarios for plotting")
        return
    
    # Set professional style
    plt.style.use('default')
    plt.rcParams.update({
        'font.size': 11,
        'font.family': 'Arial',
        'figure.figsize': (14, 10),
        'axes.grid': True,
        'grid.alpha': 0.3
    })
    
    # Create comprehensive comparison figure
    fig = plt.figure(figsize=(16, 12))
    
    # Plot 1: Cost Breakdown Comparison
    ax1 = plt.subplot(3, 2, 1)
    scenarios = list(valid_scenarios.keys())
    energy_costs = [valid_scenarios[s]['results']['energy_cost'] for s in scenarios]
    discomfort_costs = [valid_scenarios[s]['results']['discomfort_penalty'] for s in scenarios]
    scenario_names = [valid_scenarios[s]['scenario_info']['name'] for s in scenarios]
    
    x = np.arange(len(scenarios))
    width = 0.35
    
    bars1 = ax1.bar(x, energy_costs, width, label='Energy Cost', color='blue', alpha=0.7)
    bars2 = ax1.bar(x, discomfort_costs, width, bottom=energy_costs, label='Discomfort Cost', color='red', alpha=0.7)
    
    ax1.set_xlabel('Scenario')
    ax1.set_ylabel('Cost (DKK)')
    ax1.set_title('Q1b: Total Cost Breakdown by Scenario')
    ax1.set_xticks(x)
    ax1.set_xticklabels([name[:10] + '...' if len(name) > 10 else name for name in scenario_names], rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Flexibility Usage Comparison
    ax2 = plt.subplot(3, 2, 2)
    flexibility_percentages = []
    for s in scenarios:
        results = valid_scenarios[s]['results']
        total_reference = sum(results['reference_load'])
        flex_pct = ((results['total_dev_plus'] + results['total_dev_minus']) / total_reference) * 100
        flexibility_percentages.append(flex_pct)
    
    bars = ax2.bar(x, flexibility_percentages, color='green', alpha=0.7)
    ax2.set_xlabel('Scenario')
    ax2.set_ylabel('Flexibility Usage (%)')
    ax2.set_title('Total Flexibility Usage by Scenario')
    ax2.set_xticks(x)
    ax2.set_xticklabels([name[:10] + '...' if len(name) > 10 else name for name in scenario_names], rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Load Profiles Comparison (first 3 scenarios)
    ax3 = plt.subplot(3, 2, (3, 4))
    hours = np.arange(1, 25)
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    # Plot reference load first (as step plot)
    reference_load = valid_scenarios[scenarios[0]]['results']['reference_load']
    ax3.step(hours, reference_load, where='mid', linestyle='--', color='black', 
             linewidth=2, label='Reference Load', alpha=0.8)
    
    # Plot actual loads for each scenario (as step plots)
    for i, scenario_key in enumerate(scenarios[:min(5, len(scenarios))]):  # Limit to 5 scenarios for clarity
        results = valid_scenarios[scenario_key]['results']
        scenario_name = valid_scenarios[scenario_key]['scenario_info']['name']
        ax3.step(hours, results['load_schedule'], where='mid', color=colors[i], 
                linewidth=2, label=f'{scenario_name}', alpha=0.8)
    
    ax3.set_xlabel('Hour')
    ax3.set_ylabel('Load (kW)')
    ax3.set_title('Q1b: Load Schedule Comparison')
    ax3.set_xlim(0.5, 24.5)
    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Deviation Patterns (Over vs Under consumption)
    ax4 = plt.subplot(3, 2, 5)
    over_consumption = [valid_scenarios[s]['results']['total_dev_plus'] for s in scenarios]
    under_consumption = [valid_scenarios[s]['results']['total_dev_minus'] for s in scenarios]
    
    bars1 = ax4.bar(x - width/2, over_consumption, width, label='Over-consumption', color='red', alpha=0.7)
    bars2 = ax4.bar(x + width/2, under_consumption, width, label='Under-consumption', color='orange', alpha=0.7)
    
    ax4.set_xlabel('Scenario')
    ax4.set_ylabel('Total Deviation (kWh)')
    ax4.set_title('Over vs Under Consumption Patterns')
    ax4.set_xticks(x)
    ax4.set_xticklabels([name[:10] + '...' if len(name) > 10 else name for name in scenario_names], rotation=45)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Plot 5: Price Responsiveness
    ax5 = plt.subplot(3, 2, 6)
    # Calculate price responsiveness for each scenario
    responsiveness_scores = []
    for scenario_key in scenarios:
        results = valid_scenarios[scenario_key]['results']
        optimization_data = valid_scenarios[scenario_key]['optimization_data']
        
        energy_prices = optimization_data['energy_prices']
        mean_price = np.mean(energy_prices)
        
        high_price_hours = [i for i, price in enumerate(energy_prices) if price > mean_price]
        low_price_hours = [i for i, price in enumerate(energy_prices) if price <= mean_price]
        
        high_price_net_dev = sum(results['dev_minus_schedule'][h] - results['dev_plus_schedule'][h] for h in high_price_hours)
        low_price_net_dev = sum(results['dev_plus_schedule'][h] - results['dev_minus_schedule'][h] for h in low_price_hours)
        
        responsiveness = (high_price_net_dev + low_price_net_dev) / len(scenarios)
        responsiveness_scores.append(responsiveness)
    
    bars = ax5.bar(x, responsiveness_scores, color='purple', alpha=0.7)
    ax5.set_xlabel('Scenario')
    ax5.set_ylabel('Responsiveness Score')
    ax5.set_title('Price Responsiveness by Scenario')
    ax5.set_xticks(x)
    ax5.set_xticklabels([name[:10] + '...' if len(name) > 10 else name for name in scenario_names], rotation=45)
    ax5.grid(True, alpha=0.3)
    
    plt.suptitle('Q1b Part V: Comprehensive Scenario Comparison', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('Q1b_v_scenario_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Scenario comparison plot saved as 'Q1b_v_scenario_comparison.png'")


def create_threshold_analysis_plots(all_results):
    """Create advanced threshold analysis and economic behavior visualizations."""
    
    valid_scenarios = {k: v for k, v in all_results.items() if v is not None}
    
    if len(valid_scenarios) < 3:
        print("Not enough scenarios for threshold analysis")
        return
    
    # Extract data for analysis
    scenarios_list = list(valid_scenarios.keys())
    weights = [valid_scenarios[s]['scenario_info']['discomfort_weight'] for s in scenarios_list]
    total_costs = [valid_scenarios[s]['results']['optimal_cost'] for s in scenarios_list]
    energy_costs = [valid_scenarios[s]['results']['energy_cost'] for s in scenarios_list]
    discomfort_costs = [valid_scenarios[s]['results']['discomfort_penalty'] for s in scenarios_list]
    flexibility_pct = []
    
    for s in scenarios_list:
        results = valid_scenarios[s]['results']
        total_ref = sum(results['reference_load'])
        flex = ((results['total_dev_plus'] + results['total_dev_minus']) / total_ref) * 100 if total_ref > 0 else 0
        flexibility_pct.append(flex)
    
    # Sort by discomfort weight for proper plotting
    sorted_data = sorted(zip(weights, total_costs, energy_costs, discomfort_costs, flexibility_pct, scenarios_list))
    weights, total_costs, energy_costs, discomfort_costs, flexibility_pct, scenarios_list = zip(*sorted_data)
    
    # Create comprehensive analysis plots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: Economic Threshold Analysis
    ax1.semilogx(weights, total_costs, 'o-', linewidth=3, markersize=8, color='red', label='Total Cost')
    ax1.axvline(x=3.0, color='orange', linestyle='--', linewidth=2, alpha=0.8, label='Economic Threshold (~3 DKK/kWh)')
    ax1.set_xlabel('Discomfort Weight (DKK/kWh)', fontsize=12)
    ax1.set_ylabel('Total Daily Cost (DKK)', fontsize=12)
    ax1.set_title('Economic Threshold: Cost vs Discomfort Weight', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Add annotations for key behaviors
    for i, (w, cost) in enumerate(zip(weights, total_costs)):
        if w < 3.0:
            ax1.annotate('Under-consumption\nRegime', xy=(w, cost), xytext=(w*0.5, cost+5),
                        arrowprops=dict(arrowstyle='->', color='blue', alpha=0.7),
                        fontsize=10, ha='center', color='blue')
        elif w > 3.0 and i == len(weights)//2:  # Middle point
            ax1.annotate('Reference Profile\nRegime', xy=(w, cost), xytext=(w*2, cost+5),
                        arrowprops=dict(arrowstyle='->', color='green', alpha=0.7),
                        fontsize=10, ha='center', color='green')
    
    # Plot 2: Flexibility vs Cost Trade-off
    ax2.scatter(flexibility_pct, total_costs, s=100, c=weights, cmap='viridis', alpha=0.8)
    cbar = plt.colorbar(ax2.collections[0], ax=ax2)
    cbar.set_label('Discomfort Weight (DKK/kWh)', fontsize=10)
    
    for i, (flex, cost, w) in enumerate(zip(flexibility_pct, total_costs, weights)):
        ax2.annotate(f'w={w}', (flex, cost), xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    ax2.set_xlabel('Flexibility Utilization (%)', fontsize=12)
    ax2.set_ylabel('Total Daily Cost (DKK)', fontsize=12)
    ax2.set_title('Flexibility vs Cost Trade-off Analysis', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Cost Component Breakdown
    width = 0.8
    x_pos = np.arange(len(scenarios_list))
    
    bars1 = ax3.bar(x_pos, energy_costs, width, label='Energy Cost', color='blue', alpha=0.7)
    bars2 = ax3.bar(x_pos, discomfort_costs, width, bottom=energy_costs, label='Discomfort Cost', color='red', alpha=0.7)
    
    ax3.set_xlabel('Consumer Scenarios', fontsize=12)
    ax3.set_ylabel('Cost (DKK)', fontsize=12)
    ax3.set_title('Cost Breakdown: Energy vs Discomfort Components', fontsize=14, fontweight='bold')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels([f'w={w}' for w in weights], rotation=45)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Behavioral Regime Classification
    regime_colors = ['red' if w < 3.0 else 'green' for w in weights]
    regime_labels = ['Under-consumption' if w < 3.0 else 'Reference Profile' for w in weights]
    
    bars = ax4.bar(range(len(weights)), flexibility_pct, color=regime_colors, alpha=0.7)
    ax4.axhline(y=50, color='orange', linestyle='--', alpha=0.8, label='50% Flexibility')
    ax4.set_xlabel('Consumer Scenarios', fontsize=12)
    ax4.set_ylabel('Flexibility Utilization (%)', fontsize=12)
    ax4.set_title('Behavioral Regime Classification', fontsize=14, fontweight='bold')
    ax4.set_xticks(range(len(weights)))
    ax4.set_xticklabels([f'w={w}' for w in weights], rotation=45)
    
    # Add regime labels
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='red', alpha=0.7, label='Under-consumption Regime (w<3)'),
                      Patch(facecolor='green', alpha=0.7, label='Reference Profile Regime (w≥3)')]
    ax4.legend(handles=legend_elements, loc='upper right')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('Q1b_v_threshold_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Advanced threshold analysis plots saved as 'Q1b_v_threshold_analysis.png'")


if __name__ == "__main__":
    print("Starting Q1b Part V analysis...")
    results = solve_q1b_part_v()
    
    if results:
        print(f"\nQ1b Part V completed successfully!")
        print(f"Analyzed {len([r for r in results.values() if r is not None])} scenarios")
        
        print("\nCreating advanced threshold analysis visualizations...")
        create_threshold_analysis_plots(results)
        
    else:
        print("\nQ1b Part V failed.")