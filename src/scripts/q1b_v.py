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


def create_consumer_load_scenarios():
    """Create different consumer load profiles representing various flexibility preferences."""
    
    # Base profile from your data (normalized)
    base_profile = [
        0.055, 0.04, 0.04, 0.04, 0.075, 0.48, 0.76, 0.80, 0.63, 0.22,
        0.25, 0.35, 0.30, 0.28, 0.45, 0.65, 0.78, 0.90, 0.98, 0.88,
        0.88, 0.075, 0.15, 0.075, 0.055
    ][:24]  # Ensure 24 hours
    
    # Consumer archetype load profiles
    load_scenarios = {
        "tech_enthusiast": {
            "name": "Tech Enthusiast",
            "description": "Smart home, flexible schedule, night-shifted consumption",
            # Shift evening peak to night/early morning
            "profile": [0.15, 0.12, 0.10, 0.08, 0.075, 0.25, 0.45, 0.55, 0.40, 0.22,
                       0.25, 0.35, 0.30, 0.28, 0.35, 0.45, 0.55, 0.65, 0.70, 0.60,
                       0.55, 0.35, 0.25, 0.20]
        },
        "work_from_home": {
            "name": "Work from Home",
            "description": "Home office, daytime-heavy consumption pattern",
            # Higher daytime, lower evening
            "profile": [0.055, 0.04, 0.04, 0.04, 0.075, 0.25, 0.45, 0.60, 0.75, 0.80,
                       0.85, 0.90, 0.85, 0.80, 0.75, 0.65, 0.55, 0.60, 0.65, 0.55,
                       0.45, 0.25, 0.15, 0.075]
        },
        "traditional_family": {
            "name": "Traditional Family", 
            "description": "Standard evening peak, family routines",
            # Your original profile (evening peak)
            "profile": base_profile
        },
        "senior_fixed": {
            "name": "Senior Fixed Schedule",
            "description": "Early routine, consistent pattern, comfort-focused",
            # Earlier peak, more consistent
            "profile": [0.10, 0.08, 0.06, 0.06, 0.15, 0.35, 0.55, 0.65, 0.60, 0.45,
                       0.50, 0.55, 0.60, 0.65, 0.70, 0.85, 0.90, 0.85, 0.75, 0.65,
                       0.55, 0.35, 0.25, 0.15]
        }
    }
    
    return load_scenarios


def solve_q1b_original_w_scenarios():
    """
    Solve original Q1b Part V with discomfort weight variations (keep unchanged).
    """
    
    print("QUESTION 1B PART V - ORIGINAL DISCOMFORT WEIGHT ANALYSIS")
    print("Dataset: question_1b (original w variations)")
    print("=" * 70)
    
    try:
        # Load base data from question_1b
        project_root = Path(__file__).parent.parent.parent
        loader = DataLoader(base_path=str(project_root / "data"))
        
        print("Loading base data from question_1b dataset...")
        base_raw_data = loader.load_data("question_1b")
        
        # Original scenarios with w variations (unchanged)
        scenarios = {
            "highly_flexible": {
                "name": "Highly Flexible (w=0.5)",
                "discomfort_weight": 0.5,
                "description": "Very low discomfort cost - maximum flexibility",
                "archetype": "Tech-savvy consumer with smart home automation"
            },
            "moderately_flexible": {
                "name": "Moderately Flexible (w=1.5)", 
                "discomfort_weight": 1.5,
                "description": "Low discomfort cost - significant flexibility",
                "archetype": "Price-conscious consumer willing to shift loads"
            },
            "threshold_flexible": {
                "name": "Threshold Flexible (w=2.5)",
                "discomfort_weight": 2.5,
                "description": "Just below economic threshold - strategic flexibility",
                "archetype": "Selective flexibility during peak price hours only"
            },
            "inflexible": {
                "name": "Inflexible (w=5.0)",
                "discomfort_weight": 5.0,
                "description": "Above economic threshold - comfort prioritized",
                "archetype": "Traditional consumer following reference profile exactly"
            }
        }
        
        all_results = run_scenarios(base_raw_data, scenarios, modify_load=False)
        return all_results
        
    except Exception as e:
        print(f"Error in original w scenarios: {str(e)}")
        return None


