#!/usr/bin/python3

import os
import numpy as np
from typing import Dict, Any
import torch

from OpenPCDet.pcdet.config import cfg, cfg_from_yaml_file
from OpenPCDet.pcdet.models import build_network
from OpenPCDet.pcdet.utils import common_utils

import open3d as o3d

class OpenPCDetDetector:
    """
    Wraps a pretrained OpenPCDet model for single-frame inference, 
    with an option to visualize bounding boxes in Open3D.
    """

    def __init__(
        self,
        cfg_file: str,
        ckpt_file: str,
        device: str = "cuda:0",
        score_thresh: float = 0.1
    ):
        """
        :param cfg_file: Path to the .yaml config for your pretrained model 
                         (e.g. "cfgs/kitti_models/pointpillar.yaml")
        :param ckpt_file: Path to the pretrained checkpoint .pth
        :param device: 'cuda:0' or 'cpu'
        :param score_thresh: Confidence threshold for filtering detections
        """
        self.cfg_file = cfg_file
        self.ckpt_file = ckpt_file
        self.device = device
        self.score_thresh = score_thresh

        # 1) Load config
        cfg_from_yaml_file(self.cfg_file, cfg)
        self.model_cfg = cfg.MODEL

        # 2) Logger
        self.logger = common_utils.create_logger()
        self.class_names = cfg.CLASS_NAMES  # e.g. ['Car','Pedestrian','Cyclist'] for KITTI

        # 3) Build network
        self.model = build_network(model_cfg=cfg.MODEL, num_class=len(self.class_names), dataset=None)
        self.model.to(self.device)

        # 4) Load checkpoint
        self.logger.info(f"Loading checkpoint: {self.ckpt_file}")
        checkpoint = torch.load(self.ckpt_file, map_location=self.device)
        self.model.load_params_from_file(checkpoint=checkpoint, logger=self.logger, to_cpu=(self.device=="cpu"))
        self.model.eval()
        self.logger.info("[OpenPCDetDetector] Model ready.")

    @torch.no_grad()
    def detect_frame(self, bin_file: str) -> Dict[str, Any]:
        """
        Runs inference on a single .bin file (KITTI Nx4 float32).
        Returns bounding boxes above 'score_thresh'.
        """
        if not os.path.exists(bin_file):
            raise FileNotFoundError(f"bin file not found: {bin_file}")

        # 1) Load Nx4 points
        pts = np.fromfile(bin_file, dtype=np.float32).reshape(-1,4)

        # 2) Build data_dict for single-frame
        data_dict = {
            'points': pts,
            'frame_id': 0,  # dummy
        }
        data_dict = self._prep_data_dict(data_dict)

        # 3) Forward pass
        pred_dicts, _ = self.model.forward(data_dict)
        # Single batch => pred_dicts[0]
        pred_dict = pred_dicts[0]

        boxes_3d = pred_dict['pred_boxes'].cpu().numpy()
        scores_3d = pred_dict['pred_scores'].cpu().numpy()
        labels_3d = pred_dict['pred_labels'].cpu().numpy()

        # filter
        keep_mask = (scores_3d >= self.score_thresh)
        boxes_3d = boxes_3d[keep_mask]
        scores_3d = scores_3d[keep_mask]
        labels_3d = labels_3d[keep_mask]

        return {
            "boxes_3d": boxes_3d,
            "scores_3d": scores_3d,
            "labels_3d": labels_3d,
        }

    @torch.no_grad()
    def detect_and_show_frame(self, bin_file: str):
        """
        Runs detection on one .bin file, then visualizes
        the point cloud + bounding boxes in an Open3D window.
        """
        # 1) Detect
        det_result = self.detect_frame(bin_file)
        boxes_3d = det_result["boxes_3d"]
        scores_3d = det_result["scores_3d"]
        labels_3d = det_result["labels_3d"]

        # 2) Load points again for display
        pts = np.fromfile(bin_file, dtype=np.float32).reshape(-1,4)
        # We'll use open3d's PointCloud
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(pts[:,0:3])  # ignore intensity for display
        # color them all grey or something
        pcd.paint_uniform_color([0.5, 0.5, 0.5])

        # 3) For each box, create a line set geometry
        geometries = [pcd]  # start with the main point cloud
        for i in range(len(boxes_3d)):
            box = boxes_3d[i]   # [x, y, z, dx, dy, dz, heading]
            score = scores_3d[i]
            label = labels_3d[i]
            # can color by class or score
            line_set = self._create_3d_bbox_lineset(box, color=[1,0,0])  # red
            geometries.append(line_set)

        # 4) Visualize
        o3d.visualization.draw_geometries(geometries, window_name="OpenPCDet - BBoxes")

    def _prep_data_dict(self, data_dict):
        """
        Preprocess data for single-frame inference in an ad-hoc manner.
        Typically you'd replicate the logic from 'demo.py' or 'test.py'.
        """
        import torch
        pts = data_dict['points']
        data_dict['points'] = torch.from_numpy(pts).float().to(self.device)
        data_dict['batch_size'] = 1
        return data_dict

    def _create_3d_bbox_lineset(self, box_3d, color=[1,0,0]):
        """
        Creates an Open3D LineSet for a single 3D bounding box.
        box_3d: [x, y, z, dx, dy, dz, heading]
        heading is rotation around Z-axis in KITTI style.
        """
        import math
        import open3d as o3d

        cx, cy, cz, dx, dy, dz, heading = box_3d
        # dx, dy, dz => box lengths along x, y, z dimension
        # heading => rotation around z in radians

        # corners in local frame around center (cx,cy,cz)
        # nominally, box is aligned with x-axis => dx, y-axis => dy
        # We'll build corners, then rotate by heading around Z, then shift by (cx, cy, cz).
        # order: [x,y,z]
        # half dims
        hx, hy, hz = dx/2, dy/2, dz/2
        # eight corners (before rotation)
        corners = np.array([
            [ hx,  hy,  hz],
            [ hx,  hy, -hz],
            [ hx, -hy,  hz],
            [ hx, -hy, -hz],
            [-hx,  hy,  hz],
            [-hx,  hy, -hz],
            [-hx, -hy,  hz],
            [-hx, -hy, -hz],
        ], dtype=np.float32)

        # rotation around Z
        rot = np.array([
            [ math.cos(heading), -math.sin(heading), 0],
            [ math.sin(heading),  math.cos(heading), 0],
            [                0,                  0, 1]
        ], dtype=np.float32)
        corners_rot = corners @ rot.T

        # shift by center
        corners_rot[:,0] += cx
        corners_rot[:,1] += cy
        corners_rot[:,2] += cz

        # define the 12 edges of a box in index pairs
        edges = [
            (0,1), (0,2), (1,3), (2,3),   # top face
            (4,5), (4,6), (5,7), (6,7),   # bottom face
            (0,4), (1,5), (2,6), (3,7)    # vertical edges
        ]

        line_set = o3d.geometry.LineSet(
            points=o3d.utility.Vector3dVector(corners_rot),
            lines=o3d.utility.Vector2iVector(edges)
        )
        line_set.paint_uniform_color(color)
        return line_set
