# DTU Optimization Assignment 1 - Consumer Energy Flexibility

## Overview

This repository contains a complete solution for **Group Assignment 1** in the course **46750 - Optimization in Modern Power Systems**. The project implements optimization models for consumer energy flexibility analysis using mixed-integer linear programming (MILP) with Gurobi solver.

### 🎯 Assignment Scope

The project addresses consumer energy management optimization across multiple scenarios:

- **Question 1a**: Basic consumer flexibility optimization with DER integration
- **Question 1b**: Multi-consumer type analysis (Tech Enthusiast, Work-from-Home, Traditional Family, Senior)  
- **Question 1c**: Battery storage integration for enhanced flexibility
- **Question 2**: Battery investment analysis and payback calculations

### 🏗️ Key Features

- **Modular Architecture**: Clean separation between data operations, optimization models, and execution
- **Multiple Execution Options**: Run via interactive menu, command line, or individual scripts
- **Comprehensive Visualization**: Automated plot generation for all scenarios
- **Extensible Design**: Easy to add new consumer types, appliances, or optimization scenarios
- **Professional Documentation**: Detailed code documentation and usage examples

## Installation

Follow the installation instructions below to start working on your group assignment.

### 1. **Clone the repository**

To begin, create a copy of this repository for your group. 

### 2. **Create a virtual environment**

Follow these steps to set up a clean Python environment and install the required packages, so that all required packages are installed when running your code, and your project packages won’t affect the system or other projects.

#### **Option A: Using pip**

To create an isolated Python environment in a folder called venv (its own Python interpreter + its own site-packages and pip):
```bash
python -m venv venv 
```
Then activate that environment (on macOS/Linux):
```bash
source venv/bin/activate 
```
Or, using Windows cmd: `\venv\Scripts\Activate.ps1` or Windows PowerShell: `venv\Scripts\Activate.ps1`. Your shell’s PATH is changed so python/pip now point to the ones inside venv.

Install all packages listed in requirements.txt into the active virtual environment (modify the requirements file as needed).
```bash
pip install -r requirements.txt
```

#### **Option B: Using conda**

Create and activate a virtual environment, using the file environment.yaml (modify the environment file as needed):
```bash
conda env create -f environment.yaml
conda activate gurobi-opt
``` 

## 🚀 Quick Start

### Option 1: Interactive Menu (Recommended)
```bash
python src/main.py
```
This launches an interactive menu where you can select which question to run.

### Option 2: Command Line
```bash
# Run specific questions directly
python src/main.py --question 1a_iv   # Q1a part iv
python src/main.py --question 1a_v    # Q1a part v (tariff analysis)
python src/main.py --question 1b_v    # Q1b part v (consumer types)
python src/main.py --question 1c_v    # Q1c part v (battery storage)
python src/main.py --question 2b      # Q2b (investment analysis)

# List all available questions
python src/main.py --list
```

### Option 3: Individual Scripts
```bash
# Run scripts directly for more control
python src/scripts/q1a_iv.py    # Basic optimization
python src/scripts/q1a_v.py     # Tariff scenario analysis
python src/scripts/q1b_v.py     # Consumer type comparison
python src/scripts/q1c_v.py     # Battery storage analysis  
python src/scripts/q2b.py       # Investment analysis
```

### 📊 Results

All results are automatically saved to the `results/` directory:
- **Plots**: PNG files for all visualizations

## 📁 Project Architecture

The codebase follows a modular architecture for maintainability and extensibility:

```
├── src/
│   ├── main.py                 # Central entry point with menu system
│   ├── data_ops/              # Data handling operations
│   │   ├── data_loader.py     # JSON data loading and validation
│   │   ├── data_processor.py  # Data preprocessing for optimization
│   │   └── data_visualizer.py # Plot generation and visualization
│   ├── opt_model/             # Optimization model implementations
│   │   ├── opt_model_Q1a.py   # Q1a: Basic consumer flexibility
│   │   ├── opt_model_Q1b.py   # Q1b: Multi-consumer analysis  
│   │   ├── opt_model_Q1c.py   # Q1c: Battery storage integration
│   │   └── opt_model_Q2b.py   # Q2b: Investment optimization
│   ├── runner/                # Workflow orchestration
│   │   └── runner.py          # End-to-end simulation runner
│   ├── scripts/               # Individual question executables
│   │   ├── q1a_iv.py         # Q1a part iv solver
│   │   ├── q1a_v.py          # Q1a part v tariff analysis
│   │   ├── q1b_v.py          # Q1b consumer type analysis
│   │   ├── q1c_v.py          # Q1c battery analysis
│   │   └── q2b.py            # Q2b investment analysis
│   └── utils/                 # Utility functions
│       └── utils.py           # Helper functions and constants
├── data/                      # Input datasets by question
├── results/                   # Generated outputs and plots
└── requirements.txt           # Python dependencies
```

