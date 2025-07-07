@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
setlocal
cd /d %~dp0

echo 正在检查依赖项...
pip list > temp_installed_packages.txt
findstr /C:"Flask" temp_installed_packages.txt > nul
if %errorlevel% neq 0 (
    echo 依赖项未安装，正在安装...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 依赖项安装失败，请检查网络连接或手动安装依赖项。
        del temp_installed_packages.txt
        pause
        exit /b 1
    ) else (
        echo 依赖项安装成功！
    )
) else (
    echo 依赖项已安装！
)
del temp_installed_packages.txt

echo 正在启动程序...
python audio_processor_gui.py
pause