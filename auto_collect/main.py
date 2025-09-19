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

    # 修复导入路径问题
    # 添加当前目录到sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    try:
        # 首先尝试直接导入（适用于打包后的环境）
        from ui.main_window import MainWindow
        print("Successfully imported MainWindow")
    except ImportError as e:
        print(f"Direct import failed: {e}")
        try:
            # 备用：相对导入
            from .ui.main_window import MainWindow
            print("Successfully imported MainWindow via relative import")
        except ImportError as e2:
            print(f"Relative import also failed: {e2}")
            try:
                # 最后尝试：绝对路径导入
                import importlib.util
                ui_path = os.path.join(current_dir, 'ui', 'main_window.py')
                spec = importlib.util.spec_from_file_location("main_window", ui_path)
                if spec is not None and spec.loader is not None:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    MainWindow = module.MainWindow
                    print("Successfully imported MainWindow via absolute path")
                else:
                    raise ImportError("Failed to create module spec")
            except Exception as e3:
                print(f"All import methods failed: {e3}")
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