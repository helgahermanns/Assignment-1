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


def calculate_detailed_metrics_q1a_iv(results, optimization_data):
    """Calculate detailed metrics for Q1a_iv analysis"""
    
    # Energy flows
    import_total = results.get('total_imported', 0)
    export_total = results.get('total_exported', 0)
    pv_used = results.get('total_pv_used', 0)
    total_cost = results.get('optimal_cost', 0)
    
    # Get hourly data
    hourly_load = results.get('load_schedule', [])
    pv_schedule = results.get('pv_schedule', [])
    import_schedule = results.get('import_schedule', [])
    export_schedule = results.get('export_schedule', [])
    
    # Operational patterns
    hours_importing = sum(1 for imp in import_schedule if imp > 0.01)
    hours_exporting = sum(1 for exp in export_schedule if exp > 0.01)
    
    # Peak operations
    peak_import = max(import_schedule) if import_schedule else 0
    peak_export = max(export_schedule) if export_schedule else 0
    
    # PV utilization
    total_pv_available = sum(optimization_data.get('pv_max_hourly', []))
    pv_utilization = (pv_used / total_pv_available * 100) if total_pv_available > 0 else 0
    
    # Energy balance
    net_import = import_total - export_total
    grid_dependency = (import_total / (import_total + pv_used) * 100) if (import_total + pv_used) > 0 else 0
    
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
        'net_import': net_import,
        'grid_dependency': grid_dependency
    }

def solve_q1iv_professional():
    """
    Solve Q1 part iv and generate professional output.
    
    Returns:
        dict: Results dictionary or None if failed
    """
    
    print("Q1(iv) OPTIMIZATION ANALYSIS")
    print("=" * 80)
    print("QUESTION 1a PART IV - CONSUMER ENERGY FLEXIBILITY OPTIMIZATION")
    print("=" * 80)
    
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
            print("Optimization failed to find solution")
            return None
            
        # Generate professional output
        print_detailed_results(results, optimization_data)
        create_enhanced_plots(results, optimization_data)
        
        return results
        
    except Exception as e:
        print(f"Error: {e}")
        return None


def print_detailed_results(results, optimization_data):
    """Print detailed analysis results in professional format."""
    
    metrics = calculate_detailed_metrics_q1a_iv(results, optimization_data)
    
    print("\n" + "=" * 80)
    print("DETAILED ANALYSIS - OPTIMAL SOLUTION")
    print("=" * 80)
    
    print(f"\nCOST BREAKDOWN:")
    print(f"  NET TOTAL COST:         {metrics['total_cost']:.2f} DKK")
    
    print(f"\nENERGY FLOWS:")
    print(f"  Total import:           {metrics['import_total']:.2f} kWh")
    print(f"  Total export:           {metrics['export_total']:.2f} kWh")
    print(f"  Net import:             {metrics['net_import']:.2f} kWh")
    print(f"  PV self-consumption:    {metrics['pv_used']:.2f} kWh")
    print(f"  PV utilization:         {metrics['pv_utilization']:.1f}%")
    
    print(f"\nOPERATIONAL PATTERNS:")
    print(f"  Hours importing:         {metrics['hours_importing']}")
    print(f"  Hours exporting:         {metrics['hours_exporting']}")
    print(f"  Grid dependency:        {metrics['grid_dependency']:.1f}%")
    print(f"  Peak operations:")
    print(f"    - Peak import:         {metrics['peak_import']:.2f} kW")
    print(f"    - Peak export:         {metrics['peak_export']:.2f} kW")
    
    # Optimal 24-hour schedule
    print(f"\nOPTIMAL 24-HOUR SCHEDULE:")
    print(f"{'Hour':<5} {'Load':<8} {'PV Used':<8} {'Import':<8} {'Export':<8} {'Price':<8}")
    print(f"{'':5} {'(kW)':<8} {'(kW)':<8} {'(kW)':<8} {'(kW)':<8} {'(DKK/kWh)':<8}")
    print("-" * 60)
    
    for h in range(24):
        load = results['load_schedule'][h]
        pv_used = results['pv_schedule'][h] 
        import_power = results['import_schedule'][h]
        export_power = results['export_schedule'][h]
        price = optimization_data['energy_prices'][h]
        
        print(f"{h+1:<5} {load:<8.2f} {pv_used:<8.2f} {import_power:<8.2f} {export_power:<8.2f} {price:<8.2f}")
    
    print("-" * 60)
    
    print(f"\nSUMMARY:")
    print(f"The optimal solution achieves a total daily cost of {metrics['total_cost']:.2f} DKK with")
    print(f"{metrics['pv_utilization']:.1f}% PV utilization and {metrics['grid_dependency']:.1f}% grid dependency.")