def solve_q1b_load_profile_scenarios():
    """
    Solve Q1b Part V with different load profile scenarios.
    """
    
    print("\nQUESTION 1B PART V - LOAD PROFILE SCENARIO ANALYSIS")
    print("Dataset: question_1b (with different load patterns)")
    print("=" * 70)
    
    try:
        # Load base data from question_1b
        project_root = Path(__file__).parent.parent.parent
        loader = DataLoader(base_path=str(project_root / "data"))
        
        print("Loading base data from question_1b dataset...")
        base_raw_data = loader.load_data("question_1b")
        
        # Get consumer load scenarios
        load_scenarios = create_consumer_load_scenarios()
        
        # Define comprehensive scenarios combining load patterns + discomfort weights
        scenarios = {
            "tech_enthusiast": {
                "name": "Tech Enthusiast",
                "discomfort_weight": 0.5,
                "load_profile": load_scenarios["tech_enthusiast"]["profile"],
                "description": "Smart home automation, very flexible, night-shifted consumption",
                "archetype": load_scenarios["tech_enthusiast"]["description"]
            },
            "work_from_home": {
                "name": "Work from Home",
                "discomfort_weight": 1.2,
                "load_profile": load_scenarios["work_from_home"]["profile"],
                "description": "Home office schedule, moderate flexibility, daytime-heavy",
                "archetype": load_scenarios["work_from_home"]["description"]
            },
            "traditional_family": {
                "name": "Traditional Family",
                "discomfort_weight": 2.0,
                "load_profile": load_scenarios["traditional_family"]["profile"],
                "description": "Standard routines, limited flexibility, evening peak",
                "archetype": load_scenarios["traditional_family"]["description"]
            },
            "senior_fixed": {
                "name": "Senior Fixed Schedule",
                "discomfort_weight": 4.0,
                "load_profile": load_scenarios["senior_fixed"]["profile"],
                "description": "Fixed routines, comfort-focused, early evening pattern",
                "archetype": load_scenarios["senior_fixed"]["description"]
            }
        }
        
        all_results = run_scenarios(base_raw_data, scenarios, modify_load=True)
        return all_results
        
    except Exception as e:
        print(f"Error in load profile scenarios: {str(e)}")
        return None


