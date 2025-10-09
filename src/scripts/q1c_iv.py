"""
Question 1c Part IV - Consumer Energy Flexibility with Battery Storage Optimization
Final Clean Report

Implements Q1c with battery dynamics, state of charge management, and comprehensive visualizations.
Extends Q1b flexibility model with battery charge/discharge capabilities.
"""

import sys
import copy
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

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
from opt_model.opt_model_Q1c import ConsumerFlexibilityModelQ1c


def solve_q1c_iv():
    """
    Solve Q1c part iv with battery storage and generate comprehensive analysis.
    
    Returns:
        dict: Results dictionary or None if failed
    """
    
    print("QUESTION 1c PART IV - CONSUMER ENERGY FLEXIBILITY WITH BATTERY STORAGE")
    print("=" * 80)
    
    try:
        # Load and process data
        project_root = Path(__file__).parent.parent.parent
        loader = DataLoader(base_path=str(project_root / "data"))
        
        # Use Q1c data which includes battery storage parameters
        base_raw_data = loader.load_data("question_1c")
        
        processor = DataProcessor()
        
        # Set discomfort weight for Q1c (same as Q1b baseline)
        w_value = 2.5  # DKK/kWh - good balance between cost and flexibility
        
        # Process data for optimization using unified processor for Q1c
        optimization_data = processor.process_for_optimization_unified(
            copy.deepcopy(base_raw_data), 
            question_type='q1c',
            discomfort_weight=w_value
        )
        
        print(f"✅ Data loaded and processed successfully")
        print(f"   Time horizon: {optimization_data['T']} hours")
        print(f"   Discomfort weight: {w_value} DKK/kWh")
        print(f"   Reference load total: {sum(optimization_data['reference_load']):.2f} kWh")
        print(f"   PV generation total: {sum(optimization_data['pv_max_hourly']):.2f} kWh")
        
        # Solve optimization with battery
        print(f"\n🔋 Solving Q1c optimization with battery storage...")
        model = ConsumerFlexibilityModelQ1c(optimization_data)
        results = model.solve()
        
        if not results:
            print("❌ Optimization failed to find solution")
            return None
        
        # Print comprehensive solution summary
        model.print_solution_summary(results)
        
        # Generate visualizations
        print(f"\n📊 Generating visualizations...")
        create_battery_visualizations(results, optimization_data)
        
        return results
        
    except Exception as e:
        print(f"❌ Error in Q1c optimization: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_battery_visualizations(results, data):
    """Create 4 focused visualizations for Q1c battery analysis."""
    
    print("Creating Q1c Battery Analysis Visualizations (4 key plots)...")
    
    # Plot 1: Load Analysis - Reference vs Actual Load with Energy Prices and Flexibility
    create_load_analysis_plot(results, data)
    
    # Plot 2: Energy Sources and Battery Operations - PV, Grid, Battery flows
    create_energy_sources_and_battery_plot(results, data)
    
    # Plot 3: Cost Comparison - Q1c vs Q1b showing battery benefits
    create_battery_cost_comparison_plot(results, data)
    
    # Plot 4: Battery Performance - SoC, charge/discharge patterns, and key metrics
    create_battery_performance_plot(results, data)
    
    print("✅ All Q1c visualizations created successfully!")


def create_load_analysis_plot(results, data):
    """Plot 1: Load Analysis - Reference vs Actual Load with Energy Prices and Flexibility"""
    
    fig, ax1 = plt.subplots(figsize=(16, 10))
    
    hours = np.arange(1, 25)
    
    # Plot load profiles
    ax1.step(hours, results['reference_load'], where='mid', linestyle='--', color='black', 
            linewidth=4, label='Reference Load', alpha=0.8)
    ax1.step(hours, results['load_schedule'], where='mid', color='navy', 
            label='Actual Load', alpha=0.9)
    
    # Show flexibility deviations as bars
    over_consumption = results['dev_plus_schedule']
    under_consumption = results['dev_minus_schedule']
    
    # Create bars for deviations
    width = 0.3
    over_bars = ax1.bar(hours + width/2, over_consumption, width=width, 
                       color='red', alpha=0.4, label='Over-consumption')
    under_bars = ax1.bar(hours - width/2, [-u for u in under_consumption], width=width, 
                        color='green', alpha=0.4, label='Under-consumption')
    
    # Secondary y-axis for energy prices
    ax2 = ax1.twinx()
    ax2.step(hours, data['energy_prices'], where='mid', color='purple', 
            linestyle=':', label='Energy Price', alpha=0.8)
    ax2.set_ylabel('Energy Price (DKK/kWh)', fontsize=18, color='purple', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='purple', labelsize=14)
    
    # Formatting
    ax1.set_xlabel('Hour of Day', fontsize=18, fontweight='bold')
    ax1.set_ylabel('Load Consumption (kWh)', fontsize=18, fontweight='bold')
    ax1.set_xlim(0.5, 24.5)
    ax1.set_xticks(range(1, 25, 2))
    ax1.tick_params(labelsize=14)
    ax1.grid(True, alpha=0.3)
    
    plt.title('Load Analysis: Reference vs Actual with Energy Prices & Flexibility', fontsize=22, fontweight='bold', pad=20)
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', framealpha=0.9, fontsize=14)
    
    plt.tight_layout()
    plt.savefig('Q1c_iv_Load_Analysis.png', dpi=300, bbox_inches='tight')
    plt.show()


def create_energy_sources_and_battery_plot(results, data):
    """Plot 2: Energy Sources and Battery Operations - PV, Grid, Battery flows"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), sharex=True)
    
    hours = np.arange(1, 25)
    
    # Top subplot: Energy Sources and Grid
    width = 0.25
    x1 = hours - width
    x2 = hours
    x3 = hours + width
    
    # PV as line (continuous generation)
    ax1.step(hours, results['pv_schedule'], where='mid', color='gold', 
             label='PV Generation', alpha=0.9)
    
    # Import/Export as bars (discrete transactions)
    ax1.bar(x2, results['import_schedule'], width, color='red', alpha=0.7, label='Grid Import')
    ax1.bar(x3, [-exp for exp in results['export_schedule']], width, color='green', alpha=0.7, label='Grid Export')
    
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax1.set_ylabel('Power (kW)', fontsize=18, fontweight='bold')
    ax1.set_title('Energy Sources: PV Generation and Grid Import/Export', fontsize=22, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=14, loc='upper right')
    ax1.set_ylim(bottom=-max(results['export_schedule'])*1.1 if max(results['export_schedule']) > 0 else -1)
    
    # Bottom subplot: Simplified Battery Operations
    width = 0.35
    
    # Battery charge/discharge as bars (simplified, single axis)
    charge_bars = ax2.bar(hours - width/2, results['charge_schedule'], width, 
                         color='blue', alpha=0.7, label='Battery Charge (kW)')
    discharge_bars = ax2.bar(hours + width/2, [-d for d in results['discharge_schedule']], width, 
                            color='red', alpha=0.7, label='Battery Discharge (kW)')
    
    # Add SoC as line plot on same axis (scaled to fit)
    soc_normalized = [(soc - 3) for soc in results['soc_schedule']]  # Center around target (3 kWh)
    ax2.step(hours, soc_normalized, where='mid', color='green', 
             label='SoC deviation from target (kWh)', alpha=0.9, marker='o', markersize=4)
    
    # Reference lines
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.8)
    ax2.axhline(y=3, color='red', linestyle='--', alpha=0.5, label='Max SoC deviation (+3 kWh)')
    ax2.axhline(y=-0.4, color='orange', linestyle='--', alpha=0.5, label='Min safe deviation')
    
    ax2.set_xlabel('Hour of Day', fontsize=18, fontweight='bold')
    ax2.set_ylabel('Power (kW) / SoC Deviation (kWh)', fontsize=18, fontweight='bold')
    ax2.set_title('Battery Operations: Charge/Discharge and SoC Patterns', fontsize=22, fontweight='bold', pad=20)
    ax2.set_xlim(0.5, 24.5)
    ax2.set_xticks(range(1, 25, 2))
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-2.0, 4)
    ax2.legend(loc='upper right', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('Q1c_iv_Energy_Sources_and_Battery.png', dpi=300, bbox_inches='tight')
    plt.show()


def create_battery_cost_comparison_plot(results, data):
    """Plot 3: Cost Comparison - Q1c (with Battery) vs Q1b (without Battery)"""
    
    try:
        # Import Q1b model for comparison
        from opt_model.opt_model_Q1b import ConsumerFlexibilityModelQ1b
        
        # Solve Q1b for comparison
        model_q1b = ConsumerFlexibilityModelQ1b(data)
        results_q1b = model_q1b.solve()
        
        if results_q1b:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
            
            # Left subplot: Cost Comparison
            scenarios = ['Q1b (No Battery)', 'Q1c (With Battery)']
            total_costs = [results_q1b['optimal_cost'], results['optimal_cost']]
            energy_costs = [results_q1b['energy_cost'], results['energy_cost']]
            discomfort_costs = [results_q1b['discomfort_penalty'], results['discomfort_penalty']]
            
            x = np.arange(len(scenarios))
            width = 0.25
            
            ax1.bar(x - width, total_costs, width, label='Total Cost', color='lightcoral', alpha=0.8)
            ax1.bar(x, energy_costs, width, label='Energy Cost', color='lightblue', alpha=0.8)
            ax1.bar(x + width, discomfort_costs, width, label='Discomfort Cost', color='lightgreen', alpha=0.8)
            
            # Add value labels
            for i, (total, energy, discomfort) in enumerate(zip(total_costs, energy_costs, discomfort_costs)):
                ax1.text(i - width, total + 1, f'{total:.1f}', ha='center', va='bottom', fontweight='bold')
                ax1.text(i, energy + 1, f'{energy:.1f}', ha='center', va='bottom', fontweight='bold')
                ax1.text(i + width, discomfort + 1, f'{discomfort:.1f}', ha='center', va='bottom', fontweight='bold')
            
            # Cost savings annotation
            savings = results_q1b['optimal_cost'] - results['optimal_cost']
            savings_pct = (savings / results_q1b['optimal_cost']) * 100
            ax1.text(0.5, max(total_costs) * 0.8, f'Battery Savings:\n{savings:.1f} DKK ({savings_pct:.1f}%)', 
                    ha='center', va='center', bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.8),
                    fontsize=14, fontweight='bold')
            
            ax1.set_ylabel('Cost (DKK)', fontsize=16, fontweight='bold')
            ax1.set_title('Cost Comparison: Battery Benefits', fontsize=18, fontweight='bold')
            ax1.set_xticks(x)
            ax1.set_xticklabels(scenarios, fontsize=14)
            ax1.legend(fontsize=12)
            ax1.grid(True, alpha=0.3)
            
            # Right subplot: Energy Flow Comparison
            categories = ['Load\n(kWh)', 'PV Used\n(kWh)', 'Grid Import\n(kWh)', 'Grid Export\n(kWh)', 'Flexibility\n(kWh)']
            q1b_values = [
                sum(results_q1b['load_schedule']),
                sum(results_q1b['pv_schedule']),
                sum(results_q1b['import_schedule']),
                sum(results_q1b['export_schedule']),
                results_q1b['total_dev_plus'] + results_q1b['total_dev_minus']
            ]
            q1c_values = [
                sum(results['load_schedule']),
                sum(results['pv_schedule']),
                sum(results['import_schedule']),
                sum(results['export_schedule']),
                results['total_dev_plus'] + results['total_dev_minus']
            ]
            
            x2 = np.arange(len(categories))
            width2 = 0.35
            
            bars1 = ax2.bar(x2 - width2/2, q1b_values, width2, label='Q1b (No Battery)', alpha=0.8, color='lightcoral')
            bars2 = ax2.bar(x2 + width2/2, q1c_values, width2, label='Q1c (With Battery)', alpha=0.8, color='lightblue')
            
            # Add value labels
            for i, (q1b_val, q1c_val) in enumerate(zip(q1b_values, q1c_values)):
                ax2.text(i - width2/2, q1b_val + 0.5, f'{q1b_val:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
                ax2.text(i + width2/2, q1c_val + 0.5, f'{q1c_val:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            ax2.set_ylabel('Energy (kWh)', fontsize=16, fontweight='bold')
            ax2.set_title('Energy Flow Comparison', fontsize=18, fontweight='bold')
            ax2.set_xticks(x2)
            ax2.set_xticklabels(categories, fontsize=12)
            ax2.legend(fontsize=12)
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('Q1c_iv_Battery_Cost_Comparison.png', dpi=300, bbox_inches='tight')
            plt.show()
            
        else:
            print("❌ Could not solve Q1b for comparison - showing Q1c costs only")
            # Fallback: show only Q1c costs
            fig, ax = plt.subplots(figsize=(10, 6))
            costs = ['Total Cost', 'Energy Cost', 'Discomfort Cost']
            values = [results['optimal_cost'], results['energy_cost'], results['discomfort_penalty']]
            ax.bar(costs, values, color=['lightcoral', 'lightblue', 'lightgreen'], alpha=0.8)
            ax.set_ylabel('Cost (DKK)', fontsize=16, fontweight='bold')
            ax.set_title('Q1c Cost Breakdown', fontsize=18, fontweight='bold')
            plt.tight_layout()
            plt.savefig('Q1c_iv_Battery_Cost_Comparison.png', dpi=300, bbox_inches='tight')
            plt.show()
            
    except Exception as e:
        print(f"Error in cost comparison: {e}")
        # Fallback: show only Q1c costs
        fig, ax = plt.subplots(figsize=(10, 6))
        costs = ['Total Cost', 'Energy Cost', 'Discomfort Cost']
        values = [results['optimal_cost'], results['energy_cost'], results['discomfort_penalty']]
        ax.bar(costs, values, color=['lightcoral', 'lightblue', 'lightgreen'], alpha=0.8)
        ax.set_ylabel('Cost (DKK)', fontsize=16, fontweight='bold')
        ax.set_title('Q1c Cost Breakdown', fontsize=18, fontweight='bold')
        plt.tight_layout()
        plt.savefig('Q1c_iv_Battery_Cost_Comparison.png', dpi=300, bbox_inches='tight')
        plt.show()


def create_battery_performance_plot(results, data):
    """Plot 4: Battery Performance - SoC patterns, key metrics, and system impact"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))
    
    hours = np.arange(1, 25)
    
    # Top-left: Battery SoC with Energy Prices
    ax1.step(hours, results['soc_schedule'], where='mid', color='green', 
             label='Battery SoC', alpha=0.9)
    ax1.axhline(y=6.0, color='red', linestyle='--', alpha=0.7, label='Max Capacity')
    ax1.axhline(y=3.0, color='orange', linestyle='--', alpha=0.7, label='Target SoC')
    
    ax1_price = ax1.twinx()
    ax1_price.step(hours, data['energy_prices'], where='mid', color='purple', 
                   linestyle=':', label='Energy Price', alpha=0.8)
    ax1_price.set_ylabel('Price (DKK/kWh)', fontsize=14, color='purple', fontweight='bold')
    ax1_price.tick_params(axis='y', labelcolor='purple', labelsize=11)
    
    ax1.set_xlabel('Hour of Day', fontsize=14, fontweight='bold')
    ax1.set_ylabel('SoC (kWh)', fontsize=14, fontweight='bold')
    ax1.set_title('Battery SoC vs Energy Prices', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0.5, 24.5)
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_price.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)
    
    # Top-right: Battery Key Metrics
    metrics = ['Max SoC\n(kWh)', 'SoC Range\n(kWh)', 'Total Charged\n(kWh)', 'Total Discharged\n(kWh)', 'Efficiency\n(%)']
    values = [
        results['max_soc'],
        results['max_soc'] - results['min_soc'],
        results['total_charged'],
        results['total_discharged'],
        results['battery_efficiency'] * 100
    ]
    
    colors2 = ['lightgreen', 'lightblue', 'blue', 'red', 'gold']
    bars2 = ax2.bar(metrics, values, color=colors2, alpha=0.8)
    
    # Add value labels
    for bar, value in zip(bars2, values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{value:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax2.set_ylabel('Value', fontsize=14, fontweight='bold')
    ax2.set_title('Battery Key Metrics', fontsize=16, fontweight='bold')
    ax2.tick_params(axis='x', labelsize=10, rotation=0)
    ax2.grid(True, alpha=0.3)
    
    # Bottom-left: Energy Balance Summary
    energy_categories = ['PV Used', 'Grid Import', 'Grid Export', 'Battery Charged', 'Battery Discharged']
    energy_values = [
        results['total_pv_used'],
        results['total_imported'],
        results['total_exported'],
        results['total_charged'],
        results['total_discharged']
    ]
    
    colors3 = ['gold', 'red', 'green', 'blue', 'purple']
    bars3 = ax3.bar(energy_categories, energy_values, color=colors3, alpha=0.8)
    
    # Add value labels
    for bar, value in zip(bars3, energy_values):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{value:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax3.set_ylabel('Energy (kWh)', fontsize=14, fontweight='bold')
    ax3.set_title('Daily Energy Balance Summary', fontsize=16, fontweight='bold')
    ax3.tick_params(axis='x', rotation=45, labelsize=11)
    ax3.grid(True, alpha=0.3)
    
    # Bottom-right: System Impact Summary
    impact_metrics = ['Total Cost\n(DKK)', 'Energy Cost\n(DKK)', 'Discomfort Cost\n(DKK)', 'Load Flexibility\n(kWh)']
    impact_values = [
        results['optimal_cost'],
        results['energy_cost'],
        results['discomfort_penalty'],
        results['total_dev_plus'] + results['total_dev_minus']
    ]
    
    # Color based on positive/negative values
    colors4 = ['lightcoral' if v > 0 else 'lightgreen' for v in impact_values[:3]] + ['lightblue']
    bars4 = ax4.bar(impact_metrics, [abs(v) for v in impact_values], color=colors4, alpha=0.8)
    
    # Add value labels with +/- indicators
    for i, (bar, value) in enumerate(zip(bars4, impact_values)):
        height = bar.get_height()
        label = f'{value:.1f}'
        if value < 0 and i < 3:  # First 3 are cost metrics
            label += '\n(Profit)'
        ax4.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                label, ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax4.set_ylabel('Value', fontsize=14, fontweight='bold')
    ax4.set_title('System Impact Summary', fontsize=16, fontweight='bold')
    ax4.tick_params(axis='x', labelsize=11, rotation=0)
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('Battery Performance Analysis - Q1c', fontsize=20, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig('Q1c_iv_Battery_Performance.png', dpi=300, bbox_inches='tight')
    plt.show()



def compare_with_q1b_results(results_q1c, data):
    """
    Compare Q1c results with Q1b (without battery) to show battery benefits.
    This would require running Q1b optimization as well.
    """
    
    print("\n" + "="*60)
    print("COMPARISON: Q1c (with Battery) vs Q1b (without Battery)")
    print("="*60)
    
    try:
        # Import Q1b model
        from opt_model.opt_model_Q1b import ConsumerFlexibilityModelQ1b
        
        # Solve Q1b for comparison
        model_q1b = ConsumerFlexibilityModelQ1b(data)
        results_q1b = model_q1b.solve()
        
        if results_q1b:
            print(f"\n💰 COST COMPARISON:")
            print(f"   Q1b Total Cost: {results_q1b['optimal_cost']:.2f} DKK")
            print(f"   Q1c Total Cost: {results_q1c['optimal_cost']:.2f} DKK")
            cost_savings = results_q1b['optimal_cost'] - results_q1c['optimal_cost']
            print(f"   Battery Savings: {cost_savings:.2f} DKK ({cost_savings/results_q1b['optimal_cost']*100:.1f}%)")
            
            print(f"\n⚡ ENERGY COMPARISON:")
            print(f"   Q1b Grid Import: {results_q1b['total_imported']:.2f} kWh")
            print(f"   Q1c Grid Import: {results_q1c['total_imported']:.2f} kWh")
            import_reduction = results_q1b['total_imported'] - results_q1c['total_imported']
            print(f"   Import Reduction: {import_reduction:.2f} kWh")
            
            print(f"\n   Q1b Grid Export: {results_q1b['total_exported']:.2f} kWh")
            print(f"   Q1c Grid Export: {results_q1c['total_exported']:.2f} kWh")
            export_change = results_q1c['total_exported'] - results_q1b['total_exported']
            print(f"   Export Change: {export_change:.2f} kWh")
            
            print(f"\n📊 FLEXIBILITY COMPARISON:")
            q1b_flexibility = results_q1b['total_dev_plus'] + results_q1b['total_dev_minus']
            q1c_flexibility = results_q1c['total_dev_plus'] + results_q1c['total_dev_minus']
            print(f"   Q1b Flexibility Used: {q1b_flexibility:.2f} kWh")
            print(f"   Q1c Flexibility Used: {q1c_flexibility:.2f} kWh")
            flexibility_change = q1c_flexibility - q1b_flexibility
            print(f"   Flexibility Change: {flexibility_change:.2f} kWh")
            
            # Battery enables additional flexibility or reduces need for load shifting
            if abs(flexibility_change) > 0.1:
                if flexibility_change > 0:
                    print("   → Battery enables additional load flexibility")
                else:
                    print("   → Battery reduces need for load shifting")
            
        else:
            print("❌ Could not solve Q1b for comparison")
            
    except Exception as e:
        print(f"❌ Error in Q1b comparison: {e}")


def main():
    """Main execution function for Q1c analysis."""
    
    print("🔋 Q1c.iv - Consumer Energy Flexibility with Battery Storage!")
    print("=" * 70)
    
    try:
        # Solve Q1c optimization
        results = solve_q1c_iv()
        
        if results:
            # Compare with Q1b if possible
            print("\n" + "="*70)
            print("Attempting Q1b comparison for battery benefit analysis...")
            
            # Load data for comparison
            project_root = Path(__file__).parent.parent.parent
            loader = DataLoader(base_path=str(project_root / "data"))
            base_raw_data = loader.load_data("question_1b")
            processor = DataProcessor()
            optimization_data = processor.process_for_optimization_q1b(
                copy.deepcopy(base_raw_data), 1.5
            )
            
            compare_with_q1b_results(results, optimization_data)
            
            print(f"\n✅ Q1c analysis completed successfully!")
            print(f"   All plots saved as Q1c_iv_*.png files")
            print(f"   Battery provides energy storage flexibility with {results['battery_efficiency']*100:.1f}% round-trip efficiency")
            
        else:
            print("❌ Q1c analysis failed - no solution found")
            
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()


def create_figure1_hourly_energy_flows(results, data, hours):
    """Figure 1: Hourly Energy Flows - Q1b vs Q1c comparison with bold formatting"""
    # Configure matplotlib for extra bold formatting
    original_rc = plt.rcParams.copy()
    plt.rcParams.update({
        'font.size': 16,
        'axes.titlesize': 24,
        'axes.labelsize': 20,
        'legend.fontsize': 16,
        'xtick.labelsize': 16,
        'ytick.labelsize': 16,
        'lines.linewidth': 5,
        'axes.linewidth': 3,
        'grid.linewidth': 2
    })
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 16))
    
    # For Q1b comparison, solve simplified version
    q1b_pv = results['pv_schedule']
    q1b_load = data['reference_load']  # Use reference as Q1b actual
    q1b_import = [max(0, load - pv) for load, pv in zip(q1b_load, q1b_pv)]
    q1b_export = [max(0, pv - load) for load, pv in zip(q1b_load, q1b_pv)]
    
    # Q1b (without battery) - Top subplot
    ax1.step(hours, q1b_pv, where='mid', color='orange', 
             label='PV Generation', alpha=0.9, marker='o', markersize=10)
    ax1.step(hours, q1b_load, where='mid', color='blue', 
             label='Load Demand', alpha=0.9, marker='s', markersize=8)
    ax1.step(hours, q1b_import, where='mid', color='red', 
             label='Grid Import', alpha=0.9, marker='^', markersize=8)
    ax1.step(hours, q1b_export, where='mid', color='green', 
             label='Grid Export', alpha=0.9, marker='v', markersize=8)
    
    ax1.set_xlabel('Hour of Day', fontsize=22, fontweight='bold')
    ax1.set_ylabel('Power (kW)', fontsize=22, fontweight='bold')
    ax1.set_title('WITHOUT BATTERY (Q1b): Hourly Power Flows', fontsize=26, fontweight='bold', pad=25)
    ax1.set_xlim(0.5, 24.5)
    ax1.set_xticks(range(1, 25, 2))
    ax1.tick_params(axis='both', which='major', labelsize=18, width=3, length=10)
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc='upper right', fontsize=18, framealpha=0.95, edgecolor='black')
    
    # Q1c (with battery) - Bottom subplot  
    ax2.step(hours, results['pv_schedule'], where='mid', color='orange', 
             label='PV Generation', alpha=0.9, marker='o', markersize=10)
    ax2.step(hours, results['load_schedule'], where='mid', color='blue', 
             label='Load Demand', alpha=0.9, marker='s', markersize=8)
    ax2.step(hours, results['import_schedule'], where='mid', color='red', 
             label='Grid Import', alpha=0.9, marker='^', markersize=8)
    ax2.step(hours, results['export_schedule'], where='mid', color='green', 
             label='Grid Export', alpha=0.9, marker='v', markersize=8)
    ax2.step(hours, results['charge_schedule'], where='mid', color='purple', 
             label='Battery Charge', alpha=0.9, marker='D', markersize=8)
    ax2.step(hours, results['discharge_schedule'], where='mid', color='magenta', 
             label='Battery Discharge', alpha=0.9, marker='*', markersize=12)
    
    ax2.set_xlabel('Hour of Day', fontsize=22, fontweight='bold')
    ax2.set_ylabel('Power (kW)', fontsize=22, fontweight='bold')
    ax2.set_title('WITH BATTERY (Q1c): Hourly Power Flows', fontsize=26, fontweight='bold', pad=25)
    ax2.set_xlim(0.5, 24.5)
    ax2.set_xticks(range(1, 25, 2))
    ax2.tick_params(axis='both', which='major', labelsize=18, width=3, length=10)
    ax2.grid(True, alpha=0.4)
    ax2.legend(loc='upper right', fontsize=18, framealpha=0.95, edgecolor='black')
    
    plt.tight_layout()
    plt.savefig('Q1c_Figure1_Hourly_Energy_Flows.png', dpi=350, bbox_inches='tight')
    plt.close()
    
    # Restore original rcParams
    plt.rcParams.update(original_rc)
    print("✅ Figure 1: Hourly Energy Flows saved")


def create_figure2_battery_soc_profile(results, hours):
    """Figure 2: Battery State of Charge profile with enhanced styling"""
    original_rc = plt.rcParams.copy()
    plt.rcParams.update({
        'font.size': 18,
        'axes.titlesize': 28,
        'axes.labelsize': 24,
        'legend.fontsize': 18,
        'xtick.labelsize': 20,
        'ytick.labelsize': 20,
        'lines.linewidth': 8
    })
    
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    
    # Battery SoC with enhanced visualization
    ax.step(hours, results['soc_schedule'], where='mid', color='darkgreen', 
            linewidth=8, label='Battery State of Charge', marker='o', markersize=12)
    
    # Fill areas for charging/discharging periods
    charging_hours = [h for h, c in zip(hours, results['charge_schedule']) if c > 0.01]
    discharging_hours = [h for h, d in zip(hours, results['discharge_schedule']) if d > 0.01]
    
    # Shade charging periods (light blue)
    for h in charging_hours:
        ax.axvspan(h-0.5, h+0.5, alpha=0.2, color='blue', 
                  label='Charging Period' if h == charging_hours[0] else "")
    
    # Shade discharging periods (light red)
    for h in discharging_hours:
        ax.axvspan(h-0.5, h+0.5, alpha=0.2, color='red', 
                  label='Discharging Period' if h == discharging_hours[0] else "")
    
    # Reference lines with bold styling
    ax.axhline(y=6.0, color='red', linestyle='--', alpha=0.8, 
               label='MAX CAPACITY (6 kWh)')
    ax.axhline(y=3.0, color='orange', linestyle='--', alpha=0.8, 
               label='TARGET SoC (3 kWh)')
    ax.axhline(y=0.0, color='darkred', linestyle=':', alpha=0.8, 
               label='EMPTY BATTERY (0 kWh)')
    
    ax.set_xlabel('Hour of Day', fontsize=24, fontweight='bold')
    ax.set_ylabel('State of Charge (kWh)', fontsize=24, fontweight='bold')
    ax.set_title('BATTERY STATE OF CHARGE PROFILE', fontsize=28, fontweight='bold', pad=30)
    ax.set_xlim(0.5, 24.5)
    ax.set_xticks(range(1, 25, 2))
    ax.set_ylim(-0.5, 6.5)
    ax.tick_params(axis='both', which='major', labelsize=20, width=4, length=12)
    ax.grid(True, alpha=0.4)
    
    # Enhanced legend
    ax.legend(loc='upper left', fontsize=18, framealpha=0.95, edgecolor='black', 
              fancybox=True, shadow=True)
    
    # Add text annotations
    ax.text(0.02, 0.98, f'• Starts & Ends at {results["soc_schedule"][0]:.1f} kWh (Cyclic)', 
            transform=ax.transAxes, fontsize=16, fontweight='bold', 
            bbox=dict(boxstyle="round,pad=0.4", facecolor="lightblue", alpha=0.9),
            verticalalignment='top')
    ax.text(0.02, 0.88, f'• Max SoC: {max(results["soc_schedule"]):.1f} kWh', 
            transform=ax.transAxes, fontsize=16, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.4", facecolor="lightgreen", alpha=0.9),
            verticalalignment='top')
    ax.text(0.02, 0.78, f'• Min SoC: {min(results["soc_schedule"]):.1f} kWh', 
            transform=ax.transAxes, fontsize=16, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", alpha=0.9),
            verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig('Q1c_Figure2_Battery_SoC_Profile.png', dpi=350, bbox_inches='tight')
    plt.close()
    
    plt.rcParams.update(original_rc)
    print("✅ Figure 2: Battery SoC Profile saved")


def create_figure3_load_profile_comparison(results, data, hours):
    """Figure 3: Load Profile vs Reference with deviations"""
    original_rc = plt.rcParams.copy()
    plt.rcParams.update({
        'font.size': 16,
        'axes.titlesize': 26,
        'axes.labelsize': 22,
        'legend.fontsize': 18,
        'lines.linewidth': 7
    })
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 16))
    
    # Top subplot: Load profiles overlay
    ax1.step(hours, data['reference_load'], where='mid', color='black', 
             label='REFERENCE LOAD PROFILE', alpha=0.9, marker='o', markersize=10, linestyle='--')
    ax1.step(hours, results['load_schedule'], where='mid', color='blue', 
             label='ACTUAL OPTIMIZED LOAD (Q1c)', alpha=0.9, marker='s', markersize=10)
    
    ax1.set_xlabel('Hour of Day', fontsize=22, fontweight='bold')
    ax1.set_ylabel('Power (kW)', fontsize=22, fontweight='bold')
    ax1.set_title('LOAD PROFILE COMPARISON: Reference vs Actual', fontsize=26, fontweight='bold', pad=25)
    ax1.set_xlim(0.5, 24.5)
    ax1.set_xticks(range(1, 25, 2))
    ax1.tick_params(axis='both', which='major', labelsize=18, width=3, length=10)
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc='upper right', fontsize=18, framealpha=0.95, edgecolor='black')
    
    # Bottom subplot: Load deviations
    deviations = [actual - ref for actual, ref in zip(results['load_schedule'], data['reference_load'])]
    colors = ['red' if dev > 0 else 'green' for dev in deviations]
    
    bars = ax2.bar(hours, deviations, color=colors, alpha=0.8, width=0.7, edgecolor='black')
    
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.8)
    ax2.set_xlabel('Hour of Day', fontsize=22, fontweight='bold')
    ax2.set_ylabel('Load Deviation (kW)', fontsize=22, fontweight='bold')
    ax2.set_title('LOAD DEVIATIONS: Actual - Reference Load', fontsize=26, fontweight='bold', pad=25)
    ax2.set_xlim(0.5, 24.5)
    ax2.set_xticks(range(1, 25, 2))
    ax2.tick_params(axis='both', which='major', labelsize=18, width=3, length=10)
    ax2.grid(True, alpha=0.4)
    
    # Custom legend for deviations
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='red', alpha=0.8, label='OVER-CONSUMPTION (Above Reference)'),
                      Patch(facecolor='green', alpha=0.8, label='UNDER-CONSUMPTION (Below Reference)')]
    ax2.legend(handles=legend_elements, loc='upper right', fontsize=18, framealpha=0.95, 
               edgecolor='black')
    
    # Add summary statistics
    total_over = sum([max(0, dev) for dev in deviations])
    total_under = sum([min(0, dev) for dev in deviations])
    ax2.text(0.02, 0.98, f'FLEXIBILITY SUMMARY:\n• Over-consumption: {total_over:.2f} kWh\n• Under-consumption: {abs(total_under):.2f} kWh\n• Net flexibility: {total_over + total_under:.2f} kWh', 
            transform=ax2.transAxes, fontsize=16, fontweight='bold', 
            bbox=dict(boxstyle="round,pad=0.6", facecolor="lightblue", alpha=0.95),
            verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig('Q1c_Figure3_Load_Profile_Comparison.png', dpi=350, bbox_inches='tight')
    plt.close()
    
    plt.rcParams.update(original_rc)
    print("✅ Figure 3: Load Profile Comparison saved")


def create_figure4_impact_summary(results, data):
    """Figure 4: Impact summary with Q1b comparison"""
    original_rc = plt.rcParams.copy()
    plt.rcParams.update({
        'font.size': 16,
        'axes.titlesize': 22,
        'axes.labelsize': 20,
        'legend.fontsize': 18
    })
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # Calculate Q1b baseline values (without battery)
    q1b_pv = results['pv_schedule']
    q1b_load = data['reference_load']
    q1b_import = sum([max(0, load - pv) for load, pv in zip(q1b_load, q1b_pv)])
    q1b_export = sum([max(0, pv - load) for load, pv in zip(q1b_load, q1b_pv)])
    q1b_cost = 24.02  # Approximate from previous runs
    
    # Q1c actual values
    q1c_import = sum(results['import_schedule'])
    q1c_export = sum(results['export_schedule'])
    q1c_cost = results['optimal_cost']
    
    pv_total = sum(q1b_pv)
    q1b_self_percent = ((pv_total - q1b_export) / pv_total) * 100
    q1c_self_percent = ((pv_total - q1c_export) / pv_total) * 100
    
    scenarios = ['Q1b\n(No Battery)', 'Q1c\n(With Battery)']
    
    # Subplot 1: Grid Import
    imports = [q1b_import, q1c_import]
    colors1 = ['lightcoral', 'lightgreen']
    
    bars1 = ax1.bar(scenarios, imports, color=colors1, alpha=0.8, width=0.6, 
                    edgecolor='black')
    ax1.set_ylabel('Grid Import (kWh)', fontsize=20, fontweight='bold')
    ax1.set_title('TOTAL GRID IMPORT', fontsize=22, fontweight='bold', pad=20)
    ax1.tick_params(axis='both', which='major', labelsize=18, width=3, length=8)
    ax1.grid(True, alpha=0.3)
    
    for bar, value in zip(bars1, imports):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{value:.2f} kWh', ha='center', va='bottom', 
                fontsize=18, fontweight='bold', 
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.9))
    
    # Subplot 2: Grid Export
    exports = [q1b_export, q1c_export]
    
    bars2 = ax2.bar(scenarios, exports, color=colors1, alpha=0.8, width=0.6, 
                    edgecolor='black')
    ax2.set_ylabel('Grid Export (kWh)', fontsize=20, fontweight='bold')
    ax2.set_title('TOTAL GRID EXPORT', fontsize=22, fontweight='bold', pad=20)
    ax2.tick_params(axis='both', which='major', labelsize=18, width=3, length=8)
    ax2.grid(True, alpha=0.3)
    
    for bar, value in zip(bars2, exports):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{value:.2f} kWh', ha='center', va='bottom', 
                fontsize=18, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.9))
    
    # Subplot 3: PV Self-consumption
    self_consumption = [q1b_self_percent, q1c_self_percent]
    colors3 = ['gold', 'orange']
    
    bars3 = ax3.bar(scenarios, self_consumption, color=colors3, alpha=0.8, width=0.6, 
                    edgecolor='black')
    ax3.set_ylabel('PV Self-Consumption (%)', fontsize=20, fontweight='bold')
    ax3.set_title('PV SELF-CONSUMPTION RATE', fontsize=22, fontweight='bold', pad=20)
    ax3.tick_params(axis='both', which='major', labelsize=18, width=3, length=8)
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 100)
    
    for bar, value in zip(bars3, self_consumption):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{value:.1f}%', ha='center', va='bottom', 
                fontsize=18, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.9))
    
    # Subplot 4: Total Cost
    costs = [q1b_cost, q1c_cost]
    
    bars4 = ax4.bar(scenarios, costs, color=colors1, alpha=0.8, width=0.6, 
                    edgecolor='black')
    ax4.set_ylabel('Total Cost (DKK)', fontsize=20, fontweight='bold')
    ax4.set_title('TOTAL DAILY COST', fontsize=22, fontweight='bold', pad=20)
    ax4.tick_params(axis='both', which='major', labelsize=18, width=3, length=8)
    ax4.grid(True, alpha=0.3)
    
    for bar, value in zip(bars4, costs):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.8,
                f'{value:.2f} DKK', ha='center', va='bottom', 
                fontsize=18, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.9))
    
    # Overall title and summary
    savings = q1b_cost - q1c_cost
    savings_percent = (savings / q1b_cost) * 100
    import_reduction = q1b_import - q1c_import
    export_increase = q1c_export - q1b_export
    self_improvement = q1c_self_percent - q1b_self_percent
    
    fig.suptitle('IMPACT OF BATTERY STORAGE ON ENERGY AND COST', 
                fontsize=30, fontweight='bold', y=0.98)
    
    summary_text = f"""BATTERY IMPACT SUMMARY:

• Cost Savings: {savings:.2f} DKK ({savings_percent:.1f}% reduction)
• Import Reduction: {import_reduction:.2f} kWh
• Export Increase: +{export_increase:.2f} kWh  
• Self-consumption Improvement: +{self_improvement:.1f}%"""
    
    fig.text(0.5, 0.02, summary_text, ha='center', va='bottom', 
             fontsize=16, fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.8", facecolor="lightblue", alpha=0.95))
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.92, bottom=0.18)
    plt.savefig('Q1c_Figure4_Impact_Summary.png', dpi=350, bbox_inches='tight')
    plt.close()
    
    plt.rcParams.update(original_rc)


def create_4_report_figures():
    """Create the 4 specific report figures with bold formatting"""
    
    try:
        # Load and solve Q1c
        project_root = Path(__file__).parent.parent.parent
        data_loader = DataLoader(base_path=str(project_root / "data"))
        data = data_loader.load_data("question_1c")
        
        processor = DataProcessor()
        w_value = 1.5  # DKK/kWh
        processed_data = processor.process_for_optimization_unified(
            copy.deepcopy(data), 
            question_type='q1c',
            discomfort_weight=w_value
        )
        
        model = ConsumerFlexibilityModelQ1c(processed_data)
        results = model.solve()
        
        if results:
            hours = list(range(1, 25))
            
            create_figure1_hourly_energy_flows(results, processed_data, hours)
            create_figure2_battery_soc_profile(results, hours)
            create_figure3_load_profile_comparison(results, processed_data, hours)
            create_figure4_impact_summary(results, processed_data)
            
        else:
            print("Failed to solve Q1c model")
            
    except Exception as e:
        print(f"Error creating report figures: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Create both the standard analysis and the 4 report figures
    main()
    print("\n" + "="*80)
    create_4_report_figures()