def create_enhanced_plots(results, optimization_data):
    """Create enhanced plots with professional styling matching other scripts"""
    
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
        'axes.titlesize': 18,
        'axes.labelsize': 16,
        'legend.fontsize': 14
    })
    
    hours = np.arange(1, 25)
    
    # Plot 1: Load Schedule and PV Utilization
    fig1, ax1 = plt.subplots(figsize=(14, 10))
    
    ax1.step(hours, results['load_schedule'], 'b-', linewidth=4, label='Load Schedule', where='mid')
    ax1.step(hours, results['pv_schedule'], 'orange', linewidth=4, label='PV Used', where='mid')
    ax1.set_xlabel('Hour', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Power (kW)', color='black', fontsize=16, fontweight='bold')
    #ax1.set_title('Load Schedule and PV Utilization', fontsize=18, fontweight='bold', pad=25)
    ax1.set_xlim(0.5, 24.5)
    ax1.grid(True, alpha=0.3, linewidth=1)
    ax1.tick_params(axis='both', labelsize=14)
    
    # Add price on right y-axis
    ax1_price = ax1.twinx()
    ax1_price.step(hours, optimization_data['energy_prices'], 'k--', linewidth=3, alpha=0.7, label='Energy Price', where='mid')
    ax1_price.set_ylabel('Price (DKK/kWh)', color='black', fontsize=14, fontweight='bold')
    ax1_price.tick_params(axis='y', labelcolor='black', labelsize=12)
    
    # Combined legend with enhanced styling
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_price.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=14, framealpha=0.95)
    
    plt.tight_layout()
    plt.savefig('Q1iv_Load_PV.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Load and PV plot saved as 'Q1iv_Load_PV.png'")
    
    # Plot 2: Grid Import/Export
    fig2, ax2 = plt.subplots(figsize=(14, 10))
    
    ax2.bar(hours, results['import_schedule'], color='crimson', alpha=0.8, label='Import', width=0.8, edgecolor='black', linewidth=1)
    ax2.bar(hours, [-x for x in results['export_schedule']], color='forestgreen', alpha=0.8, label='Export', width=0.8, edgecolor='black', linewidth=1)
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.8, linewidth=2)
    ax2.set_xlabel('Hour', fontsize=16, fontweight='bold')
    ax2.set_ylabel('Power (kW)', color='black', fontsize=16, fontweight='bold')
    #ax2.set_title('Grid Import/Export', fontsize=18, fontweight='bold', pad=25)
    ax2.set_xlim(0.5, 24.5)
    ax2.grid(True, alpha=0.3, linewidth=1)
    ax2.tick_params(axis='both', labelsize=14)
    
    # Add price on right y-axis
    ax2_price = ax2.twinx()
    ax2_price.step(hours, optimization_data['energy_prices'], 'k--', linewidth=3, alpha=0.7, label='Energy Price', where='mid')
    ax2_price.set_ylabel('Price (DKK/kWh)', color='black', fontsize=14, fontweight='bold')
    ax2_price.tick_params(axis='y', labelcolor='black', labelsize=12)
    
    # Combined legend with enhanced styling
    lines3, labels3 = ax2.get_legend_handles_labels()
    lines4, labels4 = ax2_price.get_legend_handles_labels()
    ax2.legend(lines3 + lines4, labels3 + labels4, loc='upper left', fontsize=14, framealpha=0.95)
    
    plt.tight_layout()
    plt.savefig('Q1iv_Import_Export.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Import/Export plot saved as 'Q1iv_Import_Export.png'")


if __name__ == "__main__":
    results = solve_q1iv_professional()
    if results:
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("\nVISUALIZATIONS GENERATED:")
        print("1. Load schedule and PV utilization")
        print("2. Grid import/export patterns")
        print("\nQ1 Part IV completed successfully.")
    else:
        print("\nQ1 Part IV analysis failed.")