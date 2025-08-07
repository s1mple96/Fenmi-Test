# -*- coding: utf-8 -*-
"""
ETC申办系统打包脚本 - 优化版本
专门打包 apps/etc_apply/main_window.py
"""
import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

def create_spec_file():
    """创建优化的spec文件"""
    # 获取当前工作目录
    current_dir = os.getcwd()
    project_root = current_dir
    
    # 检查配置文件路径
    config_file = os.path.join(project_root, 'apps', 'etc_apply', 'config', 'etc_config.json')
    if not os.path.exists(config_file):
        print(f"❌ 错误：配置文件不存在 {config_file}")
        return False
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(SPEC))
project_root = r"{project_root.replace(chr(92), chr(47))}"  # 转换为正斜杠
sys.path.insert(0, project_root)

# 获取项目根目录
project_root = Path(project_root)

# 定义需要包含的数据文件 - 包含所有必要的配置文件
datas = [
    # ETC申办配置文件
    (r"{config_file.replace(chr(92), chr(47))}", 'apps/etc_apply/config'),
    # 全局配置文件
    (r"{os.path.join(project_root, 'config', 'app_config.json').replace(chr(92), chr(47))}", 'config'),
]

# 定义需要隐藏的模块（减少大小）
hiddenimports = [
    'PyQt5.QtCore',
    'PyQt5.QtWidgets', 
    'PyQt5.QtGui',
    # ETC申办UI模块
    'apps.etc_apply.ui.rtx.ui_events',
    'apps.etc_apply.ui.rtx.ui_utils',
    'apps.etc_apply.ui.rtx.ui_core',
    'apps.etc_apply.ui.rtx.ui_styles',
    'apps.etc_apply.ui.rtx.ui_component',
    'apps.etc_apply.ui.rtx.verify_dialog',
    'apps.etc_apply.ui.rtx.selection_dialogs',
    'apps.etc_apply.ui.rtx.draggable_components',
    'apps.etc_apply.ui.hcb.truck_tab_widget',
    # ETC申办服务模块 - RTX
    'apps.etc_apply.services.rtx.core_service',
    'apps.etc_apply.services.rtx.data_service',
    'apps.etc_apply.services.rtx.etc_service',
    'apps.etc_apply.services.rtx.etc_core',
    'apps.etc_apply.services.rtx.log_service',
    'apps.etc_apply.services.rtx.state_service',
    'apps.etc_apply.services.rtx.worker_thread',
    'apps.etc_apply.services.rtx.api_client',
    # ETC申办服务模块 - HCB
    'apps.etc_apply.services.hcb.truck_service',
    'apps.etc_apply.services.hcb.truck_data_service',
    'apps.etc_apply.services.hcb.truck_core_service',
    'apps.etc_apply.services.hcb.truck_state_service',
    'apps.etc_apply.services.hcb.truck_api_client',
    'apps.etc_apply.services.hcb.truck_core',
    'apps.etc_apply.services.hcb.check_vehicle_bind',
    'apps.etc_apply.services.hcb.direct_db_bind',
    'apps.etc_apply.services.hcb.manual_vehicle_bind',
    # 通用工具模块
    'common.config_util',
    'common.log_util',
    'common.mysql_util',
    'common.requestsUtil',
    'common.path_util',
    'common.plate_util',
    'common.vin_util',
    'common.vin_recent_spider',
    # requests相关模块（必需）
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    'chardet',
    # 数据库相关模块（必需）
    'pymysql',
    'pymysql.cursors',
    'pymysql.constants',
    'pymysql.protocol',
    'pymysql.charset',
    'pymysql.converters',
    'pymysql.err',
    'pymysql.util',
]

# 定义需要排除的模块（减少大小）
excludes = [
    # 科学计算和数据分析
    'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'cv2',
    'tensorflow', 'torch', 'sklearn', 'jupyter', 'IPython',
    'ipykernel', 'zmq', 'tornado', 'bokeh', 'plotly', 'seaborn',
    'statsmodels', 'sympy', 'networkx', 'nltk', 'spacy', 'gensim',
    'wordcloud', 'pygame', 'pyglet', 'pycairo', 'pycups', 'pycurl',
    'pydot', 'pygments', 'pylint', 'pytest', 'sphinx', 'docutils',
    'jinja2', 'markupsafe', 'werkzeug',
    
    # Web框架
    'flask', 'django', 'fastapi', 'uvicorn', 'gunicorn', 'celery',
    
    # 数据库（保留pymysql）
    'redis', 'pymongo', 'sqlalchemy', 'alembic', 'psycopg2',
    'cx_oracle', 'sqlite3',
    
    # 异步和网络（保留requests相关）
    'asyncio', 'aiohttp', 'websockets', 'twisted', 'gevent', 'eventlet',
    'greenlet', 'uvloop', 'httpx', 'requests_toolbelt',
    
    # 网页抓取
    'lxml', 'beautifulsoup4', 'selenium', 'playwright', 'puppeteer',
    'scrapy', 'pyppeteer', 'requests_html', 'pyquery', 'feedparser',
    'newspaper3k', 'readability', 'trafilatura', 'newspaper',
    'feedfinder', 'feedsearch', 'feedfinder2', 'feedfinder3',
    'feedfinder4', 'feedfinder5', 'feedfinder6', 'feedfinder7',
    'feedfinder8', 'feedfinder9', 'feedfinder10',
    
    # 其他不需要的模块
    'tkinter', 'wx', 'kivy', 'pygame', 'pyglet', 'arcade',
    'pyopengl', 'pyglet', 'panda3d', 'ursina', 'pygame_gui',
    'pygame_menu', 'pygame_widgets', 'pygame_gui_elements',
    
    # 项目中不需要的模块（专注ETC申办）
    'apps.data_generator',
    'apps.go_jenkins',
]

