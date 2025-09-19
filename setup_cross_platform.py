#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoCollect 跨平台构建一键设置脚本
快速配置所有必要的构建工具和文件
"""

import sys
import os
import platform
import subprocess
from pathlib import Path
import json

def banner():
    print("=" * 60)
    print("🚀 AutoCollect 跨平台构建一键设置")
    print("=" * 60)
    print("本脚本将帮您设置所有必要的构建工具和配置文件")
    print()

def check_current_setup():
    """检查当前环境配置"""
    print("🔍 检查当前环境...")
    
    setup_status = {
        "python": False,
        "pyinstaller": False, 
        "dependencies": False,
        "github_actions": False,
        "docker": False,
        "wine": False
    }
    
    # 检查 Python
    try:
        python_version = sys.version
        print(f"✅ Python: {python_version.split()[0]}")
        setup_status["python"] = True
    except:
        print("❌ Python 未安装")
    
    # 检查 PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller: {PyInstaller.__version__}")
        setup_status["pyinstaller"] = True
    except ImportError:
        print("❌ PyInstaller 未安装")
    
    # 检查项目依赖
    required_modules = ['PyQt6', 'requests', 'beautifulsoup4', 'tqdm', 'playwright', 'tweepy', 'selenium']
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'beautifulsoup4':
                __import__('bs4')
            else:
                __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if not missing_modules:
        print("✅ 项目依赖: 已安装")
        setup_status["dependencies"] = True
    else:
        print(f"❌ 项目依赖: 缺少 {', '.join(missing_modules)}")
    
    # 检查 GitHub Actions
    github_workflow = Path(".github/workflows/build.yml")
    if github_workflow.exists():
        print("✅ GitHub Actions: 已配置")
        setup_status["github_actions"] = True
    else:
        print("❌ GitHub Actions: 未配置")
    
    # 检查 Docker
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker: {result.stdout.strip()}")
            setup_status["docker"] = True
        else:
            print("❌ Docker: 未安装或未运行")
    except FileNotFoundError:
        print("❌ Docker: 未安装")
    
    # 检查 Wine (仅 macOS)
    if platform.system() == "Darwin":
        try:
            result = subprocess.run(["wine", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Wine: {result.stdout.strip()}")
                setup_status["wine"] = True
            else:
                print("❌ Wine: 未安装")
        except FileNotFoundError:
            print("❌ Wine: 未安装")
    
    return setup_status

def install_pyinstaller():
    """安装 PyInstaller"""
    print("\n📦 安装 PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller>=6.0.0"], check=True)
        print("✅ PyInstaller 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller 安装失败: {e}")
        return False

def install_dependencies():
    """安装项目依赖"""
    print("\n📦 安装项目依赖...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt 文件不存在")
        return False
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ 项目依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 项目依赖安装失败: {e}")
        return False

def setup_github_actions():
    """设置 GitHub Actions"""
    print("\n🚀 设置 GitHub Actions...")
    
    # 运行跨平台构建工具来创建 GitHub Actions 配置
    try:
        # 直接调用函数而不是运行外部进程
        from cross_platform_build import build_windows_with_github_actions
        build_windows_with_github_actions()
        print("✅ GitHub Actions 配置成功")
        return True
    except Exception as e:
        print(f"❌ GitHub Actions 配置失败: {e}")
        return False

def install_docker():
    """提供 Docker 安装指导"""
    print("\n🐳 Docker 安装指导...")
    current_os = platform.system()
    
    if current_os == "Darwin":
        print("macOS 用户请按以下步骤安装 Docker:")
        print("1. 访问 https://www.docker.com/products/docker-desktop")
        print("2. 下载 Docker Desktop for Mac")
        print("3. 安装并启动 Docker Desktop")
        print("4. 确保 Docker 正在运行（菜单栏有 Docker 图标）")
    elif current_os == "Windows":
        print("Windows 用户请按以下步骤安装 Docker:")
        print("1. 访问 https://www.docker.com/products/docker-desktop") 
        print("2. 下载 Docker Desktop for Windows")
        print("3. 安装并启动 Docker Desktop")
        print("4. 可能需要启用 WSL2")
    else:
        print("Linux 用户请按发行版安装 Docker:")
        print("Ubuntu/Debian: sudo apt install docker.io")
        print("CentOS/RHEL: sudo yum install docker")
        print("Arch: sudo pacman -S docker")
    
    print("\n安装完成后，请重新运行此脚本验证安装")

def install_wine():
    """安装 Wine (仅 macOS)"""
    print("\n🍷 安装 Wine...")
    
    if platform.system() != "Darwin":
        print("Wine 安装仅适用于 macOS")
        return False
    
    # 检查 Homebrew
    try:
        subprocess.run(["brew", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ 需要先安装 Homebrew")
        print("安装命令: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False
    
    try:
        print("正在安装 Wine，这可能需要几分钟...")
        subprocess.run(["brew", "install", "--cask", "wine-stable"], check=True)
        print("✅ Wine 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Wine 安装失败: {e}")
        print("您可以稍后手动安装: brew install --cask wine-stable")
        return False

def create_build_scripts():
    """创建便捷的构建脚本"""
    print("\n📝 创建便捷构建脚本...")
    
    # macOS/Linux 构建脚本
    build_script = """#!/bin/bash
