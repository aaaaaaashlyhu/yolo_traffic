"""
资源管理器模块

确保 VideoCapture等关键资源的正确初始化和清理
"""

from typing import Optional
from .exceptions import VideoSourceError


class VideoSourceManager:
    """视频源管理器 - 智能创建和释放资源"""
    
    def __init__(self, source: str | int = 'test4.mp4', max_retries: int = 3):
        """
        初始化视频源
        
        Args:
            source: 视频文件路径 或 摄像头ID (0)
            max_retries: 最大重试次数
            
        Raises:
            VideoSourceError: 无法打开视频源
        """
        import cv2  # 延迟导入，避免包导入时加载
        self.cv2 = cv2
        self.source = source
        self.cap = None
        self.max_retries = max_retries
        self._open()
    
    def _open(self):
        """打开视频源，支持重试"""
        for attempt in range(self.max_retries):
            try:
                self.cap = self.cv2.VideoCapture(self.source)
                
                # 检查是否成功打开
                if not self.cap.isOpened():
                    raise ValueError(f"Cannot open video source {self.source}")
                
                # 验证可以读取第一帧
                ret, _ = self.cap.read()
                if not ret:
                    raise ValueError("Cannot read from video source")
                
                # 成功打开，复位到开头
                self.cap.set(self.cv2.CAP_PROP_POS_FRAMES, 0)
                print(f"✅ Video source opened successfully: {self.source}")
                return
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"⚠️  Attempt {attempt + 1}/{self.max_retries} failed: {e}")
                else:
                    if self.cap:
                        self.cap.release()
                    raise VideoSourceError(
                        str(self.source),
                        f"Failed after {self.max_retries} attempts: {e}"
                    )
    
    def read_frame(self):
        """
        读取一帧，支持自动循环
        
        Returns:
            (bool, ndarray): 成功标志 和 帧数据
        """
        if not self.cap or not self.cap.isOpened():
            raise VideoSourceError(str(self.source), "Video source not open")
        
        ret, frame = self.cap.read()
        
        # 如果视频播放完，自动循环
        if not ret:
            self.cap.set(self.cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
        
        return ret, frame
    
    def get_property(self, prop: int):
        """获取视频属性 (fps, width, height 等)"""
        if not self.cap:
            return None
        return self.cap.get(prop)
    
    def set_property(self, prop: int, value):
        """设置视频属性"""
        if not self.cap:
            return None
        self.cap.set(prop, value)
    
    def release(self):
        """释放资源"""
        if self.cap:
            self.cap.release()
            print(f"✅ Video source released: {self.source}")
    
    def __enter__(self):
        """上下文管理器 - with 语句支持"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """自动释放资源"""
        self.release()
    
    def __del__(self):
        """析构函数 - 垃圾回收时清理"""
        try:
            self.release()
        except:
            pass


class ContextVideoCapture:
    """cv2.VideoCapture 的包装器 - 确保资源正确释放"""
    
    def __init__(self, source: str | int):
        import cv2  # 延迟导入
        self.cv2 = cv2
        self.source = source
        self.cap = None
    
    def __enter__(self):
        self.cap = self.cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise VideoSourceError(str(self.source), "Cannot open video source")
        return self.cap
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cap:
            self.cap.release()


def safe_video_read(video_path: str, max_retries: int = 3):
    """
    安全读取视频的便利函数
    
    Args:
        video_path: 视频文件路径
        max_retries: 重试次数
        
    Yields:
        (int, ndarray): 帧号 和 帧数据
    """
    with VideoSourceManager(video_path, max_retries) as video:
        frame_count = 0
        while True:
            ret, frame = video.read_frame()
            if not ret:
                break
            yield frame_count, frame
            frame_count += 1
