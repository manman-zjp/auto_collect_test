# AutoCollect 打包指南

AutoCollect 是一个 X/Telegram 数据采集工具，现已支持打包成可在 Mac 和 Windows 运行的独立可执行程序。

## 📦 打包特性

- ✅ 支持 Mac 和 Windows 平台
- ✅ 独立可执行文件，无需用户安装 Python
- ✅ 所有依赖已打包，即开即用
- ✅ 自动创建 macOS .app 应用包
- ✅ 优化的文件大小（约 313MB）

## 🛠️ 构建要求

### 系统要求
- Python 3.9 或更高版本
- pip 包管理器
- 足够的磁盘空间（至少 1GB）

### 依赖包
所有依赖已在 `requirements.txt` 中定义：
- PyQt6 >= 6.7.0 (GUI框架)
- requests >= 2.32.0 (HTTP请求)
- beautifulsoup4 >= 4.12.0 (HTML解析)
- tqdm >= 4.66.0 (进度条)
- playwright >= 1.49.0 (网页自动化)
- tweepy >= 4.14.0 (Twitter API)
- selenium >= 4.0.0 (网页自动化)
- pyinstaller >= 6.0.0 (打包工具)

## 🚀 快速开始

### 方法一：使用自动化构建脚本
```bash
# 运行跨平台构建脚本
python3 cross_platform_build.py

# 选择选项 5（全部执行）
```

### 方法二：手动构建
```bash
# 1. 安装依赖
pip3 install -r requirements.txt

# 2. 运行构建脚本
python3 build.py
```

### 方法三：使用 PyInstaller spec 文件
```bash
# 直接使用配置文件构建
pyinstaller AutoCollect.spec --clean --noconfirm
```

## 📁 构建结果

构建完成后，你会在 `dist/` 目录中找到：

### macOS 系统
```
dist/
├── AutoCollect/              # 可执行文件目录
│   ├── AutoCollect          # 主可执行文件
│   └── _internal/           # 依赖库和资源
└── AutoCollect.app/         # macOS 应用包
    ├── Contents/
    │   ├── Info.plist
    │   ├── MacOS/
    │   └── Resources/
```

### Windows 系统
```
dist/
└── AutoCollect/
    ├── AutoCollect.exe      # 主可执行文件
    └── _internal/           # 依赖库和资源
```

## 🎯 运行应用

### macOS
```bash
# 方法1：直接运行可执行文件
./dist/AutoCollect/AutoCollect

# 方法2：双击 AutoCollect.app
open dist/AutoCollect.app
```

### Windows
```cmd
# 直接运行
dist\AutoCollect\AutoCollect.exe

# 或双击 AutoCollect.exe
```

## 📋 构建选项说明

### PyInstaller 参数
- `--windowed`: 创建 GUI 应用（不显示控制台窗口）
- `--onedir`: 创建目录分发（推荐，便于调试）
- `--clean`: 清理临时文件
- `--noconfirm`: 自动覆盖输出目录

### 隐藏导入
已配置以下关键模块的隐藏导入：
- PyQt6 相关模块
- auto_collect 所有子模块
- 网络请求和解析库
- 数据库和文件操作库

## 🐛 常见问题

### 1. 构建失败：缺少依赖
```bash
# 解决方案：重新安装依赖
pip3 install --upgrade -r requirements.txt
```

### 2. macOS 应用无法打开
```bash
# 解决方案：移除隔离属性
xattr -cr dist/AutoCollect.app
```

### 3. Windows 杀毒软件误报
构建的可执行文件可能被杀毒软件误认为是病毒，这是正常现象。可以：
- 添加到杀毒软件白名单
- 使用 `--onefile` 参数重新打包

### 4. 应用启动缓慢
首次启动可能较慢（特别是 Playwright 初始化），这是正常现象。

## 🔧 高级配置

### 自定义 spec 文件
编辑 `AutoCollect.spec` 文件可以进行高级配置：
- 修改应用名称和版本
- 添加图标文件
- 调整数据文件包含规则
- 配置代码签名（macOS）

### 减小文件大小
```python
# 在 spec 文件中添加排除模块
excludes = [
    'tkinter',
    'matplotlib', 
    'numpy',
    'pandas'
]
```

### 添加图标
```python
# 在 EXE 配置中添加
icon='path/to/icon.ico'  # Windows
icon='path/to/icon.icns' # macOS
```

## 📦 分发建议

### macOS
1. 创建 DMG 安装包：
```bash
# 安装 create-dmg
brew install create-dmg

# 创建 DMG
create-dmg --volname "AutoCollect" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --app-drop-link 350 185 \
  AutoCollect.dmg dist/AutoCollect.app
```

2. 代码签名（可选）：
```bash
# 需要 Apple Developer 账户
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  dist/AutoCollect.app
```

### Windows
1. 创建安装程序（使用 Inno Setup 或 NSIS）
2. 数字签名（可选，需要代码签名证书）

## 📝 开发说明

### 项目结构优化
- 清理了临时文件和无用代码
- 优化了导入路径和依赖关系
- 增强了错误处理和日志记录
- 改进了跨平台兼容性

### 构建脚本
- `build.py`: 基础构建脚本
- `cross_platform_build.py`: 跨平台自动化构建
- `AutoCollect.spec`: PyInstaller 配置文件

## 🎉 完成

恭喜！你现在已经成功将 AutoCollect 打包成了独立的可执行程序。用户无需安装 Python 或任何依赖即可直接运行应用。

如有问题，请检查构建日志或参考上述常见问题解决方案。