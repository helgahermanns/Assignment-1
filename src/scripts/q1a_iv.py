"""
Question 1 Part IV - Consumer Energy Flexibility Optimization
Final Clean Report

Generates clean, professional output for assignment submission.
No emojis, minimal formatting, essential results only.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data_ops.data_loader import DataLoader
from data_ops.data_processor import DataProcessor
from opt_model.opt_model_Q1a import ConsumerFlexibilityModel


def solve_q1iv_professional():
    """
    Solve Q1 part iv and generate professional output.
    
    Returns:
        dict: Results dictionary or None if failed
    """
    
    print("QUESTION 1 PART IV - CONSUMER ENERGY FLEXIBILITY OPTIMIZATION")
    print("=" * 70)
    
    try:
        # Load and process data
        project_root = Path(__file__).parent.parent.parent
        data_path = project_root / "data" / "question_1a"
        
        loader = DataLoader(base_path=str(data_path.parent))
        raw_data = loader.load_data(data_path.name)
        
        processor = DataProcessor()
        optimization_data = processor.process_for_optimization(raw_data)
        
        # Solve optimization
        model = ConsumerFlexibilityModel(optimization_data)
        results = model.solve()
        
        if not results:
            print("ERROR: Optimization failed to find solution")
            return None
            
        # Generate professional output
        print_results(results, optimization_data)
        create_plot(results, optimization_data)
        
        return results
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def print_results(results, optimization_data):
    """Print clean, professional results."""
    
    print("\nOPTIMIZATION RESULTS")
    print("-" * 30)
    
    # Key metrics
    print(f"Total Daily Cost: {results['optimal_cost']:.2f} DKK")
    print(f"Total Import: {results['total_imported']:.2f} kWh")  
    print(f"Total Export: {results['total_exported']:.2f} kWh")
    print(f"PV Utilization: {results['total_pv_used']:.2f} kWh")
    
    pv_available = sum(optimization_data['pv_max_hourly'])
    pv_utilization_rate = (results['total_pv_used'] / pv_available) * 100
    print(f"PV Utilization Rate: {pv_utilization_rate:.1f}%")
    
    # Optimal 24-hour schedule
    print(f"\nOPTIMAL 24-HOUR SCHEDULE")
    print("-" * 30)
    print("Hour  Load   PV_Used Import Export")
    print("-" * 35)
    
    for h in range(24):
        load = results['load_schedule'][h]
        pv_used = results['pv_schedule'][h] 
        import_power = results['import_schedule'][h]
        export_power = results['export_schedule'][h]
        
        print(f"{h+1:4d} {load:6.2f} {pv_used:7.2f} {import_power:6.2f} {export_power:6.2f}")


def create_plot(results, optimization_data):
    """Create two separate plots for PV/Load and Import/Export"""
    
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
    
    # Plot 1: Load Schedule and PV Utilization
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    
    ax1.step(hours, results['load_schedule'], 'b-', linewidth=3, label='Load Schedule', where='mid')
    ax1.step(hours, results['pv_schedule'], 'orange', linewidth=3, label='PV Used', where='mid')
    ax1.set_xlabel('Hour', fontsize=12)
    ax1.set_ylabel('Power (kW)', color='black', fontsize=12)
    ax1.set_title('Load Schedule and PV Utilization', fontsize=14, fontweight='bold')
    ax1.set_xlim(0.5, 24.5)
    ax1.grid(True, alpha=0.3)
    
    # Add price on right y-axis
    ax1_price = ax1.twinx()
    ax1_price.step(hours, optimization_data['energy_prices'], 'k--', linewidth=2, alpha=0.7, label='Energy Price', where='mid')
    ax1_price.set_ylabel('Price (DKK/kWh)', color='black', fontsize=12)
    ax1_price.tick_params(axis='y', labelcolor='black')
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_price.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('Q1iv_Load_PV.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Load and PV plot saved as 'Q1iv_Load_PV.png'")
    
    # Plot 2: Grid Import/Export
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    
    ax2.bar(hours, results['import_schedule'], color='red', alpha=0.7, label='Import', width=0.8)
    ax2.bar(hours, [-x for x in results['export_schedule']], color='green', alpha=0.7, label='Export', width=0.8)
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax2.set_xlabel('Hour', fontsize=12)
    ax2.set_ylabel('Power (kW)', color='black', fontsize=12)
    ax2.set_title('Grid Import/Export', fontsize=14, fontweight='bold')
    ax2.set_xlim(0.5, 24.5)
    ax2.grid(True, alpha=0.3)
    
    # Add price on right y-axis
    ax2_price = ax2.twinx()
    ax2_price.step(hours, optimization_data['energy_prices'], 'k--', linewidth=2, alpha=0.7, label='Energy Price', where='mid')
    ax2_price.set_ylabel('Price (DKK/kWh)', color='black', fontsize=12)
    ax2_price.tick_params(axis='y', labelcolor='black')
    
    # Combined legend
    lines3, labels3 = ax2.get_legend_handles_labels()
    lines4, labels4 = ax2_price.get_legend_handles_labels()
    ax2.legend(lines3 + lines4, labels3 + labels4, loc='upper left', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('Q1iv_Import_Export.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Import/Export plot saved as 'Q1iv_Import_Export.png'")


if __name__ == "__main__":
    results = solve_q1iv_professional()
    if results:
        print("\nQ1 Part IV completed successfully.")
    else:
        print("\nQ1 Part IV failed.")