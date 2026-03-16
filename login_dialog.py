"""
登录/注册窗口 - PyQt6

用户身份验证和会话管理
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTabWidget, QWidget, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import pyqtSignal, Qt
from core.auth_manager import get_auth_manager


class LoginDialog(QDialog):
    """登录/注册对话框"""
    
    # 信号：登录成功时发射 (username, token)
    login_successful = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.auth_manager = get_auth_manager()
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("🔐 用户登录 - 交通标志检测系统")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton {
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout()
        
        # 标题
        title = QLabel("交通标志检测系统")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        subtitle = QLabel("智能检测 · 精准识别 · 数据导出")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)
        
        main_layout.addSpacing(20)
        
        # 标签页 - 登录和注册
        tabs = QTabWidget()
        
        # 登录标签页
        login_widget = QWidget()
        login_layout = QVBoxLayout()
        
        login_layout.addWidget(QLabel("用户名:"))
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("输入用户名")
        login_layout.addWidget(self.login_username)
        
        login_layout.addSpacing(10)
        
        login_layout.addWidget(QLabel("密码:"))
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("输入密码")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        login_layout.addWidget(self.login_password)
        
        login_layout.addSpacing(20)
        
        login_btn = QPushButton("🔓 登 录")
        login_btn.setStyleSheet("background-color: #0066cc;")
        login_btn.clicked.connect(self.handle_login)
        login_layout.addWidget(login_btn)
        
        # 演示账号提示
        demo_label = QLabel("📌 演示账号: demo / demo123")
        demo_label.setStyleSheet("color: #666; font-size: 11px;")
        login_layout.addWidget(demo_label)
        
        login_layout.addStretch()
        login_widget.setLayout(login_layout)
        tabs.addTab(login_widget, "🔓 登 录")
        
        # 注册标签页
        register_widget = QWidget()
        register_layout = QVBoxLayout()
        
        register_layout.addWidget(QLabel("用户名:"))
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("3个字符以上")
        register_layout.addWidget(self.register_username)
        
        register_layout.addSpacing(10)
        
        register_layout.addWidget(QLabel("密码:"))
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("6个字符以上")
        self.register_password.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addWidget(self.register_password)
        
        register_layout.addSpacing(10)
        
        register_layout.addWidget(QLabel("确认密码:"))
        self.register_password_confirm = QLineEdit()
        self.register_password_confirm.setPlaceholderText("再次输入密码")
        self.register_password_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addWidget(self.register_password_confirm)
        
        register_layout.addSpacing(10)
        
        register_layout.addWidget(QLabel("邮箱 (可选):"))
        self.register_email = QLineEdit()
        self.register_email.setPlaceholderText("your@email.com")
        register_layout.addWidget(self.register_email)
        
        register_layout.addSpacing(20)
        
        register_btn = QPushButton("✨ 注 册")
        register_btn.setStyleSheet("background-color: #00aa00;")
        register_btn.clicked.connect(self.handle_register)
        register_layout.addWidget(register_btn)
        
        register_layout.addStretch()
        register_widget.setLayout(register_layout)
        tabs.addTab(register_widget, "✨ 注 册")
        
        main_layout.addWidget(tabs)
        
        self.setLayout(main_layout)
        
        # 建立演示账号
        self._create_demo_account()
    
    def _create_demo_account(self):
        """创建演示账号（如果不存在）"""
        # success, msg = self.auth_manager.register("demo", "demo123", "demo@example.com")
        success, msg = self.auth_manager.register("dem", "dem123", "demo@example.com")
        if success:
            print(f"✅ {msg}")
    
    def handle_login(self):
        """处理登录"""
        username = self.login_username.text().strip()
        password = self.login_password.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "⚠️  错误", "请输入用户名和密码")
            return
        
        success, msg, token = self.auth_manager.login(username, password)
        
        if success:
            QMessageBox.information(self, "✅ 成功", msg)
            self.login_successful.emit(username, token)
            self.accept()
        else:
            QMessageBox.warning(self, "❌ 登录失败", msg)
    
    def handle_register(self):
        """处理注册"""
        username = self.register_username.text().strip()
        password = self.register_password.text().strip()
        password_confirm = self.register_password_confirm.text().strip()
        email = self.register_email.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "⚠️  错误", "用户名和密码不能为空")
            return
        
        if password != password_confirm:
            QMessageBox.warning(self, "⚠️  错误", "两次输入的密码不一致")
            return
        
        success, msg = self.auth_manager.register(username, password, email)
        
        if success:
            QMessageBox.information(self, "✅ 成功", f"{msg}\n请切换到登录标签页进行登录")
            # 清空表单
            self.register_username.clear()
            self.register_password.clear()
            self.register_password_confirm.clear()
            self.register_email.clear()
        else:
            QMessageBox.warning(self, "❌ 注册失败", msg)
