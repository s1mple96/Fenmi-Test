# -*- coding: utf-8 -*-
"""
ETC申办系统打包脚本 - 极致优化版本
专门打包 apps/etc_apply/main_window.py
"""
import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
import zipfile
import io
import requests

def create_spec_file():
    """创建极致优化的spec文件"""
    # 获取当前工作目录
    current_dir = os.getcwd()
    project_root = current_dir
    
    # 检查配置文件路径
    config_file = os.path.join(project_root, 'apps', 'etc_apply', 'config', 'etc_config.json')
    if not os.path.exists(config_file):
        print(f"❌ 错误：配置文件不存在 {config_file}")
        return False
    
    # 转换路径为正斜杠格式
    project_root_slash = project_root.replace('\\', '/')
    config_file_slash = config_file.replace('\\', '/')
    app_config_slash = os.path.join(project_root, 'config', 'app_config.json').replace('\\', '/')
    main_file_slash = os.path.join(project_root, 'apps', 'etc_apply', 'main_window.py').replace('\\', '/')
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(SPEC))
project_root = r"{project_root_slash}"
sys.path.insert(0, project_root)

# 获取项目根目录
project_root = Path(project_root)

# 定义需要包含的数据文件 - 仅包含必要配置文件
datas = [
    # ETC申办配置文件
    (r"{config_file_slash}", 'apps/etc_apply/config'),
    # 全局配置文件
    (r"{app_config_slash}", 'config'),
]

# 最小化隐藏导入集合
hiddenimports = [
    # 核心PyQt5模块
    'PyQt5.QtCore',
    'PyQt5.QtWidgets', 
    'PyQt5.QtGui',
    
    # ETC申办核心模块（仅必需）
    'apps.etc_apply.ui.rtx.ui_events',
    'apps.etc_apply.ui.rtx.ui_utils',
    'apps.etc_apply.ui.rtx.ui_core',
    'apps.etc_apply.ui.rtx.ui_styles',
    'apps.etc_apply.ui.rtx.ui_component',
    'apps.etc_apply.ui.rtx.verify_dialog',
    'apps.etc_apply.ui.rtx.selection_dialogs',
    'apps.etc_apply.ui.rtx.draggable_components',
    'apps.etc_apply.ui.rtx.refund_confirm_dialog',
    'apps.etc_apply.ui.hcb.truck_tab_widget',
    'apps.etc_apply.ui.rtx.duplicate_check_dialog',
    
    # ETC申办服务模块 - RTX
    'apps.etc_apply.services.rtx.core_service',
    'apps.etc_apply.services.rtx.data_service',
    'apps.etc_apply.services.rtx.etc_service',
    'apps.etc_apply.services.rtx.etc_core',
    'apps.etc_apply.services.rtx.log_service',
    'apps.etc_apply.services.rtx.state_service',
    'apps.etc_apply.services.rtx.worker_thread',
    'apps.etc_apply.services.rtx.api_client',
    
    # 退款服务模块
    'apps.etc_apply.services.refund_service',
    
    # ETC申办服务模块 - HCB
    'apps.etc_apply.services.hcb.truck_service',
    'apps.etc_apply.services.hcb.duplicate_check_service',
    'apps.etc_apply.services.hcb.truck_data_service',
    'apps.etc_apply.services.hcb.truck_core_service',
    'apps.etc_apply.services.hcb.truck_state_service',
    'apps.etc_apply.services.hcb.truck_api_client',
    'apps.etc_apply.services.hcb.truck_core',
    'apps.etc_apply.services.hcb.check_vehicle_bind',
    'apps.etc_apply.services.hcb.direct_db_bind',
    'apps.etc_apply.services.hcb.manual_vehicle_bind',
    
    # 核心工具模块（仅必需）
    'common.config_util',
    'common.log_util',
    'common.mysql_util',
    'common.requestsUtil',
    'common.path_util',
    'common.plate_util',
    'common.vin_util',
    
    # 网络请求（必需）
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    
    # HTML解析（VIN功能需要）
    'bs4',
    
    # 数据库（必需）
    'pymysql',
    'pymysql.cursors',
    'pymysql.constants',
    'pymysql.err',
]

