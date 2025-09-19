# -*- mode: python ; coding: utf-8 -*-
"""
AutoCollect PyInstaller 配置文件
支持 Mac 和 Windows 平台打包
"""

import os
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path.cwd()
auto_collect_path = project_root / "auto_collect"

# 数据文件和资源文件
datas = [
    # 添加存储状态文件
    (str(auto_collect_path / "storage_state.json"), "auto_collect") if (auto_collect_path / "storage_state.json").exists() else None,
    # 添加crawler模块的所有文件
    (str(auto_collect_path / "crawler"), "auto_collect/crawler"),
    # 添加ui模块的所有文件
    (str(auto_collect_path / "ui"), "auto_collect/ui"),
]
# 过滤掉None值
datas = [d for d in datas if d is not None]

# 隐藏导入
hiddenimports = [
    'PyQt6.sip',
    'PyQt6.QtCore',
    'PyQt6.QtWidgets', 
    'PyQt6.QtGui',
    'requests',
    'beautifulsoup4',
    'bs4',
    'tqdm',
    'tweepy',
    'selenium',
    'playwright',
    'sqlite3',
    'json',
    'subprocess',
    'pathlib',
    'auto_collect',
    'auto_collect.main',
    'auto_collect.ui',
    'auto_collect.ui.main_window',
    'auto_collect.crawler',
    'auto_collect.crawler.manager',
    'auto_collect.crawler.storage',
    'auto_collect.crawler.DatabaseManager',
    'auto_collect.crawler.TwitterAPIClient',
    'auto_collect.crawler.layer1_requests',
    'auto_collect.crawler.layer2_playwright',
    'auto_collect.crawler.layer3_selenium',
]

# 需要排除的模块
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'IPython',
    'jupyter',
]

# 分析选项
a = Analysis(
    ['entry_point.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 去除重复文件
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 创建可执行文件
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
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 暂时不使用图标
)

# 收集所有文件
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoCollect'
)