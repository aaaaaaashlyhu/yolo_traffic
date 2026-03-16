"""
应用程序入口 - PyQt6 交通标志检测系统

支持：
- 用户登录/注册 + Token认证
- 图片拖拽检测
- 视频逐帧处理
- 摄像头实时检测
- 结果导出（CSV + 图片）
"""

import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from login_dialog import LoginDialog
from main_window import MainWindow


def main():
    """应用程序主函数"""
    
    # 创建应用实例
    app = QApplication(sys.argv)
    
    # 设置应用样式和字体
    app.setStyle('Fusion')
    
    try:
        # 显示登录对话框
        login_dialog = LoginDialog()
        
        # 如果登录成功
        if login_dialog.exec() == LoginDialog.DialogCode.Accepted:
            # 获取登录信息
            username = login_dialog.login_successful
            
            # 由于PyQt6信号的工作方式，我们需要直接连接
            def on_login_success(username, token):
                # 创建主窗口
                main_window = MainWindow(username, token)
                main_window.show()
                login_dialog.close()
            
            login_dialog.login_successful.connect(on_login_success)
            
            # 创建主窗口（登录对话框会自动关闭）
            dialog_code = login_dialog.exec()
            
            if dialog_code == LoginDialog.DialogCode.Accepted:
                # 获取信号发出的参数
                # 这里需要保存登录信息
                pass
        else:
            # 用户取消了登录
            return 0
        
        # 运行应用
        return app.exec()
        
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")
        traceback.print_exc()
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("❌ 启动错误")
        msg_box.setText(f"应用启动失败:\n\n{str(e)}")
        msg_box.setDetailedText(traceback.format_exc())
        msg_box.exec()
        
        return 1


# 改进版本 - 处理登录信号
class ApplicationManager:
    """应用管理器 - 处理登录和主窗口切换"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')
        self.login_dialog = None
        self.main_window = None
    
    def run(self):
        """运行应用"""
        try:
            self.login_dialog = LoginDialog()
            self.login_dialog.login_successful.connect(self.on_login_success)
            self.login_dialog.exec()
            
            return self.app.exec()
            
        except Exception as e:
            print(f"❌ 应用错误: {e}")
            traceback.print_exc()
            return 1
    
    def on_login_success(self, username: str, token: str):
        """处理登录成功"""
        try:
            self.main_window = MainWindow(username, token)
            self.main_window.show()
            
            # 关闭登录窗口
            if self.login_dialog:
                self.login_dialog.close()
                
        except Exception as e:
            print(f"❌ 打开主窗口失败: {e}")
            traceback.print_exc()
            
            QMessageBox.critical(
                None,
                "❌ 错误",
                f"无法打开主窗口:\n\n{str(e)}"
            )


if __name__ == '__main__':
    app_manager = ApplicationManager()
    sys.exit(app_manager.run())
