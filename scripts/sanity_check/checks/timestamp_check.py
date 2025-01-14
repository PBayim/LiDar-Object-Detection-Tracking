#!/usr/bin/python3 

from .base_check import BaseCheck
import pandas as pd 

class TimestampCheck(BaseCheck):
    """A check to ensure the TIMESTAMP column exists and that timestamps do not run backwards. 
    """
    
    def __init__(self, timestamp_col : str = "TIMESTAMP", allow_equal : bool = True):
        """

        Args:
            timestamp_col (str, optional): Defaults to "TIMESTAMP".
            allow_equal (bool, optional): IF True, allows consecutive rows to have the same timestamp. Defaults to True.
                                            (Non-decreasing)If False, requires strictky increasing timestamps. 
        """
        
        self.timestamp_col = timestamp_col
        self.allow_equal = allow_equal
    
    def run_check(self, df: pd.DataFrame) -> dict:
        """Verifies that the specified timestamp column exists and that subsequent 
        timestamps are not in reverse order. Fails if a decreasing timestamp is found 

        Args:
            df (pd.DataFrame): Dataframe from CSV form 

        Returns:
            dict: dictionary with pass/fail info and any relevant details
        """
        
        result = {
            "checkname": "TimestampCheck",
            "passed": True,
            "messages": []
        }
        print(f"df columns : {df.columns}")
        # 1. Verify the column exists
        if self.timestamp_col not in df.columns:
            result["passed"] = False 
            result["messages"].append(
                f"column `{self.timestamp_col}` not found"
            )
            
            return result
        
        # 2. Retrieve timestamps and check ordering
        timestamps = df[self.timestamp_col].values
        
        # 3. Iterate through timestamps to ensure order
        for i in range(1, len(timestamps)):
            if self.allow_equal:
                 # Non-decreasing check (t[i] >= t[i-1])
                 if timestamps[i] < timestamps[i - 1]:
                     result["passed"] = False 
                     result["messages"].append(
                         f"Timestamp decreased at row {i}: "
                         f"{timestamps[i] < {timestamps[i -1]}}."
                     )
            else:
                # Strictly increasingly check (t[i] > t[i - 1])
                if timestamps[i] <= timestamps[i -1]:
                    result["passed"] = False 
                    result["messages"].append(
                        f"Timestamp decreased at row {i}: "
                        f"{timestamps[i] < {timestamps[i -1]}}."
                    )
        return result