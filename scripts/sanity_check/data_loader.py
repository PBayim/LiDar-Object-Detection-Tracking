#!/usr/bin/python3 

import os
import pandas as pd 
from typing import List


class LidarDataLoader:
    """A class to load LiDAR data in csv format from a specified directory
    """
    
    def __init__(self, data_dir: str):
        """

        Args:
            data_dir (str): The path to the directory containing LiDAR csv files
            with nested subdirectories
        """
        print("Initialized DataLoader")
        if not os.path.isdir(data_dir):
            print(f"The path {data_dir} doesn't exist")
            raise FileNotFoundError(f"The path {data_dir} doesn't exist")
        self.data_dir = data_dir
        
    
    def load_data(self) -> List[pd.DataFrame]:
        """Searches the datadirectory and its subdirectories for csv files and
        returns them all as a list of Dataframes

        Returns:
            List[pd.DataFrame]: List of Dataframes, each corresponding to one csv file
        """
        
        dataframes = []
        for root, dirs, files in os.walk(self.data_dir):
            for filename in files:
                if filename.lower().endswith(".csv"):
                    filepath = os.path.join(root, filename)
                    # print(filename)
                    df = pd.read_csv(filepath, delimiter=";")
                    dataframes.append(df)
                    
        return dataframes