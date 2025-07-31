# -*- coding: utf-8 -*-
# -------------------------------------------------------------
# EXE 打包工具类，支持自动生成spec并一键打包，包含所有依赖目录
# -------------------------------------------------------------
import os
import subprocess
from typing import Optional

class ExeUtil:
    """
    EXE 打包工具类，支持自动生成spec并一键打包，包含所有依赖目录。
    """
    @staticmethod
    def generate_spec(main_script: str, exe_name: str = "main_win"):
        """
        自动生成 spec 文件，所有datas路径和spec文件都以项目根目录为基准，避免路径错误
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        def data_line(folder):
            abs_path = os.path.join(project_root, folder)
            abs_path_fixed = abs_path.replace('\\', '/')
            return f"('{abs_path_fixed}/*', '{folder}')"
        datas = ',\n        '.join([data_line(f) for f in ['config', 'common', 'worker', 'winform', 'lib', 'data']])
        main_script_fixed = main_script.replace('\\', '/')
        spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [r'{main_script_fixed}'],
    pathex=[],
    binaries=[],
    datas=[
        {datas}
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{exe_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=None
)
'''
        spec_path = os.path.join(project_root, f"{exe_name}.spec")
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(spec_content)
        return spec_path

    @staticmethod
    def pack_to_exe_with_spec(main_script: str, exe_name: str = "main_win"):
        """
        一键生成spec并用pyinstaller打包，自动修正主脚本为绝对路径
        """
        main_script = os.path.abspath(main_script)
        spec_path = ExeUtil.generate_spec(main_script, exe_name)
        subprocess.run(['pyinstaller', spec_path], check=True)

    @staticmethod
    def clean_pyinstaller_cache():
        """
        清理 pyinstaller 生成的 build、dist、spec 文件
        """
        for folder in ['build', 'dist']:
            if os.path.exists(folder):
                for root, dirs, files in os.walk(folder, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(folder)
        # 删除所有 .spec 文件
        for file in os.listdir(''):
            if file.endswith('.spec'):
                os.remove(file)

if __name__ == '__main__':
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_script = os.path.join(project_root, 'main', 'main.py')
    ExeUtil.pack_to_exe_with_spec(main_script, exe_name='main_win')