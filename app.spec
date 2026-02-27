# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/dialogue_splitter_gui.py'],
    pathex=['src'],
    binaries=[],
    datas=[('resources', 'resources')],
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