def run_scenarios(base_raw_data, scenarios, modify_load=False):
    """Run optimization scenarios and return results."""
    
    all_results = {}
    processor = DataProcessor()
    
    def modify_load_profile(raw_data, new_profile):
        """Modify the usage preferences with a custom load profile."""
        data_copy = copy.deepcopy(raw_data)
        data_copy['usage_preferences'][0]['load_preferences'][0]['hourly_profile_ratio'] = new_profile
        return data_copy
        
        # Run each scenario
        for scenario_key, scenario_info in scenarios.items():
            print(f"\n--- Running Scenario: {scenario_info['name']} ---")
            print(f"Description: {scenario_info['description']}")
            print(f"Discomfort weight: {scenario_info['discomfort_weight']:.1f} DKK/kWh")
            print(f"Consumer archetype: {scenario_info['archetype']}")
            
            # Modify raw data with custom load profile
            modified_raw_data = modify_load_profile(base_raw_data, scenario_info['load_profile'])
            
            # Process data with scenario-specific discomfort weight and load profile
            optimization_data = processor.process_for_optimization_q1b(
                modified_raw_data, 
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
                
                # Print quick summary with primal and dual variables
                print(f"✓ Total Cost: {results['optimal_cost']:.2f} DKK")
                print(f"  Energy: {results['energy_cost']:.2f} DKK, Discomfort: {results['discomfort_penalty']:.2f} DKK")
                print(f"  Flexibility: +{results['total_dev_plus']:.2f} / -{results['total_dev_minus']:.2f} kWh")
                
                total_reference = sum(results['reference_load'])
                if total_reference > 0:
                    flex_percentage = ((results['total_dev_plus'] + results['total_dev_minus']) / total_reference) * 100
                    print(f"  Total Flexibility: {flex_percentage:.1f}% of reference")
                
                # Report key primal and dual variables
                print(f"📊 PRIMAL VARIABLES (Optimal Decisions):")
                print(f"  Peak Load (17-20h): {sum(results['load_schedule'][16:20]):.2f} kWh")
                print(f"  Peak Import: {sum(results['import_schedule'][16:20]):.2f} kWh") 
                print(f"  Peak Export: {sum(results['export_schedule'][16:20]):.2f} kWh")
                print(f"  Max Hourly Deviation: {max(results['dev_minus_schedule']):.2f} kWh")
                
                print(f"📈 DUAL VARIABLES (Shadow Prices - Economic Sensitivity):")
                print(f"  Avg Energy Balance Dual: {results['avg_dual_energy']:.3f} DKK/kWh")
                print(f"  Avg Deviation Dual: {results['avg_dual_deviation']:.3f} DKK/kWh")
                peak_hours = [16, 17, 18, 19]  # 17:00-20:00
                peak_energy_dual = sum(results['dual_energy_balance'][h] for h in peak_hours) / len(peak_hours)
                peak_dev_dual = sum(results['dual_deviation_balance'][h] for h in peak_hours) / len(peak_hours)
                print(f"  Peak Energy Dual (17-20h): {peak_energy_dual:.3f} DKK/kWh")
                print(f"  Peak Deviation Dual (17-20h): {peak_dev_dual:.3f} DKK/kWh")
            else:
                print(f"✗ Optimization failed for {scenario_info['name']}")
                all_results[scenario_key] = None
        
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
    
    # Generate comprehensive primal/dual summary table
    print_primal_dual_summary(valid_scenarios)
    
    # Add consumer preference analysis
    analyze_consumer_preferences(valid_scenarios)


def analyze_consumer_preferences(valid_scenarios):
    """Analyze how different consumer preferences (load patterns + discomfort weights) affect outcomes."""
    
    print(f"\n{'='*80}")
    print("CONSUMER FLEXIBILITY PREFERENCE ANALYSIS")
    print(f"{'='*80}")
    
    # Sort by discomfort weight for analysis
    sorted_scenarios = sorted(valid_scenarios.items(), 
                            key=lambda x: x[1]['scenario_info']['discomfort_weight'])
    
    print("\n🏠 CONSUMER ARCHETYPE COMPARISON:")
    print("-" * 50)
    
    for scenario_key, scenario_data in sorted_scenarios:
        info = scenario_data['scenario_info']
        results = scenario_data['results']
        
        # Calculate key metrics
        total_ref = sum(results['reference_load'])
        flexibility_pct = (results['total_dev_plus'] + results['total_dev_minus']) / total_ref * 100
        profit_loss = -results['energy_cost']  # Negative energy cost = profit
        
        # Peak hour analysis (17:00-20:00)
        peak_hours = [16, 17, 18, 19]
        peak_ref_load = sum(results['reference_load'][h] for h in peak_hours)
        peak_actual_load = sum(results['load_schedule'][h] for h in peak_hours)
        peak_reduction = peak_ref_load - peak_actual_load
        peak_reduction_pct = (peak_reduction / peak_ref_load * 100) if peak_ref_load > 0 else 0
        
        print(f"\n📊 {info['name']} (w={info['discomfort_weight']:.1f} DKK/kWh):")
        print(f"   Load Pattern: {info['archetype']}")
        print(f"   Total Cost: {results['optimal_cost']:.2f} DKK")
        print(f"   Energy Profit/Loss: {profit_loss:+.2f} DKK")
        print(f"   Overall Flexibility: {flexibility_pct:.1f}% of reference consumption")
        print(f"   Peak Hour Reduction: {peak_reduction:.2f} kWh ({peak_reduction_pct:.1f}%)")
        
        # Economic efficiency
        cost_per_kwh_ref = results['optimal_cost'] / total_ref
        print(f"   Cost Efficiency: {cost_per_kwh_ref:.3f} DKK/kWh consumed")
    
    print(f"\n{'='*80}")
    print("KEY INSIGHTS:")
    print("• Load Pattern Impact: Different baseline consumption patterns affect flexibility potential")
    print("• Discomfort Weight Effect: Higher w values reduce flexibility regardless of load pattern")
    print("• Economic Optimization: Consumers with flexible schedules can achieve greater cost savings")
    print("• Peak Hour Response: All scenarios show maximum flexibility during expensive hours (17-20h)")
    print(f"{'='*80}")


def print_primal_dual_summary(valid_scenarios):
    """Print comprehensive summary table of primal and dual variables for all scenarios."""
    
    print(f"\n{'='*80}")
    print("COMPREHENSIVE PRIMAL AND DUAL VARIABLE SUMMARY")
    print(f"{'='*80}")
    
    # Header
    print(f"{'Scenario':<20} {'w':<5} {'Cost':<8} {'Energy':<8} {'Discomf':<8} {'Flex%':<6}")
    print(f"{'':20} {'':5} {'(DKK)':<8} {'(DKK)':<8} {'(DKK)':<8} {'':6}")
    print("-" * 80)
    
    # Sort scenarios by discomfort weight
    sorted_scenarios = sorted(valid_scenarios.items(), 
                            key=lambda x: x[1]['scenario_info']['discomfort_weight'])
    
    for scenario_key, scenario_data in sorted_scenarios:
        info = scenario_data['scenario_info']
        results = scenario_data['results']
        
        # Calculate flexibility percentage
        total_ref = sum(results['reference_load'])
        flex_pct = (results['total_dev_plus'] + results['total_dev_minus']) / total_ref * 100 if total_ref > 0 else 0
        
        print(f"{info['name']:<20} {info['discomfort_weight']:<5.1f} {results['optimal_cost']:<8.2f} "
              f"{results['energy_cost']:<8.2f} {results['discomfort_penalty']:<8.2f} {flex_pct:<6.1f}")
    
    print("-" * 80)
    print("DUAL VARIABLES (Shadow Prices - Economic Interpretation)")
    print("-" * 80)
    print(f"{'Scenario':<20} {'AvgEnergyDual':<12} {'AvgDevDual':<10} {'PeakEnergyDual':<14} {'PeakDevDual':<12}")
    print(f"{'':20} {'(DKK/kWh)':<12} {'(DKK/kWh)':<10} {'(DKK/kWh)':<14} {'(DKK/kWh)':<12}")
    print("-" * 80)
    
    for scenario_key, scenario_data in sorted_scenarios:
        info = scenario_data['scenario_info'] 
        results = scenario_data['results']
        
        # Calculate peak hour duals (17:00-20:00)
        peak_hours = [16, 17, 18, 19]
        peak_energy_dual = sum(results['dual_energy_balance'][h] for h in peak_hours) / len(peak_hours)
        peak_dev_dual = sum(results['dual_deviation_balance'][h] for h in peak_hours) / len(peak_hours)
        
        print(f"{info['name']:<20} {results['avg_dual_energy']:<12.3f} {results['avg_dual_deviation']:<10.3f} "
              f"{peak_energy_dual:<14.3f} {peak_dev_dual:<12.3f}")
    
    print(f"{'='*80}")
    print("ECONOMIC INTERPRETATION:")
    print("• Energy Balance Duals (negative): Marginal cost reduction from energy constraint relaxation")
    print("• Deviation Duals (positive): Marginal cost of allowing additional flexibility") 
    print("• Peak Hour Duals: Higher absolute values show concentrated economic pressure")
    print("• Dual values reveal WHY the optimal primal decisions are economically rational")
    print(f"{'='*80}")


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

def create_energy_flow_plot(scenario_data):
    """Plot 5: Import/Export/PV time series."""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    hours = np.arange(1, 25)
    
    for i, data in enumerate(scenario_data):
        ax = axes[i]
        results = data['results']
        
        # Plot energy flows
        ax.step(hours, results['import_schedule'], where='mid', label='Grid Import', 
                color='red', linewidth=2, alpha=0.8)
        ax.step(hours, results['export_schedule'], where='mid', label='Grid Export', 
                color='green', linewidth=2, alpha=0.8)
        ax.step(hours, results['pv_schedule'], where='mid', label='PV Used', 
                color='orange', linewidth=2, alpha=0.8)
        
        # Add energy prices on secondary y-axis
        ax2 = ax.twinx()
        energy_prices = [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4,
                        0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 2.0, 2.5, 3.0, 2.5, 
                        2.0, 0.4, 0.4, 0.4]
        ax2.step(hours, energy_prices, where='mid', color='purple', linewidth=1.5, 
                linestyle=':', alpha=0.6, label='Energy Price')
        ax2.set_ylabel('Price (DKK/kWh)', color='purple', alpha=0.7)
        ax2.tick_params(axis='y', labelcolor='purple')
        
        ax.set_title(f'{data["name"]}', fontweight='bold')
        ax.set_xlabel('Hour')
        ax.set_ylabel('Energy (kWh)')
        
        # Combined legend
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)
        
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0.5, 24.5)
    
    plt.suptitle('Q1b: Energy Flow Patterns by Flexibility Scenario', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('Q1b_v_energy_flows.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Energy flow patterns plot saved as 'Q1b_v_energy_flows.png'")


def create_under_consumption_individual(scenario_data):
    """Create individual under-consumption patterns plot."""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    hours = list(range(24))
    n_scenarios = len(scenario_data)
    bar_width = 0.18
    
    # Colors for each scenario
    colors = ['#e74c3c', "#a1f312", "#0f6df1", "#2f3833"][:n_scenarios]
    
    for i, data in enumerate(scenario_data):
        results = data['results']
        under_consumption = [-dev for dev in results['dev_minus_schedule']]
        
        offset = (i - n_scenarios/2 + 0.5) * bar_width
        x_pos = [h + offset for h in hours]
        
        bars = ax.bar(x_pos, under_consumption, bar_width, 
                     label=f"{data['name']} ",
                     color=colors[i], alpha=0.8)
    
    ax.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
    ax.set_ylabel('Under-Consumption (kWh)', fontsize=12, fontweight='bold')
    ax.set_title('Consumer Under-Consumption Patterns by Scenario', 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(hours[::2])
    ax.set_xticklabels([f'{h:02d}:00' for h in hours[::2]], rotation=45)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('Q1b_Under_Consumption_Individual.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("✓ Under-consumption patterns plot saved as 'Q1b_Under_Consumption_Individual.png'")


def create_load_profiles_individual(scenario_data):
    """Plot 1: Load Profiles - Reference vs Actual (Reference on top)."""
    
    fig, ax = plt.subplots(figsize=(14, 8))
    hours = np.arange(1, 25)
    colors = ['blue', 'red', 'green', 'orange']
    
    # Plot reference load first (on top with thick dashed line)
    reference_load = scenario_data[0]['results']['reference_load']
    ax.step(hours, reference_load, where='mid', linestyle='dotted', color= "#000000", 
             linewidth=3, label='Reference Load', alpha=0.9, zorder=10)
    
    # Plot actual loads for each scenario (behind reference)
    for i, data in enumerate(scenario_data):
        results = data['results']
        w = data['weight']
        ax.step(hours, results['load_schedule'], where='mid', color=colors[i], 
                linewidth=2.5, label=f'Actual Load (w={w} DKK/kWh)', alpha=0.8, zorder=i+1)
    
    ax.set_xlabel('Hour', fontsize=14)
    ax.set_ylabel('Load (kWh)', fontsize=14)
    ax.set_title('Q1b: Load Profiles - Reference vs Actual', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0.5, 24.5)
    ax.set_ylim(0, max(reference_load) * 1.1)
    
    plt.tight_layout()
    plt.savefig('Q1b_v_load_profiles.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Plot 1: Load profiles saved as 'Q1b_v_load_profiles.png'")


def create_cost_breakdown_individual(scenario_data):
    """Plot 3: Cost Breakdown - Energy vs Discomfort."""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    scenario_names = [f"w={data['weight']}" for data in scenario_data]
    energy_costs = [data['results']['energy_cost'] for data in scenario_data]
    discomfort_costs = [data['results']['discomfort_penalty'] for data in scenario_data]
    
    width = 0.6
    x_pos = np.arange(len(scenario_data))
    
    # Handle negative energy costs (revenue) by splitting positive and negative
    positive_energy = [max(0, cost) for cost in energy_costs]
    negative_energy = [min(0, cost) for cost in energy_costs]
    
    # Plot positive energy costs
    bars1 = ax.bar(x_pos, positive_energy, width, label='Energy Cost', color='blue', alpha=0.7)
    
    # Plot negative energy costs (revenue) - these appear below zero
    bars2 = ax.bar(x_pos, negative_energy, width, label='Energy Revenue (Profit)', color='darkred', alpha=0.7)
    
    # Plot discomfort costs on top of positive energy costs
    bars3 = ax.bar(x_pos, discomfort_costs, width, bottom=positive_energy, 
                   label='Discomfort Cost', color='red', alpha=0.7)
    
    ax.set_xlabel('Consumer Scenarios', fontsize=14)
    ax.set_ylabel('Cost (DKK)', fontsize=14)
    ax.set_title('Q1b: Cost Breakdown - Energy vs Discomfort', fontsize=16, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(scenario_names, fontsize=12)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Add a horizontal line at zero to emphasize profit vs cost
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.8, linewidth=1)
    
    # Add total cost labels above bars
    for i, (energy, discomfort) in enumerate(zip(energy_costs, discomfort_costs)):
        total = energy + discomfort
        y_pos = max(energy + discomfort, energy) + 1
        ax.text(i, y_pos, f'{total:.1f} DKK', ha='center', va='bottom', 
                fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('Q1b_v_cost_breakdown.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Plot 3: Cost breakdown saved as 'Q1b_v_cost_breakdown.png'")


def create_energy_summary_individual(scenario_data):
    """Plot 4: Daily Energy Balance Summary."""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    scenario_names = [f"w={data['weight']}" for data in scenario_data]
    total_consumption = [sum(data['results']['load_schedule']) for data in scenario_data]
    total_import = [sum(data['results']['import_schedule']) for data in scenario_data]
    total_export = [sum(data['results']['export_schedule']) for data in scenario_data]
    
    x_pos = np.arange(len(scenario_data))
    width = 0.25
    
    bars1 = ax.bar(x_pos - width, total_consumption, width, label='Consumption', color='blue', alpha=0.7)
    bars2 = ax.bar(x_pos, total_import, width, label='Import', color='red', alpha=0.7)
    bars3 = ax.bar(x_pos + width, total_export, width, label='Export', color='green', alpha=0.7)
    
    ax.set_xlabel('Consumer Scenarios', fontsize=14)
    ax.set_ylabel('Daily Energy (kWh)', fontsize=14)
    ax.set_title('Q1b: Daily Energy Balance Summary', fontsize=16, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(scenario_names, fontsize=12)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bars, values in [(bars1, total_consumption), (bars2, total_import), (bars3, total_export)]:
        for bar, value in zip(bars, values):
            if value > 0.1:  # Only show labels for non-zero values
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, 
                        f'{value:.1f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('Q1b_v_energy_summary.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Plot 4: Energy summary saved as 'Q1b_v_energy_summary.png'")


def create_load_price_individual_plots(scenario_data):
    """Create 4 individual load vs price plots for each consumer scenario."""
    
    # Energy prices (from your data)
    energy_prices = [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4,
                    0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 2.0, 2.5, 3.0, 2.5, 
                    2.0, 0.4, 0.4, 0.4]
    
    hours = np.arange(1, 25)
    
    for i, data in enumerate(scenario_data):
        fig, ax1 = plt.subplots(figsize=(14, 8))
        
        # Primary y-axis: Load consumption
        color1 = 'tab:blue'
        ax1.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Load Consumption (kWh)', color=color1, fontsize=12, fontweight='bold')
        
        # Plot reference and actual load
        ax1.step(hours, data['results']['reference_load'], where='mid', 
                linestyle='--', color='gray', linewidth=3, label='Reference Load', alpha=0.8)
        ax1.step(hours, data['results']['load_schedule'], where='mid', 
                color=color1, linewidth=3, label='Actual Load', alpha=0.9)
        
        # Add PV production as dashed yellow line (faded)
        pv_production = [2.52, 2.52, 2.52, 2.52, 2.52, 2.52, 2.52, 2.52, 2.52, 2.52,
                        2.52, 2.52, 2.52, 2.52, 2.52, 2.52, 2.52, 2.52, 2.52, 2.52,
                        2.52, 2.52, 2.52, 2.52]  # PV generation from your data
        ax1.step(hours, pv_production, where='mid', 
                linestyle='--', color='gold', linewidth=2, label='PV Production', alpha=0.5)
        
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.set_xlim(0.5, 24.5)
        
        # Secondary y-axis: Energy prices
        ax2 = ax1.twinx()
        color2 = 'tab:red'
        ax2.set_ylabel('Energy Price (DKK/kWh)', color=color2, fontsize=12, fontweight='bold')
        ax2.step(hours, energy_prices, where='mid', color=color2, linewidth=2, 
                linestyle=':', label='Energy Price', alpha=0.8)
        ax2.tick_params(axis='y', labelcolor=color2)
        ax2.set_ylim(0, max(energy_prices) * 1.1)
        
        # Title and formatting
        plt.title(f'{data["name"]}: Load Response to Energy Prices\n'
                 f'(w={data["weight"]:.1f} DKK/kWh, Flexibility: {data["flexibility_pct"]:.1f}%)', 
                 fontsize=14, fontweight='bold', pad=20)
        
        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)
        
        ax1.grid(True, alpha=0.3)
        plt.tight_layout()
        
        filename = f'Q1b_Load_Price_{data["name"].replace(" ", "_")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.show()
        print(f"✓ Load-Price plot saved as '{filename}'")


def create_combined_cost_breakdown(scenario_data):
    """Create single combined cost breakdown plot for all 4 scenarios."""
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    scenario_names = [data['name'] for data in scenario_data]
    energy_costs = [data['results']['energy_cost'] for data in scenario_data]
    discomfort_costs = [data['results']['discomfort_penalty'] for data in scenario_data]
    total_costs = [data['results']['optimal_cost'] for data in scenario_data]
    
    x = np.arange(len(scenario_names))
    width = 0.35
    
    # Create stacked bars
    bars1 = ax.bar(x, energy_costs, width, label='Energy Cost/Revenue', 
                  color=['green' if cost < 0 else 'red' for cost in energy_costs], alpha=0.8)
    bars2 = ax.bar(x, discomfort_costs, width, bottom=energy_costs, 
                  label='Discomfort Cost', color='orange', alpha=0.8)
    
    # Remove trendline - just show stacked bars
    
    # Formatting
    ax.set_xlabel('Consumer Scenario', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cost Components (DKK)', fontsize=12, fontweight='bold')
    ax.set_title('Q1b: Cost Breakdown by Consumer Flexibility Preference', 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{name}\n(w={data['weight']:.1f})" for name, data in zip(scenario_names, scenario_data)], 
                      rotation=0, ha='center')
    
    # Add value labels on bars
    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        # Energy cost label
        energy_val = energy_costs[i]
        if abs(energy_val) > 0.5:
            ax.text(bar1.get_x() + bar1.get_width()/2, energy_val/2, 
                   f'{energy_val:.1f}', ha='center', va='center', 
                   fontweight='bold', color='white')
        
        # Discomfort cost label
        discomfort_val = discomfort_costs[i]
        if discomfort_val > 0.5:
            ax.text(bar2.get_x() + bar2.get_width()/2, 
                   energy_val + discomfort_val/2, 
                   f'{discomfort_val:.1f}', ha='center', va='center', 
                   fontweight='bold', color='white')
        
        # Total cost label above bars
        total_cost = total_costs[i]
        y_pos = max(energy_val + discomfort_val, energy_val) + 1
        ax.text(i, y_pos, f'Total: {total_cost:.1f}', 
                ha='center', va='bottom', fontweight='bold', color='darkblue')
    
    # Legend
    ax.legend(loc='upper left', fontsize=11)
    
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    
    plt.tight_layout()
    plt.savefig('Q1b_Combined_Cost_Breakdown.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("✓ Combined cost breakdown saved as 'Q1b_Combined_Cost_Breakdown.png'")


if __name__ == "__main__":
    print("Starting Q1b Part V comprehensive analysis...")
    
    # Run original w-variation scenarios (5 plots)
    print("\n" + "="*80)
    print("PART 1: ORIGINAL W-VARIATION SCENARIOS (5 PLOTS)")
    print("="*80)
    original_results = solve_q1b_original_w_scenarios()
    
    if original_results:
        # Generate comparison for original scenarios
        generate_scenario_comparison(original_results)
        
        # Extract and sort data by discomfort weight for plotting
        valid_scenarios = {k: v for k, v in original_results.items() if v is not None}
        scenario_data_original = []
        
        for s, data in valid_scenarios.items():
            results_data = data['results']
            scenario_info = data['scenario_info']
            total_ref = sum(results_data['reference_load'])
            flex_pct = ((results_data['total_dev_plus'] + results_data['total_dev_minus']) / total_ref) * 100 if total_ref > 0 else 0
            
            scenario_data_original.append({
                'key': s,
                'name': scenario_info['name'],
                'weight': scenario_info['discomfort_weight'],
                'results': results_data,
                'flexibility_pct': flex_pct
            })
        
        # Sort by discomfort weight
        scenario_data_original.sort(key=lambda x: x['weight'])
        
        print("\nCreating original 5 plots...")
        create_energy_flow_plot(scenario_data_original)
        create_load_profiles_individual(scenario_data_original)
        create_under_consumption_individual(scenario_data_original)
        create_cost_breakdown_individual(scenario_data_original)
        create_energy_summary_individual(scenario_data_original)
        print("✓ Original 5 plots completed!")
    
    # Run load profile scenarios (5 additional plots)
    print("\n" + "="*80)
    print("PART 2: LOAD PROFILE SCENARIOS (5 ADDITIONAL PLOTS)")
    print("="*80)
    load_results = solve_q1b_load_profile_scenarios()
    
    if load_results:
        # Generate comparison for load profile scenarios
        generate_scenario_comparison(load_results)
        
        # Extract and sort data for load profile plotting
        valid_load_scenarios = {k: v for k, v in load_results.items() if v is not None}
        scenario_data_loads = []
        
        for s, data in valid_load_scenarios.items():
            results_data = data['results']
            scenario_info = data['scenario_info']
            total_ref = sum(results_data['reference_load'])
            flex_pct = ((results_data['total_dev_plus'] + results_data['total_dev_minus']) / total_ref) * 100 if total_ref > 0 else 0
            
            scenario_data_loads.append({
                'key': s,
                'name': scenario_info['name'],
                'weight': scenario_info['discomfort_weight'],
                'results': results_data,
                'flexibility_pct': flex_pct
            })
        
        # Sort by discomfort weight
        scenario_data_loads.sort(key=lambda x: x['weight'])
        
        print("\nCreating load profile analysis plots...")
        create_load_price_individual_plots(scenario_data_loads)  # 4 individual plots
        create_combined_cost_breakdown(scenario_data_loads)      # 1 combined plot
        print("✓ Load profile 5 plots completed!")
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETED!")
    print("Total plots created: 10 (5 original w-variation + 4 load-price + 1 combined cost)")
    print(f"{'='*80}")