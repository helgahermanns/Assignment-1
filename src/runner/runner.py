from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from data_ops.data_loader import DataLoader
from data_ops.data_processor import DataProcessor
from data_ops.data_visualizer import DataVisualizer
from opt_model.opt_model_Q1 import ConsumerFlexibilityModel


class Runner:
    """
    Handles configuration setting, data loading and preparation, model(s) execution, 
    results saving and plotting for the consumer flexibility optimization.
    """

    def __init__(self, data_path: str = "data") -> None:
        """Initialize the Runner with data path."""
        self.data_path = data_path
        self.results = {}

    def run_single_simulation(self, question_name: str) -> Optional[Dict]:
        """
        Run a single simulation for a given question.

        Args:
            question_name: The question name for the simulation (e.g., 'question_1a')
            
        Returns:
            Dictionary containing optimization results
        """
        print(f"Starting simulation for {question_name}")
        print("="*50)
        
        # Step 1: Load raw data
        print("Step 1: Loading raw data...")
        data_loader = DataLoader(base_path=self.data_path)
        raw_data = data_loader.load_data(question_name)
        
        # Step 2: Process data for optimization
        print("\nStep 2: Processing data...")
        data_processor = DataProcessor()
        optimization_data = data_processor.process_for_optimization(raw_data)
        
        # Step 3: Create and run optimization model
        print("\nStep 3: Creating optimization model...")
        model = ConsumerFlexibilityModel(optimization_data)
        
        # Step 4: Solve the model
        print("\nStep 4: Solving optimization...")
        optimization_results = model.solve()
        
        if optimization_results:
            # Step 5: Process results for analysis
            print("\nStep 5: Processing results...")
            processed_results = data_processor.process_results_for_analysis(
                optimization_results, optimization_data)
            
            # Step 6: Display results
            print("\nStep 6: Results summary...")
            model.print_summary(optimization_results)
            
            # Step 7: Create detailed schedule (for backward compatibility)
            schedule_df = model.get_hourly_schedule_df(optimization_results)
            processed_results['schedule_df'] = schedule_df
            
            # Store results
            self.results[question_name] = {
                'optimization_results': optimization_results,
                'processed_results': processed_results,
                'schedule_df': schedule_df
            }
            
            return processed_results
        else:
            print("Optimization failed!")
            return None
            
    def display_detailed_schedule(self, question_name: str):
        """Display the detailed hourly schedule for a completed simulation."""
        
        if question_name not in self.results:
            print(f"No results found for {question_name}")
            return
            
        results = self.results[question_name]
        schedule_df = results['schedule_df']
        
        print(f"\nDETAILED HOURLY SCHEDULE - {question_name.upper()}")
        print("="*80)
        
        # Configure pandas display options for better formatting
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.float_format', '{:.3f}'.format)
        
        print(schedule_df.to_string(index=False))
        
        print("\n" + "="*80)
        
    def create_visualizations(self, question_name: str, save_plots: bool = True, show_plots: bool = False):
        """Create comprehensive visualizations for the optimization results."""
        
        if question_name not in self.results:
            print(f"No results found for {question_name}")
            return
            
        processed_results = self.results[question_name]['processed_results']
        
        # Initialize visualizer
        visualizer = DataVisualizer()
        
        # Create output directory
        plot_dir = Path("results") / "plots" / question_name
        if save_plots:
            plot_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\nCreating visualizations for {question_name}...")
        
        # Generate all plots
        try:
            # Main energy schedule plot
            fig1 = visualizer.plot_energy_schedule(
                processed_results, 
                save_path=str(plot_dir / "energy_schedule.png") if save_plots else None
            )
            
            # Cost breakdown analysis
            fig2 = visualizer.plot_cost_breakdown(
                processed_results,
                save_path=str(plot_dir / "cost_breakdown.png") if save_plots else None
            )
            
            # PV utilization analysis
            fig3 = visualizer.plot_pv_utilization(
                processed_results,
                save_path=str(plot_dir / "pv_utilization.png") if save_plots else None
            )
            
            # Comprehensive dashboard
            fig4 = visualizer.create_summary_dashboard(
                processed_results,
                save_path=str(plot_dir / "dashboard.png") if save_plots else None
            )
            
            if save_plots:
                # Save all plots in multiple formats
                visualizer.save_all_plots(str(plot_dir), formats=['png', 'pdf'])
                print(f"✓ All visualizations saved to {plot_dir}/")
            
            if show_plots:
                visualizer.show_all_plots()
                
        except Exception as e:
            print(f"Error creating visualizations: {e}")
            print("Continuing without plots...")
        
    def export_results(self, question_name: str, output_path: str = "results"):
        """Export results to CSV files."""
        
        if question_name not in self.results:
            print(f"No results found for {question_name}")
            return
            
        # Create output directory
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        # Get results
        results = self.results[question_name]
        optimization_results = results['optimization_results']
        processed_results = results['processed_results']
        schedule_df = results['schedule_df']
        
        # Export detailed schedule
        csv_filename = output_dir / f"{question_name}_schedule.csv"
        schedule_df.to_csv(csv_filename, index=False)
        
        # Export hourly detailed data
        hourly_df = pd.DataFrame(processed_results['hourly_data'])
        hourly_filename = output_dir / f"{question_name}_hourly_details.csv"
        hourly_df.to_csv(hourly_filename, index=False)
        
        # Export summary results
        summary_stats = processed_results['summary_stats']
        summary_data = {
            'Metric': ['Optimal Cost (DKK)', 'Total Energy Consumed (kWh)', 
                      'Total PV Used (kWh)', 'Total Imported (kWh)', 'Total Exported (kWh)',
                      'PV Utilization Rate (%)', 'Self-Consumption Rate (%)', 'Net Import (kWh)'],
            'Value': [summary_stats['total_cost'], summary_stats['total_energy_consumed'],
                     summary_stats['total_pv_used'], summary_stats['total_imported'], 
                     summary_stats['total_exported'], summary_stats['pv_utilization_rate'] * 100,
                     summary_stats['self_consumption_rate'] * 100, summary_stats['net_import']]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_filename = output_dir / f"{question_name}_summary.csv"
        summary_df.to_csv(summary_filename, index=False)
        
        print(f"✓ Results exported to {output_dir}/")
        
    def run_all_simulations(self, question_list: List[str]) -> None:
        """Run simulations for multiple questions."""
        
        for question in question_list:
            try:
                print(f"\n{'='*60}")
                print(f"RUNNING SIMULATION: {question.upper()}")
                print(f"{'='*60}")
                
                self.run_single_simulation(question)
                
            except Exception as e:
                print(f"Error running simulation for {question}: {e}")
                
        print(f"\nCompleted all simulations. Results for {len(self.results)} questions available.")