# AutoCollect 快速构建脚本

echo "🚀 AutoCollect 快速构建"
echo "选择构建方式:"
echo "1. 仅构建当前平台"
echo "2. 跨平台构建 (GitHub Actions)"
echo "3. 本地跨平台构建 (Docker)"

read -p "请选择 (1-3): " choice

case $choice in
    1)
        echo "构建当前平台..."
        python build.py
        ;;
    2)
        echo "配置 GitHub Actions..."
        python cross_platform_build.py
        ;;
    3)
        echo "本地跨平台构建..."
        python cross_platform_build.py
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo "构建完成！"
"""
    
    script_path = Path("quick_build.sh")
    script_path.write_text(build_script)
    script_path.chmod(0o755)
    
    # Windows 构建脚本
    windows_script = """@echo off
echo 🚀 AutoCollect 快速构建
echo 选择构建方式:
echo 1. 仅构建当前平台
echo 2. 跨平台构建 (GitHub Actions)

set /p choice="请选择 (1-2): "

if "%choice%"=="1" (
    echo 构建当前平台...
    python build.py
) else if "%choice%"=="2" (
    echo 配置 GitHub Actions...
    python cross_platform_build.py
) else (
    echo 无效选择
    exit /b 1
)

echo 构建完成！
pause
"""
    
    windows_script_path = Path("quick_build.bat")
    windows_script_path.write_text(windows_script)
    
    print("✅ 构建脚本创建成功:")
    print(f"  - {script_path.absolute()}")
    print(f"  - {windows_script_path.absolute()}")

def create_project_config():
    """创建项目配置文件"""
    print("\n⚙️ 创建项目配置...")
    
    config = {
        "name": "AutoCollect",
        "version": "1.0.0",
        "description": "X/T.me 数据抓取工具",
        "platforms": ["macOS", "Windows"],
        "build_tools": {
            "pyinstaller": True,
            "github_actions": True,
            "docker": True,
            "wine": platform.system() == "Darwin"
        },
        "created_by": "setup_cross_platform.py"
    }
    
    config_file = Path("build_config.json")
    config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False))
    
    print(f"✅ 项目配置已保存: {config_file.absolute()}")

def main():
    """主函数"""
    banner()
    
    # 检查当前环境
    setup_status = check_current_setup()
    
    print("\n" + "=" * 60)
    print("🛠️ 开始设置...")
    
    # 安装缺失的组件
    if not setup_status["pyinstaller"]:
        if not install_pyinstaller():
            print("⚠️ PyInstaller 安装失败，某些构建功能可能不可用")
    
    if not setup_status["dependencies"]:
        if not install_dependencies():
            print("⚠️ 依赖安装失败，请手动安装 requirements.txt 中的包")
    
    if not setup_status["github_actions"]:
        if not setup_github_actions():
            print("⚠️ GitHub Actions 配置失败，可以稍后手动配置")
    
    # 提供可选组件的安装指导
    if not setup_status["docker"]:
        install_docker()
    
    if platform.system() == "Darwin" and not setup_status["wine"]:
        choice = input("\n是否安装 Wine (用于本地 Windows 构建)? (y/N): ").lower()
        if choice == 'y':
            install_wine()
    
    # 创建便捷脚本和配置
    create_build_scripts()
    create_project_config()
    
    print("\n" + "=" * 60)
    print("🎉 设置完成！")
    print("=" * 60)
    
    print("\n📋 可用的构建方式:")
    print("1. 快速构建脚本: ./quick_build.sh (macOS/Linux) 或 quick_build.bat (Windows)")
    print("2. 跨平台构建: python cross_platform_build.py")
    print("3. 传统构建: python build.py")
    
    print("\n📖 详细说明请查看: CROSS_PLATFORM_BUILD.md")
    
    print("\n🚀 建议的下一步:")
    if setup_status["github_actions"]:
        print("1. 将代码推送到 GitHub 仓库")
        print("2. GitHub Actions 将自动构建两个平台版本")
    else:
        print("1. 运行 python cross_platform_build.py")
        print("2. 选择合适的构建方式")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())