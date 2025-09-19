#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的Windows构建脚本
在macOS上使用不同方法构建Windows版本
"""

import sys
import os
import platform
import subprocess
import shutil
from pathlib import Path
import tempfile

def check_wine():
    """检查Wine是否已安装"""
    try:
        result = subprocess.run(["wine", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Wine 已安装: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Wine 未安装")
    print("💡 安装方法:")
    print("   1. 安装 Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
    print("   2. 安装 Wine: brew install --cask wine-stable")
    return False

def build_windows_spec():
    """创建专门的Windows构建spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['entry_point.py'],
    pathex=[],
    binaries=[],
    datas=[('auto_collect', 'auto_collect')],
    hiddenimports=[
        'PyQt6.sip',
        'auto_collect.ui.main_window',
        'auto_collect.crawler.manager',
        'auto_collect.crawler.layer3_selenium',
        'auto_collect.crawler.layer4_twitter_api',
        'requests',
        'beautifulsoup4',
        'tqdm',
        'tweepy',
        'selenium',
        'playwright'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AutoCollect',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoCollect',
)
'''
    
    spec_file = Path("AutoCollect_Windows.spec")
    spec_file.write_text(spec_content)
    return spec_file

def build_windows_with_wine():
    """使用Wine构建Windows版本"""
    print("🍷 使用 Wine 构建 Windows 版本...")
    
    if not check_wine():
        return False
    
    spec_file = None  # 初始化变量
    try:
        # 设置Wine环境
        wine_env = os.environ.copy()
        wine_env['WINEARCH'] = 'win64'
        wine_env['WINEPREFIX'] = os.path.expanduser('~/.wine_autocollect')
        
        # 初始化Wine环境
        print("初始化 Wine 环境...")
        subprocess.run(['winecfg'], env=wine_env, check=False)
        
        # 在Wine环境中安装Python和依赖
        print("正在Wine环境中设置Python...")
        
        # 创建Windows构建spec文件
        spec_file = build_windows_spec()
        
        # 使用Wine运行PyInstaller
        cmd = [
            'wine', 'python', '-m', 'PyInstaller',
            str(spec_file),
            '--clean',
            '--noconfirm',
            '--distpath', 'dist_windows'
        ]
        
        print("正在使用Wine构建Windows版本...")
        result = subprocess.run(cmd, env=wine_env, check=True)
        
        print("✅ Windows版本构建成功!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Wine构建失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 构建过程出错: {e}")
        return False
    finally:
        # 清理临时文件
        if spec_file is not None and spec_file.exists():
            spec_file.unlink()

def create_windows_cross_compile():
    """创建交叉编译脚本"""
    print("📝 创建 Windows 交叉编译脚本...")
    
    # 创建虚拟机脚本
    vm_script = '''#!/bin/bash
# Windows 虚拟机构建脚本

echo "=== AutoCollect Windows 构建 ==="

# 检查是否在Windows环境
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" ]]; then
    echo "此脚本需要在Windows环境中运行"
    echo "请使用以下方法之一:"
    echo "1. 在Windows虚拟机中运行"
    echo "2. 使用Windows Subsystem for Linux (WSL)"
    echo "3. 在Windows物理机上运行"
    exit 1
fi

# 检查Python
python --version || {
    echo "请先安装Python 3.9+"
    exit 1
}

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt
pip install pyinstaller

# 构建
echo "开始构建..."
python build.py

echo "构建完成!"
echo "可执行文件位于: dist/AutoCollect/AutoCollect.exe"
'''
    
    Path("build_windows_vm.sh").write_text(vm_script)
    os.chmod("build_windows_vm.sh", 0o755)
    
    # 创建说明文档
    readme = '''# Windows 版本构建说明

由于您当前在 macOS 环境中，有以下几种方法构建 Windows 版本：

## 方法一：使用 GitHub Actions (推荐)
1. 运行 `python cross_platform_build.py`
2. 选择选项 3 或 4
3. 将代码推送到 GitHub
4. GitHub Actions 将自动构建 Windows 版本

## 方法二：使用 Wine (需要安装)
1. 安装 Wine: `brew install --cask wine-stable`
2. 运行此脚本: `python build_windows_simple.py`

## 方法三：使用 Windows 虚拟机/物理机
1. 在 Windows 环境中运行 `build_windows_vm.sh`
2. 或者运行 `python build.py`

## 方法四：使用 Docker (需要 Windows 容器支持)
1. 安装 Docker Desktop
2. 运行 `python cross_platform_build.py`
3. 选择选项 2

推荐使用方法一，最简单且不需要额外软件。
'''
    
    Path("WINDOWS_BUILD_README.md").write_text(readme)
    
    print("✅ 脚本已创建:")
    print("  - build_windows_vm.sh (Windows环境使用)")
    print("  - WINDOWS_BUILD_README.md (详细说明)")

def main():
    """主函数"""
    print("🔨 Windows 构建向导")
    print("=" * 40)
    
    current_os = platform.system()
    if current_os != "Darwin":
        print("此脚本设计为在 macOS 上运行")
        return 1
    
    options = {
        "1": "尝试使用 Wine 构建 (需要安装 Wine)",
        "2": "创建 Windows 构建脚本和说明",
        "3": "运行完整的跨平台构建工具"
    }
    
    print("请选择构建方式:")
    for key, value in options.items():
        print(f"  {key}. {value}")
    
    choice = input("\n选择 (1-3): ").strip()
    
    if choice == "1":
        return 0 if build_windows_with_wine() else 1
        
    elif choice == "2":
        create_windows_cross_compile()
        print("\n✅ 已创建 Windows 构建脚本")
        print("📋 查看 WINDOWS_BUILD_README.md 了解详细使用方法")
        return 0
        
    elif choice == "3":
        # 运行跨平台构建工具
        try:
            os.system("python cross_platform_build.py")
            return 0
        except Exception as e:
            print(f"❌ 运行跨平台构建工具失败: {e}")
            return 1
    else:
        print("❌ 无效选择")
        return 1

if __name__ == "__main__":
    sys.exit(main())