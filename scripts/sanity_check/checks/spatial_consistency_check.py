#!/usr/bin/python3

import numpy as np
import pandas as pd
from .base_check import BaseCheck

class SpatialConsistencyCheck(BaseCheck):
    """
    A basic check to confirm that LiDAR point coordinates (X, Y, Z) are within
    plausible boundaries and that the 'ground' doesn't deviate wildly from an
    expected Z-level (optional).
    """

    def __init__(
        self,
        x_col="X",
        y_col="Y",
        z_col="Z",
        bounding_box_limits=None,
        expected_ground_z=None,
        ground_tolerance=0.5
    ):
        """
        :param x_col, y_col, z_col: Names of the coordinate columns.
        :param bounding_box_limits: Optional 6-tuple (xmin, xmax, ymin, ymax, zmin, zmax)
                                   used for bounding-box checks.
        :param expected_ground_z: If set, we do a rough check that the lowest points
                                  in the cloud are near this Z-value. (e.g., 0.0 if the
                                  LiDAR is at some known height above the ground plane).
        :param ground_tolerance: Allowed +/- difference for 'ground' checks.
                                 (e.g., 0.5 → ±0.5 around expected_ground_z).
        """
        self.x_col = x_col
        self.y_col = y_col
        self.z_col = z_col
        self.bounding_box_limits = bounding_box_limits
        self.expected_ground_z = expected_ground_z
        self.ground_tolerance = ground_tolerance

    def run_check(self, df: pd.DataFrame) -> dict:
        """
        1. Confirms the X, Y, Z columns exist.
        2. (Optional) Checks bounding-box constraints if bounding_box_limits is provided.
        3. (Optional) If expected_ground_z is set, check that the bottom ~10% of points
           are near that level (rough ground-plane check).

        :param df: A DataFrame representing a LiDAR frame or CSV file.
        :return: A dictionary with pass/fail info and descriptive messages.
        """
        result = {
            "check_name": "SpatialConsistencyCheck",
            "passed": True,
            "messages": []
        }

        # 1. Verify required columns
        required_cols = {self.x_col, self.y_col, self.z_col}
        if not required_cols.issubset(df.columns):
            result["passed"] = False
            missing_cols = required_cols - set(df.columns)
            result["messages"].append(
                f"Missing columns: {list(missing_cols)}"
            )
            return result

        # Extract numeric arrays
        x_vals = df[self.x_col].dropna().values
        y_vals = df[self.y_col].dropna().values
        z_vals = df[self.z_col].dropna().values

        # 2. Bounding-Box Check
        if self.bounding_box_limits is not None:
            xmin, xmax, ymin, ymax, zmin, zmax = self.bounding_box_limits
            # Compute actual min & max
            actual_xmin, actual_xmax = x_vals.min(), x_vals.max()
            actual_ymin, actual_ymax = y_vals.min(), y_vals.max()
            actual_zmin, actual_zmax = z_vals.min(), z_vals.max()

            # Any dimension out of range → fail
            if (actual_xmin < xmin or actual_xmax > xmax or
                actual_ymin < ymin or actual_ymax > ymax or
                actual_zmin < zmin or actual_zmax > zmax):
                result["passed"] = False
                msg = (
                    "Bounding box check failed. "
                    f"Found X in [{actual_xmin:.2f}, {actual_xmax:.2f}], "
                    f"Y in [{actual_ymin:.2f}, {actual_ymax:.2f}], "
                    f"Z in [{actual_zmin:.2f}, {actual_zmax:.2f}]. "
                    f"Expected X in [{xmin}, {xmax}], "
                    f"Y in [{ymin}, {ymax}], "
                    f"Z in [{zmin}, {zmax}]."
                )
                result["messages"].append(msg)
            else:
                msg = (
                    "Bounding box within expected limits. "
                    f"X in [{actual_xmin:.2f}, {actual_xmax:.2f}], "
                    f"Y in [{actual_ymin:.2f}, {actual_ymax:.2f}], "
                    f"Z in [{actual_zmin:.2f}, {actual_zmax:.2f}]."
                )
                result["messages"].append(msg)

        # 3. Rough Ground Check
        if self.expected_ground_z is not None and len(z_vals) > 0:
            # Sort Z and take ~10th percentile as "ground" level
            z_sorted = np.sort(z_vals)
            ground_level_estimate = np.percentile(z_sorted, 10)  # 10% percentile

            lower_bound = self.expected_ground_z - self.ground_tolerance
            upper_bound = self.expected_ground_z + self.ground_tolerance

            if not (lower_bound <= ground_level_estimate <= upper_bound):
                result["passed"] = False
                msg = (
                    "Ground check failed. "
                    f"Estimated ground level ~{ground_level_estimate:.2f}, "
                    f"expected ~{self.expected_ground_z}±{self.ground_tolerance}."
                )
                result["messages"].append(msg)
            else:
                msg = (
                    f"Ground check passed. 10th percentile Z ~{ground_level_estimate:.2f} "
                    f"is within {self.ground_tolerance} of {self.expected_ground_z}."
                )
                result["messages"].append(msg)

        return result