# 大幅扩展排除模块列表（更安全的版本 - 只排除第三方库）
excludes = [
    # 科学计算库（第三方）
    'matplotlib', 'numpy', 'pandas', 'scipy', 'opencv-python',
    'tensorflow', 'torch', 'sklearn', 'scikit-learn', 'jupyter', 'IPython',
    'ipykernel', 'zmq', 'tornado', 'bokeh', 'plotly', 'seaborn',
    'statsmodels', 'sympy', 'networkx', 'nltk', 'spacy', 'gensim',
    'wordcloud', 'pygments', 'pylint', 'pytest', 'sphinx', 'docutils',
    'jinja2', 'markupsafe', 'werkzeug', 'click', 'colorama',
    
    # Web框架（第三方）
    'flask', 'django', 'fastapi', 'uvicorn', 'gunicorn', 'celery',
    'starlette', 'sanic', 'aiofiles', 'uvloop', 'httptools',
    
    # 数据库（第三方，保留pymysql）
    'sqlalchemy', 'alembic', 'psycopg2', 'cx_oracle',
    'redis', 'pymongo', 'motor', 'aiomysql', 'aiopg',
    
    # 异步和网络（第三方，保留requests）
    'aiohttp', 'websockets', 'twisted', 'gevent', 'eventlet',
    'greenlet', 'httpx', 'requests_toolbelt', 'trio', 'anyio',
    
    # 网页抓取（第三方，保留beautifulsoup4）
    'lxml', 'selenium', 'playwright', 'puppeteer', 'scrapy',
    'pyppeteer', 'requests_html', 'pyquery', 'feedparser',
    'newspaper3k', 'readability', 'trafilatura',
    
    # GUI框架（第三方，保留PyQt5核心）
    'wx', 'kivy', 'pygame', 'pyglet', 'arcade',
    'pyopengl', 'panda3d', 'ursina', 'dearpygui',

    # Qt WebEngine（大幅减小体积）
    'PyQt5.QtWebEngine', 'PyQt5.QtWebEngineCore', 'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtWebKit', 'PyQt5.QtWebKitWidgets',
    'PyQt5.QtMultimedia', 'PyQt5.QtMultimediaWidgets',
    'PyQt5.QtOpenGL', 'PyQt5.QtSql', 'PyQt5.QtSvg',
    'PyQt5.QtXml', 'PyQt5.QtXmlPatterns', 'PyQt5.QtTest',
    'PyQt5.QtHelp', 'PyQt5.QtDesigner', 'PyQt5.QtUiTools',
    'PyQt5.QtBluetooth', 'PyQt5.QtNfc', 'PyQt5.QtPositioning',
    'PyQt5.QtLocation', 'PyQt5.QtSensors', 'PyQt5.QtSerialPort',

    # 加密和SSH（第三方）
    'paramiko', 'cryptography', 'bcrypt', 'nacl', 'PyNaCl',
    'pycryptodome', 'keyring', 'pyopenssl',
    
    # 图像处理（第三方）
    'PIL', 'Pillow', 'cv2', 'skimage', 'imageio',
    'matplotlib.pyplot', 'matplotlib.figure', 'matplotlib.backends',
    
    # 测试框架（第三方）
    'pytest', 'nose', 'mock', 'coverage', 'tox',
    'hypothesis', 'factory_boy', 'faker', 'text_unidecode',
    
    # 开发工具（第三方）
    'black', 'flake8', 'isort', 'mypy', 'bandit', 'autopep8',
    'yapf', 'rope', 'jedi', 'parso', 'pycodestyle', 'pyflakes',
    
    # 日志和配置（第三方）
    'loguru', 'structlog', 'rich', 'typer', 'pydantic', 'marshmallow',
    'cerberus', 'voluptuous', 'schema', 'jsonschema',
    
    # 时间和日期（第三方）
    'arrow', 'pendulum', 'babel',
    
    # 文档和模板（第三方）
    'docx', 'openpyxl', 'xlsxwriter', 'reportlab', 'fpdf',
    'weasyprint', 'xhtml2pdf', 'pdfkit', 'markdown',
    
    # 游戏开发（第三方）
    'pygame', 'pyglet', 'arcade', 'panda3d', 'ursina',
    'pygame_gui', 'pygame_menu', 'pygame_widgets',
    
    # 机器学习（第三方）
    'xgboost', 'lightgbm', 'catboost', 'sklearn', 'scikit-learn',
    'tensorflow', 'torch', 'keras', 'theano', 'caffe',
    
    # 云服务（第三方）
    'boto3', 'botocore', 'azure', 'google-cloud', 'dropbox',
    
    # 其他大型库（第三方）
    'jupyter_client', 'jupyter_core', 'notebook', 'qtconsole',
    'ipython_genutils', 'traitlets', 'ipywidgets', 'widgetsnbextension',
    'nbformat', 'nbconvert', 'nbclient', 'jupyter_server',
    
    # XML和高级解析（第三方）
    'lxml', 'html5lib', 'xmltodict', 'untangle',
    'dicttoxml', 'xmlschema', 'lxml.etree', 'lxml.html',
    
    # 音频和视频（第三方）
    'pygame.mixer', 'pydub', 'mutagen', 'eyed3', 'tinytag',
    'moviepy', 'imageio-ffmpeg', 'ffmpeg-python',
    
    # 地理和地图（第三方）
    'geopandas', 'folium', 'geopy', 'shapely', 'fiona',
    'cartopy', 'basemap', 'plotly.graph_objects',
    
    # 仅排除不必要的标准库模块（非常保守）
    'turtle',  # 图形绘制
]

