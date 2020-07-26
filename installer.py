import PyInstaller.__main__

PyInstaller.__main__.run([
    'test/myPrinter.py',
    # '--hidden-import=PySide2.QtXml',
    '--name=Farazist',
    '--onedir',
    # '--windowed',
])

# pyinstaller --onefile --windowed --hidden-import PySide2.QtXml main.py
