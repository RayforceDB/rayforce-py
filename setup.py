import os
from setuptools import setup, Extension

current_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(current_dir, 'raypy')

rayforce_module = Extension(
    'raypy._rayforce',
    sources=['raypy/rayforce.c'],
    libraries=['rayforce'],
    library_dirs=['raypy/'],
    include_dirs=['raypy/core'],
    extra_compile_args=['-fPIC'],
    extra_link_args=['-Wl,-rpath,' + lib_path]
)

setup(
    name='raypy',
    version='0.1',
    ext_modules=[rayforce_module],
)
