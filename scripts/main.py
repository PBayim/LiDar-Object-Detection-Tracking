#!/usr/bin/python3 

import os, glob

from sanity_check.data_loader import LidarDataLoader
from sanity_check.checks.header_check import HeaderCheck
from sanity_check.checks.range_check import RangeCheck
from sanity_check.checks.timestamp_check import TimestampCheck
from sanity_check.checks.statistics_check import StaticticsCheck
from sanity_check.checks.spatial_consistency_check import SpatialConsistencyCheck
from utils.df_pcd_converter import DFToPCDConverter
from utils.pcd_to_bin_converter import PCDToBINConverter
from utils.text_file_reader import TextFileReader
# from inference.model_inference import OpenPCDetDetector
from OpenPCDet.tools.inference import OpenPCDetDetector
import argparse



def main(sanity_check : bool = False, convert_csv: bool = False, convert_pcd = False, inference : bool = False, data_dir: str = "../data/192.168.26.26_2020-11-25_20-01-45_frame-2566_part_4"):
    # 1. Load data 
    loader = LidarDataLoader(data_dir)
    dataframes = loader.load_data()
    
    if not inference: 
        if sanity_check:
            # 2. Instantiate the checks 
            
            ts_check = TimestampCheck(timestamp_col="TIMESTAMP", allow_equal=False)
            
            distance_check = RangeCheck(col="DISTANCE", min_val=50.0, max_val=250.0)
            
            header_check = HeaderCheck()
            
            stats_check = StaticticsCheck(
                columns_to_check = ["DISTANCE", "INTENSITY"],
                outlier_method="zscore",
                zscore_threshold=3.5,
                max_outlier_ratio=0.03,
                iqr_threshold=3.0
            )
            
            sp_check = SpatialConsistencyCheck(
                x_col="X",
                y_col="Y",
                z_col="Z",
                bounding_box_limits=(-100, 100, -100, 100, -1, 30),
                expected_ground_z=0.0,
                ground_tolerance=0.5
            )
            
            
            # 3. Run check on each DataFrame
            for i, df in enumerate(dataframes):
                print(f"--- Checking DataFrame #{i} ---")
                
                # Header check 
                hc_result = header_check.run_check(df=df)
                print("Header Check:", hc_result)
                
                # # Timestamp check
                ts_check_result = ts_check.run_check(df=df)
                print("Timestamp Check:", ts_check_result)
                
                # Range Check
                rc_result = distance_check.run_check(df=df)
                print("Range Check:", rc_result)
                
                # Statistic Check
                stat_result = stats_check.run_check(df=df)
                print("StatisticCheck result", stat_result)
                
                # Spatial consistency check 
                # sp_result = sp_check.run_check(df=df)
                # print("Spatial Check : ", sp_result)
                if convert_csv:
                    outname = f"{data_dir}/frame_{i}.pcd"
                    converter = DFToPCDConverter(
                        df=df,
                        output_pcd=outname,
                        x_col="X",
                        y_col="Y",
                        z_col="Z",
                        intensity_col="INTENSITY",
                        pcd_version="0.7",
                        data_mode="ascii"
                    )
                    converter.run_conversion()
                
        if convert_pcd: 
            pcd_files = glob.glob(os.path.join(data_dir, "*.pcd"))
            pcd_count = len(pcd_files)
            
            if pcd_count == 0:
                print(f"No .pcd files found in : {data_dir}")
            
            print(f"Found {pcd_count} .pcd files in {data_dir}")
            
            # Create folder for inference
            velodyne_folder = os.path.join(data_dir, "data/kitti/testing/velodyne")
            image_sets_folder = os.path.join(data_dir, "data/kitti/testing/ImageSets")
            if not os.path.exists(velodyne_folder): os.makedirs(velodyne_folder)
            elif not os.path.exists(image_sets_folder): os.makedirs(image_sets_folder)
            print(f"velodyne folder : {velodyne_folder}")
            print(f"ImageSets folder : {image_sets_folder}")
            test_file = os.path.join(image_sets_folder, "test.txt")
            print(f"test txt file : {test_file}")
            
            with open(test_file, "w") as txt_file:
            
                for idx in range(pcd_count):
                    pcd_file = pcd_files[idx]
                    # Derive the corresponding .bin path
                    base_name = os.path.splitext(os.path.basename(pcd_file))[0]
                    bin_path = os.path.join(velodyne_folder, f"{base_name}.bin")
                    
                    # Create converter and run 
                    convert_pcd = PCDToBINConverter(pcd_file, bin_path)
                    convert_pcd.run_conversion()
                    
                    txt_file.write(bin_path + "\n")
                    
                    if (idx+1) >= pcd_count:
                        print(f"Reached the maximum {idx}+1 == {pcd_count}")
                        txt_file.close()
                        break 
    else: # If we are inferencing 
        
        parser = argparse.ArgumentParser()
        parser.add_argument('--cfg_file', type=str, required=False, help='Path to .yaml config')
        parser.add_argument('--ckpt_file', type=str, required=False, help='Path to .pth checkpoint')
        parser.add_argument('--data_path', type=str, required=False, help='Folder or file containing .bin')
        parser.add_argument('--device', type=str, default='cuda:0')
        parser.add_argument('--score_thresh', type=float, default=0.1)
        parser.add_argument('--ext', type=str, default='.bin')
        
        args = parser.parse_args()
        # We assume the bin folder and files exist already
        bin_folder = data_dir + "/data/kitti/testing/ImageSets"
        bin_files_path = os.path.join(bin_folder, "test.txt")
        
        text_reader = TextFileReader(bin_files_path)  
        bin_files = text_reader.read_lines()     
        
        print(f"First bin file path: {bin_files[0]}")
        data_path = data_dir + "/data/kitti/testing/velodyne"
        
        detector = OpenPCDetDetector(
            cfg_file="cfgs/kitti_models/pointpillar.yaml",
            ckpt_file="inference/models/pointpillar_7728.pth",
            data_path=data_path,
            device="cuda:0",
            score_thresh=0.1
        )
        # Just show bounding boxes for one frame
        results = detector.run_inference(show_vis=True)
        print("All frames processed, results length = ", len(results))

        
        
if __name__ == "__main__":
    main(
        sanity_check=False, 
        convert_csv=False, 
        convert_pcd=False, 
        inference= True, 
        data_dir= "../data/192.168.26.26_2020-11-25_20-01-45_frame-1899_part_1")