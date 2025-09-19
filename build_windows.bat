@echo off
echo ====================================================
echo AutoCollect Windows 构建脚本
echo ====================================================

REM 检查 Python 是否已安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Python，请先安装 Python 3.9 或更高版本
    pause
    exit /b 1
)

echo 正在安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 依赖安装失败，请检查网络连接和权限
    pause
    exit /b 1
)

echo.
echo 开始构建应用...
python build.py
if errorlevel 1 (
    echo 构建失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo ====================================================
echo 构建完成！
echo 可执行文件位于: dist\AutoCollect\AutoCollect.exe
echo ====================================================
pause