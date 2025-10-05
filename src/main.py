"""
Main function to execute the optimization workflow.

This function creates instances of the Runner class, prepares input data,
and runs simulations following the teacher's recommended structure.

Suggested structure:
- Import necessary modules and functions.
- Define a main function to encapsulate the workflow (e.g. Create an instance of your the Runner class, Run a single simulation or multiple simulations, Save results and generate plots if necessary.)
- Prepare input data for a single simulation or multiple simulations.
- Execute main function when the script is run directly.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

# Import necessary modules and functions
from data_ops.data_loader import DataLoader
from data_ops.data_processor import DataProcessor
from opt_model.opt_model_Q1 import ConsumerFlexibilityModel
from runner.runner import Runner



def main():
    """
    Main function to encapsulate the optimization workflow.
    
    Creates instances of Runner class, prepares input data, 
    and runs single/multiple simulations as recommended by teacher.
    """
    
    print("=" * 70)
    print("DTU OPTIMIZATION ASSIGNMENT - MAIN WORKFLOW")
    print("=" * 70)
    
    try:
        # Prepare input data for simulation
        print("1. Preparing input data...")
        
        # Define data path (modify as needed for different questions)
        data_folder = "question_1a"  # Change this for Q1b, Q1c, Q2, Q3, etc.
        
        # Create instance of DataLoader
        loader = DataLoader()
        raw_data = loader.load_data(data_folder)
        print(f"   ✓ Loaded data from {data_folder}")
        
        # Create instance of DataProcessor  
        processor = DataProcessor()
        optimization_data = processor.process_for_optimization(raw_data)
        print("   ✓ Data processed for optimization")
        
        # Create instance of your Runner class
        print("\\n2. Creating Runner instance...")
        runner = Runner(data_path="data")
        print("   ✓ Runner instance created")
        
        # Run a single simulation (Q1 part iv)
        print("\\n3. Running simulation...")
        results = runner.run_single_simulation(data_folder)
        
        if results:
            print("   ✓ Optimization completed successfully!")
            
            # Display key results  
            print("\\n4. Simulation Results:")
            print(f"   • Optimal daily cost: {results['optimal_cost']:.2f} DKK")
            print(f"   • Total energy consumed: {results['total_energy_consumed']:.2f} kWh")  
            print(f"   • PV energy used: {results['total_pv_used']:.2f} kWh")
            
            # Save results and generate plots if necessary
            print("\\n5. Saving results and generating plots...")
            runner.export_results(data_folder, output_path="results")
            runner.create_visualizations(data_folder, save_plots=True, show_plots=True)
            print("   ✓ Results saved and plots generated")
            
        else:
            print("   ✗ Optimization failed!")
            
    except Exception as e:
        print(f"ERROR: {e}")
        print("\\nTroubleshooting:")
        print("- Check that Gurobi is installed and licensed")
        print("- Verify data files exist in data/ folders")
        print("- Ensure required Python packages are installed")


if __name__ == "__main__":
    # Execute main function when the script is run directly
    main()