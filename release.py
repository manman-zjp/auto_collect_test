#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoCollect 一键发布脚本
自动处理版本标签、Git 操作和发布流程
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

def run_command(cmd, description=""):
    """运行命令并处理错误"""
    print(f"🔄 {description}..." if description else f"🔄 运行: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout.strip():
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 错误: {e}")
        if e.stderr:
            print(f"详细错误: {e.stderr}")
        return False

def get_current_version():
    """获取当前版本"""
    try:
        result = subprocess.run(["git", "tag", "--sort=-version:refname"], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0]
        return "v0.0.0"
    except:
        return "v0.0.0"

def increment_version(version, increment_type="patch"):
    """递增版本号"""
    # 移除 'v' 前缀
    if version.startswith('v'):
        version = version[1:]
    
    parts = version.split('.')
    if len(parts) != 3:
        parts = ['1', '0', '0']
    
    major, minor, patch = map(int, parts)
    
    if increment_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif increment_type == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    return f"v{major}.{minor}.{patch}"

def check_git_status():
    """检查 Git 状态"""
    print("🔍 检查 Git 状态...")
    
    # 检查是否有未提交的更改
    result = subprocess.run(["git", "status", "--porcelain"], 
                          capture_output=True, text=True)
    if result.stdout.strip():
        print("⚠️ 检测到未提交的更改:")
        print(result.stdout)
        return False
    
    # 检查是否有远程仓库
    result = subprocess.run(["git", "remote", "-v"], 
                          capture_output=True, text=True)
    if not result.stdout.strip():
        print("❌ 未配置远程仓库")
        print("请先添加远程仓库: git remote add origin <仓库地址>")
        return False
    
    print("✅ Git 状态正常")
    return True

def create_changelog():
    """创建更新日志"""
    changelog_file = Path("CHANGELOG.md")
    
    if not changelog_file.exists():
        changelog_content = """# AutoCollect 更新日志

## [Unreleased]
### 新增
- 跨平台构建支持 (Windows & macOS)
- GitHub Actions 自动构建
- 数据库管理界面优化
- 线程管理改进

### 修复
- 修复应用启动问题
- 修复 .app 包启动问题
- 改进错误处理

### 改进
- 优化用户界面
- 提升构建稳定性
- 完善文档

---

## 版本格式说明
- **新增**: 新功能
- **修复**: Bug 修复
- **改进**: 现有功能优化
- **删除**: 移除的功能
"""
        changelog_file.write_text(changelog_content, encoding='utf-8')
        print(f"✅ 创建了更新日志: {changelog_file}")
    
    return changelog_file

def update_version_file(version):
    """更新版本文件"""
    version_info = {
        "version": version,
        "build_date": datetime.now().isoformat(),
        "platforms": ["macOS", "Windows"],
        "build_system": "GitHub Actions"
    }
    
    version_file = Path("version.json")
    version_file.write_text(json.dumps(version_info, indent=2, ensure_ascii=False))
    print(f"✅ 更新版本文件: {version}")

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 AutoCollect 一键发布工具")
    print("=" * 60)
    
    # 检查 Git 状态
    if not check_git_status():
        return 1
    
    # 获取当前版本
    current_version = get_current_version()
    print(f"📋 当前版本: {current_version}")
    
    # 选择版本递增类型
    print("\n请选择版本递增类型:")
    print("1. Patch (修复版本) - 例: v1.0.0 → v1.0.1")
    print("2. Minor (功能版本) - 例: v1.0.0 → v1.1.0") 
    print("3. Major (主要版本) - 例: v1.0.0 → v2.0.0")
    print("4. 自定义版本")
    
    choice = input("请选择 (1-4): ").strip()
    
    if choice == "1":
        new_version = increment_version(current_version, "patch")
    elif choice == "2":
        new_version = increment_version(current_version, "minor")
    elif choice == "3":
        new_version = increment_version(current_version, "major")
    elif choice == "4":
        new_version = input("请输入新版本 (格式: v1.0.0): ").strip()
        if not new_version.startswith('v'):
            new_version = 'v' + new_version
    else:
        print("❌ 无效选择")
        return 1
    
    print(f"🎯 新版本: {new_version}")
    
    # 确认发布
    confirm = input(f"\n确认发布版本 {new_version}? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 发布已取消")
        return 0
    
    print(f"\n🚀 开始发布 {new_version}...")
    
    # 创建/更新文件
    create_changelog()
    update_version_file(new_version)
    
    # Git 操作
    steps = [
        (["git", "add", "."], "添加所有更改到暂存区"),
        (["git", "commit", "-m", f"发布版本 {new_version}"], "提交更改"),
        (["git", "tag", new_version], "创建版本标签"),
        (["git", "push"], "推送提交到远程仓库"),
        (["git", "push", "origin", new_version], "推送标签到远程仓库")
    ]
    
    for cmd, desc in steps:
        if not run_command(cmd, desc):
            print(f"❌ 发布失败在步骤: {desc}")
            return 1
    
    print("\n" + "=" * 60)
    print("🎉 发布成功!")
    print("=" * 60)
    print(f"📦 版本: {new_version}")
    print("🔗 GitHub Actions 将自动构建以下版本:")
    print("   • Windows 可执行程序")
    print("   • macOS 应用程序")
    print("   • 跨平台发布包")
    
    print(f"\n📋 后续步骤:")
    print("1. 访问 GitHub 仓库查看构建状态")
    print("2. 在 Actions 页面监控构建进度")
    print("3. 构建完成后在 Releases 页面下载产物")
    print("4. 测试下载的应用程序")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())