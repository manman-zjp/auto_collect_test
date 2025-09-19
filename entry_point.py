#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoCollect 应用程序入口点
支持开发环境和打包后环境
"""

import sys
import os
from pathlib import Path

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，处理打包后的情况"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的路径
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境中的路径
    base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def setup_environment():
    """设置环境变量和路径"""
    # 添加auto_collect到Python路径
    project_root = Path(__file__).parent / "auto_collect"
    if project_root.exists():
        sys.path.insert(0, str(project_root))
    
    # 打包后的路径处理
    if hasattr(sys, '_MEIPASS'):
        sys.path.insert(0, sys._MEIPASS)
        sys.path.insert(0, os.path.join(sys._MEIPASS, 'auto_collect'))
    
    print(f"Python executable: {sys.executable}")
    print(f"Project root: {project_root}")
    print(f"Working directory: {os.getcwd()}")

def main():
    """主程序入口函数"""
    setup_environment()
    
    try:
        # 导入主模块
        from main import main as app_main
        print("Successfully imported main module")
        return app_main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Trying alternative import...")
        try:
            # 尝试直接导入
            from auto_collect.main import main as app_main
            print("Successfully imported via auto_collect.main")
            return app_main()
        except ImportError as e2:
            print(f"Alternative import also failed: {e2}")
            raise e
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        
        # 显示错误对话框
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "Error", f"Failed to start application:\n{str(e)}")
        except:
            pass
        raise

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code or 0)
    except Exception as e:
        print(f"Application startup failed: {e}")
        sys.exit(1)