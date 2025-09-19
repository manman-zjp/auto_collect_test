# 🚀 GitHub Actions 自动构建指南

## ✅ 配置完成

恭喜！我已经为您配置了完整的 GitHub Actions 自动构建系统，现在您可以：

- 🔄 **自动构建** - 每次推送代码自动构建 Windows 和 macOS 版本
- 📦 **自动打包** - 自动创建包含两个平台的发布包
- 🏷️ **版本发布** - 推送标签自动创建 GitHub Release

## 📁 已创建的文件

```
.github/
└── workflows/
    ├── build.yml      # 主构建工作流
    └── release.yml    # 发布工作流
```

## 🎯 使用方法

### 1. 推送代码到 GitHub

```bash
# 如果还没有 Git 仓库，先初始化
git init
git add .
git commit -m "添加跨平台构建支持"

# 推送到 GitHub (替换为您的仓库地址)
git remote add origin https://github.com/你的用户名/AutoCollect.git
git push -u origin main
```

### 2. 查看构建状态

推送后，访问您的 GitHub 仓库：
- 点击 **Actions** 标签页
- 查看 **Build AutoCollect Cross-Platform** 工作流
- 等待构建完成（约 5-10 分钟）

### 3. 下载构建产物

构建完成后：
- 点击具体的构建任务
- 在 **Artifacts** 部分下载：
  - `AutoCollect-Windows-xxx` - Windows 版本
  - `AutoCollect-macOS-xxx` - macOS 版本
  - `AutoCollect-Release-xxx` - 跨平台发布包

### 4. 创建正式发布 (可选)

```bash
# 创建版本标签
git tag v1.0.0
git push origin v1.0.0
```

这将触发发布工作流，自动在 GitHub Releases 页面创建正式发布。

## 🔧 工作流详解

### 主构建工作流 (build.yml)

**触发条件：**
- 推送到 main/master 分支
- 创建 Pull Request
- 手动触发

**构建内容：**
1. **Windows 构建**
   - 在 Windows Server 环境构建
   - 生成 `AutoCollect.exe`
   - 包含所有依赖

2. **macOS 构建**
   - 在 macOS 环境构建
   - 生成可执行文件和 `.app` 包
   - 支持 Intel 和 Apple Silicon

3. **发布包创建**
   - 合并两个平台版本
   - 创建统一的发布包
   - 包含使用说明

### 发布工作流 (release.yml)

**触发条件：**
- 推送版本标签 (如 v1.0.0)

**功能：**
- 自动构建两个平台版本
- 创建 GitHub Release
- 上传构建产物
- 生成发布说明

## 📋 构建产物结构

### Windows 版本
```
AutoCollect-Windows-xxx.zip
└── AutoCollect/
    ├── AutoCollect.exe      # 主程序
    ├── _internal/           # 依赖库
    └── 其他文件...
```

### macOS 版本
```
AutoCollect-macOS-xxx.zip
├── AutoCollect/
│   ├── AutoCollect          # 命令行版本
│   └── _internal/
└── AutoCollect.app/         # 应用包版本
    └── Contents/
        ├── MacOS/
        ├── Resources/
        └── Info.plist
```

### 跨平台发布包
```
AutoCollect-Release-xxx.zip
├── README.md               # 使用说明
├── Windows/
│   └── AutoCollect/
└── macOS/
    ├── AutoCollect/
    └── AutoCollect.app/
```

## 🚨 常见问题

### 1. 构建失败
- 检查 `requirements.txt` 是否包含所有依赖
- 确保 `entry_point.py` 文件存在
- 查看 Actions 日志获取详细错误

### 2. 找不到构建产物
- 等待构建完全完成（绿色对勾）
- 在 Actions 页面点击具体的构建任务
- 滚动到底部查看 Artifacts 部分

### 3. 下载的文件无法运行
- Windows：添加到杀毒软件白名单
- macOS：运行 `xattr -cr AutoCollect.app`

## 🎉 优势

✅ **零配置** - 推送代码自动构建  
✅ **跨平台** - 同时支持 Windows 和 macOS  
✅ **专业级** - 企业级 CI/CD 流程  
✅ **版本管理** - 自动化版本发布  
✅ **免费使用** - GitHub Actions 免费额度充足  

## 🔄 后续操作

1. **推送代码到 GitHub** - 触发首次构建
2. **测试下载的程序** - 确保功能正常
3. **创建第一个发布版本** - 使用标签触发正式发布
4. **分享给用户** - 提供下载链接

现在您的 AutoCollect 项目已经具备了专业级的跨平台自动构建能力！🚀