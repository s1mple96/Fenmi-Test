
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [r'E:/Fenmi-Test/main/main_win.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('E:/Fenmi-Test/config/*', 'config'),
        ('E:/Fenmi-Test/utils/*', 'utils'),
        ('E:/Fenmi-Test/worker/*', 'worker'),
        ('E:/Fenmi-Test/winform/*', 'winform'),
        ('E:/Fenmi-Test/lib/*', 'lib'),
        ('E:/Fenmi-Test/data/*', 'data')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
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
    name='main_win',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=None
)
