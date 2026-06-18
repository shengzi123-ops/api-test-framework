@echo off
chcp 65001 >nul
title API自动化测试一键启动器

echo ===============================================
echo          API 自动化测试一键启动器 v1.0
echo ===============================================
echo.

:: 检查Python环境
echo 📦 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到Python环境，请先安装Python
    pause
    exit /b 1
)

:: 激活虚拟环境（如果存在）
if exist "venv\Scripts\activate.bat" (
    echo 📦 激活虚拟环境...
    call venv\Scripts\activate.bat
)

:: 调用Python主脚本
echo 🚀 启动测试主程序...
python run_tests.py

:: 等待用户查看结果
echo.
echo ===============================================
echo              测试完成！按任意键退出
echo ===============================================
pause >nul