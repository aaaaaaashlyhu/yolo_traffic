#!/usr/bin/env python
"""
一键启动脚本 - 快速运行应用

这是最简单的启动方式，自动处理所有初始化
"""

import sys
import os
from pathlib import Path

# 确保在项目目录
os.chdir(Path(__file__).parent)

def main():
    """主启动函数"""
    
    print("\n" + "=" * 70)
    print("🎯 交通标志检测系统".center(70))
    print("=" * 70)
    print("\n⏳ 初始化应用中...\n")
    
    try:
        # 导入应用管理器
        from app import ApplicationManager
        
        # 运行应用
        manager = ApplicationManager()
        exit_code = manager.run()
        
        return exit_code
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("\n请先安装依赖:")
        print("  pip install -r requirements_pyqt6.txt")
        return 1
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