a = Analysis(
    [r"{os.path.join(project_root, 'apps', 'etc_apply', 'main_window.py').replace(chr(92), chr(47))}"],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ETCApplySystem',  # 使用英文名称避免编码问题
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Windows下禁用strip
    upx=True,    # 使用UPX压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件路径
)
'''
    
    with open('etc_apply.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 已创建优化的spec文件")
    return True

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller>=5.0'], 
                      check=True, capture_output=True)
        print("✅ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyInstaller安装失败")
        return False

def build_exe():
    """构建exe文件"""
    print("🔨 开始构建exe文件...")
    print("⏳ 这可能需要几分钟时间，请耐心等待...")
    
    start_time = time.time()
    
    try:
        # 使用优化的spec文件构建，实时显示输出
        process = subprocess.Popen([
            sys.executable, '-m', 'PyInstaller',
            '--clean',  # 清理临时文件
            '--noconfirm',  # 不询问确认
            'etc_apply.spec'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
           universal_newlines=True, bufsize=1, encoding='utf-8')
        
        # 实时显示输出
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # 只显示重要的进度信息
                if any(keyword in output.lower() for keyword in ['info:', 'warning:', 'error:', 'analysis', 'pyz', 'exe']):
                    print(f"📋 {output.strip()}")
        
        # 等待进程完成
        return_code = process.poll()
        
        if return_code == 0:
            elapsed_time = time.time() - start_time
            print(f"✅ exe文件构建成功！耗时: {elapsed_time:.1f} 秒")
            
            # 显示文件大小
            exe_path = 'dist/ETCApplySystem.exe'
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"📊 exe文件大小: {size_mb:.2f} MB")
                
                # 重命名为中文名称
                new_name = 'dist/ETC申办系统.exe'
                if os.path.exists(new_name):
                    os.remove(new_name)
                os.rename(exe_path, new_name)
                print(f"✅ 已重命名为: {new_name}")
            return True
        else:
            print(f"❌ 构建失败，返回码: {return_code}")
            return False
            
    except Exception as e:
        print(f"❌ 构建异常: {e}")
        return False

def cleanup():
    """清理临时文件"""
    print("🧹 清理临时文件...")
    
    # 删除构建目录
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # 删除spec文件
    if os.path.exists('etc_apply.spec'):
        os.remove('etc_apply.spec')
    
    # 删除__pycache__目录
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                shutil.rmtree(os.path.join(root, dir_name))
    
    print("✅ 清理完成")

def main():
    """主函数"""
    print("🚀 ETC申办系统打包工具")
    print("=" * 50)
    
    # 检查当前目录和关键文件
    main_file = 'apps/etc_apply/main_window.py'
    
    if not os.path.exists(main_file):
        print("❌ 错误：请在项目根目录运行此脚本")
        print("   当前目录应该包含 apps/etc_apply/main_window.py 文件")
        return
    
    # 检查配置文件
    config_file = 'apps/etc_apply/config/etc_config.json'
    app_config_file = 'config/app_config.json'
    
    if not os.path.exists(config_file):
        print(f"❌ 错误：ETC配置文件不存在 {config_file}")
        return
        
    if not os.path.exists(app_config_file):
        print(f"⚠️  警告：全局配置文件不存在 {app_config_file}")
        print("   将跳过该配置文件的打包")
    
    print(f"✅ 找到ETC主文件: {main_file}")
    print(f"✅ 找到ETC配置文件: {config_file}")
    if os.path.exists(app_config_file):
        print(f"✅ 找到全局配置文件: {app_config_file}")
    
    # 检查关键模块是否存在
    critical_modules = [
        'apps/etc_apply/ui/rtx/ui_events.py',
        'apps/etc_apply/ui/rtx/ui_utils.py', 
        'apps/etc_apply/services/rtx/etc_service.py',
        'apps/etc_apply/services/hcb/truck_service.py',
        'common/config_util.py',
        'common/mysql_util.py'
    ]
    
    missing_modules = []
    for module in critical_modules:
        if not os.path.exists(module):
            missing_modules.append(module)
        else:
            print(f"✅ 关键模块存在: {module}")
    
    if missing_modules:
        print("\n⚠️  警告：以下关键模块缺失，可能影响打包:")
        for module in missing_modules:
            print(f"   - {module}")
        print()
    
    # 安装PyInstaller
    if not install_pyinstaller():
        return
    
    # 创建spec文件
    if not create_spec_file():
        return
    
    # 构建exe
    if build_exe():
        # 清理临时文件
        cleanup()
        
        print("\n🎉 打包完成！")
        print("📁 exe文件位置: dist/ETC申办系统.exe")
        print("\n💡 使用说明：")
        print("   - 确保配置文件 apps/etc_apply/config/etc_config.json 正确")
        print("   - 首次运行可能需要较长时间")
        print("   - 如果遇到问题，请检查网络连接和数据库配置")
        print("   - 建议在目标机器上测试运行")
        
        if missing_modules:
            print("\n⚠️  提醒：由于部分模块缺失，请测试所有功能是否正常")
    else:
        print("❌ 打包失败，请检查错误信息")

if __name__ == "__main__":
    main() 