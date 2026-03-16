"""
主应用窗口 - PyQt6

支持图片拖拽、视频逐帧、摄像头实时检测、结果导出
"""

import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import csv

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QScrollArea, QFileDialog, QMessageBox, QSpinBox,
    QComboBox, QCheckBox, QProgressBar, QStatusBar, QSlider
)
from PyQt6.QtGui import QImage, QPixmap, QFont, QDragEnterEvent, QDropEvent
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer, QSize

from core.model_manager import ModelManager
from core.auth_manager import get_auth_manager
from core.tracker import SimpleTracker


class DetectionWorker(QThread):
    """后台检测线程"""
    
    frame_ready = pyqtSignal(QImage)
    stats_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._running = True
        self.model_manager = ModelManager()
        self.tracker = SimpleTracker(max_age=30, min_hits=3)  # 初始化追踪器
        
        try:
            self.model_signs = self.model_manager.load_sign_model()
            self.model_general = self.model_manager.load_general_model()
        except Exception as e:
            self.error_occurred.emit(f"❌ 模型加载失败: {e}")
    
    def process_frame(self, frame: np.ndarray, conf_threshold: float = 0.5) -> tuple:
        """
        处理单帧图像
        
        Args:
            frame: 输入帧
            conf_threshold: 置信度阈值
            
        Returns:
            (处理后的帧, 检测统计)
        """
        try:
            # 检测标志
            results_signs = self.model_signs.predict(frame, conf=conf_threshold, verbose=False)
            
            # 检测行人/车辆
            results_general = self.model_general.predict(
                frame, 
                classes=[0, 2, 5, 7],  # person, car, bus, truck
                conf=conf_threshold,
                verbose=False
            )
            
            # 统计检测结果
            sign_boxes = results_signs[0].boxes
            general_boxes = results_general[0].boxes
            
            stats = {
                'signs': len(sign_boxes),
                'people': 0,
                'vehicles': 0,
                'detections': []
            }
            
            # 绘制标志检测结果
            annotated = results_signs[0].plot()
            
            # 统计并绘制行人和车辆
            for box in general_boxes:
                cls_id = int(box.cls[0])
                class_name = self.model_general.names.get(cls_id, "Unknown")
                
                if cls_id == 0:
                    stats['people'] += 1
                else:
                    stats['vehicles'] += 1
                
                # 绘制框
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                
                # 根据类别选择颜色
                color = (0, 255, 0) if cls_id == 0 else (255, 0, 0)
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    annotated,
                    f"{class_name} {conf:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2
                )
                
                stats['detections'].append({
                    'class': class_name,
                    'confidence': conf,
                    'bbox': [x1, y1, x2, y2]
                })
            
            # 标志统计
            for box in sign_boxes:
                cls_id = int(box.cls[0])
                class_name = self.model_signs.names.get(cls_id, "Sign")
                conf = float(box.conf[0])
                
                stats['detections'].append({
                    'class': class_name,
                    'confidence': conf,
                    'type': 'sign'
                })
            
            return annotated, stats
            
        except Exception as e:
            self.error_occurred.emit(f"检测错误: {e}")
            return frame, {'signs': 0, 'people': 0, 'vehicles': 0, 'detections': []}
    
    def get_tracked_detections(self, frame: np.ndarray, conf_threshold: float = 0.5, 
                               tracker: Optional['SimpleTracker'] = None) -> tuple:
        """
        获取带追踪ID的检测结果
        
        Args:
            frame: 输入帧
            conf_threshold: 置信度阈值
            tracker: 追踪器对象
            
        Returns:
            (标注的帧, 追踪统计信息)
        """
        try:
            # 获取基础检测结果
            results_signs = self.model_signs.predict(frame, conf=conf_threshold, verbose=False)
            results_general = self.model_general.predict(
                frame, 
                classes=[0, 2, 5, 7],
                conf=conf_threshold,
                verbose=False
            )
            
            # 整理成检测列表
            all_detections = []
            
            # 标志检测
            for box in results_signs[0].boxes:
                cls_id = int(box.cls[0])
                class_name = self.model_signs.names.get(cls_id, "Sign")
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                all_detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': conf,
                    'class_name': class_name,
                    'class_id': cls_id,
                    'type': 'sign'
                })
            
            # 行人/车辆检测
            for box in results_general[0].boxes:
                cls_id = int(box.cls[0])
                class_name = self.model_general.names.get(cls_id, "Unknown")
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                all_detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': conf,
                    'class_name': class_name,
                    'class_id': cls_id,
                    'type': 'object'
                })
            
            # 使用追踪器更新
            annotated = frame.copy()
            track_info = {}
            
            if tracker is not None:
                track_info = tracker.update(all_detections, frame.shape)
                annotated = tracker.draw_tracks(annotated, track_info.get('tracked_detections', []))
            else:
                # 不使用追踪时，直接绘制检测结果
                for det in all_detections:
                    x1, y1, x2, y2 = det['bbox']
                    class_name = det['class_name']
                    conf = det['confidence']
                    
                    color = (0, 255, 0) if det['class_id'] == 0 else (255, 0, 0)
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(
                        annotated,
                        f"{class_name} {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        color,
                        2
                    )
            
            stats = {
                'signs': len([d for d in all_detections if d['type'] == 'sign']),
                'people': track_info.get('total_people', len([d for d in all_detections if d['class_id'] == 0])),
                'vehicles': track_info.get('total_vehicles', len([d for d in all_detections if d['class_id'] in [2, 5, 7]])),
                'tracking_active': tracker is not None,
                'tracked_objects': track_info.get('active_tracks', 0)
            }
            
            return annotated, stats
            
        except Exception as e:
            self.error_occurred.emit(f"追踪错误: {e}")
            return frame, {'signs': 0, 'people': 0, 'vehicles': 0, 'tracking_active': False, 'tracked_objects': 0}
    
    def stop(self):
        """停止线程"""
        self._running = False
        self.wait()


