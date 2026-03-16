"""
核心模块包

包含异常处理、模型管理、资源管理等基础功能
"""

from .exceptions import (
    TrafficSignDetectionError,
    ModelLoadError,
    VideoSourceError,
    InferenceError,
    ConfigError,
    ResourceError,
)

from .model_manager import ModelManager, get_model_manager
from .resource_manager import VideoSourceManager, ContextVideoCapture, safe_video_read

__all__ = [
    'TrafficSignDetectionError',
    'ModelLoadError',
    'VideoSourceError',
    'InferenceError',
    'ConfigError',
    'ResourceError',
    'ModelManager',
    'get_model_manager',
    'VideoSourceManager',
    'ContextVideoCapture',
    'safe_video_read',
]
