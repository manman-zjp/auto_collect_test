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

def check_dependencies():
    """检查构建依赖"""
    print("检查构建依赖...")
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} 已安装")
    except ImportError:
        print("✗ PyInstaller 未安装，正在安装...")
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
            print(f"✓ {package_name} 已安装")
        except ImportError:
            print(f"✗ {package_name} 未安装")
            return False
    
    return True

def clean_build_dirs():
    """清理构建目录"""
    print("清理构建目录...")
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"✓ 已清理 {dir_name}")

def create_macos_app(dist_dir):
    """在macOS上创建.app包"""
    print("\n创建macOS应用程序包...")
    
    app_name = "AutoCollect.app"
    app_dir = dist_dir.parent / app_name
    
    try:
        # 创建应用程序包结构
        contents_dir = app_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        # 创建目录
        for dir_path in [contents_dir, macos_dir, resources_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 复制可执行文件和依赖
        if dist_dir.exists():
            shutil.copytree(dist_dir, macos_dir / "AutoCollect", dirs_exist_ok=True)
        
        # 创建Info.plist文件
        info_plist = contents_dir / "Info.plist"
        plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>AutoCollect/AutoCollect</string>
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
</dict>
</plist>'''
        
        info_plist.write_text(plist_content)
        
        # 创建启动脚本
        launcher_script = macos_dir / "AutoCollect_launcher"
        launcher_content = f'''#!/bin/bash
cd "$(dirname "$0")"
./AutoCollect/AutoCollect
'''
        launcher_script.write_text(launcher_content)
        launcher_script.chmod(0o755)
        
        print(f"✓ 已创建 {app_dir.absolute()}")
        
    except Exception as e:
        print(f"创建macOS应用程序包失败: {e}")

def build_app():
    """为当前平台构建可执行文件"""
    system = platform.system()
    print(f"为 {system} 平台构建应用...")
    
    # 检查依赖
    if not check_dependencies():
        print("依赖检查失败，请先安装所有必需的依赖")
        return False
    
    # 清理构建目录
    clean_build_dirs()
    
    # 检查storage_state.json是否存在
    storage_file = Path("auto_collect/storage_state.json")
    if not storage_file.exists():
        storage_file.parent.mkdir(parents=True, exist_ok=True)
        storage_file.write_text("{}")
        print("创建了空的 storage_state.json 文件")
    
    # 使用spec文件构建
    spec_file = "AutoCollect.spec"
    if Path(spec_file).exists():
        print(f"使用 {spec_file} 进行构建...")
        cmd = [sys.executable, "-m", "PyInstaller", spec_file, "--clean", "--noconfirm"]
    else:
        print("使用命令行参数进行构建...")
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
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功完成!")
        
        # 显示构建结果位置
        dist_dir = Path("dist/AutoCollect")
        if dist_dir.exists():
            print(f"\n构建结果位置: {dist_dir.absolute()}")
            
            # 显示应用大小
            total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
            print(f"应用总大小: {total_size / (1024*1024):.1f} MB")
            
            # 在macOS上创建应用程序包
            if system == "Darwin":
                create_macos_app(dist_dir)
        
        return True
    except subprocess.CalledProcessError as e:
        print("构建失败:")
        print(f"错误代码: {e.returncode}")
        print(f"错误输出: {e.stderr}")
        if e.stdout:
            print(f"标准输出: {e.stdout}")
        return False
    except Exception as e:
        print(f"构建过程中发生未知错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("AutoCollect 应用构建工具")
    print("=" * 50)
    
    # 检查是否需要跨平台构建
    if len(sys.argv) > 1 and sys.argv[1] == '--cross-platform':
        print("🚀 启动跨平台构建模式")
        try:
            os.system("python cross_platform_build.py")
            return 0
        except Exception as e:
            print(f"❌ 跨平台构建失败: {e}")
            return 1
    
    success = build_app()
    
    if success:
        print("\n" + "=" * 50)
        print("构建完成！")
        print("可执行文件位于 dist/ 目录中")
        
        # 提示跨平台构建选项
        current_os = platform.system()
        if current_os == "Darwin":
            print("\n📝 提示: 要构建 Windows 版本，请运行:")
            print("  python build.py --cross-platform")
            print("  或")
            print("  python cross_platform_build.py")
        
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("构建失败！请检查错误信息")
        print("=" * 50)
    
    return 0 if success else 1

if __name__ == "__main__":
    success = main()
    sys.exit(success)