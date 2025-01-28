#!/usr/bin/python3 

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
from typing import List, Optional

class Matplotlib3DVisualizer:
    """
    A class to visualize LiDAR frames (each a DataFrame with X, Y, Z) 
    in a basic 3D matplotlib environment. 
    """

    def __init__(
        self,
        x_col: str = "X",
        y_col: str = "Y",
        z_col: str = "Z",
        color_by: Optional[str] = None
    ):
        """
        :param x_col, y_col, z_col: Column names for coordinates.
        :param color_by: If set, we color the points by that numeric column 
                         (e.g. "INTENSITY"), using a colormap.
        """
        self.x_col = x_col
        self.y_col = y_col
        self.z_col = z_col
        self.color_by = color_by

    def plot_frame_static(self, df: pd.DataFrame, title: str = "LiDAR Frame"):
        """
        Plots a single LiDAR frame as a 3D scatter in a brand-new figure.
        """
        x = df[self.x_col].dropna().values
        y = df[self.y_col].dropna().values
        z = df[self.z_col].dropna().values
        if len(x) == 0:
            print("No points to display in this frame.")
            return

        if self.color_by and (self.color_by in df.columns):
            cvals = df[self.color_by].dropna().values
            if len(cvals) != len(x):
                print(f"Warning: mismatch in color_by column '{self.color_by}', defaulting to single color.")
                cvals = "blue"
        else:
            cvals = "blue"

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.set_title(title)
        ax.set_xlabel(self.x_col)
        ax.set_ylabel(self.y_col)
        ax.set_zlabel(self.z_col)

        if isinstance(cvals, str):
            # Single color
            ax.scatter(x, y, z, c=cvals, marker='.', alpha=0.6)
        else:
            # Numeric array => use a colormap
            scatter = ax.scatter(x, y, z, c=cvals, cmap='viridis', marker='.', alpha=0.6)
            fig.colorbar(scatter, ax=ax, label=self.color_by)

        plt.show()

    def animate_frames(self, frames: List[pd.DataFrame], interval_ms=200):
        """
        Creates an animation that cycles through each DataFrame frame in 3D.
        :param frames: a list of DataFrames, each representing one LiDAR snapshot
        :param interval_ms: how long to display each frame (in milliseconds)
        """

        if len(frames) == 0:
            print("No frames to animate.")
            return

        # We'll create one figure, one Axes3D
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(projection='3d')
        self.ax.set_xlabel(self.x_col)
        self.ax.set_ylabel(self.y_col)
        self.ax.set_zlabel(self.z_col)

        # We store the scatter object in the init
        self.scatter = None
        self.frames = frames

        # For a consistent viewpoint, we can capture min/max from all frames
        # or set them manually (just an example):
        #   self.ax.set_xlim(-50, 50)
        #   self.ax.set_ylim(-50, 50)
        #   self.ax.set_zlim(-5, 30)

        # Let's define initialization and update functions for FuncAnimation:

        def init():
            self.ax.set_title("LiDAR Animation")
            # We'll start with an empty scatter
            self.scatter = self.ax.scatter([], [], [], c="blue", marker='.', alpha=0.6)
            return (self.scatter,)

        def update(frame_i):
            df = self.frames[frame_i]
            x = df[self.x_col].dropna().values
            y = df[self.y_col].dropna().values
            z = df[self.z_col].dropna().values
            if len(x) == 0:
                # If empty, just hide the points by passing empty arrays
                x = []
                y = []
                z = []

            # Color logic
            if self.color_by and (self.color_by in df.columns):
                cvals = df[self.color_by].dropna().values
                if len(cvals) != len(x):
                    cvals = "blue"
            else:
                cvals = "blue"

            # We'll clear and re-plot. 
            # In older matplotlib, we might re-create the scatter. 
            self.ax.collections.clear()

            if isinstance(cvals, str):
                self.scatter = self.ax.scatter(x, y, z, c=cvals, marker='.', alpha=0.6)
            else:
                self.scatter = self.ax.scatter(x, y, z, c=cvals, cmap='viridis', marker='.', alpha=0.6)

            self.ax.set_title(f"Frame {frame_i}")
            return (self.scatter,)

        self.anim = animation.FuncAnimation(
            self.fig,
            func=update,
            frames=len(frames),
            init_func=init,
            interval=interval_ms,
            blit=False
        )
        plt.show()
