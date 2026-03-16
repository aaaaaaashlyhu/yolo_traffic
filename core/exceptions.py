"""
异常处理模块

定义项目特定的异常类，用于统一的错误管理和日志记录
"""


class TrafficSignDetectionError(Exception):
    """项目基础异常类"""
    pass


class ModelLoadError(TrafficSignDetectionError):
    """模型加载异常"""
    
    def __init__(self, model_path: str, reason: str = ""):
        self.model_path = model_path
        self.reason = reason
        message = f"Failed to load model from '{model_path}'"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class VideoSourceError(TrafficSignDetectionError):
    """视频源异常"""
    
    def __init__(self, source: str, reason: str = ""):
        self.source = source
        self.reason = reason
        message = f"Cannot access video source '{source}'"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class InferenceError(TrafficSignDetectionError):
    """推理异常"""
    
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Inference error: {reason}")


class ConfigError(TrafficSignDetectionError):
    """配置异常"""
    
    def __init__(self, config_key: str, reason: str = ""):
        self.config_key = config_key
        self.reason = reason
        message = f"Configuration error for '{config_key}'"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class ResourceError(TrafficSignDetectionError):
    """资源异常 (内存、文件等)"""
    
    def __init__(self, resource_type: str, reason: str = ""):
        self.resource_type = resource_type
        self.reason = reason
        message = f"{resource_type} resource error"
        if reason:
            message += f": {reason}"
        super().__init__(message)