class MainWindow(QMainWindow):
    """主应用窗口"""
    
    def __init__(self, username: str, token: str):
        super().__init__()
        
        self.username = username
        self.token = token
        self.auth_manager = get_auth_manager()
        self.worker = DetectionWorker()
        
        # 输出目录
        self.output_dir = Path('detection_results')
        self.output_dir.mkdir(exist_ok=True)
        
        # 当前处理数据
        self.current_frame = None
        self.detection_results = []
        
        # 视频相关属性初始化
        self.video_path = None
        self.video_cap = None
        self.video_fps = 0
        self.total_frames = 0
        self.video_playing = False
        self.video_timer = None
        
        # 摄像头相关属性初始化
        self.camera_cap = None
        self.camera_timer = None
        
        # 追踪器 - 用于视频和摄像头处理
        self.video_tracker = SimpleTracker(max_age=30, min_hits=3)
        self.camera_tracker = SimpleTracker(max_age=30, min_hits=3)
        
        self.init_ui()
        self.connect_signals()
        
        # 验证Token
        is_valid, user_info = self.auth_manager.verify_token(token)
        if not is_valid:
            QMessageBox.warning(self, "❌ Token失效", "请重新登录")
            self.close()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"🎯 交通标志检测系统 - {self.username}")
        self.setGeometry(0, 0, 1400, 900)
        self.setStyleSheet(self._get_stylesheet())
        
        # 中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        
        # 左侧 - 检测区域
        left_layout = QVBoxLayout()
        
        # 图像显示
        self.image_label = QLabel()
        self.image_label.setMinimumSize(600, 500)
        self.image_label.setStyleSheet("border: 2px dashed #0066cc; background-color: #f9f9f9;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText("📌 拖拽图片到此处\n或点击按钮选择")
        self.image_label.setAcceptDrops(True)
        self.image_label.dragEnterEvent = self.dragEnterEvent
        self.image_label.dropEvent = self.dropEvent
        
        left_layout.addWidget(self.image_label)
        
        # 标签页 - 不同功能
        tabs = QTabWidget()
        
        # 标签页 1 - 图片检测
        image_widget = self._create_image_tab()
        tabs.addTab(image_widget, "🖼️  图片检测")
        
        # 标签页 2 - 视频逐帧
        video_widget = self._create_video_tab()
        tabs.addTab(video_widget, "🎬 视频逐帧")
        
        # 标签页 3 - 摄像头检测
        camera_widget = self._create_camera_tab()
        tabs.addTab(camera_widget, "📹 实时摄像头")
        
        left_layout.addWidget(tabs)
        
        # 右侧 - 信息面板
        right_layout = QVBoxLayout()
        
        # 用户信息
        user_info_group = self._create_user_info_panel()
        right_layout.addWidget(user_info_group)
        
        # 检测参数
        params_group = self._create_params_panel()
        right_layout.addWidget(params_group)
        
        # 结果统计
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("background-color: white; padding: 10px; border-radius: 4px;")
        self.stats_label.setText("📊 检测统计\n待处理...")
        right_layout.addWidget(self.stats_label)
        
        # 操作按钮
        button_layout = QVBoxLayout()
        
        export_img_btn = QPushButton("💾 导出结果图")
        export_img_btn.clicked.connect(self.export_image)
        export_img_btn.setStyleSheet("background-color: #00aa00; color: white;")
        button_layout.addWidget(export_img_btn)
        
        export_csv_btn = QPushButton("📊 导出检测CSV")
        export_csv_btn.clicked.connect(self.export_csv)
        export_csv_btn.setStyleSheet("background-color: #aa6600; color: white;")
        button_layout.addWidget(export_csv_btn)
        
        open_folder_btn = QPushButton("📁 打开结果文件夹")
        open_folder_btn.clicked.connect(self.open_results_folder)
        open_folder_btn.setStyleSheet("background-color: #0066aa; color: white;")
        button_layout.addWidget(open_folder_btn)
        
        logout_btn = QPushButton("🚪 登出")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("background-color: #aa0000; color: white;")
        button_layout.addWidget(logout_btn)
        
        right_layout.addLayout(button_layout)
        right_layout.addStretch()
        
        # 将左右布局添加到主布局
        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 1)
        
        central_widget.setLayout(main_layout)
        
        # 状态栏
        self.statusBar().showMessage("✅ 系统就绪")
    
    def _get_stylesheet(self) -> str:
        """获取应用样式表"""
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 20px;
                border: 1px solid #bbb;
            }
            QTabBar::tab:selected {
                background-color: #0066cc;
                color: white;
            }
            QLabel {
                font-size: 11px;
            }
            QLineEdit, QSpinBox, QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            QPushButton {
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
                color: white;
                border: none;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:pressed {
                opacity: 0.8;
            }
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }
        """
    
    def _create_user_info_panel(self) -> QWidget:
        """创建用户信息面板"""
        from PyQt6.QtWidgets import QGroupBox
        
        group = QGroupBox("👤 用户信息")
        layout = QVBoxLayout()
        
        # 用户统计信息
        user_stats = self.auth_manager.get_user_stats(self.token)
        
        if user_stats:
            info_text = f"""
            用户名: {user_stats['username']}
            角色: {user_stats['role']}
            检测次数: {user_stats['detections_count']}
            登录时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """
            
            label = QLabel(info_text.strip())
            label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 3px;")
            layout.addWidget(label)
        
        group.setLayout(layout)
        return group
    
    def _create_params_panel(self) -> QWidget:
        """创建检测参数面板"""
        from PyQt6.QtWidgets import QGroupBox
        
        group = QGroupBox("⚙️  检测参数")
        layout = QVBoxLayout()
        
        # 置信度阈值
        layout.addWidget(QLabel("置信度阈值:"))
        self.conf_slider = QSlider(Qt.Orientation.Horizontal)
        self.conf_slider.setMinimum(10)
        self.conf_slider.setMaximum(95)
        self.conf_slider.setValue(50)
        self.conf_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        layout.addWidget(self.conf_slider)
        
        self.conf_label = QLabel("0.50")
        self.conf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.conf_slider.valueChanged.connect(
            lambda v: self.conf_label.setText(f"{v/100:.2f}")
        )
        layout.addWidget(self.conf_label)
        
        # 检测模式
        layout.addWidget(QLabel("检测模式:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["标志+行人", "仅标志", "仅行人/车辆"])
        layout.addWidget(self.mode_combo)
        
        # IOU阈值
        layout.addWidget(QLabel("IOU阈值:"))
        self.iou_spin = QSpinBox()
        self.iou_spin.setMinimum(10)
        self.iou_spin.setMaximum(95)
        self.iou_spin.setValue(45)
        self.iou_spin.setSuffix(" %")
        layout.addWidget(self.iou_spin)
        
        group.setLayout(layout)
        return group
    
    def _create_image_tab(self) -> QWidget:
        """创建图片检测标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 选择图片按钮
        select_btn = QPushButton("📂 选择图片")
        select_btn.setStyleSheet("background-color: #0066cc;")
        select_btn.clicked.connect(self.select_image)
        layout.addWidget(select_btn)
        
        # 检测按钮
        detect_btn = QPushButton("🔍 开始检测")
        detect_btn.setStyleSheet("background-color: #00aa00;")
        detect_btn.clicked.connect(self.detect_image)
        layout.addWidget(detect_btn)
        
        # 进度条
        self.image_progress = QProgressBar()
        self.image_progress.setVisible(False)
        layout.addWidget(self.image_progress)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_video_tab(self) -> QWidget:
        """创建视频逐帧标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 选择视频
        select_video_btn = QPushButton("🎬 选择视频")
        select_video_btn.setStyleSheet("background-color: #0066cc;")
        select_video_btn.clicked.connect(self.select_video)
        layout.addWidget(select_video_btn)
        
        # 重放控制
        control_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("▶️  播放")
        self.play_btn.setStyleSheet("background-color: #00aa00;")
        self.play_btn.clicked.connect(self.play_video)
        control_layout.addWidget(self.play_btn)
        
        self.pause_btn = QPushButton("⏸️  暂停")
        self.pause_btn.setStyleSheet("background-color: #aa6600;")
        self.pause_btn.clicked.connect(self.pause_video)
        control_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("⏹️  停止")
        self.stop_btn.setStyleSheet("background-color: #aa0000;")
        self.stop_btn.clicked.connect(self.stop_video)
        control_layout.addWidget(self.stop_btn)
        
        layout.addLayout(control_layout)
        
        # 帧位置
        layout.addWidget(QLabel("视频进度:"))
        
        self.frame_slider = QSlider(Qt.Orientation.Horizontal)
        self.frame_slider.sliderMoved.connect(self.video_frame_changed)
        layout.addWidget(self.frame_slider)
        
        self.frame_label = QLabel("Frame: 0 / 0")
        layout.addWidget(self.frame_label)
        
        # FPS显示
        self.fps_label = QLabel("FPS: 0")
        layout.addWidget(self.fps_label)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_camera_tab(self) -> QWidget:
        """创建摄像头标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 摄像头选择
        layout.addWidget(QLabel("摄像头设备:"))
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["默认摄像头", "摄像头2", "摄像头3"])
        layout.addWidget(self.camera_combo)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        self.camera_start_btn = QPushButton("▶️  开启")
        self.camera_start_btn.setStyleSheet("background-color: #00aa00;")
        self.camera_start_btn.clicked.connect(self.start_camera)
        control_layout.addWidget(self.camera_start_btn)
        
        self.camera_stop_btn = QPushButton("⏹️  关闭")
        self.camera_stop_btn.setStyleSheet("background-color: #aa0000;")
        self.camera_stop_btn.clicked.connect(self.stop_camera)
        control_layout.addWidget(self.camera_stop_btn)
        
        layout.addLayout(control_layout)
        
        # FPS和分辨率
        self.camera_fps_label = QLabel("FPS: 0 | 分辨率: 0x0")
        layout.addWidget(self.camera_fps_label)
        
        # 捕获截图
        capture_btn = QPushButton("📸 捕获当前帧")
        capture_btn.setStyleSheet("background-color: #0066cc;")
        capture_btn.clicked.connect(self.capture_camera_frame)
        layout.addWidget(capture_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """处理拖拽释放事件"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self._load_image(file_path)
    
    def select_image(self):
        """选择图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp);;All Files (*)"
        )
        if file_path:
            self._load_image(file_path)
    
    def _load_image(self, file_path: str):
        """加载图片"""
        try:
            image = cv2.imread(file_path)
            if image is None:
                QMessageBox.warning(self, "❌ 错误", "无法读取图片")
                return
            
            self.current_frame = image
            self._display_frame(image)
            self.statusBar().showMessage(f"✅ 已加载: {Path(file_path).name}")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ 错误", f"加载失败: {e}")
    
    def _display_frame(self, frame: np.ndarray):
        """在标签中显示帧"""
        # 调整大小以适应窗口
        height, width = frame.shape[:2]
        max_width, max_height = 600, 500
        
        if width > max_width or height > max_height:
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            frame = cv2.resize(frame, (new_width, new_height))
        
        # 转换为RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, c = frame_rgb.shape
        
        # 转换为QImage
        bytes_per_line = 3 * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # 显示
        pixmap = QPixmap.fromImage(qt_image)
        self.image_label.setPixmap(pixmap.scaledToWidth(600, Qt.TransformationMode.SmoothTransformation))
    
    def detect_image(self):
        """检测当前图片"""
        if self.current_frame is None:
            QMessageBox.warning(self, "⚠️  提示", "请先选择或拖拽一张图片")
            return
        
        try:
            conf = self.conf_slider.value() / 100.0
            mode = self.mode_combo.currentText()  # 获取检测模式
            
            self.image_progress.setVisible(True)
            self.image_progress.setValue(50)
            
            # 执行检测
            annotated_frame, stats = self.worker.process_frame(self.current_frame, conf)
            
            # 根据检测模式过滤结果
            filtered_frame = self.current_frame.copy()
            filtered_detections = []
            
            if mode == "仅标志":
                # 只保留标志检测结果
                for d in stats['detections']:
                    if d.get('type') == 'sign' or 'Mandatory' in d['class'] or 'Warning' in d['class']:
                        filtered_detections.append(d)
                stats['people'] = 0
                stats['vehicles'] = 0
                # 重新绘制仅显示标志的结果
                filtered_frame = self.worker.model_signs.predict(self.current_frame, conf=conf, verbose=False)[0].plot()
                
            elif mode == "仅行人/车辆":
                # 只保留行人和车辆
                for d in stats['detections']:
                    if d.get('type') != 'sign' and 'Mandatory' not in d['class'] and 'Warning' not in d['class']:
                        filtered_detections.append(d)
                stats['signs'] = 0
                # 重新绘制
                result_general = self.worker.model_general.predict(
                    self.current_frame, 
                    classes=[0, 2, 5, 7],
                    conf=conf,
                    verbose=False
                )
                filtered_frame = result_general[0].plot()
                
            else:  # "标志+行人"
                filtered_detections = stats['detections']
                filtered_frame = annotated_frame
            
            self.current_frame = filtered_frame  # 保存标注后的图片
            self.detection_results = [
                {
                    'timestamp': datetime.now().isoformat(),
                    'type': d['class'],
                    'confidence': d.get('confidence', 0),
                    'bbox': d.get('bbox', [])
                }
                for d in filtered_detections
            ]
            
            self._display_frame(filtered_frame)
            
            # 更新统计信息
            self._update_stats(stats)
            
            self.image_progress.setValue(100)
            self.statusBar().showMessage(f"✅ 检测完成 (模式: {mode})")
            
            # 更新用户检测次数
            self.auth_manager.update_detection_count(self.token)
            
        except Exception as e:
            QMessageBox.critical(self, "❌ 错误", f"检测失败: {e}")
        finally:
            self.image_progress.setVisible(False)
    
    def select_video(self):
        """选择视频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频",
            "",
            "Video Files (*.mp4 *.avi *.mov);;All Files (*)"
        )
        if file_path:
            self.video_path = file_path
            self.video_cap = cv2.VideoCapture(file_path)
            self.video_fps = self.video_cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # 配置滑块
            self.frame_slider.setMaximum(self.total_frames - 1)
            self.frame_label.setText(f"Frame: 0 / {self.total_frames}")
            
            self.statusBar().showMessage(f"✅ 已加载视频: {Path(file_path).name}")
    
    def play_video(self):
        """播放视频"""
        if self.video_cap is None:
            QMessageBox.warning(self, "⚠️  提示", "请先选择视频")
            return
        
        # 重置视频追踪器
        self.video_tracker.reset()
        
        self.video_playing = True
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self._process_video_frame)
        self.video_timer.start(int(1000 / self.video_fps) if self.video_fps > 0 else 33)
    
    def pause_video(self):
        """暂停视频"""
        if self.video_timer is not None:
            self.video_timer.stop()
            self.video_playing = False
    
    def stop_video(self):
        """停止视频"""
        self.pause_video()
        if self.video_cap is not None:
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.frame_slider.setValue(0)
    
    def video_frame_changed(self, value: int):
        """视频帧滑块改变"""
        if self.video_cap is not None:
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, value)
            ret, frame = self.video_cap.read()
            if ret:
                self._display_frame(frame)
                self.frame_label.setText(f"Frame: {value} / {self.total_frames}")
    
    def _process_video_frame(self):
        """处理视频帧（带追踪）"""
        if self.video_cap is None:
            return
        
        ret, frame = self.video_cap.read()
        if not ret:
            self.pause_video()
            return
        
        # 检测
        conf = self.conf_slider.value() / 100.0
        mode = self.mode_combo.currentText()  # 获取检测模式
        
        # 使用追踪器处理帧
        tracked_frame, stats = self.worker.get_tracked_detections(
            frame, conf, self.video_tracker
        )
        
        # 根据检测模式过滤结果（视频处理）
        if mode == "仅标志":
            filtered_frame = self.worker.model_signs.predict(frame, conf=conf, verbose=False)[0].plot()
            stats['people'] = 0
            stats['vehicles'] = 0
            stats['tracked_objects'] = 0
        elif mode == "仅行人/车辆":
            # 继续使用当前的追踪帧，but只显示行人/车辆部分
            # 统计已经是正确的（从 get_tracked_detections 中）
            stats['signs'] = 0  # 仅显示行人/车辆
            # 重新绘制仅显示行人/车辆的版本
            result_general = self.worker.model_general.predict(
                frame,
                classes=[0, 2, 5, 7],
                conf=conf,
                verbose=False
            )
            filtered_frame = result_general[0].plot()
        else:  # "标志+行人"
            filtered_frame = tracked_frame
        
        self._display_frame(filtered_frame)
        self._update_stats(stats)
        
        # 更新滑块位置
        current_frame = int(self.video_cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.frame_slider.blockSignals(True)
        self.frame_slider.setValue(current_frame)
        self.frame_slider.blockSignals(False)
        self.frame_label.setText(f"Frame: {current_frame} / {self.total_frames}")
    
    def start_camera(self):
        """启动摄像头"""
        camera_idx = self.camera_combo.currentIndex()
        
        # 重置摄像头追踪器
        self.camera_tracker.reset()
        
        self.camera_cap = cv2.VideoCapture(camera_idx)
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self._process_camera_frame)
        self.camera_timer.start(33)  # ~30 FPS
        
        self.statusBar().showMessage(f"✅ 摄像头已启动")
    
    def stop_camera(self):
        """关闭摄像头"""
        if self.camera_timer is not None:
            self.camera_timer.stop()
        if self.camera_cap is not None:
            self.camera_cap.release()
        self.statusBar().showMessage("⏹️  摄像头已关闭")
    
    def _process_camera_frame(self):
        """处理摄像头帧（带追踪）"""
        if self.camera_cap is None:
            return
        
        ret, frame = self.camera_cap.read()
        if not ret:
            return
        
        # 检测
        conf = self.conf_slider.value() / 100.0
        mode = self.mode_combo.currentText()  # 获取检测模式
        
        # 使用追踪器处理帧
        tracked_frame, stats = self.worker.get_tracked_detections(
            frame, conf, self.camera_tracker
        )
        
        # 根据检测模式过滤结果（摄像头实时处理）
        if mode == "仅标志":
            filtered_frame = self.worker.model_signs.predict(frame, conf=conf, verbose=False)[0].plot()
            stats['people'] = 0
            stats['vehicles'] = 0
            stats['tracked_objects'] = 0
        elif mode == "仅行人/车辆":
            result_general = self.worker.model_general.predict(
                frame,
                classes=[0, 2, 5, 7],
                conf=conf,
                verbose=False
            )
            filtered_frame = result_general[0].plot()
            stats['signs'] = 0
        else:  # "标志+行人"
            filtered_frame = tracked_frame
        
        self._display_frame(filtered_frame)
        self.current_frame = filtered_frame
        self._update_stats(stats)
        
        # 更新FPS和分辨率
        h, w = frame.shape[:2]
        fps = self.camera_cap.get(cv2.CAP_PROP_FPS)
        self.camera_fps_label.setText(f"FPS: {fps:.1f} | 分辨率: {w}x{h}")
    
    def capture_camera_frame(self):
        """从摄像头捕获当前帧"""
        if self.current_frame is None:
            QMessageBox.warning(self, "⚠️  提示", "请先启动摄像头")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"capture_{timestamp}.png"
        
        cv2.imwrite(str(filename), self.current_frame)
        QMessageBox.information(self, "✅ 成功", f"已保存: {filename.name}")
    
    def _update_stats(self, stats: dict):
        """更新统计信息显示"""
        tracking_info = ""
        if stats.get('tracking_active'):
            tracking_info = f"        🎯 追踪对象: {stats.get('tracked_objects', 0)}\n"
        
        text = f"""
        📊 检测统计
        
        标志数: {stats['signs']}
        行人数: {stats['people']}
        车辆数: {stats['vehicles']}
        {tracking_info}
        总检测: {len(stats.get('detections', []))}
        """
        
        self.stats_label.setText(text.strip())
    
    def export_image(self):
        """导出检测结果图片"""
        if self.current_frame is None:
            QMessageBox.warning(self, "⚠️  提示", "没有可导出的图片")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"detection_{timestamp}.png"
        
        cv2.imwrite(str(filename), self.current_frame)
        QMessageBox.information(self, "✅ 成功", f"已导出: {filename.name}")
    
    def export_csv(self):
        """导出检测结果CSV"""
        if not self.detection_results:
            QMessageBox.warning(self, "⚠️  提示", "没有检测结果可导出")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"detection_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['timestamp', 'type', 'confidence', '用户', 'Token'])
                writer.writeheader()
                
                for result in self.detection_results:
                    writer.writerow({
                        'timestamp': result['timestamp'],
                        'type': result['type'],
                        'confidence': f"{result['confidence']:.2f}",
                        '用户': self.username,
                        'Token': self.token[:20] + '...'
                    })
            
            QMessageBox.information(self, "✅ 成功", f"已导出: {filename.name}")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ 错误", f"导出失败: {e}")
    
    def open_results_folder(self):
        """打开结果文件夹"""
        import subprocess
        import sys
        
        try:
            if sys.platform == 'win32':
                subprocess.run(['explorer', str(self.output_dir.absolute())])
            else:
                subprocess.run(['open', str(self.output_dir.absolute())])
        except Exception as e:
            QMessageBox.critical(self, "❌ 错误", f"无法打开文件夹: {e}")
    
    def logout(self):
        """登出"""
        reply = QMessageBox.question(
            self,
            "确认登出",
            "确定要登出吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.auth_manager.logout(self.token)
            self.close()
    
    def connect_signals(self):
        """连接信号"""
        self.worker.frame_ready.connect(self._display_frame)
        self.worker.error_occurred.connect(
            lambda msg: QMessageBox.critical(self, "❌ 错误", msg)
        )
    
    def closeEvent(self, event):
        """关闭事件"""
        # 关闭摄像头和视频
        if self.camera_cap is not None:
            self.camera_cap.release()
        if self.video_cap is not None:
            self.video_cap.release()
        
        # 重置追踪器
        self.video_tracker.reset()
        self.camera_tracker.reset()
        
        # 停止工作线程
        self.worker.stop()
        
        event.accept()
