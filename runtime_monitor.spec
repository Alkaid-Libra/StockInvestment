# -*- mode: python ; coding: utf-8 -*-
# from PyInstaller.utils.hooks import collect_dynamic_libs
# binaries = collect_dynamic_libs('py_mini_racer')
a = Analysis(
    ['runtime_monitor.py'],
    pathex=[],
    binaries=[],
    datas=[('D:/ProgramFiles/Miniconda/envs/finance/Lib/site-packages/akshare/file_fold', 'akshare/file_fold'),
    ('D:/ProgramFiles/Miniconda/envs/finance/Lib/site-packages/py_mini_racer/mini_racer.dll', '.'),
    ('D:/ProgramFiles/Miniconda/envs/finance/Lib/site-packages/py_mini_racer/icudtl.dat', '.'),
    ('D:/ProgramFiles/Miniconda/envs/finance/Lib/site-packages/py_mini_racer/snapshot_blob.bin', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='runtime_monitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='iu_runtime_monitor_icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='runtime_monitor',
)