### 🔧 Core Modules

#### `data_ops/` - Data Operations
- **`data_loader.py`**: Loads and validates JSON input files for consumers, appliances, usage preferences, DER production, and bus parameters
- **`data_processor.py`**: Transforms raw data into optimization-ready formats, handles time series processing and constraint preparation
- **`data_visualizer.py`**: Creates comprehensive plots for cost analysis, energy flows, battery states, and scenario comparisons

#### `opt_model/` - Optimization Models  
- **`opt_model_Q1a.py`**: Consumer flexibility optimization with DER integration, flexible loads, and grid interaction
- **`opt_model_Q1b.py`**: Multi-consumer scenario analysis with different user behavior patterns
- **`opt_model_Q1c.py`**: Battery storage optimization with state-of-charge constraints and cycling efficiency
- **`opt_model_Q2b.py`**: Investment analysis model for battery sizing and payback calculations

#### `runner/` - Workflow Management
- **`runner.py`**: Orchestrates complete simulation workflows from data loading through result visualization

#### `scripts/` - Executable Scripts
Individual scripts for each assignment question that can be run independently or through the main dispatcher.

## Input Data Structure

The repositories include base datasets under the `data/question_name` directories, organized as follows:

- **Consumers Data (`consumers.json`)**  
    Contains a list of consumers, each with:
    - `consumer_id`: Unique identifier for the consumer
    - `connection_bus`: Bus ID where the consumer is connected
    - `list_appliances`: List of appliance IDs owned by the consumer

- **Appliances Data (`appliance_params.json`)**  
    Contains a list of all appliances and their technical characteristics. Each appliance entry includes:

    - **For DERs (Distributed Energy Resources):**
        - `DER_id`: Unique identifier for the DER appliance
        - `DER_type`: DER technology type (e.g., "PV" for solar photovoltaic, "wind" for wind turbine)
        - `max_power_kW`: Maximum power output (kW)
        - `min_power_ratio`: Minimum operating power as a fraction of max power (unitless, 0–1)
        - `max_ramp_rate_up_ratio`: Maximum allowed increase in power per time step, as a fraction of max power (unitless, 0–1)
        - `max_ramp_rate_down_ratio`: Maximum allowed decrease in power per time step, as a fraction of max power (unitless, 0–1)

    - **For Loads:**
        - `load_id`: Unique identifier for the load appliance
        - `load_type`: Type of load (e.g., "EV", "heater")
        - `max_load_kWh_per_hour`: Maximum energy consumption per hour (kWh/h)
        - `max_ramp_rate_up_ratio`: Maximum allowed increase in load per time step, as a fraction of max load (unitless, 0–1)
        - `max_ramp_rate_down_ratio`: Maximum allowed decrease in load per time step, as a fraction of max load (unitless, 0–1)
        - `min_on_time_h`: Minimum consecutive hours the load must stay ON (h)
        - `min_off_time_h`: Minimum consecutive hours the load must stay OFF (h)

    - **For Storages:**
        - `storage_id`: Unique identifier for the storage appliance
        - `storage_capacity_kWh`: Total energy storage capacity (kWh)
        - `max_charging_power_ratio`: Maximum charging power as a fraction of storage capacity per hour (unitless, 0–1)
        - `max_discharging_power_ratio`: Maximum discharging power as a fraction of storage capacity per hour (unitless, 0–1)
        - `charging_efficiency`: Fraction of energy retained during charging (unitless, 0–1)
        - `discharging_efficiency`: Fraction of energy retained during discharging (unitless, 0–1)

**Note:** All ratios are relative to the respective appliance's maximum capacity or power. Units are indicated in parentheses.
    

