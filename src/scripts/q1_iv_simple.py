"""
Q1 PART IV - Simple Script
Consumer Energy Flexibility Optimization

This script ONLY does Question 1 part iv.
No fancy stuff, no complications, just solve Q1iv.

What this does:
1. Read your JSON files (bus_params.json, appliance_params.json, etc.)
2. Put the numbers into the optimization problem
3. Ask Gurobi to solve it (find the cheapest energy schedule)
4. Show you the answer

Usage:
    python q1_iv_simple.py
"""

import sys
from pathlib import Path

# Add the parent folder so we can import our code
sys.path.append(str(Path(__file__).parent.parent))

from data_ops.data_loader import DataLoader
from data_ops.data_processor import DataProcessor
from data_ops.data_visualizer import DataVisualizer
from opt_model.opt_model_Q1 import ConsumerFlexibilityModel
import matplotlib.pyplot as plt


def solve_q1_iv():
    """
    Solve Question 1 part iv in the simplest way possible.
    """
    
    print("🔥 QUESTION 1 PART IV - Consumer Energy Flexibility")
    print("="*60)
    print("What we're doing:")
    print("• Reading your data files")
    print("• Setting up the optimization problem") 
    print("• Finding the cheapest 24-hour energy schedule")
    print("="*60)
    
    try:
        # STEP 1: Read the JSON files
        print("\n📖 STEP 1: Reading data files...")
        # Use absolute path to be sure
        project_root = Path(__file__).parent.parent.parent
        data_path = project_root / "data"
        data_loader = DataLoader(base_path=str(data_path))
        raw_data = data_loader.load_data("question_1a")
        print("✓ Successfully read all JSON files!")
        
        # STEP 2: Organize the data for optimization
        print("\n🔧 STEP 2: Preparing data for optimization...")
        processor = DataProcessor()
        optimization_data = processor.process_for_optimization(raw_data)
        print("✓ Data is ready for optimization!")
        
        # Show what we got from the data
        print(f"\n📊 What we found in your data:")
        print(f"├─ Energy prices: {len(optimization_data['energy_prices'])} hours")
        print(f"├─ Import tariff: {optimization_data['import_tariff']} DKK/kWh")
        print(f"├─ Export tariff: {optimization_data['export_tariff']} DKK/kWh")
        print(f"├─ PV max power: {optimization_data['appliances']['PV_01']['max_power']} kW")
        print(f"├─ Load max power: {optimization_data['load_max']} kW")
        print(f"└─ Min daily energy: {optimization_data['min_daily_energy']} kWh")
        
        # STEP 3: Create the optimization problem
        print(f"\n🧠 STEP 3: Creating optimization problem...")
        print("This creates all the math:")
        print("• Variables: load, PV_used, import, export (for each hour)")
        print("• Constraints: energy balance, capacity limits, min energy")
        print("• Objective: minimize daily cost")
        
        model = ConsumerFlexibilityModel(optimization_data)
        print("✓ Optimization problem created!")
        
        # STEP 4: Solve it!
        print(f"\n🚀 STEP 4: Solving with Gurobi...")
        print("Gurobi is now finding the cheapest energy schedule...")
        
        results = model.solve()
        
        if results:
            print("🎉 SUCCESS! Found optimal solution!")
            
            # STEP 5: Show the main results
            print(f"\n📋 MAIN RESULTS:")
            print(f"├─ Optimal daily cost: {results['optimal_cost']:.2f} DKK")
            print(f"├─ Total energy used: {results['total_energy_consumed']:.2f} kWh")
            print(f"├─ PV energy used: {results['total_pv_used']:.2f} kWh")  
            print(f"├─ Energy imported: {results['total_imported']:.2f} kWh")
            print(f"└─ Energy exported: {results['total_exported']:.2f} kWh")
            
            # STEP 6: Show complete 24-hour optimal schedule
            print(f"\n📅 COMPLETE 24-HOUR OPTIMAL ENERGY SCHEDULE:")
            print("Hour | Load  | PV Used | PV Avail | Import | Export | Price | Hourly Cost")
            print("-" * 85)
            pv_available = optimization_data['pv_max_hourly']
            for h in range(24):
                load = results['load_schedule'][h]
                pv_used = results['pv_schedule'][h]
                pv_avail = pv_available[h]
                imp = results['import_schedule'][h]  
                exp = results['export_schedule'][h]
                price = optimization_data['energy_prices'][h]
                
                # Calculate hourly cost: import cost - export revenue
                import_cost = imp * (price + optimization_data['import_tariff'])
                export_revenue = exp * (price - optimization_data['export_tariff'])
                hourly_cost = import_cost - export_revenue
                
                print(f"{h+1:4d} | {load:5.2f} | {pv_used:7.2f} | {pv_avail:8.2f} | "
                      f"{imp:6.2f} | {exp:6.2f} | {price:5.2f} | {hourly_cost:10.3f}")
            
            print("-" * 85)
            
            # STEP 7: Cost breakdown analysis
            print(f"\n� COST BREAKDOWN ANALYSIS:")
            total_import_cost = sum(results['import_schedule'][h] * 
                                  (optimization_data['energy_prices'][h] + optimization_data['import_tariff']) 
                                  for h in range(24))
            total_export_revenue = sum(results['export_schedule'][h] * 
                                     (optimization_data['energy_prices'][h] - optimization_data['export_tariff']) 
                                     for h in range(24))
            
            print(f"├─ Total import cost: {total_import_cost:.2f} DKK")
            print(f"├─ Total export revenue: {total_export_revenue:.2f} DKK")
            print(f"├─ Net cost: {total_import_cost - total_export_revenue:.2f} DKK")
            print(f"└─ PV self-consumption: {results['total_pv_used']:.1f} kWh (saves grid purchases)")
            
            # STEP 8: Create visualizations
            print(f"\n📊 CREATING VISUALIZATIONS...")
            try:
                # Process results for visualization using DataProcessor
                processed_visualization_data = processor.process_results_for_analysis(results, optimization_data)
                
                visualizer = DataVisualizer()
                
                # Generate plots
                print("📈 Creating energy schedule plot...")
                visualizer.plot_energy_schedule(processed_visualization_data)
                
                print("💰 Creating cost breakdown plot...")
                visualizer.plot_cost_breakdown(processed_visualization_data)
                
                print("☀️ Creating PV utilization plot...")
                visualizer.plot_pv_utilization(processed_visualization_data)
                
                # Actually display the plots
                plt.show()
                
                print("✓ All visualizations displayed! Check the plot windows.")
                
            except Exception as e:
                print(f"⚠️ Visualization failed: {e}")
                import traceback
                traceback.print_exc()
                print("Continuing without plots...")
            
            print(f"\n💡 INTERPRETATION:")
            print(f"• The consumer should follow this hourly schedule to minimize cost")  
            print(f"• Daily cost is {results['optimal_cost']:.2f} DKK (negative = profit)")
            print(f"• PV utilization: {results['total_pv_used']:.1f}/{sum(optimization_data['pv_max_hourly']):.1f} kWh available")
            pv_util_pct = (results['total_pv_used'] / sum(optimization_data['pv_max_hourly'])) * 100 if sum(optimization_data['pv_max_hourly']) > 0 else 0
            print(f"• PV self-consumption rate: {pv_util_pct:.1f}%")
            
            # Verify energy constraint
            print(f"\n✅ CONSTRAINT VERIFICATION:")
            print(f"├─ Minimum daily energy required: {optimization_data['min_daily_energy']:.1f} kWh")
            print(f"├─ Actual daily energy consumed: {results['total_energy_consumed']:.1f} kWh")
            constraint_ok = results['total_energy_consumed'] >= optimization_data['min_daily_energy'] - 1e-6
            print(f"└─ Energy constraint satisfied: {'✓ YES' if constraint_ok else '✗ NO'}")
            
            print(f"\n✅ Q1 PART IV COMPLETED!")
            print(f"✓ Answer: Minimum daily cost = {results['optimal_cost']:.2f} DKK")
            
            return results
            
        else:
            print("❌ Optimization failed!")
            print("This means Gurobi couldn't find a solution.")
            print("Check your data files for errors.")
            return None
            
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("Make sure these files exist in ../data/question_1a/:")
        print("  - bus_params.json")
        print("  - appliance_params.json") 
        print("  - DER_production.json")
        print("  - usage_preference.json")
        print("  - consumer_params.json")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure Gurobi is installed:")
        print("  pip install gurobipy")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Something went wrong. Check the error message above.")


if __name__ == "__main__":
    # This runs when you execute: python q1_iv_simple.py
    solve_q1_iv()