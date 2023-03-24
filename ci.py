#!/usr/bin/env python3

import os, sys, requests, yaml
from patch import patch

match sys.platform:
    case 'win32':
        build_tool_url: str = 'https://dl.google.com/android/repository/build-tools_r30-rc4-windows.zip'
        apk_signer: str = 'buildtools/android-R/apksigner.bat'
        apk_tool_url: str = 'https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/windows/apktool.bat'
        apktool: str = 'apktool/apktool.bat'
    case 'linux':
        build_tool_url: str = 'https://dl.google.com/android/repository/build-tools_r30-rc4-linux.zip'
        apk_signer: str = 'buildtools/android-R/apksigner'
        apk_tool_url: str = 'https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool'
        apktool: str = 'apktool/apktool'
    case 'darwin':
        build_tool_url: str = 'https://dl.google.com/android/repository/build-tools_r30-rc4-macosx.zip'
        apk_signer: str = 'buildtools/android-R/apksigner'
        apk_tool_url: str = 'https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/osx/apktool'
        apktool: str = 'apktool/apktool'
    case _:
        raise Exception('Unsupported platform')

if not os.path.exists('buildtools'):
    os.makedirs('buildtools')
    print('Downloading Android SDK Build Tools...')
    with open('buildtools.zip', 'wb') as f:
        f.write(requests.get(build_tool_url).content)
    import zipfile

    with zipfile.ZipFile('buildtools.zip', 'r') as zip_ref:
        zip_ref.extractall('buildtools')
    os.remove('buildtools.zip')

    if not sys.platform == 'win32':
        os.chmod(apk_signer, 0o755)

if not os.path.exists('apktool'):
    os.makedirs('apktool')
    print('Downloading apktool...')
    with open(apktool, 'wb') as f:
        f.write(requests.get(apk_tool_url).content)
    if not sys.platform == 'win32':
        os.chmod(apktool, 0o755)
    with open('apktool/apktool.jar', 'wb') as f:
        f.write(requests.get('https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.7.0.jar').content)

config: dict = yaml.safe_load(open('ci.yaml', 'r'))
version: str = config['version']
locales: list[str] = config['locales']
platforms: dict[str, str] = config['platforms']

for folder in ['original_packages', 'patched_packages']:
    if not os.path.exists(folder):
        os.makedirs(folder)

keystore_password: str | None = os.environ.get('KEYSTORE_PASSWORD')
source_api: str | None = os.environ.get('SOURCE_API')
target_api: str | None = os.environ.get('TARGET_API')
token_prefix: str | None = os.environ.get('TOKEN_PREFIX')

for platform in platforms:
    extension: str = platforms[platform].split('.')[-1]
    original_package_filename = os.path.join('original_packages', f'{platform}.{extension}')
    if not os.path.exists(original_package_filename):
        print(f'Downloading {platform} original package...')
        open(
            original_package_filename, 'wb'
        ).write(
            requests.get(platforms[platform]).content
        )
    for locale in locales:
        print(f'Patching {platform} with locale {locale}...')
        patch(
            platform=platform,
            package_orig_filename=os.path.join('original_packages', f'{platform}.{extension}'),
            output_dir='patched_packages',
            keystore_password=keystore_password,
            source_api=source_api,
            target_api=target_api,
            game_version=version,
            locale=locale,
            token_prefix=token_prefix,
            apksigner=apk_signer,
            apktool=apktool,
        )
