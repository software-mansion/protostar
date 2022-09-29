# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

import crypto_cpp_py

block_cipher = None
extra_files = [
    ("cairo", "cairo"),
    ('templates', 'templates'),
    ('runtime_constant_values.json', 'info'),
] + collect_data_files('starkware')
# Extra imports which are necessary for executing hints
extra_imports = [
        "eth_hash.auto",
        "certifi",
    ] + collect_submodules('starkware')

binaries = [(f"{crypto_cpp_py.__path__[0]}/../libcrypto_c_exports.*", ".")]

a = Analysis(['binary_entrypoint.py'],
             pathex=[],
             binaries=binaries,
             datas=extra_files,
             hiddenimports=extra_imports,
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='protostar',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='protostar')
