#!/usr/bin/python3 

import pandas as pd 
import numpy as np
import os 


class DFToPCDConverter:
    
    def __init__(
        self,
        df: pd.DataFrame,
        output_pcd: str,
        x_col: str = "X",
        y_col: str = "Y",
        z_col: str = "Z",
        intensity_col: str = "INTENSITY",
        pcd_version: str = "0.7",
        data_mode: str = "ascii"
    ):
        """
        :param df: The DataFrame representing one LiDAR frame (with columns X, Y, Z, optionally INTENSITY).
        :param output_pcd: Path to the output .pcd file.
        :param x_col, y_col, z_col: Column names for coordinates in df.
        :param intensity_col: Column name for intensity. If not present, we ignore it.
        :param pcd_version: e.g. "0.7" for PCD format.
        :param data_mode: "ascii" or "binary" (this example only implements ASCII).
        """
        self.df = df
        self.output_pcd = output_pcd
        self.x_col = x_col
        self.y_col = y_col
        self.z_col = z_col
        self.intensity_col = intensity_col
        self.pcd_version = pcd_version
        self.data_mode = data_mode.lower()

        self.has_intensity = False
        self.num_points = 0

        # Arrays we'll fill after reading
        self.x = None
        self.y = None
        self.z = None
        self.i = None

    def run_conversion(self):
        """
        Main entry: parse columns from self.df, build a PCD header, write file.
        """
        self._extract_points()
        header = self._create_pcd_header()
        self._write_pcd(header)
        print(f"[DataFrameToPCDConverter] Wrote {self.num_points} points => {self.output_pcd}")

    def _extract_points(self):
        """
        Internal: extracts X,Y,Z,(INTENSITY) from df, ensuring consistent lengths.
        """
        # 1) Check columns
        for c in [self.x_col, self.y_col, self.z_col]:
            if c not in self.df.columns:
                raise ValueError(f"Required column '{c}' missing in DataFrame.")

        x_arr = self.df[self.x_col].dropna().values
        y_arr = self.df[self.y_col].dropna().values
        z_arr = self.df[self.z_col].dropna().values

        min_len = min(len(x_arr), len(y_arr), len(z_arr))
        x_arr = x_arr[:min_len]
        y_arr = y_arr[:min_len]
        z_arr = z_arr[:min_len]

        self.x = x_arr
        self.y = y_arr
        self.z = z_arr
        self.num_points = min_len

        # 2) Check intensity if present
        if self.intensity_col and (self.intensity_col in self.df.columns):
            i_arr = self.df[self.intensity_col].dropna().values
            i_len = len(i_arr)
            if i_len < min_len:
                min_len = i_len
            # clamp everything to min_len
            self.x = self.x[:min_len]
            self.y = self.y[:min_len]
            self.z = self.z[:min_len]
            i_arr = i_arr[:min_len]

            self.i = i_arr
            self.has_intensity = True
            self.num_points = min_len
        else:
            self.has_intensity = False

        if self.num_points == 0:
            raise ValueError("No valid points to convert (empty after NaN drop).")

    def _create_pcd_header(self):
        """
        Builds ASCII PCD v0.7 header, either with or without intensity.
        """
        lines = []
        lines.append(f"# .PCD v{self.pcd_version} - Point Cloud Data file format")
        lines.append(f"VERSION {self.pcd_version}")

        if self.has_intensity:
            lines.append("FIELDS x y z intensity")
            lines.append("SIZE 4 4 4 4")
            lines.append("TYPE F F F F")
            lines.append("COUNT 1 1 1 1")
        else:
            lines.append("FIELDS x y z")
            lines.append("SIZE 4 4 4")
            lines.append("TYPE F F F")
            lines.append("COUNT 1 1 1")

        lines.append(f"WIDTH {self.num_points}")
        lines.append("HEIGHT 1")
        lines.append("VIEWPOINT 0 0 0 1 0 0 0")
        lines.append(f"POINTS {self.num_points}")

        # For simplicity, we handle only ASCII in this example
        if self.data_mode == "binary":
            raise NotImplementedError("Binary PCD not implemented here.")
        else:
            lines.append("DATA ascii")

        return lines

    def _write_pcd(self, header_lines):
        """
        Writes out the ASCII PCD file: header, then each point line.
        """
        with open(self.output_pcd, "w") as f:
            # Write header
            for line in header_lines:
                f.write(line + "\n")

            # Write points
            if self.has_intensity:
                for idx in range(self.num_points):
                    f.write(f"{self.x[idx]:.6f} {self.y[idx]:.6f} {self.z[idx]:.6f} {self.i[idx]:.6f}\n")
            else:
                for idx in range(self.num_points):
                    f.write(f"{self.x[idx]:.6f} {self.y[idx]:.6f} {self.z[idx]:.6f}\n")