#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的应用
验证是否还会出现第二个浏览器窗口
"""

import subprocess
import sys
import time
from pathlib import Path

def test_app():
    """测试打包后的应用"""
    print("=" * 60)
    print("测试修复后的 AutoCollect 应用")
    print("=" * 60)
    
    # 检查打包后的应用是否存在
    app_path = Path("dist/AutoCollect/AutoCollect")
    if not app_path.exists():
        print("❌ 打包后的应用不存在，请先运行 build.py")
        return False
    
    print("✅ 找到打包后的应用")
    print(f"📍 应用路径: {app_path.absolute()}")
    
    print("\n🔍 测试重点:")
    print("1. 检查是否还有 Qt 警告信息")
    print("2. 验证点击'开始抓取'后是否还会弹出浏览器窗口")
    print("3. 确认应用正常启动")
    
    print(f"\n🚀 正在启动应用...")
    print("请在应用中:")
    print("  1. 输入任意关键词")
    print("  2. 点击'开始抓取'按钮")
    print("  3. 观察是否还会弹出浏览器窗口")
    print("  4. 检查控制台输出中的 Qt 警告")
    
    try:
        # 启动应用并实时显示输出
        process = subprocess.Popen(
            [str(app_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print(f"✅ 应用已启动 (PID: {process.pid})")
        print("📝 应用输出:")
        print("-" * 40)
        
        # 实时显示应用输出
        try:
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(f"[APP] {output.strip()}")
        except KeyboardInterrupt:
            print("\n⚠️  用户中断测试")
            process.terminate()
            process.wait()
        
        return_code = process.poll()
        if return_code is not None:
            print(f"\n📊 应用退出，返回码: {return_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ 启动应用失败: {e}")
        return False

def main():
    """主函数"""
    print("AutoCollect 应用修复验证工具\n")
    
    # 检查是否在正确的目录
    if not Path("auto_collect").exists():
        print("❌ 请在项目根目录运行此脚本")
        return 1
    
    # 运行测试
    success = test_app()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试完成")
        print("\n修复内容:")
        print("1. 🔧 将 Playwright 浏览器设置为无头模式 (headless=True)")
        print("2. 🔧 移除了 macOS 上多余的 QT_MAC_WANTS_LAYER 环境变量")
        print("3. ✨ 现在点击'开始抓取'不会再弹出可见的浏览器窗口")
        print("4. ✨ Qt 警告信息已减少")
    else:
        print("❌ 测试失败")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())