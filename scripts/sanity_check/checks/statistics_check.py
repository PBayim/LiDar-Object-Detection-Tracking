#!/usr/bin/python3 

import numpy as np 
import pandas as pd 
from .base_check import BaseCheck


class StaticticsCheck(BaseCheck):
    """A check class that computes descriptive statistics for specified columns 
    and flags potential issues such as too many outliers or invalid distributions
    """
    
    def __init__(self,
                 columns_to_check=None,
                 outlier_method="zscore",
                 zscore_threshold=3.5,
                 iqr_threshold=3.0,
                 max_outlier_ratio=0.05):
        """

        Args:
            columns_to_check (_type_, optional):  If None, Defaults to ["DISTANCE", "INTENSITY"]
            outlier_method (str, optional):  Defaults to "zscore".
            zcore_threshold (float, optional):  Defaults to 3.5.
            iqr_threshold (float, optional):  Defaults to 3.0.
            max_outlier_ratio (float, optional):  Defaults to 0.05.
        """
        
        if columns_to_check is None:
            columns_to_check = ["DISTANCE", "INTENSITY"]
        self.columns_to_check = columns_to_check
        self.outlier_method = outlier_method
        self.zscore_threshold = zscore_threshold
        self.iqr_factor = iqr_threshold
        self.max_outlier_ratio = max_outlier_ratio
    
    
    def run_check(self, df: pd.DataFrame) -> dict:
        """For each specified column, compute mean, std, min, max, median, etc...
        Then detect outliers based on zscore or IQR

        Args:
            df (pd.DataFrame): Dataframe reprensation a LiDAR frame / CSV file

        Returns:
            dict: Dictionary with pass/fail info, outlier details, and stats
        """

        result = {
            "check_name": "StatisticsCheck",
            "passed": True,
            "details": {},
            "messages": []
        }
        
        for col in self.columns_to_check:
            if col not in df.columns:
                result["passed"] = False
                msg = f"Column `{col}` not found in Dataframe"
                result["messages"].append(msg)
                continue 
            
            # Drop NaN/inf values to avoid errors
            data = df[col].dropna().replace([np.inf, -np.inf], np.nan).dropna()
            if data.empty: # If not valid data points
                result["passed"] = False
                msg = f"Column `{col}` has no valied data (NaN/Inf)"
                result["messages"].append(msg)
                continue 
            
            # Compute basic stats
            col_min = data.min()
            col_max = data.max()
            col_mean = data.mean()
            col_median = data.median()
            col_std = data.std()
            n_points = len(data)

            # Outlier detection
            if self.outlier_method == "zscore":
                # Z-score: (x - mean) / std
                # large absolute values => outlier
                z_scores = (data - col_mean) / (col_std + 1e-10)
                outliers = data[np.abs(z_scores) > self.zscore_threshold]
            elif self.outlier_method == "iqr":
                # IQR-based: outliers lie outside [Q1 - factor*IQR, Q3 + factor*IQR]
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - self.iqr_factor * IQR
                upper_bound = Q3 + self.iqr_factor * IQR
                outliers = data[(data < lower_bound) | (data > upper_bound)]
            else:
                # Default fallback: no outlier detection
                outliers = pd.Series(dtype=data.dtype)

            outlier_count = len(outliers)
            outlier_ratio = outlier_count / n_points if n_points > 0 else 0.0

            # Mark as failed if outlier ratio is too high
            column_passed = True
            if outlier_ratio > self.max_outlier_ratio:
                column_passed = False
                result["passed"] = False
                msg = (
                    f"Column '{col}': outlier ratio {outlier_ratio:.2%} "
                    f"exceeds threshold of {self.max_outlier_ratio:.2%}."
                )
                result["messages"].append(msg)

            # Store stats & outlier info
            result["details"][col] = {
                "column_passed": column_passed,
                "count": n_points,
                "min": col_min,
                "max": col_max,
                "mean": col_mean,
                "median": col_median,
                "std": col_std,
                "outlier_count": outlier_count,
                "outlier_ratio": outlier_ratio,
                "outlier_method": self.outlier_method
            }

        return result