import PyInstaller.__main__

PyInstaller.__main__.run([
    'main2.py',
    '--hidden-import=PySide2.QtXml',
    '--name=Farazist',
    '--onedir',
    '--windowed',
])

# pyinstaller --onefile --windowed --hidden-import PySide2.QtXml main.py
