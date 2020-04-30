import PyInstaller.__main__

package_name = 'Farazist'

PyInstaller.__main__.run([
    'main.py',
    '--hidden-import=PySide2.QtXml',
    '--name=%s' % package_name,
    '--onefile',
    '--windowed',
])

# pyinstaller --onefile --windowed --hidden-import PySide2.QtXml main.py