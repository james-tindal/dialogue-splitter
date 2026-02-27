# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

ffmpeg_lib = '/usr/local/Cellar/ffmpeg/7.1_4/lib'
ffmpeg_binaries = []
for f in os.listdir(ffmpeg_lib):
    if f.endswith('.dylib'):
        ffmpeg_binaries.append((os.path.join(ffmpeg_lib, f), '.'))

# Collect all from audio_separator and its dependencies
datas_audio, binaries_audio, hiddenimports_audio = collect_all('audio_separator')
datas_onnx, binaries_onnx, hiddenimports_onnx = collect_all('onnxruntime')
datas_torch, binaries_torch, hiddenimports_torch = collect_all('torch')
datas_torchaudio, binaries_torchaudio, hiddenimports_torchaudio = collect_all('torchaudio')
datas_librosa, binaries_librosa, hiddenimports_librosa = collect_all('librosa')

# Combine everything
datas = datas_audio + datas_onnx + datas_torch + datas_torchaudio + datas_librosa + [('resources', 'resources')]
binaries = binaries_audio + binaries_onnx + binaries_torch + binaries_torchaudio + binaries_librosa + [('/usr/local/bin/ffmpeg', '.')] + ffmpeg_binaries
hiddenimports = hiddenimports_audio + hiddenimports_onnx + hiddenimports_torch + hiddenimports_torchaudio + hiddenimports_librosa + ['importlib.metadata']

a = Analysis(
    ['src/dialogue_splitter_gui.py'],
    pathex=['src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='Dialogue Splitter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Dialogue Splitter',
)
app = BUNDLE(
    coll,
    name='Dialogue Splitter.app',
    bundle_identifier='com.dialogue-splitter.app',
    icon='resources/logo.png',
    info_plist={
        'CFBundleName': 'Dialogue Splitter',
        'CFBundleDisplayName': 'Dialogue Splitter',
        'CFBundleIdentifier': 'com.dialogue-splitter.app',
        'CFBundleVersion': '1.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleExecutable': 'Dialogue Splitter',
        'LSMinimumSystemVersion': '10.13',
        'NSPrincipalClass': 'NSApplication',
        'LSEnvironment': {
            'PATH': '@executable_path/../Frameworks'
        },
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Video File',
                'CFBundleTypeRole': 'Viewer',
                'LSHandlerRank': 'Alternate',
                'LSItemContentTypes': [
                    'public.movie',
                    'public.video',
                    'com.apple.quicktime-movie',
                    'public.mpeg-4',
                    'public.avi',
                ],
            },
        ],
    },
)
