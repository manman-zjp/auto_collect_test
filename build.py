#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoCollect 构建脚本
支持 Mac 和 Windows 平台的独立可执行文件打包
"""

import sys
import os
import platform
import subprocess
import shutil
from pathlib import Path

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    # 设置环境变量确保正确的编码
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def check_dependencies():
    """检查构建依赖"""
    try:
        print("检查构建依赖...")
    except UnicodeEncodeError:
        print("Checking build dependencies...")
    
    # 检查PyInstaller
    try:
        import PyInstaller
        try:
            print(f"✓ PyInstaller {PyInstaller.__version__} 已安装")
        except UnicodeEncodeError:
            print(f"✓ PyInstaller {PyInstaller.__version__} installed")
    except ImportError:
        try:
            print("✗ PyInstaller 未安装，正在安装...")
        except UnicodeEncodeError:
            print("✗ PyInstaller not installed, installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # 检查其他依赖
    required_modules = {
        'PyQt6': 'PyQt6',
        'requests': 'requests', 
        'beautifulsoup4': 'bs4',
        'tqdm': 'tqdm',
        'playwright': 'playwright',
        'tweepy': 'tweepy',
        'selenium': 'selenium'
    }
    
    for package_name, import_name in required_modules.items():
        try:
            __import__(import_name)
            try:
                print(f"✓ {package_name} 已安装")
            except UnicodeEncodeError:
                print(f"✓ {package_name} installed")
        except ImportError:
            try:
                print(f"✗ {package_name} 未安装")
            except UnicodeEncodeError:
                print(f"✗ {package_name} not installed")
            return False
    
    return True

def clean_build_dirs():
    """清理构建目录"""
    try:
        print("清理构建目录...")
    except UnicodeEncodeError:
        print("Cleaning build directories...")
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            try:
                print(f"✓ 已清理 {dir_name}")
            except UnicodeEncodeError:
                print(f"✓ Cleaned {dir_name}")

def create_macos_app(dist_dir):
    """在macOS上创建.app包"""
    try:
        print("\n创建macOS应用程序包...")
    except UnicodeEncodeError:
        print("\nCreating macOS application bundle...")
    
    app_name = "AutoCollect.app"
    app_dir = dist_dir.parent / app_name
    
    try:
        # 删除旧的.app包
        if app_dir.exists():
            shutil.rmtree(app_dir)
        
        # 创建应用程序包结构
        contents_dir = app_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        # 创建目录
        for dir_path in [contents_dir, macos_dir, resources_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 复制整个应用目录到MacOS目录下（重命名避免冲突）
        if dist_dir.exists():
            app_exec_dir = macos_dir / "AutoCollect_App" 
            shutil.copytree(dist_dir, app_exec_dir)
        
        # 创建Info.plist文件
        info_plist = contents_dir / "Info.plist"
        plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>AutoCollect</string>
    <key>CFBundleIdentifier</key>
    <string>com.autocollect.app</string>
    <key>CFBundleName</key>
    <string>AutoCollect</string>
    <key>CFBundleDisplayName</key>
    <string>AutoCollect</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSBackgroundOnly</key>
    <false/>
</dict>
</plist>'''
        
        info_plist.write_text(plist_content)
        
        # 创建启动脚本
        launcher_script = macos_dir / "AutoCollect"
        launcher_content = '''#!/bin/bash
# AutoCollect 应用启动器

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 设置工作目录为应用包所在目录的上级目录
cd "$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")" 

# 启动应用程序
exec "$SCRIPT_DIR/AutoCollect_App/AutoCollect" "$@"
'''
        launcher_script.write_text(launcher_content)
        launcher_script.chmod(0o755)
        
        try:
            print(f"✓ 已创建 {app_dir.absolute()}")
        except UnicodeEncodeError:
            print(f"✓ Created {app_dir.absolute()}")
        
    except Exception as e:
        try:
            print(f"创建macOS应用程序包失败: {e}")
        except UnicodeEncodeError:
            print(f"Failed to create macOS application bundle: {e}")

def build_app():
    """为当前平台构建可执行文件"""
    system = platform.system()
    try:
        print(f"为 {system} 平台构建应用...")
    except UnicodeEncodeError:
        print(f"Building application for {system} platform...")
    
    # 检查依赖
    if not check_dependencies():
        try:
            print("依赖检查失败，请先安装所有必需的依赖")
        except UnicodeEncodeError:
            print("Dependency check failed, please install all required dependencies")
        return False
    
    # 清理构建目录
    clean_build_dirs()
    
    # 检查storage_state.json是否存在
    storage_file = Path("auto_collect/storage_state.json")
    if not storage_file.exists():
        storage_file.parent.mkdir(parents=True, exist_ok=True)
        storage_file.write_text("{}")
        try:
            print("创建了空的 storage_state.json 文件")
        except UnicodeEncodeError:
            print("Created empty storage_state.json file")
    
    # 使用spec文件构建
    spec_file = "AutoCollect.spec"
    if Path(spec_file).exists():
        try:
            print(f"使用 {spec_file} 进行构建...")
        except UnicodeEncodeError:
            print(f"Building with {spec_file}...")
        cmd = [sys.executable, "-m", "PyInstaller", spec_file, "--clean", "--noconfirm"]
    else:
        try:
            print("使用命令行参数进行构建...")
        except UnicodeEncodeError:
            print("Building with command line arguments...")
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--windowed",
            "--onedir",
            "--name", "AutoCollect",
            "--add-data", f"auto_collect{os.pathsep}auto_collect",
            "--hidden-import", "PyQt6.sip",
            "--hidden-import", "auto_collect.ui.main_window",
            "--hidden-import", "auto_collect.crawler.manager",
            "--collect-all", "auto_collect",
            "--clean",
            "--noconfirm",
            "entry_point.py"
        ]
    
    try:
        print(f"执行命令: {' '.join(cmd)}")
    except UnicodeEncodeError:
        print(f"Executing command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        try:
            print("构建成功完成!")
        except UnicodeEncodeError:
            print("Build completed successfully!")
        
        # 显示构建结果位置
        dist_dir = Path("dist/AutoCollect")
        if dist_dir.exists():
            try:
                print(f"\n构建结果位置: {dist_dir.absolute()}")
            except UnicodeEncodeError:
                print(f"\nBuild result location: {dist_dir.absolute()}")
            
            # 显示应用大小
            total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
            try:
                print(f"应用总大小: {total_size / (1024*1024):.1f} MB")
            except UnicodeEncodeError:
                print(f"Application total size: {total_size / (1024*1024):.1f} MB")
            
            # 在macOS上创建应用程序包
            if system == "Darwin":
                create_macos_app(dist_dir)
        
        return True
    except subprocess.CalledProcessError as e:
        try:
            print("构建失败:")
            print(f"错误代码: {e.returncode}")
            print(f"错误输出: {e.stderr}")
            if e.stdout:
                print(f"标准输出: {e.stdout}")
        except UnicodeEncodeError:
            print("Build failed:")
            print(f"Error code: {e.returncode}")
            print(f"Error output: {e.stderr}")
            if e.stdout:
                print(f"Standard output: {e.stdout}")
        return False
    except Exception as e:
        try:
            print(f"构建过程中发生未知错误: {e}")
        except UnicodeEncodeError:
            print(f"Unknown error during build: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    try:
        print("AutoCollect 应用构建工具")
    except UnicodeEncodeError:
        print("AutoCollect Application Build Tool")
    print("=" * 50)
    
    # 检查是否需要跨平台构建
    if len(sys.argv) > 1 and sys.argv[1] == '--cross-platform':
        try:
            print("🚀 启动跨平台构建模式")
        except UnicodeEncodeError:
            print("🚀 Starting cross-platform build mode")
        try:
            os.system("python cross_platform_build.py")
            return 0
        except Exception as e:
            try:
                print(f"❌ 跨平台构建失败: {e}")
            except UnicodeEncodeError:
                print(f"❌ Cross-platform build failed: {e}")
            return 1
    
    success = build_app()
    
    if success:
        print("\n" + "=" * 50)
        try:
            print("构建完成！")
            print("可执行文件位于 dist/ 目录中")
        except UnicodeEncodeError:
            print("Build completed!")
            print("Executable files are located in dist/ directory")
        
        # 提示跨平台构建选项
        current_os = platform.system()
        if current_os == "Darwin":
            try:
                print("\n📝 提示: 要构建 Windows 版本，请运行:")
                print("  python build.py --cross-platform")
                print("  或")
                print("  python cross_platform_build.py")
            except UnicodeEncodeError:
                print("\n📝 Tip: To build Windows version, run:")
                print("  python build.py --cross-platform")
                print("  or")
                print("  python cross_platform_build.py")
        
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        try:
            print("构建失败！请检查错误信息")
        except UnicodeEncodeError:
            print("Build failed! Please check error messages")
        print("=" * 50)
    
    return 0 if success else 1

if __name__ == "__main__":
    success = main()
    sys.exit(success)