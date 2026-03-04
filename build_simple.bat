@echo off
chcp 65001 >nul
echo ========================================
echo 照片GPS信息写入工具 - 简化打包脚本
echo ========================================
echo.

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)
echo Python环境检查通过
echo.

echo [2/4] 安装依赖包...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖包安装失败
    pause
    exit /b 1
)
echo 依赖包安装完成
echo.

echo [3/4] 开始打包（非单文件模式）...
python -m PyInstaller --windowed --name "PhotoGPSWriter" --add-data "gps_parser.py;." --add-data "exif_handler.py;." --add-data "gps_matcher.py;." --add-data "photo_gps_app.py;." main.py
if errorlevel 1 (
    echo 错误: 打包失败
    pause
    exit /b 1
)
echo.

echo [4/4] 打包完成!
echo ========================================
echo 程序位于: dist\PhotoGPSWriter\
echo 运行: dist\PhotoGPSWriter\PhotoGPSWriter.exe
echo ========================================
echo.
pause
