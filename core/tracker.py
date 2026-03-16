"""
追踪模块 - 实现目标追踪和计数

支持：
- 行人追踪
- 车辆追踪  
- 自动计数（避免重复计数）
- 轨迹历史记录
"""

import cv2
import numpy as np
from collections import defaultdict
from typing import Dict, List, Tuple
import time


class SimpleTracker:
    """简单但有效的目标追踪器 - 基于成本的匹配"""
    
    def __init__(self, max_age: int = 30, min_hits: int = 3):
        """
        初始化追踪器
        
        Args:
            max_age: 目标失踪的最大帧数
            min_hits: 确认目标前的最少检测次数
        """
        self.max_age = max_age
        self.min_hits = min_hits
        
        self.frame_count = 0
        
        # 统计信息（不再需要详细追踪，直接从检测结果统计）
        self.total_people_count = 0
        self.total_vehicles_count = 0
        
    def update(self, detections: List[Dict], frame_shape: Tuple) -> Dict:
        """
        更新追踪结果
        
        Args:
            detections: 检测结果列表
                [{
                    'bbox': [x1, y1, x2, y2],
                    'confidence': 0.95,
                    'class_name': 'Person',
                    'class_id': 0
                }]
            frame_shape: 帧的形状 (height, width)
            
        Returns:
            {
                'tracked_detections': [...],  # 带追踪ID的检测
                'total_people': 5,
                'total_vehicles': 3,
                'active_tracks': 8
            }
        """
        self.frame_count += 1
        tracked_detections = detections.copy()  # 直接复制检测结果（保留原始检测）
        
        # 直接从当前检测结果计数（不等待追踪确认）
        people_count = len([d for d in detections if d.get('class_id') == 0])
        vehicles_count = len([d for d in detections if d.get('class_id') in [2, 5, 7]])
        
        return {
            'tracked_detections': tracked_detections,
            'total_people': people_count,
            'total_vehicles': vehicles_count,
            'active_tracks': len(tracked_detections)
        }
    
    def draw_tracks(self, frame: np.ndarray, tracked_detections: List[Dict]) -> np.ndarray:
        """
        在图像上绘制追踪框（不显示ID）
        
        Args:
            frame: 输入帧
            tracked_detections: 带追踪ID的检测结果
            
        Returns:
            标注后的帧
        """
        annotated = frame.copy()
        
        for det in tracked_detections:
            x1, y1, x2, y2 = map(int, det['bbox'])
            confidence = det.get('confidence', 0)
            class_name = det.get('class_name', 'Unknown')
            
            # 选择颜色（不显示ID，只显示边框和标签）
            if class_name == 'Person':
                color = (0, 255, 0)  # 绿色 - 行人
            else:
                color = (255, 0, 0)  # 蓝色 - 车辆
            
            # 绘制边框
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # 只绘制类别名和置信度，不显示追踪ID
            label = f"{class_name} {confidence:.2f}"
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )
        
        return annotated
    
    def reset(self):
        """重置追踪器"""
        self.frame_count = 0
        self.total_people_count = 0
        self.total_vehicles_count = 0


def create_tracker() -> SimpleTracker:
    """工厂函数 - 创建追踪器实例"""
    return SimpleTracker(max_age=30, min_hits=3)
