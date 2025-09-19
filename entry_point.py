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
        return os.path.join(getattr(sys, '_MEIPASS'), relative_path)
    # 开发环境中的路径
    base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def setup_environment():
    """设置环境变量和路径"""
    # 添加auto_collect到Python路径
    project_root = Path(__file__).parent
    auto_collect_path = project_root / "auto_collect"
    
    # 确保各种路径都在sys.path中
    paths_to_add = [
        str(project_root),
        str(auto_collect_path)
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # 打包后的路径处理
    if hasattr(sys, '_MEIPASS'):
        meipass = getattr(sys, '_MEIPASS')
        sys.path.insert(0, meipass)
        sys.path.insert(0, os.path.join(meipass, 'auto_collect'))
    
    print(f"Python executable: {sys.executable}")
    print(f"Project root: {project_root}")
    print(f"Auto collect path: {auto_collect_path}")
    print(f"Working directory: {os.getcwd()}")
    print(f"sys.path (first 5): {sys.path[:5]}")

def main():
    """主程序入口函数"""
    setup_environment()
    
    try:
        # 导入主模块
        from auto_collect.main import main as app_main
        print("Successfully imported main module from auto_collect.main")
        return app_main()
    except ImportError as e:
        print(f"Import from auto_collect.main failed: {e}")
        print("Trying alternative import...")
        try:
            # 尝试直接导入  # type: ignore
            from main import main as app_main  # type: ignore
            print("Successfully imported via main")
            return app_main()
        except ImportError as e2:
            print(f"Alternative import also failed: {e2}")
            # 最后尝试：手动构建路径
            try:
                import importlib.util
                main_path = Path(__file__).parent / "auto_collect" / "main.py"
                print(f"Trying to load from: {main_path}")
                
                if main_path.exists():
                    spec = importlib.util.spec_from_file_location("main", main_path)
                    if spec is not None and spec.loader is not None:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        app_main = module.main
                        print("Successfully imported via absolute path")
                        return app_main()
                    else:
                        raise ImportError("Failed to create module spec")
                else:
                    raise ImportError(f"Main module not found at {main_path}")
            except Exception as e3:
                print(f"Absolute path import failed: {e3}")
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