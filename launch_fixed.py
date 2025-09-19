#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoCollect 紧急修复版本
强制窗口显示并简化初始化
"""

import sys
import os
from pathlib import Path

# 添加auto_collect到Python路径
project_root = Path(__file__).parent / "auto_collect"
if project_root.exists():
    sys.path.insert(0, str(project_root))

def main():
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # 在macOS上设置特殊标志
        if sys.platform == "darwin":
            # 确保应用程序在前台启动
            os.environ["QT_MAC_WANTS_LAYER"] = "1"
        
        app = QApplication(sys.argv)
        
        # 强制设置应用程序属性
        app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
        app.setQuitOnLastWindowClosed(True)
        
        print("QApplication created successfully")
        
        # 导入并创建主窗口
        from ui.main_window import MainWindow
        
        window = MainWindow()
        print("MainWindow created")
        
        # 强制设置窗口属性
        window.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        window.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        
        # 设置窗口到屏幕中央
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            window_size = window.size()
            x = (screen_geometry.width() - window_size.width()) // 2
            y = (screen_geometry.height() - window_size.height()) // 2
            window.move(x, y)
            print(f"Window moved to center: {x}, {y}")
        
        # 强制显示窗口
        window.show()
        window.raise_()
        window.activateWindow()
        
        # 移除置顶标志
        window.setWindowFlags(Qt.WindowType.Window)
        window.show()
        
        print(f"Window visible: {window.isVisible()}")
        print(f"Window position: {window.x()}, {window.y()}")
        print(f"Window size: {window.width()}x{window.height()}")
        
        # 在macOS上使用AppleScript强制显示
        if sys.platform == "darwin":
            try:
                import subprocess
                app_name = "Python"  # 或者应用程序的实际名称
                script = f'''
                tell application "System Events"
                    tell process "{app_name}"
                        set frontmost to true
                    end tell
                end tell
                '''
                subprocess.run(["osascript", "-e", script], check=False)
                print("AppleScript executed to bring window to front")
            except Exception as e:
                print(f"AppleScript failed: {e}")
        
        print("Starting event loop...")
        return app.exec()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())