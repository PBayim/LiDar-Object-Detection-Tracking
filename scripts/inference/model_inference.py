#!/usr/bin/python3


import os
import numpy as np
from typing import List, Dict, Any 

import torch

from OpenPCDet.pcdet.config import cfg, cfg_from_yaml_file
from OpenPCDet.pcdet.models import build_network
from OpenPCDet.pcdet.utils import common_utils


class OpenPCDetDetector:
    
    def __init__(
        self,
        cfg_file: str, 
        ckpt_file: str,
        device: str = "cuda:0",
        score_thresh: float = 0.1
        
    ):
        """Warps a pretrained OpenPCDet model for single-frame inference,
            loading .bin files (KITTI-like Nx4)

        Args:
            cfg_file (str): Path to the .yaml config for the pretrained model
            ckpt_file (str): Path to the pretrained checkpoint .pth
            device (_type_, optional): cpu or gpu. Defaults to "cuda:0".
            score_thresh (float, optional): COnfidence threshold to filter detections. Defaults to 0.1.
        """
        
        self.cfg_file = cfg_file
        self.ckpt_file = ckpt_file
        self.device = device
        self.score_thresh = score_thresh
        
        # Load config
        cfg_from_yaml_file(self.cfg_file, cfg)
        self.model_cfg = cfg.MODEL  
        
        # Logger
        self.logger = common_utils.create_logger()
        self.class_names = cfg.CLASS_NAMES # tools/kitti_models/modelxxx.yaml
        
        # Build network
        self.model = build_network(model_cfg=cfg.MODEL, num_class=len(self.class_names), dataset=None)
        self.model.to(self.device)
        
        # Load checkpoint 
        self.logger.info(f"Loading checkpoint: {self.ckpt_file}")
        checkpoint = torch.load(self.ckpt_file, map_location=self.device)
        self.model.load_params_from_file(checkpoint=checkpoint, logger=self.logger, to_cpu=(self.device=="cpu"))
        self.model.eval()
        self.logger.info("[OpenPCDetDetector] Model ready.")
        
        
    @torch.no_grad()
    def detect_frame(self, bin_file: str):
        
        
        if not os.path.exists(bin_file):
            raise FileNotFoundError(f"bin file not found: {bin_file}")
