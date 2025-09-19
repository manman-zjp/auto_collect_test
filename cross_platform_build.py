#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoCollect 跨平台构建脚本
支持同时构建 macOS 和 Windows 版本
"""

import sys
import os
import platform
import subprocess
import shutil
import tempfile
import json
from pathlib import Path
from datetime import datetime

def get_project_info():
    """获取项目信息"""
    return {
        "name": "AutoCollect",
        "version": "1.0.0",
        "description": "X/T.me 数据抓取工具",
        "author": "AutoCollect Team"
    }

def build_current_platform():
    """构建当前平台版本"""
    print(f"🔨 构建当前平台 ({platform.system()}) 版本...")
    
    # 调用现有的构建脚本
    try:
        result = subprocess.run([sys.executable, "build.py"], check=True, capture_output=True, text=True)
        print("✅ 当前平台构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 当前平台构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def build_windows_with_docker():
    """使用 Docker 构建 Windows 版本"""
    print("🐳 使用 Docker 构建 Windows 版本...")
    
    # 创建 Dockerfile
    dockerfile_content = '''FROM python:3.12-windowsservercore

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pyinstaller

# 构建应用
RUN python build_windows_docker.py

# 输出构建结果
CMD ["cmd"]
'''
    
    dockerfile_path = Path("Dockerfile.windows")
    dockerfile_path.write_text(dockerfile_content)
    
    # 创建 Windows Docker 构建脚本
    windows_build_script = '''
import sys
import os
import subprocess
from pathlib import Path

def build_windows():
    """Windows Docker 环境下的构建"""
    print("开始 Windows 构建...")
    
    # 检查storage_state.json
    storage_file = Path("auto_collect/storage_state.json")
    if not storage_file.exists():
        storage_file.parent.mkdir(parents=True, exist_ok=True)
        storage_file.write_text("{}")
    
    # PyInstaller 命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--windowed",
        "--onedir", 
        "--name", "AutoCollect",
        "--add-data", "auto_collect;auto_collect",
        "--hidden-import", "PyQt6.sip",
        "--hidden-import", "auto_collect.ui.main_window",
        "--hidden-import", "auto_collect.crawler.manager",
        "--collect-all", "auto_collect",
        "--clean",
        "--noconfirm",
        "entry_point.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("Windows 构建成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Windows 构建失败: {e}")
        return False

if __name__ == "__main__":
    build_windows()
'''
    
    Path("build_windows_docker.py").write_text(windows_build_script)
    
    try:
        # 构建 Docker 镜像
        print("正在构建 Docker 镜像...")
        subprocess.run([
            "docker", "build", 
            "-f", "Dockerfile.windows",
            "-t", "autocollect-windows-builder",
            "."
        ], check=True)
        
        # 运行容器并复制构建结果
        print("正在运行 Windows 构建...")
        container_name = "autocollect-windows-build"
        
        # 运行容器
        subprocess.run([
            "docker", "run", "--name", container_name,
            "autocollect-windows-builder"
        ], check=True)
        
        # 复制构建结果
        os.makedirs("dist_windows", exist_ok=True)
        subprocess.run([
            "docker", "cp", 
            f"{container_name}:/app/dist/.",
            "dist_windows/"
        ], check=True)
        
        # 清理容器
        subprocess.run(["docker", "rm", container_name], check=False)
        
        print("✅ Windows 版本构建成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Windows Docker 构建失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 未找到 Docker，请先安装 Docker Desktop")
        return False
    finally:
        # 清理临时文件
        for temp_file in ["Dockerfile.windows", "build_windows_docker.py"]:
            if Path(temp_file).exists():
                Path(temp_file).unlink()

def build_windows_with_github_actions():
    """使用 GitHub Actions 构建 Windows 版本"""
    print("🚀 配置 GitHub Actions 自动构建...")
    
    # 创建 GitHub Actions 工作流
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_content = '''name: Build AutoCollect Cross-Platform

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build-windows:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
        
    - name: Build Windows executable
      run: |
        python build.py
        
    - name: Upload Windows artifact
      uses: actions/upload-artifact@v4
      with:
        name: AutoCollect-Windows
        path: dist/AutoCollect/
        
  build-macos:
    runs-on: macos-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
        
    - name: Build macOS executable
      run: |
        python build.py
        
    - name: Upload macOS artifact
      uses: actions/upload-artifact@v4
      with:
        name: AutoCollect-macOS
        path: |
          dist/AutoCollect/
          dist/AutoCollect.app/
'''
    
    workflow_file = workflow_dir / "build.yml"
    workflow_file.write_text(workflow_content)
    
    print("✅ GitHub Actions 工作流已创建")
    print("📝 请将代码推送到 GitHub，Actions 将自动构建两个平台版本")
    print(f"📁 工作流文件: {workflow_file.absolute()}")
    
    return True

def create_release_package():
    """创建发布包"""
    print("📦 创建发布包...")
    
    project_info = get_project_info()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 创建发布目录
    release_dir = Path(f"release_{timestamp}")
    release_dir.mkdir(exist_ok=True)
    
    # 复制 macOS 版本
    macos_dist = Path("dist")
    if macos_dist.exists():
        macos_release = release_dir / "macOS"
        macos_release.mkdir(exist_ok=True)
        
        # 复制可执行文件
        if (macos_dist / "AutoCollect").exists():
            shutil.copytree(macos_dist / "AutoCollect", macos_release / "AutoCollect")
        
        # 复制 .app 包
        if (macos_dist / "AutoCollect.app").exists():
            shutil.copytree(macos_dist / "AutoCollect.app", macos_release / "AutoCollect.app")
            
        print("✅ macOS 版本已复制到发布包")
    
    # 复制 Windows 版本（如果存在）
    windows_dist = Path("dist_windows")
    if windows_dist.exists():
        windows_release = release_dir / "Windows"
        windows_release.mkdir(exist_ok=True)
        shutil.copytree(windows_dist, windows_release / "AutoCollect")
        print("✅ Windows 版本已复制到发布包")
    
    # 创建说明文件
    readme_content = f'''# {project_info["name"]} v{project_info["version"]}

{project_info["description"]}

## 系统要求

### macOS
- macOS 10.14 或更高版本
- 支持 Intel 和 Apple Silicon 处理器

### Windows  
- Windows 10 或更高版本
- 64 位系统

## 安装方法

### macOS
1. 方法一：双击 `AutoCollect.app` 
2. 方法二：在终端中运行 `./macOS/AutoCollect/AutoCollect`

### Windows
1. 解压后双击 `Windows/AutoCollect/AutoCollect.exe`

## 功能特性

- ✅ X/Twitter 数据抓取
- ✅ Telegram 链接提取  
- ✅ 数据库管理
- ✅ 跨平台支持
- ✅ 图形界面操作

## 技术支持

如有问题请联系开发团队。

---
构建时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
'''
    
    (release_dir / "README.md").write_text(readme_content, encoding='utf-8')
    
    # 创建版本信息文件
    version_info = {
        "name": project_info["name"],
        "version": project_info["version"], 
        "build_time": datetime.now().isoformat(),
        "platforms": [],
        "files": {}
    }
    
    if macos_dist.exists():
        version_info["platforms"].append("macOS")
        version_info["files"]["macos"] = "macOS/AutoCollect/"
        version_info["files"]["macos_app"] = "macOS/AutoCollect.app/"
        
    if windows_dist.exists():
        version_info["platforms"].append("Windows")
        version_info["files"]["windows"] = "Windows/AutoCollect/"
    
    (release_dir / "version.json").write_text(json.dumps(version_info, indent=2, ensure_ascii=False))
    
    print(f"✅ 发布包已创建: {release_dir.absolute()}")
    return release_dir

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 AutoCollect 跨平台构建工具")
    print("=" * 60)
    
    current_os = platform.system()
    print(f"当前系统: {current_os}")
    
    # 构建选项
    build_options = {
        "1": "仅构建当前平台",
        "2": "使用 Docker 构建 Windows 版本（需要 Docker）", 
        "3": "配置 GitHub Actions 自动构建",
        "4": "构建当前平台 + 配置 GitHub Actions"
    }
    
    print("\n构建选项:")
    for key, value in build_options.items():
        print(f"  {key}. {value}")
    
    choice = input("\n请选择构建选项 (1-4): ").strip()
    
    success = False
    
    if choice == "1":
        success = build_current_platform()
        
    elif choice == "2":
        # 先构建当前平台
        if build_current_platform():
            success = build_windows_with_docker()
        
    elif choice == "3":
        success = build_windows_with_github_actions()
        
    elif choice == "4":
        # 构建当前平台并配置 GitHub Actions
        platform_success = build_current_platform()
        github_success = build_windows_with_github_actions()
        success = platform_success and github_success
        
    else:
        print("❌ 无效选项")
        return 1
    
    if success and choice in ["1", "2", "4"]:
        # 创建发布包
        release_dir = create_release_package()
        
        print("\n" + "=" * 60)
        print("🎉 构建完成！")
        print("=" * 60)
        print(f"📁 发布包位置: {release_dir.absolute()}")
        
        if choice == "2":
            print("📋 包含平台: macOS, Windows")
        else:
            print(f"📋 包含平台: {current_os}")
            if choice == "4":
                print("📝 GitHub Actions 已配置，推送代码后可获得 Windows 版本")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())