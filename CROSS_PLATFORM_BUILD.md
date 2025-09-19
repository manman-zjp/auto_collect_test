# AutoCollect 跨平台构建指南

## 🎯 概述

AutoCollect 现在支持同时生成 macOS 和 Windows 运行程序，提供多种构建方案满足不同需求。

## 🚀 快速开始

### 方法一：使用跨平台构建工具（推荐）

```bash
python cross_platform_build.py
```

#### 构建选项说明：

1. **仅构建当前平台** - 快速构建当前系统版本
2. **使用 Docker 构建 Windows 版本** - 在 macOS 上本地构建 Windows 版本（需要 Docker）
3. **配置 GitHub Actions 自动构建** - 设置云端自动构建（最推荐）
4. **构建当前平台 + 配置 GitHub Actions** - 本地构建 + 云端构建

### 方法二：使用传统构建脚本

```bash
# 仅构建当前平台
python build.py

# 启用跨平台模式
python build.py --cross-platform
```

### 方法三：使用简化 Windows 构建

```bash
python build_windows_simple.py
```

## 📋 构建方案详解

### 🌟 GitHub Actions 自动构建（推荐）

**优点：**
- ✅ 最简单，无需本地安装额外软件
- ✅ 自动构建两个平台版本
- ✅ 云端构建，不占用本地资源
- ✅ 构建结果可下载保存

**使用步骤：**
1. 运行 `python cross_platform_build.py`
2. 选择选项 3 或 4
3. 将代码推送到 GitHub 仓库
4. GitHub Actions 自动构建并提供下载

**构建产物：**
- `AutoCollect-macOS.zip` - macOS 版本
- `AutoCollect-Windows.zip` - Windows 版本

### 🐳 Docker 本地构建

**优点：**
- ✅ 本地即时构建
- ✅ 完全控制构建过程
- ✅ 可离线使用

**前提条件：**
- 安装 Docker Desktop

**使用步骤：**
1. 安装 Docker Desktop
2. 运行 `python cross_platform_build.py`
3. 选择选项 2
4. 等待构建完成

### 🍷 Wine 模拟构建

**优点：**
- ✅ 轻量级解决方案
- ✅ 不需要虚拟机

**前提条件：**
```bash
# 安装 Wine
brew install --cask wine-stable
```

**使用步骤：**
1. 运行 `python build_windows_simple.py`
2. 选择选项 1
3. 配置 Wine 环境（首次使用）

### 💻 虚拟机/物理机构建

**适用场景：**
- 有 Windows 环境可用
- 需要在真实 Windows 环境测试

**使用步骤：**
1. 在 Windows 环境中运行 `build_windows_vm.sh`
2. 或直接运行 `python build.py`

## 📦 构建产物说明

### macOS 版本
```
macOS/
├── AutoCollect/           # 可执行文件目录
│   ├── AutoCollect        # 主程序
│   └── _internal/         # 依赖库
└── AutoCollect.app/       # macOS 应用包
```

### Windows 版本
```
Windows/
└── AutoCollect/
    ├── AutoCollect.exe    # 主程序
    └── _internal/         # 依赖库
```

## 🔧 配置文件

### GitHub Actions 工作流
- 位置：`.github/workflows/build.yml`
- 自动触发：推送到 main/master 分支
- 手动触发：GitHub 网页界面

### PyInstaller 规格文件
- `AutoCollect.spec` - 通用构建配置
- `AutoCollect_Windows.spec` - Windows 专用配置

## 🚨 常见问题

### 1. GitHub Actions 构建失败
**解决方案：**
- 检查 `requirements.txt` 是否完整
- 确保所有必要文件已提交
- 查看 Actions 日志定位具体错误

### 2. Docker 构建失败
**解决方案：**
- 确保 Docker Desktop 正在运行
- 检查磁盘空间是否充足
- 重新安装 Docker Desktop

### 3. Wine 构建问题
**解决方案：**
- 重新初始化 Wine 环境：`rm -rf ~/.wine_autocollect`
- 更新 Wine 版本：`brew upgrade wine-stable`

### 4. 构建的应用无法启动
**解决方案：**
- macOS：运行 `xattr -cr AutoCollect.app` 移除隔离属性
- Windows：添加到杀毒软件白名单

## 📈 推荐构建流程

### 开发阶段
```bash
# 快速本地测试
python build.py
```

### 发布阶段
```bash
# 生成完整发布包
python cross_platform_build.py
# 选择选项 4（本地 + GitHub Actions）
```

### 持续集成
- 设置 GitHub Actions
- 每次推送自动构建
- 发布时下载构建产物

## 🎉 特性优势

- ✅ **一键构建** - 单个命令生成多平台版本
- ✅ **智能选择** - 根据环境自动推荐最佳方案
- ✅ **完整打包** - 包含所有依赖，开箱即用
- ✅ **多种方案** - 适应不同开发环境和需求
- ✅ **自动化** - GitHub Actions 无人值守构建
- ✅ **专业级** - 企业级 CI/CD 流程支持

---

🔗 **快速链接：**
- [GitHub Actions 工作流示例](https://github.com/actions/starter-workflows)
- [Docker Desktop 下载](https://www.docker.com/products/docker-desktop)
- [Wine 安装指南](https://wiki.winehq.org/MacOS)