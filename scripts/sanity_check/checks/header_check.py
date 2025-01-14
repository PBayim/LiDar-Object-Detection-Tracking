#!/usr/bin/python3 

from .base_check import BaseCheck
import pandas as pd

class HeaderCheck(BaseCheck):
    """A check to ensure that the dataframe has the expected column headers
    """
    
    def __init__(self, required_columns=None):
        """

        Args:
            required_columns (_type_, optional): A list of column names that must be present.
            If not provided, default to typical lidar columns. 
        """
        
        if required_columns is None:
            required_columns = [
                "X", "Y", "Z", 
                "DISTANCE", "INTENSITY", 
                "POINT_ID", "RETURN_ID", 
                "AMBIENT", "TIMESTAMP"
            ]
        self.required_columns = required_columns
    
    
    def run_check(self, df: pd.DataFrame) -> dict:
        #return super().run_check(df)
        """Ensures that all required columns exist. Logs any missing or unexpected columns. 

        Args:
            df (pd.DataFrame): a single LiDAR frame in csv form 

        Returns:
            dict: A dictionary with pass/fail info and any relevant details
        """
        
        result = {
            "check_name": "HeaderCheck",
            "passed": True,
            "missing_columns": [],
            "unexpected_columns": []
        }
        
        # Current columns in dataframe
        existing_columns = set(df.columns)
        required = set(self.required_columns)
        
        # Identify missing
        missing = required - existing_columns
        
        if missing: 
            result["passed"] = False
            result["missing_columns"] = list(missing)
        
        # Identify unexpected 
        extras = existing_columns - required
        if extras:
            # Not necessarily a fail, but might be worth noting (out of this scope though)
            result["unexpected_columns"] = list(extras)
        
        return result