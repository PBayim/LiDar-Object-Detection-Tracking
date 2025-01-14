#!/usr/bin/python3 

from .base_check import BaseCheck
import pandas as pd 


class RangeCheck(BaseCheck):
    """A check to sensure that values in a particular numeric column ("DISTANCE" in this case)
    are within a specific min/max range
    """
    
    def __init__(self, col : str="DISTANCE", min_val : float=50.0, max_val : float= 250.0):
        """

        Args:
            col (str, optional): Name of the column to check. Defaults to "DISTANCE".
            min_val (float, optional): Minimum value (inclusive). Defaults to 50.0.
            max_val (float, optional): Maximum value (inclusive). Defaults to 250.0.
        """ 
        self.col = col
        self.min_val = min_val
        self.max_val = max_val
    
    def run_check(self, df: pd.DataFrame) -> dict:
        """Checks wether the specified column is present and wheter its values

        Args:
            df (pd.DataFrame): A Dataframe representing a single LiDAR frame in CSV form 

        Returns:
            dict: A dictionary with pass/fail info any relevant details. 
        """
        
        result = {
            "check_name": "RangeCheck",
            "column": self.col,
            "passed": True,
            "out_of_range_indices": []
        }
        
        # Ensure the required column exists 
        if self.col not in df.columns:
            result["passed"] = False 
            result["message"] = f"Missing column: {self.col}"
            return result
        
        # Identity out-of-range values 
        out_of_range_mask = (df[self.col] < self.min_val) | (df[self.col] > self.max_val)
        out_of_range_df = df[out_of_range_mask]
        
        if not out_of_range_df.empty:
            # Mark as fail if any values are out o the expected range
            result["passed"] = False
            result["out_of_range_indices"] = out_of_range_df.index.to_list()
            result["message"] = (
                f"{len(out_of_range_df)} rows have {self.col} values."
                f"outside [{self.min_val}, {self.max_val}]."
            )