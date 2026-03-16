"""
配置管理模块 - 集中管理应用配置

包含:
- 检测参数默认值
- UI 相关配置
- 路径配置
- 安全设置
"""

from pathlib import Path
from typing import Dict, Any
import json


class Config:
    """应用全局配置"""
    
    # ==================== 路径配置 ====================
    PROJECT_ROOT = Path(__file__).parent
    OUTPUT_DIR = PROJECT_ROOT / 'detection_results'
    USER_DB_PATH = PROJECT_ROOT / 'users_db.json'
    
    # ==================== 模型配置 ====================
    MODELS = {
        'sign_detection': {
            'primary': PROJECT_ROOT / 'bestvvv.pt',
            'fallback': PROJECT_ROOT / 'yolov8n.pt',
            'description': 'Traffic Sign Detection Model'
        },
        'general_detection': {
            'primary': PROJECT_ROOT / 'yolo11n.pt',
            'fallback': PROJECT_ROOT / 'yolov8n.pt',
            'description': 'General Object Detection (YOLO)'
        }
    }
    
    # ==================== 检测参数 ====================
    DETECTION = {
        'confidence_threshold': 0.50,      # 默认置信度
        'iou_threshold': 0.45,              # IOU 阈值
        'max_detections': 300,              # 最大检测数
        'conf_range': (0.10, 0.95),        # 置信度范围
        'iou_range': (0.10, 0.95),         # IOU 范围
    }
    
    # ==================== 视频配置 ====================
    VIDEO = {
        'supported_formats': ('.mp4', '.avi', '.mov', '.mkv', '.flv'),
        'max_frame_size': (1920, 1080),    # 最大分辨率
        'target_fps': 30,                   # 目标 FPS
        'frame_buffer_size': 10,            # 缓冲帧数
    }
    
    # ==================== 摄像头配置 ====================
    CAMERA = {
        'default_device': 0,                # 默认摄像头 ID
        'target_fps': 30,
        'resolution': (640, 480),           # 目标分辨率
        'enable_autofocus': True,
    }
    
    # ==================== 图片配置 ====================
    IMAGE = {
        'supported_formats': ('.jpg', '.jpeg', '.png', '.bmp', '.tiff'),
        'max_size': (4096, 4096),           # 最大分辨率
        'export_format': 'png',             # 导出格式
        'export_quality': 95,               # 导出质量
    }
    
    # ==================== UI 配置 ====================
    UI = {
        'window_width': 1400,
        'window_height': 900,
        'image_display_width': 600,
        'image_display_height': 500,
        'preview_scale': 0.95,              # 预览缩放比例
        'theme': 'Fusion',                  # Qt 主题
    }
    
    # ==================== 认证配置 ====================
    AUTH = {
        'token_expiry_hours': 24,           # Token 过期时间
        'password_min_length': 6,           # 密码最小长度
        'username_min_length': 3,           # 用户名最小长度
        'max_login_attempts': 5,            # 最大登录尝试次数
        'lockout_minutes': 15,              # 锁定时间（分钟）
        'hash_iterations': 100000,          # PBKDF2 迭代次数
    }
    
    # ==================== 数据导出配置 ====================
    EXPORT = {
        'csv_delimiter': ',',
        'csv_encoding': 'utf-8',
        'image_format': 'png',
        'include_metadata': True,           # CSV 中包含元数据
        'timestamp_format': '%Y-%m-%d %H:%M:%S',
    }
    
    # ==================== 日志配置 ====================
    LOGGING = {
        'log_dir': PROJECT_ROOT / 'logs',
        'log_file': 'app.log',
        'log_level': 'INFO',
        'max_log_size': 10485760,           # 10MB
        'backup_count': 5,
    }
    
    # ==================== 性能配置 ====================
    PERFORMANCE = {
        'num_threads': 4,                   # CPU 线程数
        'batch_size': 1,                    # 推理批大小
        'device': 'cuda',                   # 'cuda' 或 'cpu'
        'cache_models': True,               # 缓存加载的模型
    }
    
    # ==================== 静态方法 ====================
    
    @staticmethod
    def get_model_path(model_type: str) -> Path:
        """获取模型路径"""
        if model_type in Config.MODELS:
            primary = Config.MODELS[model_type]['primary']
            if primary.exists():
                return primary
            else:
                return Config.MODELS[model_type]['fallback']
        return None
    
    @staticmethod
    def is_image_file(file_path: str) -> bool:
        """检查是否为支持的图片格式"""
        return Path(file_path).suffix.lower() in Config.IMAGE['supported_formats']
    
    @staticmethod
    def is_video_file(file_path: str) -> bool:
        """检查是否为支持的视频格式"""
        return Path(file_path).suffix.lower() in Config.VIDEO['supported_formats']
    
    @staticmethod
    def initialize_directories():
        """初始化必要的目录"""
        Config.OUTPUT_DIR.mkdir(exist_ok=True)
        Config.LOGGING['log_dir'] = Path(Config.LOGGING['log_dir'])
        Config.LOGGING['log_dir'].mkdir(exist_ok=True)
    
    @staticmethod
    def to_dict() -> Dict[str, Any]:
        """导出配置为字典"""
        return {
            'paths': {
                'project_root': str(Config.PROJECT_ROOT),
                'output_dir': str(Config.OUTPUT_DIR),
                'user_db': str(Config.USER_DB_PATH),
            },
            'models': {k: {kk: str(vv) if isinstance(vv, Path) else vv for kk, vv in v.items()} 
                      for k, v in Config.MODELS.items()},
            'detection': Config.DETECTION,
            'video': Config.VIDEO,
            'camera': Config.CAMERA,
            'image': Config.IMAGE,
            'ui': Config.UI,
            'auth': Config.AUTH,
            'export': Config.EXPORT,
            'logging': Config.LOGGING,
            'performance': Config.PERFORMANCE,
        }
    
    @staticmethod
    def save_config(file_path: str = 'config.json'):
        """保存配置到 JSON 文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(Config.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"✅ 配置已保存到: {file_path}")
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
    
    @staticmethod
    def load_config(file_path: str = 'config.json') -> Dict[str, Any]:
        """从 JSON 文件加载配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✅ 配置已加载自: {file_path}")
            return config
        except Exception as e:
            print(f"⚠️  无法加载配置文件: {e}")
            return None


# 初始化目录
Config.initialize_directories()

# 配置别名，供快速访问
DETECTION_CONFIG = Config.DETECTION
VIDEO_CONFIG = Config.VIDEO
CAMERA_CONFIG = Config.CAMERA
AUTH_CONFIG = Config.AUTH
EXPORT_CONFIG = Config.EXPORT


def print_config():
    """打印完整配置信息"""
    import json
    
    print("\n" + "=" * 80)
    print("⚙️  应用配置".center(80))
    print("=" * 80 + "\n")
    
    config_dict = Config.to_dict()
    print(json.dumps(config_dict, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    # 打印配置
    print_config()
    
    # 保存配置示例
    Config.save_config('config_example.json')
    print("\n📄 示例配置已保存到: config_example.json")
