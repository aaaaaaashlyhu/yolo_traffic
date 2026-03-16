"""
模型管理器模块

统一的模型加载、缓存和错误处理，避免代码重复
"""

import os
from typing import Optional, Dict, Any
from .exceptions import ModelLoadError


class ModelManager:
    """模型单例管理器 - 避免重复加载相同模型"""
    
    _instance = None
    _models: Dict[str, Any] = {}  # 改为 Any，避免导入 YOLO 类型注解
    
    def __new__(cls):
        """单例模式 - 全局只有一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        return cls()
    
    def load_model(self, model_path: str, fallback_path: Optional[str] = None):
        """
        加载模型，支持缓存和自动降级
        
        Args:
            model_path: 模型文件路径
            fallback_path: 降级备选模型路径
            
        Returns:
            YOLO 模型实例
            
        Raises:
            ModelLoadError: 无法加载模型
        """
        from ultralytics import YOLO  # 延迟导入
        
        # 如果已缓存，直接返回
        if model_path in self._models:
            return self._models[model_path]
        
        # 尝试加载主模型
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            model = YOLO(model_path)
            self._models[model_path] = model
            return model
            
        except Exception as e:
            # 如果有降级方案，尝试加载
            if fallback_path:
                try:
                    print(f"⚠️  Failed to load {model_path}: {e}")
                    print(f"📦 Using fallback model: {fallback_path}")
                    
                    if fallback_path in self._models:
                        return self._models[fallback_path]
                    
                    model = YOLO(fallback_path)
                    self._models[fallback_path] = model
                    return model
                    
                except Exception as fallback_error:
                    raise ModelLoadError(
                        model_path,
                        f"Primary model failed: {e}, Fallback also failed: {fallback_error}"
                    )
            else:
                raise ModelLoadError(model_path, str(e))
    
    def load_sign_model(self, primary: str = 'bestvvv.pt', 
                        fallback: str = 'yolov8n.pt'):
        """加载交通标志检测模型"""
        return self.load_model(primary, fallback)
    
    def load_general_model(self, primary: str = 'yolo11n.pt',
                          fallback: str = 'yolov8n.pt'):
        """加载通用检测模型（行人、车辆）"""
        return self.load_model(primary, fallback)
    
    def clear_cache(self):
        """清空模型缓存（释放内存）"""
        self._models.clear()
        print("✅ Model cache cleared")
    
    def get_cached_models(self):
        """获取所有已缓存的模型"""
        return list(self._models.keys())


def get_model_manager() -> ModelManager:
    """工厂函数 - 获取模型管理器单例"""
    return ModelManager.get_instance()
