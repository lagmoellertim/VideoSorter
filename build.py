import os
import sys

if len(sys.argv) > 1:
    if sys.argv[1] == "-c":
        consoleMode = True
    elif sys.argv[1] == "-w":
        consoleMode = False
    elif sys.argv[1] == "--help":
        print("-c : Console Mode\n-w : Windowed Mode")
        sys.exit()
    else:
        print("Unknown Argument\n\nPossibleArguments:\n\n-c : Console Mode\n-w : Windowed Mode")
else:
    consoleMode = False
if consoleMode == True:
    mode = "Console Mode"
else:
    mode = "Windowed Mode"
print("Building in "+mode)
specFileContent = """# -*- mode: python -*-
block_cipher = None
a = Analysis(['videosorter.py'],
             pathex=[''],
             binaries=None,
             datas=None,
             hiddenimports=['babelfish.converters.alpha3b',
             'babelfish.converters.alpha2',
             'babelfish.converters.alpha3t',
             'babelfish.converters.countryname',
             'babelfish.converters.name',
             'babelfish.converters.opensubtitles',
             'babelfish.converters.scope',
             'babelfish.converters.type'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries + Tree('data/babelfish', 'babelfish') + Tree('data/guessit', 'guessit') + Tree('data/videosorter', 'data/videosorter'),
          a.zipfiles,
          a.datas,
          name='VideoSorter',
          icon='data/videosorter/icon.ico',
          debug=False,
          strip=False,
          upx=True,
          console={})""".format(str(consoleMode))

specFile = open("videosorter.spec","w+")
specFile.writelines(specFileContent)
specFile.close()
os.system("pyinstaller videosorter.spec")
os.remove("videosorter.spec")