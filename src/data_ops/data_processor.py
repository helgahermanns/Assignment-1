import json
import csv
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional


class DataProcessor:
    """
    Processes raw data from DataLoader into structured format for optimization.
    
    Responsibilities:
    - Transform raw JSON/CSV data into optimization parameters
    - Validate data consistency and completeness
    - Calculate derived parameters (e.g., hourly PV capacity)
    - Structure data for optimization model input
    
    Example usage:
    >>> processor = DataProcessor()
    >>> opt_data = processor.process_for_optimization(raw_data)
    """

    def __init__(self):
        """Initialize the DataProcessor."""
        self.processed_data = {}

    def process_for_optimization(self, raw_data: dict) -> dict:
        """
        Process raw data into optimization-ready format.
        
        Args:
            raw_data: Dictionary containing raw data from DataLoader
            
        Returns:
            Dictionary containing structured optimization parameters
        """
        print("Processing data for optimization...")
        
        # Extract and process each data component
        bus_params = self._process_bus_parameters(raw_data.get('bus_params'))
        appliance_params = self._process_appliance_parameters(raw_data.get('appliance_params'))
        der_production = self._process_der_production(raw_data.get('DER_production'))
        consumer_params = self._process_consumer_parameters(raw_data.get('consumer_params'))
        
        # Get load max power for unit conversion
        load_max_power = appliance_params.get('FFL_01', {}).get('max_power', 3.0)
        
        # Process usage preferences (needs load_max_power for unit conversion)
        usage_preferences = self._process_usage_preferences(raw_data, load_max_power)
        
        # Calculate derived parameters
        pv_max_hourly = self._calculate_pv_hourly_capacity(
            der_production.get('pv_profile', []),
            appliance_params.get('PV_01', {}).get('max_power', 3.0)
        )
        
        # Structure data for optimization
        optimization_data = {
            'T': 24,  # Time horizon (hours)
            'import_tariff': bus_params.get('import_tariff'),
            'export_tariff': bus_params.get('export_tariff'),
            'max_import': bus_params.get('max_import'),
            'max_export': bus_params.get('max_export'),
            'energy_prices': bus_params.get('energy_prices'),
            'pv_max_hourly': pv_max_hourly,
            'load_max': appliance_params.get('FFL_01', {}).get('max_power', 3.0),
            'min_daily_energy': usage_preferences.get('min_daily_energy'),
            'consumer_id': consumer_params.get('consumer_id'),
            'appliances': appliance_params
        }
        
        # Validate processed data
        self._validate_optimization_data(optimization_data)
        
        print("✓ Data processing completed successfully!")
        return optimization_data

    def _process_bus_parameters(self, bus_data: Optional[List[Dict]]) -> dict:
        """Process bus/grid parameters."""
        if not bus_data or not bus_data[0]:
            raise ValueError("Bus parameters are required but not found")
        
        bus_info = bus_data[0]  # Assuming single bus
        
        return {
            'import_tariff': bus_info['import_tariff_DKK/kWh'],
            'export_tariff': bus_info['export_tariff_DKK/kWh'],
            'max_import': bus_info['max_import_kW'],
            'max_export': bus_info['max_export_kW'],
            'energy_prices': bus_info['energy_price_DKK_per_kWh'],
            'penalty_excess_import': bus_info.get('penalty_excess_import_DKK/kWh', 0),
            'penalty_excess_export': bus_info.get('penalty_excess_export_DKK/kWh', 0)
        }

    def _process_appliance_parameters(self, appliance_data: Optional[Dict]) -> dict:
        """Process appliance parameters (DER and loads)."""
        if not appliance_data:
            raise ValueError("Appliance parameters are required but not found")
        
        appliances = {}
        
        # Process DER (PV) parameters
        if 'DER' in appliance_data and appliance_data['DER']:
            for der in appliance_data['DER']:
                appliances[der['DER_id']] = {
                    'type': 'DER',
                    'der_type': der.get('DER_type', 'PV'),
                    'max_power': der['max_power_kW'],
                    'min_ratio': der['min_power_ratio'],
                    'ramp_up': der['max_ramp_rate_up_ratio'],
                    'ramp_down': der['max_ramp_rate_down_ratio']
                }
                
        # Process load parameters
        if 'load' in appliance_data and appliance_data['load']:
            for load in appliance_data['load']:
                appliances[load['load_id']] = {
                    'type': 'load',
                    'load_type': load.get('load_type', 'flexible'),
                    'max_power': load['max_load_kWh_per_hour'],
                    'min_ratio': load['min_load_ratio'],
                    'ramp_up': load['max_ramp_rate_up_ratio'],
                    'ramp_down': load['max_ramp_rate_down_ratio'],
                    'min_on_time': load.get('min_on_time_h', 0),
                    'min_off_time': load.get('min_off_time_h', 0)
                }
        
        return appliances

    def _process_der_production(self, der_data: Optional[List[Dict]]) -> dict:
        """Process DER production profiles."""
        if not der_data:
            return {'pv_profile': [0.0] * 24}  # Default to no production
        
        der_info = der_data[0]  # Assuming single DER
        
        return {
            'consumer_id': der_info.get('consumer_ID'),
            'der_type': der_info.get('DER_type', 'solar'),
            'pv_profile': der_info.get('hourly_profile_ratio', [0.0] * 24)
        }

    def _process_usage_preferences(self, raw_data: dict, load_max_power: float = 3.0) -> dict:
        """Process usage preferences (handle both singular and plural naming)."""
        usage_key = None
        if 'usage_preference' in raw_data:
            usage_key = 'usage_preference'
        elif 'usage_preferences' in raw_data:
            usage_key = 'usage_preferences'
        
        if not usage_key or not raw_data[usage_key]:
            return {'min_daily_energy': 8.0 * load_max_power}  # Default value in kWh
        
        usage_data = raw_data[usage_key][0]
        load_prefs = usage_data.get('load_preferences', [])
        
        min_daily_energy = 8.0 * load_max_power  # Default in kWh
        if load_prefs:
            # This is in hour-equivalents, need to convert to kWh
            hour_equivalent = load_prefs[0].get('min_total_energy_per_day_hour_equivalent', 8.0)
            # Convert hour-equivalents to kWh: hour_equivalent × max_power
            min_daily_energy = hour_equivalent * load_max_power
            
            print(f"📏 Unit conversion: {hour_equivalent} hour-equiv × {load_max_power} kW = {min_daily_energy} kWh")
        
        return {
            'min_daily_energy': min_daily_energy,
            'grid_preferences': usage_data.get('grid_preferences'),
            'der_preferences': usage_data.get('DER_preferences'),
            'storage_preferences': usage_data.get('storage_preferences'),
            'heat_pump_preferences': usage_data.get('heat_pump_preferences')
        }

    def _process_consumer_parameters(self, consumer_data: Optional[List[Dict]]) -> dict:
        """Process consumer parameters."""
        if not consumer_data:
            return {'consumer_id': 'C1', 'appliances': []}
        
        consumer_info = consumer_data[0]
        
        return {
            'consumer_id': consumer_info.get('consumer_id', 'C1'),
            'connection_bus': consumer_info.get('connection_bus', 'Bus1'),
            'appliances': consumer_info.get('list_appliances', [])
        }

    def _calculate_pv_hourly_capacity(self, pv_profile: List[float], pv_max_power: float) -> List[float]:
        """Calculate hourly PV capacity from profile and maximum power."""
        if len(pv_profile) != 24:
            raise ValueError(f"PV profile must have 24 hours, got {len(pv_profile)}")
        
        return [ratio * pv_max_power for ratio in pv_profile]

    def _validate_optimization_data(self, data: dict) -> None:
        """Validate that optimization data is complete and consistent."""
        required_keys = [
            'T', 'import_tariff', 'export_tariff', 'max_import', 'max_export',
            'energy_prices', 'pv_max_hourly', 'load_max', 'min_daily_energy'
        ]
        
        for key in required_keys:
            if key not in data or data[key] is None:
                raise ValueError(f"Required parameter '{key}' is missing or None")
        
        # Validate time series data
        if len(data['energy_prices']) != data['T']:
            raise ValueError(f"Energy prices must have {data['T']} hours")
        
        if len(data['pv_max_hourly']) != data['T']:
            raise ValueError(f"PV profile must have {data['T']} hours")
        
        # Validate positive values
        if data['min_daily_energy'] <= 0:
            raise ValueError("Minimum daily energy must be positive")
        
        print("✓ Data validation passed")

    def process_results_for_analysis(self, optimization_results: dict, input_data: dict) -> dict:
        """
        Process optimization results for analysis and visualization.
        
        Args:
            optimization_results: Results from optimization model
            input_data: Original input parameters
            
        Returns:
            Processed results ready for analysis and plotting
        """
        # Create detailed hourly analysis
        hourly_data = []
        
        for t in range(input_data['T']):
            hour_data = {
                'hour': t + 1,
                'energy_price': input_data['energy_prices'][t],
                'pv_available': input_data['pv_max_hourly'][t],
                'pv_used': optimization_results['pv_schedule'][t],
                'pv_curtailed': input_data['pv_max_hourly'][t] - optimization_results['pv_schedule'][t],
                'load': optimization_results['load_schedule'][t],
                'import': optimization_results['import_schedule'][t],
                'export': optimization_results['export_schedule'][t],
                'net_import': optimization_results['import_schedule'][t] - optimization_results['export_schedule'][t],
                'import_cost': (input_data['energy_prices'][t] + input_data['import_tariff']) * optimization_results['import_schedule'][t],
                'export_revenue': (input_data['energy_prices'][t] - input_data['export_tariff']) * optimization_results['export_schedule'][t]
            }
            hourly_data.append(hour_data)
        
        # Calculate summary statistics
        summary_stats = {
            'total_cost': optimization_results['optimal_cost'],
            'total_energy_consumed': sum(optimization_results['load_schedule']),
            'total_pv_generated': sum(input_data['pv_max_hourly']),
            'total_pv_used': optimization_results['total_pv_used'],
            'pv_utilization_rate': optimization_results['total_pv_used'] / sum(input_data['pv_max_hourly']) if sum(input_data['pv_max_hourly']) > 0 else 0,
            'self_consumption_rate': optimization_results['total_pv_used'] / optimization_results['total_energy_consumed'] if optimization_results['total_energy_consumed'] > 0 else 0,
            'total_imported': optimization_results['total_imported'],
            'total_exported': optimization_results['total_exported'],
            'net_import': optimization_results['total_imported'] - optimization_results['total_exported'],
            'avg_energy_price': np.mean(input_data['energy_prices']),
            'peak_energy_price': max(input_data['energy_prices']),
            'min_energy_price': min(input_data['energy_prices'])
        }
        
        return {
            'hourly_data': hourly_data,
            'summary_stats': summary_stats,
            'input_parameters': input_data,
            'raw_results': optimization_results
        }