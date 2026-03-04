@echo off
chcp 65001 >nul
echo 正在启动照片GPS信息写入工具...
python main.py
if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查是否已安装所有依赖包
    echo 运行命令: pip install -r requirements.txt
    pause
)
