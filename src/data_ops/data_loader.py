# -----------------------------
# Load Data
# -----------------------------
import json
import csv
import pandas as pd
from pathlib import Path


class DataLoader:
    """
    Loads energy system input data from JSON and CSV files.
    
    Responsibilities:
    - Read files from specified directories
    - Parse JSON and CSV data
    - Store raw data without processing
    
    Example usage:
    >>> data_loader = DataLoader()
    >>> raw_data = data_loader.load_data('question_1a')
    """

    def __init__(self, base_path: str = "data"):
        """Initialize the DataLoader with base data path."""
        self.base_path = Path(base_path)

    def load_data(self, question_name: str) -> dict:
        """
        Load all data files for a specific question.
        
        Args:
            question_name: Name of the question folder (e.g., 'question_1a')
            
        Returns:
            Dictionary containing raw data from all files
        """
        question_path = self.base_path / question_name
        
        if not question_path.exists():
            raise FileNotFoundError(f"Question folder {question_path} not found")
        
        # Load all data files in the question directory
        data = self._load_dataset(question_path)
        
        print(f"Successfully loaded {len(data)} data files for {question_name}")
        return data
        
    def _load_dataset(self, question_path: Path) -> dict:
        """Helper function to load all JSON and CSV files in the question directory."""
        data = {}
        
        # Load JSON files
        for file_path in question_path.glob("*.json"):
            file_key = file_path.stem  # filename without extension
            
            try:
                with open(file_path, 'r') as f:
                    data[file_key] = json.load(f)
                print(f"+ Loaded {file_key}.json")
            except Exception as e:
                print(f"- Error loading {file_path}: {e}")
        
        # Load CSV files (if any)
        for file_path in question_path.glob("*.csv"):
            file_key = file_path.stem
            
            try:
                data[file_key] = pd.read_csv(file_path)
                print(f"+ Loaded {file_key}.csv")
            except Exception as e:
                print(f"- Error loading {file_path}: {e}")
                
        return data

    def load_data_file(self, question_name: str, file_name: str):
        """
        Load a specific data file.
        
        Args:
            question_name: Name of the question folder
            file_name: Name of the specific file to load
            
        Returns:
            Loaded data from the specified file
        """
        question_path = self.base_path / question_name
        file_path = question_path / file_name
        
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} not found")
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r') as f:
                return json.load(f)
        elif file_path.suffix.lower() == '.csv':
            return pd.read_csv(file_path)
        else:
            with open(file_path, 'r') as f:
                return f.read()