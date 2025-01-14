#!/usr/bin/python3 

from abc import ABC, abstractmethod
import pandas as pd 


class BaseCheck(ABC):
    """An abstract base class defining the interface for all sanity-check classes. 
    Each subclass should implement the `run_check` method, which returns a dictionary 
    or a custom object with pass/fail info and additional details.
    """
    
    @abstractmethod
    def run_check(self, df: pd.DataFrame):
        """Performs the check on the given pd.Dataframe

        Args:
            df (pd.DataFrame): The Dataframe containing the Lidar data

        Returns:
            dict: A dictionary with:
            - "check_name": str
            - "passed": bool
        """
        pass 