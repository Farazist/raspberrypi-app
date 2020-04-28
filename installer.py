import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--hidden-import PySide2.QtXml',
    '--name=Farazist',
    '--onefile',
    '--windowed',
])