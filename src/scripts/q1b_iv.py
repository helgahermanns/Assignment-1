"""
Question 1b Part IV - Consumer Energy Flexibility with Preference Deviations
Final Clean Report

Generates clean, professional output for Q1b assignment submission.
Implements the flexibility model with deviation variables and discomfort costs.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data_ops.data_loader import DataLoader
from data_ops.data_processor import DataProcessor
from opt_model.opt_model_Q1b import ConsumerFlexibilityModelQ1b


def solve_q1b_iv_professional(discomfort_weight=1.0):
    """
    Solve Q1b part iv and generate professional output.
    
    Args:
        discomfort_weight: Weight for penalizing deviations from reference load (DKK/kWh)
    
    Returns:
        dict: Results dictionary or None if failed
    """
    
    print("QUESTION 1B PART IV - FLEXIBILITY WITH PREFERENCE DEVIATIONS")
    print("=" * 70)
    print(f"Discomfort weight: {discomfort_weight} DKK/kWh for all deviations")
    
    try:
        # Load and process data for Q1b
        project_root = Path(__file__).parent.parent.parent
        data_path = project_root / "data" / "question_1b"
        
        loader = DataLoader(base_path=str(data_path.parent))
        raw_data = loader.load_data(data_path.name)
        
        processor = DataProcessor()
        optimization_data = processor.process_for_optimization_q1b(
            raw_data, discomfort_weight
        )
        
        # Solve optimization
        model = ConsumerFlexibilityModelQ1b(optimization_data)
        results = model.solve()
        
        if not results:
            print("ERROR: Optimization failed to find solution")
            return None
            
        # Generate professional output
        print_results(results, optimization_data)
        create_plots(results, optimization_data)
        
        return results
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def print_results(results, optimization_data):
    """Print clean, professional results for Q1b."""
    
    print("\nOPTIMIZATION RESULTS")
    print("-" * 30)
    
    # Key metrics
    print(f"Total Daily Cost: {results['optimal_cost']:.2f} DKK")
    print(f"  - Energy Cost: {results['energy_cost']:.2f} DKK")
    print(f"  - Discomfort Penalty: {results['discomfort_penalty']:.2f} DKK")
    
    print(f"\nEnergy Balance:")
    print(f"Total Consumption: {results['total_energy_consumed']:.2f} kWh")
    print(f"Reference Load: {sum(results['reference_load']):.2f} kWh")
    print(f"Total Import: {results['total_imported']:.2f} kWh")  
    print(f"Total Export: {results['total_exported']:.2f} kWh")
    print(f"PV Utilization: {results['total_pv_used']:.2f} kWh")
    
    pv_available = sum(optimization_data['pv_max_hourly'])
    if pv_available > 0:
        pv_utilization_rate = (results['total_pv_used'] / pv_available) * 100
        print(f"PV Utilization Rate: {pv_utilization_rate:.1f}%")
    
    print(f"\nFlexibility Usage:")
    print(f"Over-consumption: {results['total_dev_plus']:.2f} kWh")
    print(f"Under-consumption: {results['total_dev_minus']:.2f} kWh")
    
    total_reference = sum(results['reference_load'])
    if total_reference > 0:
        flexibility_usage = ((results['total_dev_plus'] + results['total_dev_minus']) / total_reference) * 100
        print(f"Total Flexibility: {flexibility_usage:.1f}% of reference")
    
    # Optimal 24-hour schedule
    print(f"\nOPTIMAL 24-HOUR SCHEDULE")
    print("-" * 50)
    print("Hour  Ref   Load   Dev+   Dev-   PV   Import Export")
    print("-" * 55)
    
    for h in range(24):
        ref = results['reference_load'][h]
        load = results['load_schedule'][h]
        dev_plus = results['dev_plus_schedule'][h]
        dev_minus = results['dev_minus_schedule'][h]
        pv_used = results['pv_schedule'][h] 
        import_power = results['import_schedule'][h]
        export_power = results['export_schedule'][h]
        
        print(f"{h+1:4d} {ref:5.2f} {load:6.2f} {dev_plus:6.2f} {dev_minus:6.2f} "
              f"{pv_used:5.2f} {import_power:6.2f} {export_power:6.2f}")


def create_plots(results, optimization_data):
    """Create comprehensive plots for Q1b analysis."""
    
    # Set professional style
    plt.style.use('default')
    plt.rcParams.update({
        'font.size': 12,
        'font.family': 'Arial',
        'figure.figsize': (10, 6),
        'axes.grid': True,
        'grid.alpha': 0.3
    })
    
    hours = np.arange(1, 25)
    
    # Plot 1: Reference vs Actual Load with Deviations
    fig1, ax1 = plt.subplots(figsize=(12, 8))
    
    ax1.step(hours, results['reference_load'], 'k--', linewidth=2, 
             label='Reference Load', where='mid', alpha=0.8)
    ax1.step(hours, results['load_schedule'], 'b-', linewidth=3, 
             label='Actual Load', where='mid')
    
    # Highlight deviations
    for h in range(24):
        if results['dev_plus_schedule'][h] > 0.01:  # Over-consumption
            ax1.bar(h+1, results['dev_plus_schedule'][h], 
                   bottom=results['reference_load'][h], 
                   color='red', alpha=0.5, width=0.8)
        if results['dev_minus_schedule'][h] > 0.01:  # Under-consumption
            ax1.bar(h+1, -results['dev_minus_schedule'][h], 
                   bottom=results['reference_load'][h], 
                   color='orange', alpha=0.5, width=0.8)
    
    # Custom legend entries for deviations
    from matplotlib.patches import Rectangle
    dev_plus_patch = Rectangle((0, 0), 1, 1, facecolor='red', alpha=0.5, label='Over-consumption')
    dev_minus_patch = Rectangle((0, 0), 1, 1, facecolor='orange', alpha=0.5, label='Under-consumption')
    
    ax1.set_xlabel('Hour', fontsize=12)
    ax1.set_ylabel('Power (kW)', color='black', fontsize=12)
    ax1.set_title('Q1b: Load Profile with Flexibility Deviations', fontsize=14, fontweight='bold')
    ax1.set_xlim(0.5, 24.5)
    ax1.grid(True, alpha=0.3)
    
    # Add price on right y-axis
    ax1_price = ax1.twinx()
    ax1_price.step(hours, optimization_data['energy_prices'], 'g--', linewidth=2, 
                   alpha=0.7, label='Energy Price', where='mid')
    ax1_price.set_ylabel('Price (DKK/kWh)', color='green', fontsize=12)
    ax1_price.tick_params(axis='y', labelcolor='green')
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_price.get_legend_handles_labels()
    custom_patches = [dev_plus_patch, dev_minus_patch]
    custom_labels = ['Over-consumption', 'Under-consumption']
    
    ax1.legend(lines1 + lines2 + custom_patches, labels1 + labels2 + custom_labels, 
              loc='upper left', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('Q1b_iv_Load_Flexibility.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Load flexibility plot saved as 'Q1b_iv_Load_Flexibility.png'")
    
    # Plot 2: Cost Breakdown Analysis
    fig2, (ax2, ax3) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Subplot 2a: Energy vs Discomfort Costs
    energy_costs_hourly = [
        (optimization_data['energy_prices'][h] + optimization_data['import_tariff']) * results['import_schedule'][h] - 
        (optimization_data['energy_prices'][h] - optimization_data['export_tariff']) * results['export_schedule'][h]
        for h in range(24)
    ]
    
    # Use single discomfort weight for both over and under consumption
    discomfort_weight = optimization_data.get('discomfort_weight', 1.0)
    discomfort_costs_hourly = [
        discomfort_weight * (results['dev_plus_schedule'][h] + results['dev_minus_schedule'][h])
        for h in range(24)
    ]
    
    ax2.bar(hours, energy_costs_hourly, color='blue', alpha=0.7, label='Energy Costs', width=0.8)
    ax2.bar(hours, discomfort_costs_hourly, bottom=energy_costs_hourly, 
            color='red', alpha=0.7, label='Discomfort Costs', width=0.8)
    
    ax2.set_xlabel('Hour', fontsize=12)
    ax2.set_ylabel('Cost (DKK)', fontsize=12)
    ax2.set_title('Hourly Cost Breakdown: Energy vs Discomfort', fontsize=14, fontweight='bold')
    ax2.set_xlim(0.5, 24.5)
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    # Subplot 2b: Grid Import/Export with PV
    ax3.bar(hours, results['import_schedule'], color='red', alpha=0.7, label='Import', width=0.8)
    ax3.bar(hours, [-x for x in results['export_schedule']], color='green', alpha=0.7, 
            label='Export', width=0.8)
    ax3.step(hours, results['pv_schedule'], color='orange', linewidth=3, 
             label='PV Used', where='mid')
    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    ax3.set_xlabel('Hour', fontsize=12)
    ax3.set_ylabel('Power (kW)', fontsize=12)
    ax3.set_title('Grid Interactions and PV Utilization', fontsize=14, fontweight='bold')
    ax3.set_xlim(0.5, 24.5)
    ax3.legend(fontsize=11)
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('Q1b_iv_Cost_Grid_Analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Cost and grid analysis plot saved as 'Q1b_iv_Cost_Grid_Analysis.png'")


def analyze_flexibility_behavior(results, optimization_data):
    """Analyze and print flexibility behavior insights."""
    
    print("\nFLEXIBILITY BEHAVIOR ANALYSIS")
    print("-" * 40)
    
    # Find patterns in flexibility usage
    high_price_hours = [i for i, price in enumerate(optimization_data['energy_prices']) 
                       if price > np.mean(optimization_data['energy_prices'])]
    low_price_hours = [i for i, price in enumerate(optimization_data['energy_prices']) 
                      if price <= np.mean(optimization_data['energy_prices'])]
    
    # Calculate flexibility during high/low price periods
    high_price_over = sum(results['dev_plus_schedule'][h] for h in high_price_hours)
    high_price_under = sum(results['dev_minus_schedule'][h] for h in high_price_hours)
    low_price_over = sum(results['dev_plus_schedule'][h] for h in low_price_hours)
    low_price_under = sum(results['dev_minus_schedule'][h] for h in low_price_hours)
    
    print(f"High Price Hours ({len(high_price_hours)} hours):")
    print(f"  Over-consumption: {high_price_over:.2f} kWh")
    print(f"  Under-consumption: {high_price_under:.2f} kWh")
    
    print(f"Low Price Hours ({len(low_price_hours)} hours):")
    print(f"  Over-consumption: {low_price_over:.2f} kWh")
    print(f"  Under-consumption: {low_price_under:.2f} kWh")
    
    # Check price-responsiveness
    if high_price_under > high_price_over:
        print("✓ Price-responsive: More under-consumption during high prices")
    if low_price_over > low_price_under:
        print("✓ Price-responsive: More over-consumption during low prices")


if __name__ == "__main__":
    # Test with literature-based baseline discomfort cost
    # Reference: Strbac, G. (2008) - typical demand response flexibility costs: 5-20 DKK/kWh
    # Using mid-range value of 10 DKK/kWh as baseline
    print("Running Q1b Part IV with literature-based discomfort cost (10 DKK/kWh)...")
    results = solve_q1b_iv_professional(discomfort_weight=2.95)
    
    if results:
        # Note: analyze_flexibility_behavior would need optimization_data parameter
        print("\nQ1b Part IV completed successfully.")
    else:
        print("\nQ1b Part IV failed.")