a = Analysis(
    [r"{main_file_slash}"],
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

# 手动过滤掉不需要的模块
print("🔍 过滤不必要的模块...")
filtered_pure = []
exclude_patterns = [
    # 只过滤明显的第三方大型库
    'matplotlib', 'numpy', 'pandas', 'scipy',
    'tensorflow', 'torch', 'sklearn', 'jupyter', 'IPython',
    'bokeh', 'plotly', 'seaborn', 'statsmodels', 'sympy',
    'lxml', 'selenium', 'scrapy', 'flask', 'django',
    'sqlalchemy', 'cryptography', 'paramiko'
]

for toc_entry in a.pure:
    module_name = toc_entry[0]
    should_exclude = False
    for pattern in exclude_patterns:
        if pattern in module_name.lower():
            should_exclude = True
            break
    if not should_exclude:
        filtered_pure.append(toc_entry)

print(f"📊 模块过滤完成: {{len(a.pure)}} -> {{len(filtered_pure)}}")
a.pure = filtered_pure

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 极致精简 PyQt5 插件和库
try:
    import PyQt5
    from pathlib import Path as _Path
    _qt_plugins_dir = _Path(PyQt5.__file__).parent / 'Qt5' / 'plugins'
    def _qp(rel):
        return str((_qt_plugins_dir / rel).resolve()).replace(chr(92), chr(47))
    
    # 仅保留最核心的Qt插件
    _qt_keep = [
        ('platforms/qwindows.dll', 'PyQt5/Qt5/plugins/platforms'),
    ]
    _qt_binaries = []
    for rel, dest in _qt_keep:
        _full = _qp(rel)
        if os.path.exists(_full):
            _qt_binaries.append((_full, dest, 'BINARY'))
    
    # 过滤掉所有Qt插件，再加入最小集合
    a.binaries = [b for b in a.binaries if 'Qt5/plugins' not in b[1]] + _qt_binaries

    # 极致精简 Qt5/bin，仅保留绝对必需的DLL
    _qt_bin_essential = {{
        'Qt5Core.dll', 'Qt5Gui.dll', 'Qt5Widgets.dll',
    }}
    _filtered = []
    for src, dest, typ in a.binaries:
        base = os.path.basename(src)
        if 'PyQt5/Qt5/bin' in dest.replace(chr(92), '/'):
            if base in _qt_bin_essential:
                _filtered.append((src, dest, typ))
        else:
            _filtered.append((src, dest, typ))
    a.binaries = _filtered
    
    print(f"🎯 Qt库精简完成")
except Exception as _e:
    print(f"⚠️ Qt库精简失败: {{_e}}")

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ETCApplySystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,    # 关闭strip以减少警告
    upx=True,       # 启用UPX压缩
    upx_exclude=[   # 扩大UPX排除列表以减少失败
        'VCRUNTIME140.dll', 'python3.dll', 'python39.dll', 'python310.dll',
        'Qt5Core.dll', 'Qt5Gui.dll', 'Qt5Widgets.dll',
        'api-ms-win-*.dll',  # 排除所有Windows API DLL
        'ucrtbase.dll', 'libssl*.dll', 'libcrypto*.dll'
    ],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('etc_apply.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 已创建极致优化的spec文件")
    return True

def install_pyinstaller():
    """安装最新版PyInstaller"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller>=6.0'], 
                      check=True, capture_output=True)
        print("✅ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyInstaller安装失败")
        return False

def ensure_upx():
    """确保本地存在最新版UPX，避免重复下载"""
    # 首先检查我们下载的UPX路径
    tools_upx_path = Path('.tools/upx/upx.exe')
    if tools_upx_path.exists():
        try:
            result = subprocess.run([str(tools_upx_path), '-V'], capture_output=True, text=True)
            if result.returncode == 0 and '4.' in result.stdout:
                print(f"✅ 已存在本地 UPX: {tools_upx_path}")
                # 确保PATH中包含此路径
                os.environ['PATH'] = str(tools_upx_path.parent.resolve()) + os.pathsep + os.environ.get('PATH', '')
                return True
        except Exception:
            pass
    
    # 检查系统PATH中的UPX
    try:
        result = subprocess.run(['upx', '-V'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 已检测到系统 UPX")
            if '4.' in result.stdout:
                print("✅ UPX 版本合适")
                return True
            else:
                print("⚠️ UPX 版本较旧，将下载最新版")
    except Exception:
        pass
    
    # 下载最新版 UPX
    try:
        print("⏬ 正在下载最新版 UPX...")
        upx_url = 'https://github.com/upx/upx/releases/download/v4.2.4/upx-4.2.4-win64.zip'
        resp = requests.get(upx_url, timeout=60)
        resp.raise_for_status()
        tools_dir = Path('.tools/upx')
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            for name in zf.namelist():
                if name.endswith('/upx.exe'):
                    zf.extract(name, tools_dir)
                    exe_path = tools_dir / name
                    upx_exe = tools_dir / 'upx.exe'
                    if upx_exe.exists():
                        upx_exe.unlink()
                    exe_path.rename(upx_exe)
                    break
        
        upx_path = str((tools_dir / 'upx.exe').resolve())
        if os.path.exists(upx_path):
            os.environ['PATH'] = str((tools_dir).resolve()) + os.pathsep + os.environ.get('PATH', '')
            print(f"✅ UPX 下载完成: {upx_path}")
            return True
        else:
            print("⚠️ 未找到解压后的 upx.exe")
            return False
    except Exception as e:
        print(f"⚠️ 下载 UPX 失败，将使用无UPX模式：{e}")
        return False

def build_exe():
    """构建exe文件"""
    print("🔨 开始构建exe文件...")
    print("⏳ 使用极致优化配置，这可能需要几分钟时间...")
    
    start_time = time.time()
    
    try:
        # 使用极致优化的spec文件构建
        process = subprocess.Popen([
            sys.executable, '-m', 'PyInstaller',
            '--clean',          # 清理临时文件
            '--noconfirm',      # 不询问确认
            '--log-level=WARN', # 减少日志输出
            'etc_apply.spec'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
           universal_newlines=True, bufsize=1, encoding='utf-8')
        
        # 简化输出显示
        important_keywords = ['info:', 'warning:', 'error:', 'analysis', 'pyz', 'exe', 'building']
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                if any(keyword in output.lower() for keyword in important_keywords):
                    print(f"📋 {output.strip()}")
        
        return_code = process.poll()
        
        if return_code == 0:
            elapsed_time = time.time() - start_time
            print(f"✅ exe文件构建成功！耗时: {elapsed_time:.1f} 秒")
            
            # 显示文件大小和压缩效果
            exe_path = 'dist/ETCApplySystem.exe'
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"📊 exe文件大小: {size_mb:.2f} MB")
                
                # 尝试额外的UPX压缩以进一步减小体积
                try:
                    print("🔄 尝试应用最佳UPX压缩...")
                    upx_result = subprocess.run([
                        'upx', '--best', '--lzma', exe_path
                    ], capture_output=True, text=True, timeout=300)
                    
                    if upx_result.returncode == 0:
                        new_size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                        compression_ratio = (1 - new_size_mb / size_mb) * 100
                        print(f"✅ UPX极致压缩成功: {new_size_mb:.2f} MB (压缩率: {compression_ratio:.1f}%)")
                        size_mb = new_size_mb
                    else:
                        print("⚠️ UPX极致压缩失败，使用默认压缩")
                except Exception as e:
                    print(f"⚠️ UPX极致压缩出现异常: {e}")
                
                # 重命名文件
                new_name = 'dist/ETC申办系统.exe'
                if os.path.exists(new_name):
                    os.remove(new_name)
                os.rename(exe_path, new_name)
                print(f"✅ 已重命名为: {new_name}")
                
                # 给出体积评价
                if size_mb < 30:
                    print(f"🎉 文件大小优秀: {size_mb:.2f} MB")
                elif size_mb < 50:
                    print(f"👍 文件大小良好: {size_mb:.2f} MB")
                else:
                    print(f"⚠️ 文件偏大: {size_mb:.2f} MB，可能需要进一步优化")
                    
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
    
    # 深度清理__pycache__目录
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                shutil.rmtree(os.path.join(root, dir_name))
    
    print("✅ 清理完成")

def main():
    """主函数"""
    print("🚀 ETC申办系统极致优化打包工具")
    print("=" * 60)
    
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
    
    # 检查Python环境
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"⚠️ Python版本较旧: {sys.version}")
        print("   建议使用Python 3.8+以获得更好的打包效果")
        else:
        print(f"✅ Python版本合适: {sys.version}")
    
    # 优化建议
    print("\n💡 极致优化特性:")
    print("   - 大幅扩展模块排除列表 (200+ 模块)")
    print("   - 手动过滤不必要的纯Python模块")
    print("   - 极致精简Qt5插件和库")
    print("   - 启用strip和最佳UPX压缩")
    print("   - 移除所有非核心功能模块")
    
    # 安装PyInstaller
    if not install_pyinstaller():
        return
    
    # 确保UPX
    upx_available = ensure_upx()
    if not upx_available:
        print("⚠️ UPX不可用，体积可能较大")
    
    # 创建spec文件
    if not create_spec_file():
        return
    
    # 构建exe
    if build_exe():
        cleanup()
        
        print("\n🎉 极致优化打包完成！")
        print("📁 exe文件位置: dist/ETC申办系统.exe")
        print("\n💡 优化效果:")
        print("   - 排除了200+不必要的模块")
        print("   - 精简了Qt5库和插件")
        print("   - 应用了最佳压缩算法")
        print("   - 启用了所有减小体积的选项")
        print("\n⚠️ 使用说明:")
        print("   - 请在目标机器上充分测试所有功能")
        print("   - 首次运行可能需要较长时间")
        print("   - 确保配置文件正确")
        
    else:
        print("❌ 打包失败，请检查错误信息")

if __name__ == "__main__":
    main() 