- **Usage Preferences (`usage_preference.json`)**  
    Specifies user-defined preferences and constraints for energy usage and appliance operation. Example structure:
    - `consumer_id`: Unique identifier for the consumer
    - `_preferences`: containing
        - **Grid preferences**: Preferences for grid interaction (e.g., "prefer self-consumption", "allow export up to X kWh")
        - **DER preferences**: Preferences for usage of distributed energy resources (e.g., "curtailment cost", "limit wind export", "green consumption ratio")
        - **Load preferences**: Preferences for consumption (daily/hourly) and flexibility:
            - `load_id`: Unique load identifier
            - `min_total_energy_per_day_hour_equivalent`: Minimum daily energy usage (kWh or equivalent hours)
            - `max_total_energy_per_day_hour_equivalent`: Maximum daily energy usage (kWh or equivalent hours)
            - `hourly_profile_ratio`: Desired hourly usage pattern (array of ratios)
        - **Storages**: Preferences for usage of energy storage:
            - `storage_id`: Unique storage identifier
            - `initial_soc_ratio`: Initial state of charge (0–1)
            - `final_soc_ratio`: Desired final state of charge (0–1)
        - **Heat pumps**: Preferences for heat pump operation (e.g., "min runtime", "preferred hours")

- **DER Production (`DER_production.json`)**  
    Contains time series data for DER output profiles at each consumer location.
    - `consumer_id`: Location where the DER is evaluated
    - `DER_type`: Type of DER (e.g., "PV", "wind")
    - `hourly_profile_ratio`: Array of normalized hourly production values (0–1)

- **Bus Data (`bus_params.json`)**  
    Defines technical and economic parameters for each network bus.
    - `bus_id`: Unique bus identifier
    - `import_tariff`: Tariff for net energy import (DKK/kWh)
    - `export_tariff`: Tariff for net energy export (DKK/kWh)
    - `max_import_kw`: Maximum allowed import power (kW)
    - `max_export_kw`: Maximum allowed export power (kW)
    - `price_DKK_per_kWh`: Additional price information if applicable

**Note:**  
These files allow customization of user behavior, DER production, and network constraints for simulation and optimization. The data structure is designed for compatibility with the optimization models and easy extension for new scenarios.

## 💡 Usage Examples

### Example 1: Run Complete Analysis
```bash
# Interactive menu - select multiple questions
python src/main.py

# Or run all questions in sequence
python src/main.py --question 1a_iv
python src/main.py --question 1a_v  
python src/main.py --question 1b_v
python src/main.py --question 1c_v
python src/main.py --question 2b
```

### Example 2: Custom Analysis
```python
# Run custom optimization with modified data
from src.runner.runner import Runner
from src.data_ops.data_loader import DataLoader

# Load and modify data
loader = DataLoader()
data = loader.load_data("question_1a")

# Modify tariffs for sensitivity analysis
data['bus_params'][0]['import_tariff'] *= 1.5  # 50% higher import tariff

# Run optimization with modified data
runner = Runner()
results = runner.run_custom_simulation(data)
```

### Example 3: Batch Processing
```python
# Run multiple scenarios with different parameters
scenarios = [
    {"name": "base_case", "import_multiplier": 1.0},
    {"name": "high_tariff", "import_multiplier": 1.5}, 
    {"name": "low_tariff", "import_multiplier": 0.7}
]

for scenario in scenarios:
    # Modify data and run optimization
    # Compare results across scenarios
```

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 1. Gurobi License Error
```
Error: Model too large for restricted Gurobi license
```
**Solution**: 
- Ensure academic license is installed: `grbgetkey YOUR_LICENSE_KEY`
- Check license status: `python -c "import gurobipy; print(gurobipy.gurobi.version())"`

#### 2. Module Import Errors
```
ModuleNotFoundError: No module named 'src.data_ops'
```
**Solution**:
- Run from project root directory
- Or add to Python path: `export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"`

#### 3. Data File Not Found
```
FileNotFoundError: data/question_1a/appliance_params.json
```
**Solution**:
- Verify data files exist in correct directory structure
- Check file names match exactly (case-sensitive)

#### 4. Optimization Infeasible
```
Optimization was terminated with status INFEASIBLE
```
**Solution**:
- Check constraint compatibility in usage preferences
- Verify energy balance feasibility
- Review appliance power ratings vs. requirements

### Performance Tips

1. **Large Models**: Use Gurobi parameters for better performance:
   ```python
   model.setParam('Threads', 4)
   model.setParam('MIPGap', 0.01)
   ```

2. **Memory Usage**: Process data in chunks for large datasets

3. **Debugging**: Enable detailed logging:
   ```python
   model.setParam('OutputFlag', 1)  # Show solver output
   ```

## 📊 Expected Results

### Question 1a Results
- **Daily Cost**: ~15-25 DKK depending on tariff scenario
- **PV Utilization**: 60-80% self-consumption
- **Grid Interaction**: Balanced import/export patterns

