#!/usr/bin/python3 

from data_loader import LidarDataLoader
from checks.header_check import HeaderCheck
from checks.range_check import RangeCheck
from checks.timestamp_check import TimestampCheck

def main():
    # 1. Load data 
    loader = LidarDataLoader(data_dir="../../data/192.168.26.26_2020-11-25_20-01-45_frame-1899_part_1")
    dataframes = loader.load_data()
    
    # 2. Instantiate the checks 
    ts_check = TimestampCheck(timestamp_col="TIMESTAMP", allow_equal=False)
    distance_check = RangeCheck(col="DISTANCE", min_val=50.0, max_val=250.0)
    header_check = HeaderCheck()
    
    
    # 3. Run check on each DataFrame
    for i, df in enumerate(dataframes):
        print(f"--- Checking DataFrame #{i} ---")
        
        # # Header check 
        # hc_result = header_check.run_check(df=df)
        # print("Header Check:", hc_result)
        
        # # Timestamp check
        # ts_check_result = ts_check.run_check(df)
        # print("Timestamp Check:", ts_check_result)
        
        # Range Check
        rc_result = distance_check.run_check(df)
        print("Range Check:", rc_result)
        



if __name__ == "__main__":
    main()