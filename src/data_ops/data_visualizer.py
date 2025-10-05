import json
import csv
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.figure as mfig
import seaborn as sns
from typing import Dict, List, Optional


class DataVisualizer:
    """
    Creates visualizations for optimization results and analysis.
    
    Responsibilities:
    - Generate plots for energy schedules and costs
    - Create summary charts and statistics
    - Export plots to various formats
    - Provide interactive plotting options
    
    Example usage:
    >>> visualizer = DataVisualizer()
    >>> visualizer.plot_energy_schedule(processed_results)
    >>> visualizer.save_all_plots("output_folder")
    """

    def __init__(self, style: str = "seaborn-v0_8", figsize: tuple = (12, 8)):
        """
        Initialize the DataVisualizer.
        
        Args:
            style: Matplotlib style for plots
            figsize: Default figure size for plots
        """
        # Set plotting style
        plt.style.use('default')  # Use default style as seaborn styles may not be available
        sns.set_palette("husl")
        
        self.figsize = figsize
        self.plots = {}  # Store generated plots
        
    def plot_energy_schedule(self, processed_results: dict, save_path: Optional[str] = None) -> mfig.Figure:
        """
        Create a comprehensive energy schedule plot.
        
        Args:
            processed_results: Processed results from DataProcessor
            save_path: Optional path to save the plot
            
        Returns:
            matplotlib Figure object
        """
        hourly_data = pd.DataFrame(processed_results['hourly_data'])
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Consumer Energy Flexibility - Optimal Schedule', fontsize=16, fontweight='bold')
        
        # Plot 1: Energy flows
        ax1.plot(hourly_data['hour'], hourly_data['pv_available'], 'gold', linewidth=2, 
                label='PV Available', marker='o', markersize=4)
        ax1.plot(hourly_data['hour'], hourly_data['pv_used'], 'orange', linewidth=2, 
                label='PV Used', marker='s', markersize=4)
        ax1.plot(hourly_data['hour'], hourly_data['load'], 'blue', linewidth=2, 
                label='Load', marker='^', markersize=4)
        ax1.set_xlabel('Hour')
        ax1.set_ylabel('Power (kW)')
        ax1.set_title('Energy Production and Consumption')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(1, 24)
        
        # Plot 2: Grid interactions
        ax2.bar(hourly_data['hour'], hourly_data['import'], alpha=0.7, 
                color='red', label='Import')
        ax2.bar(hourly_data['hour'], -hourly_data['export'], alpha=0.7, 
                color='green', label='Export')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax2.set_xlabel('Hour')
        ax2.set_ylabel('Power (kW)')
        ax2.set_title('Grid Import/Export')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0.5, 24.5)
        
        # Plot 3: Energy prices and costs
        ax3_twin = ax3.twinx()
        bars = ax3.bar(hourly_data['hour'], hourly_data['import_cost'], alpha=0.7, 
                      color='red', label='Import Cost')
        bars2 = ax3.bar(hourly_data['hour'], -hourly_data['export_revenue'], alpha=0.7, 
                       color='green', label='Export Revenue')
        line = ax3_twin.plot(hourly_data['hour'], hourly_data['energy_price'], 'black', 
                            linewidth=2, marker='o', markersize=3, label='Energy Price')
        
        ax3.set_xlabel('Hour')
        ax3.set_ylabel('Cost/Revenue (DKK)', color='black')
        ax3_twin.set_ylabel('Energy Price (DKK/kWh)', color='black')
        ax3.set_title('Hourly Costs and Energy Prices')
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim(0.5, 24.5)
        
        # Combine legends
        lines1, labels1 = ax3.get_legend_handles_labels()
        lines2, labels2 = ax3_twin.get_legend_handles_labels()
        ax3.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # Plot 4: Summary statistics
        ax4.axis('off')
        summary_stats = processed_results['summary_stats']
        
        summary_text = f"""
        OPTIMIZATION RESULTS SUMMARY
        
        Total Daily Cost: {summary_stats['total_cost']:.2f} DKK
        
        Energy Balance:
        • Total Consumption: {summary_stats['total_energy_consumed']:.2f} kWh
        • Total PV Used: {summary_stats['total_pv_used']:.2f} kWh
        • Self-Consumption Rate: {summary_stats['self_consumption_rate']*100:.1f}%
        
        Grid Interactions:
        • Total Imported: {summary_stats['total_imported']:.2f} kWh
        • Total Exported: {summary_stats['total_exported']:.2f} kWh
        • Net Import: {summary_stats['net_import']:.2f} kWh
        
        PV Utilization:
        • PV Generation: {summary_stats['total_pv_generated']:.2f} kWh
        • PV Utilization: {summary_stats['pv_utilization_rate']*100:.1f}%
        
        Price Statistics:
        • Average Price: {summary_stats['avg_energy_price']:.2f} DKK/kWh
        • Price Range: {summary_stats['min_energy_price']:.2f} - {summary_stats['peak_energy_price']:.2f} DKK/kWh
        """
        
        ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        
        # Save plot if path provided
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Energy schedule plot saved to {save_path}")
        
        self.plots['energy_schedule'] = fig
        return fig

    def plot_cost_breakdown(self, processed_results: dict, save_path: Optional[str] = None) -> mfig.Figure:
        """Create a detailed cost breakdown visualization."""
        hourly_data = pd.DataFrame(processed_results['hourly_data'])
        summary_stats = processed_results['summary_stats']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Cost Analysis', fontsize=16, fontweight='bold')
        
        # Hourly cost breakdown
        ax1.bar(hourly_data['hour'], hourly_data['import_cost'], alpha=0.8, 
                color='red', label='Import Cost')
        ax1.bar(hourly_data['hour'], -hourly_data['export_revenue'], alpha=0.8, 
                color='green', label='Export Revenue')
        
        net_cost = hourly_data['import_cost'] - hourly_data['export_revenue']
        ax1.plot(hourly_data['hour'], net_cost, color='black', linewidth=2, 
                marker='o', markersize=4, label='Net Hourly Cost')
        
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax1.set_xlabel('Hour')
        ax1.set_ylabel('Cost (DKK)')
        ax1.set_title('Hourly Cost Breakdown')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(0.5, 24.5)
        
        # Total cost components pie chart
        total_import_cost = hourly_data['import_cost'].sum()
        total_export_revenue = hourly_data['export_revenue'].sum()
        
        if total_export_revenue > 0:
            costs = [total_import_cost, total_export_revenue]
            labels = [f'Import Costs\n{total_import_cost:.2f} DKK', 
                     f'Export Revenue\n{total_export_revenue:.2f} DKK']
            colors = ['red', 'green']
            
            wedges, texts, autotexts = ax2.pie(costs, labels=labels, colors=colors, autopct='%1.1f%%',
                                              startangle=90, textprops={'fontsize': 10})
            ax2.set_title(f'Cost Components\nNet Cost: {summary_stats["total_cost"]:.2f} DKK')
        else:
            ax2.text(0.5, 0.5, f'Total Cost: {summary_stats["total_cost"]:.2f} DKK\n(No exports)', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=12)
            ax2.set_title('Cost Summary')
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Cost breakdown plot saved to {save_path}")
        
        self.plots['cost_breakdown'] = fig
        return fig

    def plot_pv_utilization(self, processed_results: dict, save_path: Optional[str] = None) -> mfig.Figure:
        """Create PV utilization and self-consumption analysis."""
        hourly_data = pd.DataFrame(processed_results['hourly_data'])
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle('PV Generation and Utilization Analysis', fontsize=16, fontweight='bold')
        
        # PV generation vs utilization
        ax1.fill_between(hourly_data['hour'], 0, hourly_data['pv_available'], 
                        alpha=0.3, color='gold', label='PV Available')
        ax1.fill_between(hourly_data['hour'], 0, hourly_data['pv_used'], 
                        alpha=0.7, color='orange', label='PV Used')
        ax1.fill_between(hourly_data['hour'], hourly_data['pv_used'], 
                        hourly_data['pv_available'], 
                        alpha=0.5, color='red', label='PV Curtailed')
        
        ax1.set_xlabel('Hour')
        ax1.set_ylabel('Power (kW)')
        ax1.set_title('PV Generation vs Utilization')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(1, 24)
        
        # Self-consumption and export pattern
        bars1 = ax2.bar(hourly_data['hour'], hourly_data['load'], alpha=0.7, 
                       color='blue', label='Total Load')
        bars2 = ax2.bar(hourly_data['hour'], hourly_data['pv_used'], alpha=0.7, 
                       color='orange', label='PV Self-Consumption')
        
        # Add export as negative bars
        ax2.bar(hourly_data['hour'], -hourly_data['export'], alpha=0.7, 
               color='green', label='PV Export')
        
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax2.set_xlabel('Hour')
        ax2.set_ylabel('Power (kW)')
        ax2.set_title('Load Coverage and PV Export')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0.5, 24.5)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ PV utilization plot saved to {save_path}")
        
        self.plots['pv_utilization'] = fig
        return fig

    def create_summary_dashboard(self, processed_results: dict, save_path: Optional[str] = None) -> mfig.Figure:
        """Create a comprehensive dashboard with all key visualizations."""
        # This combines multiple smaller plots into one dashboard
        fig = plt.figure(figsize=(20, 12))
        
        # Create a grid layout
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        hourly_data = pd.DataFrame(processed_results['hourly_data'])
        summary_stats = processed_results['summary_stats']
        
        # Main energy flow plot (spans 2 columns)
        ax_main = fig.add_subplot(gs[0, :2])
        ax_main.plot(hourly_data['hour'], hourly_data['pv_available'], 'gold', linewidth=3, 
                    label='PV Available', marker='o')
        ax_main.plot(hourly_data['hour'], hourly_data['load'], 'blue', linewidth=3, 
                    label='Load', marker='^')
        ax_main.bar(hourly_data['hour'], hourly_data['import'], alpha=0.6, 
                   color='red', label='Import')
        ax_main.bar(hourly_data['hour'], -hourly_data['export'], alpha=0.6, 
                   color='green', label='Export')
        ax_main.set_title('Energy Flow Overview', fontsize=14, fontweight='bold')
        ax_main.legend()
        ax_main.grid(True, alpha=0.3)
        
        # Cost analysis (top right)
        ax_cost = fig.add_subplot(gs[0, 2])
        net_cost = hourly_data['import_cost'] - hourly_data['export_revenue']
        ax_cost.plot(hourly_data['hour'], net_cost, 'black', linewidth=2)
        # Fill areas based on positive/negative values
        for i in range(len(net_cost)):
            if net_cost.iloc[i] > 0:
                ax_cost.bar(hourly_data['hour'].iloc[i], net_cost.iloc[i], 
                          alpha=0.6, color='red', width=0.8)
            elif net_cost.iloc[i] < 0:
                ax_cost.bar(hourly_data['hour'].iloc[i], net_cost.iloc[i], 
                          alpha=0.6, color='green', width=0.8)
        ax_cost.set_title('Hourly Net Cost', fontsize=12)
        ax_cost.grid(True, alpha=0.3)
        
        # More detailed plots can be added to the remaining subplots...
        
        # Summary statistics (bottom)
        ax_summary = fig.add_subplot(gs[2, :])
        ax_summary.axis('off')
        
        summary_text = f"""
        OPTIMIZATION DASHBOARD SUMMARY
        
        Economic Results: Total Cost = {summary_stats['total_cost']:.2f} DKK | Avg. Price = {summary_stats['avg_energy_price']:.2f} DKK/kWh
        
        Energy Balance: Consumption = {summary_stats['total_energy_consumed']:.1f} kWh | PV Used = {summary_stats['total_pv_used']:.1f} kWh | Self-Consumption = {summary_stats['self_consumption_rate']*100:.1f}%
        
        Grid Interaction: Imported = {summary_stats['total_imported']:.1f} kWh | Exported = {summary_stats['total_exported']:.1f} kWh | Net Import = {summary_stats['net_import']:.1f} kWh
        """
        
        ax_summary.text(0.5, 0.5, summary_text, transform=ax_summary.transAxes, 
                       fontsize=12, ha='center', va='center',
                       bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        plt.suptitle('Consumer Energy Flexibility - Optimization Dashboard', 
                     fontsize=18, fontweight='bold')
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Dashboard saved to {save_path}")
        
        self.plots['dashboard'] = fig
        return fig

    def save_all_plots(self, output_dir: str = "plots", formats: List[str] = ['png', 'pdf']):
        """Save all generated plots to specified directory."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        for plot_name, fig in self.plots.items():
            for fmt in formats:
                filename = output_path / f"{plot_name}.{fmt}"
                fig.savefig(filename, dpi=300, bbox_inches='tight', format=fmt)
        
        print(f"✓ All plots saved to {output_path}/ in formats: {formats}")

    def show_all_plots(self):
        """Display all generated plots."""
        plt.show()
