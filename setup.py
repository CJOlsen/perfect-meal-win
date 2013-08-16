from distutils.core import setup
import py2exe

from glob import glob
data_files = [("", glob(r'C:\Users\cj\Desktop\perfect-meal-master\foods-2011-10-03.json'))]

setup(
    data_files=data_files,
    options = {'py2exe': {'bundle_files': 1}},
    windows = [{'script': 'perfectmeal_gui.py'}],
    zipfile = None,
)

