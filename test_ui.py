#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的UI测试脚本
用于诊断窗口显示问题
"""

import sys
import os
from pathlib import Path

# 添加auto_collect到Python路径
project_root = Path(__file__).parent / "auto_collect"
sys.path.insert(0, str(project_root))

print(f"Python executable: {sys.executable}")
print(f"sys.path: {sys.path}")
print(f"Working directory: {os.getcwd()}")

try:
    from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
    from PyQt6.QtCore import Qt

    print("PyQt6 imported successfully")

    app = QApplication(sys.argv)
    print("QApplication created")

    # 创建一个简单的测试窗口
    window = QWidget()
    window.setWindowTitle("AutoCollect - 测试窗口")
    window.resize(400, 300)
    
    layout = QVBoxLayout()
    label = QLabel("如果您能看到这个窗口，说明Qt界面正常工作")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    button = QPushButton("点击测试")
    
    def on_click():
        label.setText("按钮点击成功！")
    
    button.clicked.connect(on_click)
    
    layout.addWidget(label)
    layout.addWidget(button)
    window.setLayout(layout)
    
    print("Test window created")
    
    # 强制显示窗口
    window.show()
    window.raise_()
    window.activateWindow()
    
    print("Test window shown")
    print(f"Window visible: {window.isVisible()}")
    print(f"Window position: {window.x()}, {window.y()}")
    print(f"Window size: {window.width()}x{window.height()}")
    
    # 在macOS上尝试置于前台
    if sys.platform == "darwin":
        import subprocess
        try:
            subprocess.run(["osascript", "-e", 'tell application "System Events" to set frontmost of first process whose unix id is ' + str(os.getpid()) + ' to true'], check=False)
            print("macOS frontmost script executed")
        except Exception as e:
            print(f"macOS frontmost script failed: {e}")
    
    print("Starting event loop...")
    sys.exit(app.exec())

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)