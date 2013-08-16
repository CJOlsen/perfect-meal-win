from distutils.core import setup
import py2exe

from glob import glob
data_files = [("Microsoft.VC90.CRT",
               glob(r'C:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*')),
              ("", glob(r'C:\Users\cj\Desktop\perfect-meal-master\foods-2011-10-03.json'))]

setup(
    data_files=data_files,
    options = {'py2exe': {'bundle_files': 1}},
    windows = [{'script': 'perfectmeal_gui.py'}],
    zipfile = None,
)

#setup(windows=['perfectmeal_gui.py'],)
      #zipfile = r"library.zip",)
