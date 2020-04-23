import PyInstaller.__main__

package_name = 'GPIO'

PyInstaller.__main__.run([
    'main.py',
    '--name=%s' % package_name,
    '--onefile',
    '--windowed',
])