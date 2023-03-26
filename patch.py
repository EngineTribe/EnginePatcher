# !/usr/bin/env python3

import yaml, os, math, shutil, subprocess, py7zr


def patch(
        package_orig_filename: str,
        platform: str,
        output_dir: str,
        keystore_password: str,
        game_version: str,
        locale: str,
        source_api: str,
        target_api: str,
        token_prefix: str,
        apksigner: str,
        apktool: str
):
    if os.path.exists('working'):
        shutil.rmtree('working')
    os.makedirs('working')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def extract_package_windows():
        process = subprocess.Popen(
            ['7z', 'x', '-y', '-o' + os.path.join('working'), package_orig_filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.wait()

    def strip_package_windows():
        for file in ['$PLUGINSDIR', '$TEMP']:
            if os.path.exists(os.path.join('working', file)):
                shutil.rmtree(
                    os.path.join('working', file),
                )
        for file in ['uninst.exe', 'unins000.dat', 'unins000.exe']:
            if os.path.exists(os.path.join('working', file)):
                os.remove(
                    os.path.join('working', file),
                )
        if os.path.exists(os.path.join('working', 'SMM-WE.exe')):
            os.rename(
                os.path.join('working', 'SMM-WE.exe'),
                os.path.join('working', 'SMM_WE.exe')
            )
        if os.path.exists(os.path.join('working', '${SMM_WE}.exe')):
            os.rename(
                os.path.join('working', '${SMM_WE}.exe'),
                os.path.join('working', 'SMM_WE.exe')
            )
        if not os.path.exists(os.path.join('working', 'splash.png')):
            shutil.copyfile(
                os.path.join('splash.png'),
                os.path.join('working', 'splash.png')
            )
        shutil.copyfile(
            os.path.join('fonts', 'fontcjk.ttf'),
            os.path.join('working', 'fontcjk.ttf')
        )
        if os.path.exists(os.path.join('working', 'font_as.ttf')):
            os.remove(
                os.path.join('working', 'font_as.ttf'),
            )

    def game_executable_filename_windows() -> list[str]:
        return ['data.win'] if os.path.exists(os.path.join('working', 'data.win')) else ['SMM_WE.exe']

    def output_package_filename_windows() -> str:
        return f'SMM_WE_EngineTribe_{game_version}_PC_{locale}.7z'

    def repack_windows():
        archive_filename = os.path.join(output_dir, output_package_filename_windows())
        archive = py7zr.SevenZipFile(archive_filename, 'w')
        archive.writeall('working')
        archive.close()

    def extract_package_android():
        process = subprocess.Popen(
            [
                apktool,
                'd',
                '-f',
                '-o',
                os.path.join('working'),
                package_orig_filename
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.wait()

    def strip_package_android():
        shutil.copyfile(
            os.path.join('fonts', 'fontcjk.ttf'),
            os.path.join('working', 'assets', 'fontcjk.ttf')
        )
        if os.path.exists(os.path.join('working', 'assets', 'font_as.ttf')):
            os.remove(
                os.path.join('working', 'assets', 'font_as.ttf'),
            )
        # ignore "!!"
        apktool_yaml = yaml.load(
            '\n'.join(open(os.path.join('working', 'apktool.yml'), 'r').readlines()[1:]),
            Loader=yaml.FullLoader,

        )
        version_name = apktool_yaml['versionInfo']['versionName']
        if 'ET' not in version_name:
            version_name = version_name + f' ET {game_version}'
        apktool_yaml['versionInfo']['versionName'] = version_name
        open(os.path.join('working', 'apktool.yml'), 'w').write(
            f'!!brut.androlib.meta.MetaInfo\n' +
            yaml.dump(apktool_yaml)
        )

    def game_executable_filename_android() -> list[str]:
        size = os.path.getsize(os.path.join('working', 'lib', 'arm64-v8a', 'libyoyo.so'))
        return [
            'lib/armeabi-v7a/libyoyo.so',
            'lib/arm64-v8a/libyoyo.so',
        ] if size > 9 * 1024 * 1024 else [
            'assets/game.droid'
        ]

    def output_package_filename_android() -> str:
        return f'SMM_WE_EngineTribe_{game_version}_Android_{locale}.apk'

    def repack_android():
        filename = os.path.join(output_dir, output_package_filename_android())
        process = subprocess.Popen(
            [
                apktool,
                'b',
                '-o',
                filename,
                os.path.join('working')
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.wait()
        process = subprocess.Popen(
            [
                apksigner,
                'sign',
                '--ks',
                'keystore/enginetribe.keystore',
                '--ks-key-alias',
                'EngineTribe',
                filename
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        process.communicate(input=keystore_password.encode('utf-8'))
        process.wait()

    match platform:
        case 'PC':
            extract_package = extract_package_windows
            strip_package = strip_package_windows
            game_executable_filenames = game_executable_filename_windows
            output_package_filename = output_package_filename_windows
            repack = repack_windows
        case 'MB':
            extract_package = extract_package_android
            strip_package = strip_package_android
            game_executable_filenames = game_executable_filename_android
            output_package_filename = output_package_filename_android
            repack = repack_android
        case _:
            raise Exception('Unsupported platform (PC/MB)')
    if os.path.exists(os.path.join(output_dir, output_package_filename())):
        print('Package already patched, skipping...')
        return
    print('  Extracting package...')
    extract_package()
    print('  Stripping package...')
    strip_package()
    for game_executable_filename in game_executable_filenames():
        print('  Replacing strings for', game_executable_filename)
        tokens: list[str] = yaml.safe_load(open('tokens.yaml', 'r'))['tokens']
        token: str = f'{token_prefix}{platform}{locale}'.upper()
        locale_file = yaml.safe_load(open(f'locales/{locale}.yaml', 'r'))
        whitelist: list[str] = yaml.safe_load(open('whitelist.yaml', 'r'))['whitelist']
        package: bytes = open(os.path.join('working', game_executable_filename), 'rb').read()

        for key in locale_file:
            original_key: bytes = key.encode('utf-8')
            replaced_key: bytes = locale_file[key].encode('utf-8')
            if len(original_key) < len(replaced_key):
                raise Exception(f'Original string {original_key} is longer than replaced string {replaced_key}')
            elif len(original_key) == len(replaced_key):
                if key in whitelist:
                    package = package.replace(original_key, replaced_key)
                else:
                    package = package.replace(original_key, replaced_key, 1)
            else:
                left_padding: bytes = bytes((' ' * math.floor((len(original_key) - len(replaced_key)) / 2)).encode())
                right_padding: bytes = bytes((' ' * math.ceil((len(original_key) - len(replaced_key)) / 2)).encode())
                if key in whitelist:
                    package = package.replace(original_key, left_padding + replaced_key + right_padding)
                else:
                    package = package.replace(original_key, left_padding + replaced_key + right_padding, 1)
        for key in tokens:
            package = package.replace(key.encode(), token.encode())
        package = package.replace(source_api.encode(), target_api.encode())
        print('  Writing game executable...')
        open(os.path.join('working', game_executable_filename), 'wb').write(package)
    print('  Repacking package...')
    repack()

    print('Done for', platform, locale, game_version, package_orig_filename, output_package_filename())


if __name__ == '__main__':
    package_orig_filename: str | None = os.environ.get('ORIGINAL_PACKAGE_FILENAME')
    keystore_password: str | None = os.environ.get('KEYSTORE_PASSWORD')
    game_version: str | None = os.environ.get('GAME_VERSION')
    locale: str | None = os.environ.get('LOCALE')
    source_api: str | None = os.environ.get('SOURCE_API')
    target_api: str | None = os.environ.get('TARGET_API')
    token_prefix: str | None = os.environ.get('TOKEN_PREFIX')
    platform: str | None = os.environ.get('PLATFORM')
    apksigner: str = os.environ.get('APKSIGNER', 'apksigner')
    apktool: str = os.environ.get('APKTOOL', 'apktool')
    output_dir: str = os.environ.get('OUTPUT_DIR', 'output')
    patch(
        package_orig_filename,
        platform,
        output_dir,
        keystore_password,
        game_version,
        locale,
        source_api,
        target_api,
        token_prefix,
        apksigner,
        apktool
    )
