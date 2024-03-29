import PyInstaller.__main__
import platform

SYS_OS = platform.system()
SYS_ARCH = platform.architecture()[0][:2]
suffix = f"{'_macos' if SYS_OS == 'Darwin' else ''}{'_x86' if SYS_ARCH == '32' else ''}{'.exe' if SYS_OS == 'Windows' else ''}"

def main():
    opts = [
        'sv_dlp/__main__.py',
        '--onefile',
        f'--name=sv-dlp{suffix}',
        '--icon=docs/icon.ico',
        '--distpath=dist/bin',
    ]

    print(f"Building sv-dlp for platform {SYS_OS} with architecture {SYS_ARCH}")
    PyInstaller.__main__.run(opts)

if __name__ == '__main__':
    main()