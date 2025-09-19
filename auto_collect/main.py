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

def main():
    """主程序入口函数"""
    # 添加调试信息
    print("Python executable:", sys.executable)
    print("sys.path:", sys.path)
    print("__file__:", __file__)
    print("Current working directory:", os.getcwd())

    try:
        # 首先尝试相对导入
        from .ui.main_window import MainWindow
        print("Successfully imported MainWindow")
    except ImportError as e:
        print(f"Relative import failed: {e}")
        try:
            # 备用：绝对导入
            from ui.main_window import MainWindow
            print("Successfully imported MainWindow via absolute import")
        except ImportError as e2:
            print(f"Absolute import also failed: {e2}")
            import traceback
            traceback.print_exc()
            raise

    from PyQt6.QtWidgets import QApplication

    # 在 macOS 上优化显示效果
    if sys.platform == "darwin":
        # 不再设置 QT_MAC_WANTS_LAYER，因为 Layer-backing 已经默认启用
        print("检测到 macOS 系统")
    
    app = QApplication(sys.argv)
    print("Created QApplication")
    
    try:
        window = MainWindow()
        print("Created MainWindow")
        
        # 确保窗口在屏幕中央显示并强制激活
        window.move(100, 100)  # 移动到屏幕左上角偏移位置
        window.show()  # 先显示窗口
        window.raise_()  # 将窗口提到最前
        window.activateWindow()  # 激活窗口
        
        # 在macOS上强制将窗口置于前台
        if sys.platform == "darwin":
            try:
                # 尝试将应用程序置于前台
                import subprocess
                subprocess.run(["osascript", "-e", 'tell application "System Events" to set frontmost of first process whose unix id is ' + str(os.getpid()) + ' to true'], check=False)
            except:
                pass
        
        print("Configured window")
        print("应用程序已启动，窗口应该可见")
        print(f"窗口位置: {window.x()}, {window.y()}")
        print(f"窗口大小: {window.width()}x{window.height()}")
        print("如果看不到窗口，请检查 Dock 或使用 Cmd+Tab 切换")
        
        return app.exec()
    except Exception as e:
        print(f"启动应用程序时出错: {e}")
        import traceback
        traceback.print_exc()
        # 在GUI应用中显示错误对话框
        try:
            from PyQt6.QtWidgets import QMessageBox
            error_app = QApplication(sys.argv)
            QMessageBox.critical(None, "错误", f"启动应用程序时出错:\n{str(e)}\n\n请查看终端输出了解详细信息。")
        except:
            pass
        raise

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        sys.exit(1)