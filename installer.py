import PyInstaller.__main__

package_name = 'GPIO'
cv_path = '/usr/lib/python3/dist-packages/cv2/python-3.7'

PyInstaller.__main__.run([
    'main.py',
    '--name=%s' % package_name,
    '--onefile',
    '--windowed',
    # '--paths=%s' % cv_path,
])