### Question 1b Results  
- **Consumer Variation**: 20-30% cost difference between consumer types
- **Flexibility Value**: Tech enthusiasts save 15-20% vs. traditional users
- **Load Patterns**: Clear differentiation in usage profiles

### Question 1c Results
- **Battery Value**: 10-15% additional cost savings
- **Storage Utilization**: 80-90% cycling efficiency
- **Grid Support**: Reduced peak import/export

### Question 2 Results
- **Investment Analysis**: 3-7 year payback period
- **Optimal Sizing**: 5-15 kWh capacity range
- **Sensitivity**: High dependence on tariff structure

## 🔄 Optimization Workflow

The optimization process follows a structured pipeline:

### 1. Data Loading & Validation
```python
# Load raw JSON data files
data_loader = DataLoader(base_path="data")
raw_data = data_loader.load_data("question_1a")
```
- Validates JSON schema compliance
- Checks data consistency across files
- Handles missing values and defaults

### 2. Data Processing
```python
# Transform for optimization model
data_processor = DataProcessor()
optimization_data = data_processor.process_for_optimization(raw_data)
```
- Converts time series to matrix format
- Calculates derived parameters (ramp rates, efficiency factors)
- Prepares constraint coefficient matrices

### 3. Model Creation & Solving
```python
# Create and solve optimization model
model = ConsumerFlexibilityModel(optimization_data)
results = model.solve()
```
- Builds MILP formulation with Gurobi
- Applies consumer flexibility constraints
- Optimizes over 24-hour horizon

### 4. Result Processing & Visualization
```python
# Generate plots and save results
visualizer = DataVisualizer()
visualizer.create_comprehensive_plots(results, save_path="results/")
```
- Produces cost breakdown analysis
- Visualizes energy flows and battery states  
- Generates comparison plots across scenarios

## 🧮 Key Functions & Classes

### Core Optimization Classes

#### `ConsumerFlexibilityModel` (Q1a)
**Purpose**: Basic consumer energy flexibility optimization
**Key Methods**:
- `_create_variables()`: Decision variables for energy flows, appliance states
- `_create_constraints()`: Energy balance, appliance limits, grid constraints
- `_create_objective()`: Minimize total daily energy cost
- `solve()`: Execute optimization and return results

#### `MultiConsumerModel` (Q1b)  
**Purpose**: Analyze different consumer behavior patterns
**Key Features**:
- Consumer type differentiation (Tech Enthusiast, Traditional Family, etc.)
- Varying usage preferences and flexibility levels
- Comparative cost analysis across consumer types

#### `BatteryStorageModel` (Q1c)
**Purpose**: Integrate battery storage for enhanced flexibility
**Key Constraints**:
- State-of-charge (SoC) dynamics
- Charging/discharging efficiency
- Power rating limitations
- Energy capacity constraints

### Data Processing Functions

#### `DataLoader.load_data(question_name)`
**Purpose**: Load all JSON files for a specific question
**Returns**: Dictionary with consumers, appliances, preferences, DER production, bus parameters
**Validation**: Checks file existence, JSON validity, required fields

#### `DataProcessor.process_for_optimization(raw_data)`
**Purpose**: Transform raw data into optimization-ready format
**Operations**:
- Time series normalization
- Parameter matrix construction  
- Constraint coefficient calculation
- Default value assignment

### Visualization Functions

#### `DataVisualizer.create_cost_breakdown_plot()`
- Stacked bar charts for cost components
- Import/export tariff analysis
- Daily cost comparison across scenarios

#### `DataVisualizer.create_energy_flow_plot()`
- Hourly energy balance visualization
- Load vs. generation profiles
- Battery charging/discharging patterns

#### `DataVisualizer.create_battery_analysis_plot()`
- State-of-charge time series
- Charging efficiency analysis
- Battery utilization metrics

## 📈 Optimization Model Details

### Decision Variables
- **Energy flows**: Import/export from grid, DER production, load consumption
- **Battery states**: Charging/discharging power, state-of-charge
- **Appliance control**: On/off states, power levels for flexible loads

### Objective Function
Minimize total daily cost:
```
minimize: Σt [import_tariff[t] × import[t] - export_tariff[t] × export[t]]
```

### Key Constraints
1. **Energy Balance**: Generation + Import = Load + Export + Battery Charging
2. **Appliance Limits**: Power within rated capacities, ramp rate limits
3. **Battery Dynamics**: SoC evolution with charging/discharging efficiency
4. **Grid Limits**: Import/export within bus capacity constraints
5. **User Preferences**: Minimum/maximum daily energy requirements


